# services/ner-service/app/kafka_worker.py
import asyncio
import json
import logging
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from sqlalchemy.dialects.postgresql import insert

from .config import settings
from .database import get_engine, get_session, NamedEntity, PostEntity, Base
from .extractor import EntityExtractor

logger = logging.getLogger(__name__)

async def consume_and_extract():
    # Инициализация
    extractor = EntityExtractor()
    engine = get_engine(settings.database_url)
    Session = get_session(engine)
    
    # Создаём таблицы если нет
    Base.metadata.create_all(bind=engine)
    
    # Kafka consumer
    consumer = AIOKafkaConsumer(
        settings.input_topic,  # text_for_ner
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id="ner-service-group",
        auto_offset_reset="earliest",
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    
    # Kafka producer для отправки результатов
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        value_serializer=lambda m: json.dumps(m, ensure_ascii=False).encode('utf-8')
    )
    
    await consumer.start()
    await producer.start()
    
    logger.info(f"🚀 NER Service started. Listening to: {settings.input_topic}")
    
    try:
        async for message in consumer:
            try:
                article_data = message.value
                article_id = article_data.get('article_id') or article_data.get('id')
                
                if not article_id:
                    logger.warning("⚠️ No article_id in message")
                    continue
                
                # Собираем текст для анализа
                title = article_data.get('title', '')
                text = article_data.get('text', '')
                full_text = f"{title} {text}"
                
                if not full_text.strip():
                    continue
                
                # 🔍 Извлекаем сущности
                logger.info(f"🔍 Extracting entities for article {article_id}...")
                entities = extractor.extract(full_text)
                
                if not entities:
                    logger.debug(f"⚠️ No entities found for article {article_id}")
                    continue
                
                # 💾 Сохраняем в БД
                db = Session()
                saved_entities = []
                
                try:
                    for ent in entities:
                        # UPSERT: если сущность уже есть — получаем её ID, если нет — создаём
                        stmt = insert(NamedEntity).values(
                            name=ent['text'],
                            entity_type=ent['type']
                        ).on_conflict_do_update(
                            index_elements=['name'],
                            set_={'entity_type': ent['type']}
                        ).returning(NamedEntity.id)
                        
                        result = db.execute(stmt).scalar_one()
                        entity_id = result
                        
                        # Связываем статью с сущностью
                        post_stmt = insert(PostEntity).values(
                            post_id=article_id,
                            entity_id=entity_id
                        ).on_conflict_do_nothing(
                            index_elements=['post_id', 'entity_id']
                        )
                        db.execute(post_stmt)
                        
                        saved_entities.append({
                            'text': ent['text'],
                            'type': ent['type'],
                            'id': entity_id
                        })
                    
                    db.commit()
                    logger.info(f"✅ Article {article_id}: saved {len(saved_entities)} entities")
                    
                except Exception as e:
                    db.rollback()
                    logger.error(f"❌ DB error for article {article_id}: {e}")
                    continue
                finally:
                    db.close()
                
                # 📤 Отправляем результат в Kafka для следующих сервисов
                output_message = {
                    **article_data,
                    'entities': saved_entities
                }
                await producer.send_and_wait(settings.output_topic, output_message)
                logger.debug(f"📤 Sent to {settings.output_topic}: {len(saved_entities)} entities")
                
            except Exception as e:
                logger.error(f"❌ Error processing message: {e}", exc_info=True)
                continue
    
    except KeyboardInterrupt:
        logger.info("🛑 Stopping NER Service...")
    finally:
        await consumer.stop()
        await producer.stop()
        engine.dispose()
        logger.info("✅ NER Service stopped")