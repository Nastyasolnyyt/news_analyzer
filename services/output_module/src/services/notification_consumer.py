"""
Notification Consumer для отправки email при упоминании отслеживаемых сущностей
"""

import asyncio
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime

from aiokafka import AIOKafkaConsumer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, and_

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
    """Consumer для обработки статей и отправки уведомлений"""

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
        """Инициализация подключений"""
        logger.info("Initializing Notification Consumer...")

        # Подключение к БД
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

        # Подключение к Kafka
        self.consumer = AIOKafkaConsumer(
            self.kafka_input_topic,
            bootstrap_servers=self.kafka_bootstrap_servers,
            group_id=self.kafka_group_id,
            auto_offset_reset="earliest",
            max_poll_records=10,
            session_timeout_ms=30000,
        )

        await self.consumer.start()
        logger.info(
            f"✅ Kafka Consumer started. Listening to topic: {self.kafka_input_topic}"
        )

    async def shutdown(self):
        """Остановка потребителя"""
        if self.consumer:
            await self.consumer.stop()
        if self.engine:
            await self.engine.dispose()
        logger.info("Notification Consumer stopped")

    async def run(self):
        """Главный цикл потребителя"""
        try:
            await self.initialize()

            logger.info("🎯 Starting to consume messages...")
            async for message in self.consumer:
                try:
                    await self._process_message(message)
                except Exception as e:
                    logger.error(f"❌ Error processing message: {e}", exc_info=True)

        except Exception as e:
            logger.error(f"❌ Consumer error: {e}", exc_info=True)
            raise
        finally:
            await self.shutdown()

    async def _process_message(self, message):
        """Обработать одну статью"""
        try:
            # Парсим сообщение
            data = json.loads(message.value.decode("utf-8"))
            logger.debug(f"📬 Received message: {data.get('id', 'unknown')}")

            # Извлекаем данные статьи
            article_id = data.get("id") or data.get("post_id")
            article_entities = data.get("entities", [])  # [{"id": 123, "name": "...", "type": "PER"}]
            article_title = data.get("title", "")
            article_summary = data.get("summary") or data.get("text", "")[:500]
            article_link = data.get("link") or data.get("url")
            risk_level = data.get("risk_level", "low")
            sentiment = data.get("sentiment_label", "neutral")

            if not article_entities:
                logger.debug("⏭️  No entities in article, skipping")
                return

            # Для каждой сущности в статье ищем пользователей, которые её отслеживают
            entity_ids = [e["id"] for e in article_entities]
            await self._send_notifications_for_entities(
                entity_ids=entity_ids,
                article_id=article_id,
                article_title=article_title,
                article_summary=article_summary,
                article_link=article_link,
                entities=article_entities,
                risk_level=risk_level,
                sentiment=sentiment,
            )

        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in message: {e}")
        except KeyError as e:
            logger.error(f"❌ Missing required field: {e}")

    async def _send_notifications_for_entities(
        self,
        entity_ids: List[int],
        article_id: int,
        article_title: str,
        article_summary: str,
        article_link: Optional[str],
        entities: List[Dict],
        risk_level: str,
        sentiment: str,
    ):
        """Отправить уведомления всем пользователям, отслеживающим эти сущности"""

        async with self.AsyncSessionLocal() as session:
            # Ищем все триггеры, которые отслеживают эти сущности и ВКЛЮЧЕНЫ
            stmt = select(NotificationTrigger).where(
                and_(
                    NotificationTrigger.trigger_type.in_(["organization", "person"]),
                    NotificationTrigger.trigger_value.in_([str(e_id) for e_id in entity_ids]),
                    NotificationTrigger.enabled == True,
                )
            )
            result = await session.execute(stmt)
            triggers = result.scalars().all()

            if not triggers:
                logger.debug(
                    f"⏭️  No enabled triggers for entities {entity_ids}, skipping"
                )
                return

            logger.info(
                f"🔔 Found {len(triggers)} triggers for entities {entity_ids}"
            )

            # Группируем триггеры по пользователю
            users_to_notify = {}
            for trigger in triggers:
                if trigger.user_id not in users_to_notify:
                    users_to_notify[trigger.user_id] = []
                users_to_notify[trigger.user_id].append(trigger)

            # Отправляем уведомления каждому пользователю
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
        triggers: List[NotificationTrigger],
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
            # Получаем email канал пользователя
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
                logger.debug(
                    f"⏭️  User {user_id} has no enabled email channel, skipping"
                )
                return

            # Получаем настройки уведомлений пользователя
            settings_stmt = select(NotificationSettings).where(
                NotificationSettings.user_id == user_id
            )
            settings_result = await session.execute(settings_stmt)
            settings = settings_result.scalars().first()

            if not settings or not settings.enabled:
                logger.debug(f"⏭️  Notifications disabled for user {user_id}, skipping")
                return

            # Находим сущности, которые упоминаются в статье и отслеживаются пользователем
            tracked_entities = [
                e
                for e in entities
                if any(
                    trigger.trigger_value == str(e["id"]) for trigger in triggers
                )
            ]

            if not tracked_entities:
                logger.debug(
                    f"⏭️  No tracked entities in article for user {user_id}"
                )
                return

            # Формируем информацию о первой отслеживаемой сущности
            first_entity = tracked_entities[0]
            entity_name = first_entity.get("name", "Unknown")
            entity_type = first_entity.get("entity_type") or first_entity.get(
                "type", "ORG"
            )
            entity_type_name = "organization" if entity_type == "ORG" else "person"

            # Формируем тему письма
            subject = f"🔔 Signal Desk: Упоминание {entity_name}"
            if len(tracked_entities) > 1:
                subject += f" и ещё {len(tracked_entities) - 1}"

            # Отправляем email
            success = await self.email_service.send_notification_email(
                to_email=email_channel.channel_address,
                subject=subject,
                article_title=article_title,
                article_summary=article_summary,
                article_link=article_link,
                entity_name=entity_name,
                entity_type=entity_type_name,
                risk_level=risk_level,
                sentiment=sentiment,
            )

            if success:
                logger.info(
                    f"✅ Email sent to user {user_id} ({email_channel.channel_address}) "
                    f"for article {article_id}"
                )
            else:
                logger.warning(
                    f"⚠️  Failed to send email to user {user_id} "
                    f"({email_channel.channel_address})"
                )

        except Exception as e:
            logger.error(
                f"❌ Error sending notification to user {user_id}: {e}",
                exc_info=True,
            )


# Точка входа
async def run_notification_consumer(
    database_url: str,
    kafka_bootstrap_servers: str,
    kafka_input_topic: str = "articles_analyzed",
    kafka_group_id: str = "notifications-sender-group",
):
    """Запустить consumer уведомлений"""
    consumer = NotificationConsumer(
        database_url=database_url,
        kafka_bootstrap_servers=kafka_bootstrap_servers,
        kafka_input_topic=kafka_input_topic,
        kafka_group_id=kafka_group_id,
    )

    try:
        await consumer.run()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await consumer.shutdown()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise
