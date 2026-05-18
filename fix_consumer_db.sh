#!/bin/bash
# fix_consumer_db.sh - запускать из ~/news_analyzer
cat > services/output_module/src/services/notification_consumer.py << 'PYEOF'
"""
Notification Consumer — использует синхронный psycopg2 (async engine не нужен,
consumer и так работает в asyncio через run_in_executor для блокирующих операций).
"""
import asyncio
import json
import logging
from typing import List, Dict, Optional

from aiokafka import AIOKafkaConsumer
from sqlalchemy import create_engine, select, and_, or_
from sqlalchemy.orm import sessionmaker

from src.infrastructure.postgres.models import (
    NotificationTrigger,
    NotificationChannel,
    NotificationSettings,
)
from src.services.email_service import get_email_service

logger = logging.getLogger(__name__)


class NotificationConsumer:
    def __init__(
        self,
        database_url: str,
        kafka_bootstrap_servers: str,
        kafka_input_topic: str = "articles_analyzed",
        kafka_group_id: str = "notifications-sender-group",
    ):
        self.database_url = database_url
        self.kafka_bootstrap_servers = kafka_bootstrap_servers
        self.kafka_input_topic = kafka_input_topic
        self.kafka_group_id = kafka_group_id

        # Синхронный движок — psycopg2 не требует asyncpg
        db_url = database_url
        if "+asyncpg" in db_url:
            db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)

        self.engine = create_engine(db_url, pool_pre_ping=True, pool_size=5)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.consumer = None
        self.email_service = get_email_service()

    async def initialize(self):
        logger.info("Инициализация Notification Consumer...")

        self.consumer = AIOKafkaConsumer(
            self.kafka_input_topic,
            bootstrap_servers=self.kafka_bootstrap_servers,
            group_id=self.kafka_group_id,
            auto_offset_reset="earliest",
            max_poll_records=10,
            session_timeout_ms=30000,
        )
        await self.consumer.start()
        logger.info("✅ Kafka Consumer запущен. Топик: %s", self.kafka_input_topic)

        if self.email_service.is_configured():
            logger.info("✅ Email relay: %s:%s", self.email_service.smtp_host, self.email_service.smtp_port)
        else:
            logger.warning("⚠️  Email relay не настроен")

    async def shutdown(self):
        if self.consumer:
            await self.consumer.stop()
        if self.engine:
            self.engine.dispose()
        logger.info("Notification Consumer остановлен")

    async def run(self):
        try:
            await self.initialize()
            async for message in self.consumer:
                try:
                    await self._process_message(message)
                except Exception as e:
                    logger.error("❌ Ошибка обработки сообщения: %s", e, exc_info=True)
        except Exception as e:
            logger.error("❌ Критическая ошибка consumer: %s", e, exc_info=True)
            raise
        finally:
            await self.shutdown()

    async def _process_message(self, message):
        try:
            data = json.loads(message.value.decode("utf-8"))
        except Exception:
            return

        article_id = data.get("id") or data.get("post_id") or data.get("article_id")
        article_entities = data.get("entities", [])
        article_title = data.get("title", "Новая статья")
        article_summary = (data.get("summary") or data.get("text", ""))[:500]
        article_link = data.get("link") or data.get("url")
        risk_level = data.get("risk_level", "low")
        sentiment = data.get("sentiment_label", "neutral")

        if not article_entities:
            return

        logger.info("📬 Статья %s: %d сущностей", article_id, len(article_entities))

        # Запускаем синхронную работу с БД в executor
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            self._handle_entities_sync,
            article_entities, article_id, article_title,
            article_summary, article_link, risk_level, sentiment,
        )

    def _handle_entities_sync(
        self, entities, article_id, article_title,
        article_summary, article_link, risk_level, sentiment,
    ):
        """Синхронная часть — работа с БД через psycopg2."""
        session = self.SessionLocal()
        try:
            entity_ids_str = [str(e["id"]) for e in entities if "id" in e]
            entity_names = [
                e.get("name", e.get("text", "")).lower().strip()
                for e in entities
                if e.get("name") or e.get("text")
            ]

            if not entity_ids_str and not entity_names:
                return

            conditions = []
            if entity_ids_str:
                conditions.append(NotificationTrigger.trigger_value.in_(entity_ids_str))
            for name in entity_names:
                if name:
                    conditions.append(NotificationTrigger.trigger_value.ilike(f"%{name}%"))

            if not conditions:
                return

            triggers = session.execute(
                select(NotificationTrigger).where(
                    and_(
                        NotificationTrigger.trigger_type.in_(
                            ["entity", "organization", "person", "ORG", "PER"]
                        ),
                        or_(*conditions),
                        NotificationTrigger.enabled == True,
                    )
                )
            ).scalars().all()

            if not triggers:
                logger.debug("⏭️  Нет триггеров для сущностей")
                return

            logger.info("🔔 Найдено %d триггеров", len(triggers))

            users: Dict[int, List] = {}
            for t in triggers:
                users.setdefault(t.user_id, []).append(t)

            for user_id, user_triggers in users.items():
                self._send_to_user_sync(
                    session, user_id, user_triggers, article_id,
                    article_title, article_summary, article_link,
                    entities, risk_level, sentiment,
                )
        finally:
            session.close()

    def _send_to_user_sync(
        self, session, user_id, triggers, article_id,
        article_title, article_summary, article_link,
        entities, risk_level, sentiment,
    ):
        try:
            channel = session.execute(
                select(NotificationChannel).where(
                    and_(
                        NotificationChannel.user_id == user_id,
                        NotificationChannel.channel_type == "email",
                        NotificationChannel.enabled == True,
                    )
                )
            ).scalars().first()

            if not channel or not channel.channel_address:
                return

            settings = session.execute(
                select(NotificationSettings).where(
                    NotificationSettings.user_id == user_id
                )
            ).scalars().first()

            if settings and not settings.enabled:
                return

            trigger = triggers[0]
            trigger_value = trigger.trigger_value

            matched_entity = None
            for e in entities:
                name = e.get("name") or e.get("text") or ""
                if (
                    trigger_value == str(e.get("id", ""))
                    or trigger_value.lower() in name.lower()
                    or name.lower() in trigger_value.lower()
                ):
                    matched_entity = e
                    break
            if not matched_entity:
                matched_entity = entities[0] if entities else {}

            entity_name = matched_entity.get("name") or matched_entity.get("text") or trigger_value
            entity_type_raw = matched_entity.get("type") or matched_entity.get("entity_type") or "ORG"
            entity_type = "organization" if entity_type_raw in ("ORG", "organization") else "person"

            subject = f"🔔 Упоминание: {entity_name}"
            if len(triggers) > 1:
                subject += f" (+{len(triggers)-1} ещё)"

            # Синхронная отправка
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText

            html = self.email_service._build_html(
                article_title=article_title,
                article_summary=article_summary,
                article_link=article_link,
                entity_name=entity_name,
                entity_type=entity_type,
                risk_level=risk_level,
                sentiment=sentiment,
            )

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.email_service.from_name} <{self.email_service.from_email}>"
            msg["To"] = channel.channel_address
            msg.attach(MIMEText(html, "html", "utf-8"))

            with smtplib.SMTP(self.email_service.smtp_host, self.email_service.smtp_port, timeout=30) as srv:
                srv.send_message(msg)

            logger.info(
                "✅ Email → %s (user=%s, сущность=%s)",
                channel.channel_address, user_id, entity_name,
            )
        except Exception as e:
            logger.error("❌ Ошибка отправки user %s: %s", user_id, e)


async def run_notification_consumer(
    database_url: str,
    kafka_bootstrap_servers: str,
    kafka_input_topic: str = "articles_analyzed",
    kafka_group_id: str = "notifications-sender-group",
):
    consumer = NotificationConsumer(
        database_url=database_url,
        kafka_bootstrap_servers=kafka_bootstrap_servers,
        kafka_input_topic=kafka_input_topic,
        kafka_group_id=kafka_group_id,
    )
    try:
        await consumer.run()
    except KeyboardInterrupt:
        await consumer.shutdown()
PYEOF

echo "✅ notification_consumer.py обновлён"

echo ""
echo "=== Перезапускаем notification-consumer ==="
docker compose up -d --no-deps --force-recreate notification-consumer
sleep 6

echo ""
echo "=== Логи (последние 20 строк) ==="
docker compose logs notification-consumer --tail=20

echo ""
echo "=== Проверяем relay ==="
docker exec notification-consumer python3 -c "
import smtplib
try:
    s = smtplib.SMTP('mailrelay', 25, timeout=10)
    print('✅ Postfix relay доступен!')
    s.quit()
except Exception as e:
    print(f'❌ {e}')
"
