from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from aiokafka import AIOKafkaConsumer

from app.config import settings
from app.graph_builder import KnowledgeGraphBuilder
from app.redis_storage import RedisGraphStorage

logger = logging.getLogger(__name__)


async def _connect_consumer() -> AIOKafkaConsumer:
    attempt = 0
    while True:
        consumer = AIOKafkaConsumer(
            settings.kafka_input_topic,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id=settings.kafka_group_id,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
        )
        try:
            await consumer.start()
            logger.info(
                "Kafka consumer started topic=%s group=%s",
                settings.kafka_input_topic,
                settings.kafka_group_id,
            )
            return consumer
        except Exception as e:
            attempt += 1
            logger.warning(
                "Kafka unavailable (%s), retry in %ss (attempt %s)",
                e,
                settings.kafka_consumer_retry_interval_sec,
                attempt,
            )
            try:
                await consumer.stop()
            except Exception:
                pass
            if settings.kafka_consumer_max_retries and attempt >= settings.kafka_consumer_max_retries:
                raise
            await asyncio.sleep(settings.kafka_consumer_retry_interval_sec)


async def run_kafka_consumer(storage: RedisGraphStorage) -> None:
    builder = KnowledgeGraphBuilder()
    while True:
        consumer: AIOKafkaConsumer | None = None
        try:
            consumer = await _connect_consumer()
            async for message in consumer:
                try:
                    raw_val = message.value
                    if isinstance(raw_val, memoryview):
                        raw_val = raw_val.tobytes()
                    if isinstance(raw_val, (bytes, bytearray)):
                        article_data = json.loads(raw_val.decode("utf-8"))
                    elif isinstance(raw_val, dict):
                        article_data = raw_val
                    else:
                        logger.debug("Skip message with unexpected value type")
                        continue
                    if not isinstance(article_data, dict):
                        logger.debug("Skip message: root JSON is not an object")
                        continue
                    article_id_raw = article_data.get("article_id")
                    entities = article_data.get("entities", [])
                    if article_id_raw is None:
                        logger.debug("Skip message without article_id")
                        continue
                    try:
                        article_id = int(article_id_raw)
                    except (TypeError, ValueError):
                        logger.debug("Skip message with non-int article_id")
                        continue
                    await builder.process_article_entities(storage, article_id, entities)
                except json.JSONDecodeError:
                    logger.warning("Skip message: invalid JSON payload")
                except UnicodeDecodeError:
                    logger.warning("Skip message: payload is not valid UTF-8")
                except Exception:
                    logger.exception("Error processing Kafka message")
        except asyncio.CancelledError:
            if consumer is not None:
                await consumer.stop()
            raise
        except Exception:
            logger.exception("Kafka consumer loop failed, will reconnect")
            if consumer is not None:
                try:
                    await consumer.stop()
                except Exception:
                    pass
            await asyncio.sleep(settings.kafka_consumer_retry_interval_sec)
