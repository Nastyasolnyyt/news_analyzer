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

from app.classifier import HFRiskClassifier

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
INPUT_TOPIC = os.getenv("KAFKA_TOPIC", "risk_types_done")
OUTPUT_TOPIC = os.getenv("OUTPUT_TOPIC", "risk_final_ready")
DATABASE_URL = os.getenv("DATABASE_URL")

Base = declarative_base()

class Risk(Base):
    __tablename__ = "risks"
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, nullable=False, unique=True)
    
    # Заполняет risk-classifier (может быть пустым при первом запуске)
    risk_type = Column(String, nullable=True)           
    risk_type_confidence = Column(Float, nullable=True)
    
    # Заполняет risklevel-classifier
    risk_level = Column(String, nullable=True)          
    risk_confidence = Column(Float, nullable=True)

async def consume_and_classify():
    logger.info("Инициализирую классификатор Hugging Face...")
    classifier = HFRiskClassifier()
    
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    
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
                
                title = article_data.get('title', '')
                text = article_data.get('text', '')
                full_text = f"{title} {text}"
                
                if not full_text.strip():
                    logger.warning(f"Пустой текст для статьи {article_id}")
                    continue
                
                logger.info(f"Классифицирую статью {article_id}...")
                result = classifier.classify(full_text)  
                
                session = Session()
                try:
                    
                    stmt = insert(Risk).values(
                        article_id=article_id,
                        risk_level=result["risk_level"],        
                        risk_confidence=result["confidence"],
                        risk_type="определяется..."  
                    ).on_conflict_do_update(
                        index_elements=['article_id'],
                        set_={
                            'risk_level': result["risk_level"],      
                            'risk_confidence': result["confidence"]  
                        }
                    )
                    session.execute(stmt)
                    session.commit()
                    logger.info(
                        f"Статья {article_id}: {result['risk_level']} "
                        f"(уверенность: {result['confidence']:.2f})"
                    )
                finally:
                    session.close()
                
                # Отправляем результат дальше
                output_message = {
                    **article_data,
                    'risk_level': result["risk_level"],
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