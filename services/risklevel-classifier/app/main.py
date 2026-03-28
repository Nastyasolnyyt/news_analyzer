"""
Основной модуль микросервиса классификации уровня риска.
Использует Hugging Face модели вместо OpenRouter.
"""
import asyncio
import json
import logging
import os
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import insert

# Импортируем наш классификатор
from app.classifier import HFRiskClassifier

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Конфиг из переменных о кружения
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
INPUT_TOPIC = os.getenv("KAFKA_TOPIC", "risk_types_done")
OUTPUT_TOPIC = os.getenv("OUTPUT_TOPIC", "risk_final_ready")
DATABASE_URL = os.getenv("DATABASE_URL")

# Модель БД для сохранения результатов
Base = declarative_base()

class Risk(Base):
    __tablename__ = "risks"
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, nullable=False, unique=True)
    risk_type = Column(String, nullable=False)  # high, medium, low
    confidence = Column(Float, nullable=True)


async def consume_and_classify():
    """Основной цикл: читает из Kafka, классифицирует, сохраняет в БД."""
    
    # Инициализируем классификатор
    logger.info("Инициализирую классификатор Hugging Face...")
    classifier = HFRiskClassifier()
    
    # Подключение к БД
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    
    # Kafka потребитель и продюсер
    consumer = AIOKafkaConsumer(
        INPUT_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="risklevel-classifier-group",
        auto_offset_reset="earliest",
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda m: json.dumps(m, ensure_ascii=False).encode('utf-8')
    )
    
    await consumer.start()
    await producer.start()
    
    logger.info(f"Сервис запущен. Слушаю топик: {INPUT_TOPIC}")
    
    try:
        async for message in consumer:
            try:
                article_data = message.value
                article_id = article_data.get('article_id') or article_data.get('id')
                
                # Собираем текст для анализа
                title = article_data.get('title', '')
                text = article_data.get('text', '')
                full_text = f"{title} {text}"
                
                if not full_text.strip():
                    logger.warning(f"Пустой текст для статьи {article_id}")
                    continue
                
                # Классифицируем с помощью Hugging Face
                logger.info(f"Классифицирую статью {article_id}...")
                result = classifier.classify(full_text)
                
                # Сохраняем в БД
                session = Session()
                try:
                    stmt = insert(Risk).values(
                        article_id=article_id,
                        risk_type=result["risk_level"],        
                        confidence=result["confidence"]        
                    ).on_conflict_do_update(
                        index_elements=['article_id'],
                        set_={
                            'risk_type': result["risk_level"],      
                            'confidence': result["confidence"]      
                        }
                    )
                    session.execute(stmt)
                    session.commit()
                    logger.info(f"Статья {article_id}: {result.risk_type} (уверенность: {result.confidence:.2f})")
                finally:
                    session.close()
                
                # Отправляем результат дальше для Elasticsearch-sync
                output_message = {
                    **article_data,
                    'risk_type': result["risk_level"],       
                    'risk_confidence': result["confidence"]  
                }
                await producer.send_and_wait(OUTPUT_TOPIC, output_message)
                
            except Exception as e:
                logger.error(f"Ошибка обработки сообщения: {e}", exc_info=True)
                continue
    
    except KeyboardInterrupt:
        logger.info("Остановка сервиса...")
    finally:
        await consumer.stop()
        await producer.stop()


if __name__ == "__main__":
    asyncio.run(consume_and_classify())