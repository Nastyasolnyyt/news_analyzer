import asyncio
import json
import logging
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from app.config import settings
from app.classifier import MistralNeuralClassifier
from app.storage import save_risk_result
from app.models import RiskResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("risk-worker")

async def consume_from_kafka():
    # Инициализируем классификатор
    classifier = MistralNeuralClassifier(api_key=settings.openrouter_api_key)
    
    # Настраиваем потребителя Kafka
    consumer = AIOKafkaConsumer(
        settings.input_topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=settings.kafka_group_id,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    # (Опционально) Настраиваем продюсера, если хочешь отправлять результат дальше
    producer = AIOKafkaProducer(bootstrap_servers=settings.kafka_bootstrap_servers)

    await consumer.start()
    await producer.start()
    
    logger.info(f"Worker started. Listening to topic: {settings.input_topic}")

    try:
        async for msg in consumer:
            article_data = msg.value
            article_id = article_data.get('id')
            text = article_data.get('text') or article_data.get('title', "")

            logger.info(f"Processing article ID: {article_id}")

            # 1. Классифицируем нейросетью
            result = classifier.classify(text)

            # 2. Сохраняем в PostgreSQL (в таблицу 'risks')
            if article_id:
                save_risk_result(article_id, result)
                logger.info(f"Saved risk for ID {article_id}: {result.risk_type}")

                # 3. Отправляем в следующий топик для Elasticsearch-sync
                article_data['risk_type'] = result.risk_type
                article_data['confidence'] = result.confidence
                
                await producer.send_and_wait(
                    settings.output_topic, 
                    json.dumps(article_data).encode('utf-8')
                )

    except Exception as e:
        logger.error(f"Worker error: {e}")
    finally:
        await consumer.stop()
        await producer.stop()

if __name__ == "__main__":
    asyncio.run(consume())
