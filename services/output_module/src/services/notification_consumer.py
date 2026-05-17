"""
ИСПРАВЛЕНО:
1. Поиск триггеров теперь работает по ИМЕНИ сущности (trigger_value = имя),
   а не только по числовому ID — так работает UI на странице /notifications
2. Добавлена поддержка trigger_type="entity" (универсальный тип из UI)
3. Исправлена логика: если пользователь добавил сущность через UI, триггер
   создаётся с trigger_value = название сущности, а не её ID в БД
4. Добавлено логирование для диагностики
"""
import asyncio
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime

from aiokafka import AIOKafkaConsumer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, and_, or_

from src.infrastructure.postgres.models import (
    NotificationTrigger,
    NotificationChannel,
    NotificationSettings,
    Article,
    User,
)
from src.services.email_service import get_email_service

logger = logging.getLogger(__name__)


class NotificationConsumer:
    """Consumer для обработки статей и отправки уведомлений при упоминании сущностей"""

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

        self.engine = None
        self.AsyncSessionLocal = None
        self.consumer = None
        self.email_service = get_email_service()

    async def initialize(self):
        logger.info("Инициализация Notification Consumer...")

        self.engine = create_async_engine(
            self.database_url,
            echo=False,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
        )
        self.AsyncSessionLocal = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

        self.consumer = AIOKafkaConsumer(
            self.kafka_input_topic,
            bootstrap_servers=self.kafka_bootstrap_servers,
            group_id=self.kafka_group_id,
            auto_offset_reset="earliest",
            max_poll_records=10,
            session_timeout_ms=30000,
        )

        await self.consumer.start()
        logger.info(f"✅ Kafka Consumer запущен. Топик: {self.kafka_input_topic}")

        if self.email_service.is_configured():
            logger.info(
                f"✅ Email сервис настроен: {self.email_service.smtp_username}"
            )
        else:
            logger.warning(
                "⚠️  Email сервис НЕ настроен — уведомления не будут отправляться. "
                "Задайте SMTP_USERNAME и SMTP_PASSWORD в .env"
            )

    async def shutdown(self):
        if self.consumer:
            await self.consumer.stop()
        if self.engine:
            await self.engine.dispose()
        logger.info("Notification Consumer остановлен")

    async def run(self):
        try:
            await self.initialize()
            async for message in self.consumer:
                try:
                    await self._process_message(message)
                except Exception as e:
                    logger.error(f"❌ Ошибка обработки сообщения: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"❌ Критическая ошибка consumer: {e}", exc_info=True)
            raise
        finally:
            await self.shutdown()

    async def _process_message(self, message):
        """Обработать одну статью из Kafka"""
        try:
            data = json.loads(message.value.decode("utf-8"))

            article_id = data.get("id") or data.get("post_id") or data.get("article_id")
            article_entities = data.get("entities", [])
            article_title = data.get("title", "Новая статья")
            article_summary = (data.get("summary") or data.get("text", ""))[:500]
            article_link = data.get("link") or data.get("url")
            risk_level = data.get("risk_level", "low")
            sentiment = data.get("sentiment_label", "neutral")

            if not article_entities:
                logger.debug("⏭️  Нет сущностей в статье, пропускаю")
                return

            logger.info(
                f"📬 Статья {article_id}: {len(article_entities)} сущностей, "
                f"risk={risk_level}, sentiment={sentiment}"
            )

            await self._send_notifications_for_entities(
                entities=article_entities,
                article_id=article_id,
                article_title=article_title,
                article_summary=article_summary,
                article_link=article_link,
                risk_level=risk_level,
                sentiment=sentiment,
            )

        except json.JSONDecodeError as e:
            logger.error(f"❌ Невалидный JSON: {e}")
        except Exception as e:
            logger.error(f"❌ Ошибка обработки сообщения: {e}", exc_info=True)

    async def _send_notifications_for_entities(
        self,
        entities: List[Dict],
        article_id: int,
        article_title: str,
        article_summary: str,
        article_link: Optional[str],
        risk_level: str,
        sentiment: str,
    ):
        """Найти триггеры для сущностей и отправить уведомления"""

        async with self.AsyncSessionLocal() as session:
            # Собираем все идентификаторы для поиска триггеров:
            # - числовые ID сущностей
            # - имена сущностей (строки)
            entity_ids_str = [str(e["id"]) for e in entities if "id" in e]
            entity_names = [
                e.get("name", e.get("text", "")).lower().strip()
                for e in entities
                if e.get("name") or e.get("text")
            ]

            if not entity_ids_str and not entity_names:
                return

            # ИСПРАВЛЕНО: ищем триггеры по:
            # 1. trigger_value = строковый ID сущности (старый способ)
            # 2. trigger_value = имя сущности (новый способ из UI)
            # trigger_type может быть "entity", "organization", "person"
            conditions = []
            if entity_ids_str:
                conditions.append(
                    NotificationTrigger.trigger_value.in_(entity_ids_str)
                )
            if entity_names:
                # Ищем по частичному совпадению имени (case-insensitive)
                for name in entity_names:
                    if name:
                        conditions.append(
                            NotificationTrigger.trigger_value.ilike(f"%{name}%")
                        )

            if not conditions:
                return

            stmt = select(NotificationTrigger).where(
                and_(
                    NotificationTrigger.trigger_type.in_(
                        ["entity", "organization", "person", "ORG", "PER"]
                    ),
                    or_(*conditions),
                    NotificationTrigger.enabled == True,
                )
            )
            result = await session.execute(stmt)
            triggers = result.scalars().all()

            if not triggers:
                logger.debug(
                    f"⏭️  Нет триггеров для сущностей: ids={entity_ids_str[:3]}, "
                    f"names={entity_names[:3]}"
                )
                return

            logger.info(f"🔔 Найдено {len(triggers)} триггеров для уведомлений")

            # Группируем по пользователю
            users_to_notify: Dict[int, List] = {}
            for trigger in triggers:
                users_to_notify.setdefault(trigger.user_id, []).append(trigger)

            # Отправляем каждому пользователю
            for user_id, user_triggers in users_to_notify.items():
                await self._send_notification_to_user(
                    user_id=user_id,
                    triggers=user_triggers,
                    article_id=article_id,
                    article_title=article_title,
                    article_summary=article_summary,
                    article_link=article_link,
                    entities=entities,
                    risk_level=risk_level,
                    sentiment=sentiment,
                    session=session,
                )

    async def _send_notification_to_user(
        self,
        user_id: int,
        triggers: List,
        article_id: int,
        article_title: str,
        article_summary: str,
        article_link: Optional[str],
        entities: List[Dict],
        risk_level: str,
        sentiment: str,
        session: AsyncSession,
    ):
        """Отправить уведомление конкретному пользователю"""
        try:
            # Получаем email канал
            channel_stmt = select(NotificationChannel).where(
                and_(
                    NotificationChannel.user_id == user_id,
                    NotificationChannel.channel_type == "email",
                    NotificationChannel.enabled == True,
                )
            )
            channel_result = await session.execute(channel_stmt)
            email_channel = channel_result.scalars().first()

            if not email_channel or not email_channel.channel_address:
                logger.debug(f"⏭️  У пользователя {user_id} нет email-канала")
                return

            # Проверяем настройки уведомлений
            settings_stmt = select(NotificationSettings).where(
                NotificationSettings.user_id == user_id
            )
            settings_result = await session.execute(settings_stmt)
            settings = settings_result.scalars().first()

            if settings and not settings.enabled:
                logger.debug(f"⏭️  Уведомления отключены для пользователя {user_id}")
                return

            # Определяем сущность из триггера
            trigger = triggers[0]
            trigger_value = trigger.trigger_value

            # Ищем сущность по имени или ID
            matched_entity = None
            for e in entities:
                entity_name = e.get("name") or e.get("text") or ""
                entity_id_str = str(e.get("id", ""))
                if (
                    trigger_value == entity_id_str
                    or trigger_value.lower() in entity_name.lower()
                    or entity_name.lower() in trigger_value.lower()
                ):
                    matched_entity = e
                    break

            if not matched_entity:
                matched_entity = entities[0] if entities else {}

            entity_name = matched_entity.get("name") or matched_entity.get("text") or trigger_value
            entity_type_raw = matched_entity.get("type") or matched_entity.get("entity_type") or "ORG"
            entity_type_human = "organization" if entity_type_raw in ("ORG", "organization") else "person"

            # Формируем тему
            subject = f"🔔 Упоминание: {entity_name}"
            if len(triggers) > 1:
                subject += f" (+{len(triggers) - 1} ещё)"

            # Отправляем
            success = await self.email_service.send_notification_email(
                to_email=email_channel.channel_address,
                subject=subject,
                article_title=article_title,
                article_summary=article_summary,
                article_link=article_link,
                entity_name=entity_name,
                entity_type=entity_type_human,
                risk_level=risk_level,
                sentiment=sentiment,
            )

            if success:
                logger.info(
                    f"✅ Email отправлен пользователю {user_id} "
                    f"({email_channel.channel_address}), статья {article_id}, "
                    f"сущность: {entity_name}"
                )
            else:
                logger.warning(
                    f"⚠️  Не удалось отправить email пользователю {user_id}"
                )

        except Exception as e:
            logger.error(
                f"❌ Ошибка отправки уведомления пользователю {user_id}: {e}",
                exc_info=True,
            )


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
        logger.info("Остановка...")
        await consumer.shutdown()
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        raise