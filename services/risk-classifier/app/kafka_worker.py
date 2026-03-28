"""
services/risk-classifier/app/kafka_worker.py
ИСПРАВЛЕННЫЙ: использует локальную HF модель вместо OpenRouter
"""
import asyncio
import json
import logging
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from .config import settings
from .classifier import RiskTypeClassifier
from .storage import save_risk_type
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("risk-worker")


async def consume_from_kafka():
    """Main Kafka consumer для анализа типов риска"""
    
    # Инициализируем классификатор ПОД ОДИН РАЗ (очень тяжелый объект)
    logger.info("Инициализирую классификатор типов риска...")
    classifier = RiskTypeClassifier()
    logger.info("Классификатор готов")
    
    # Настраиваем потребителя Kafka
    consumer = AIOKafkaConsumer(
        settings.input_topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=settings.kafka_group_id,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset="earliest"
    )

    # Продюсер для отправки результатов дальше
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        value_serializer=lambda m: json.dumps(m, ensure_ascii=False).encode('utf-8')
    )

    await consumer.start()
    await producer.start()
    
    logger.info(f"✅ Worker запущен. Слушаю топик: {settings.input_topic}")

    try:
        async for msg in consumer:
            try:
                article_data = msg.value
                article_id = article_data.get('article_id') or article_data.get('id')
                
                if not article_id:
                    logger.warning("Нет article_id в сообщении")
                    continue
                
                # Собираем текст для анализа
                title = article_data.get('title', '')
                text = article_data.get('text', '')
                full_text = f"{title} {text}"
                
                if not full_text.strip():
                    logger.warning(f"Пустой текст для статьи {article_id}")
                    continue
                
                # КЛАССИФИКАЦИЯ типа риска (политический/экономический/социальный)
                logger.info(f"Анализирую тип риска для статьи {article_id}...")
                result = classifier.classify(full_text)
                
                # Сохраняем в БД таблицу risks
                save_risk_type(article_id, result["risk_type"], result["confidence"])
                
                # Отправляем результат дальше для risklevel-classifier
                output_message = {
                    **article_data,
                    'risk_type': result['risk_type'],
                    'risk_type_confidence': result['confidence']
                }
                await producer.send_and_wait(settings.output_topic, output_message)
                
                logger.info(f"Статья {article_id}: {result['risk_type']} ({result['confidence']:.2f})")
                
            except Exception as e:
                logger.error(f"Ошибка обработки сообщения: {e}", exc_info=True)
                continue

    except KeyboardInterrupt:
        logger.info("Остановка worker...")
    finally:
        await consumer.stop()
        await producer.stop()
        logger.info("Worker остановлен")


async def main():
    await consume_from_kafka()


if __name__ == "__main__":
    asyncio.run(main())