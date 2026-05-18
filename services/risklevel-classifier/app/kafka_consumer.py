"""
risk-classifier/app/kafka_worker.py
ИСПРАВЛЕНО:
1. Добавлено подробное логирование для диагностики пайплайна
2. Добавлена проверка что сообщения действительно отправляются в risk_types_done
3. Исправлена передача article_id в сообщение
"""
import asyncio
import json
import logging
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from .config import settings
from .classifier import HFRiskClassifier
from .storage import save_risk_level
from sqlalchemy import create_engine, text as sql_text
from sqlalchemy.orm import sessionmaker

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("risk-worker")


async def consume_from_kafka():
    """Main Kafka consumer для анализа типов риска"""

    logger.info("Инициализирую классификатор типов риска...")
    classifier = HFRiskClassifier()
    logger.info("Классификатор готов")

    # Проверяем подключение к БД при старте
    try:
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(sql_text("SELECT 1"))
        logger.info("Подключение к БД успешно")
    except Exception as e:
        logger.error(f"Ошибка подключения к БД: {e}")
        raise

    consumer = AIOKafkaConsumer(
        settings.input_topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=settings.kafka_group_id,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset="earliest"
    )

    producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        value_serializer=lambda m: json.dumps(m, ensure_ascii=False).encode('utf-8')
    )

    await consumer.start()
    await producer.start()

    logger.info(f"Worker запущен.")
    logger.info(f"  Читаю из топика: {settings.input_topic}")
    logger.info(f"  Отправляю в топик: {settings.output_topic}")

    processed_count = 0

    try:
        async for msg in consumer:
            try:
                article_data = msg.value

                # Получаем ID статьи — поддерживаем оба варианта ключа
                article_id = article_data.get('article_id') or article_data.get('id')

                if not article_id:
                    logger.warning(f"Пропускаю сообщение без article_id: {list(article_data.keys())}")
                    continue

                title = article_data.get('title', '')
                text = article_data.get('text', '')
                full_text = f"{title} {text}".strip()

                if not full_text:
                    logger.warning(f"Пустой текст для статьи {article_id}, пропускаю")
                    continue

                logger.info(f"Анализирую тип риска для статьи {article_id}...")

                # Классификация типа риска
                result = classifier.classify(full_text)

                logger.info(
                    f"Статья {article_id}: "
                    f"risk_level={result['risk_level']}, "
                    f"confidence={result['confidence']:.2f}"
                )

                # Сохраняем в БД
                save_risk_level(article_id, result["risk_level"], result["confidence"])

                # ИСПРАВЛЕНО: явно указываем article_id в сообщении
                # (некоторые сообщения могут иметь только 'id', а не 'article_id')
                output_message = {
                    **article_data,
                    'article_id': article_id,  # гарантируем наличие article_id
                    'risk_level': result['risk_level'],
                    'risk_type_confidence': result['confidence']
                }

                await producer.send_and_wait(settings.output_topic, output_message)

                processed_count += 1
                logger.info(
                    f"Статья {article_id} отправлена в {settings.output_topic} "
                    f"(всего обработано: {processed_count})"
                )

            except Exception as e:
                logger.error(f"Ошибка обработки сообщения: {e}", exc_info=True)
                continue

    except KeyboardInterrupt:
        logger.info("Остановка worker...")
    finally:
        await consumer.stop()
        await producer.stop()
        logger.info(f"Worker остановлен. Обработано статей: {processed_count}")


async def main():
    await consume_from_kafka()


if __name__ == "__main__":
    asyncio.run(main())
