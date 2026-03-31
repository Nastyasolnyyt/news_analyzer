# services/ner-service/app/kafka_worker.py
import asyncio
import json
import logging
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from .config import settings
from .database import get_engine, get_session, NamedEntity, PostEntity, Base
from .extractor import EntityExtractor

logger = logging.getLogger(__name__)


async def consume_and_extract():
    extractor = EntityExtractor()
    engine = get_engine(settings.database_url)
    Session = get_session(engine)
    
    Base.metadata.create_all(bind=engine)
    
    consumer = AIOKafkaConsumer(
        settings.input_topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id="ner-service-group",
        auto_offset_reset="earliest",
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        value_serializer=lambda m: json.dumps(m, ensure_ascii=False).encode('utf-8')
    )
    
    await consumer.start()
    await producer.start()
    
    logger.info(f"NER Service started. Listening to: {settings.input_topic}")
    
    try:
        async for message in consumer:
            try:
                article_data = message.value
                article_id = article_data.get('article_id') or article_data.get('id')
                
                if not article_id:
                    logger.warning("No article_id in message")
                    continue
                
                title = article_data.get('title', '')
                text = article_data.get('text', '')
                full_text = f"{title} {text}"
                
                if not full_text.strip():
                    continue
                
                logger.info(f"Extracting entities for article {article_id}...")
                entities = extractor.extract(full_text)
                
                if not entities:
                    logger.debug(f"No entities found for article {article_id}")
                    continue
                
                db = Session()
                saved_entities = []
                
                try:
                    for ent in entities:
                        entity_name = ent['text']
                        entity_type = ent['type']
                        
                        # 1. Find or create NamedEntity
                        existing = db.execute(
                            select(NamedEntity.id).where(NamedEntity.name == entity_name)
                        ).scalar_one_or_none()
                        
                        if existing:
                            db.execute(
                                update(NamedEntity)
                                .where(NamedEntity.id == existing)
                                .values(entity_type=entity_type)
                            )
                            entity_id = existing
                        else:
                            new_entity = NamedEntity(name=entity_name, entity_type=entity_type)
                            db.add(new_entity)
                            db.flush()
                            entity_id = new_entity.id
                        
                        # 2. Check if link already exists (composite PK: post_id + entity_id)
                        existing_link = db.execute(
                            select(1).where(
                                (PostEntity.post_id == article_id) & 
                                (PostEntity.entity_id == entity_id)
                            )
                        ).scalar_one_or_none()
                        
                        # Insert link only if it doesn't exist
                        if existing_link is None:
                            db.add(PostEntity(post_id=article_id, entity_id=entity_id))
                        
                        # Always add to saved_entities list
                        saved_entities.append({
                            'text': entity_name,
                            'type': entity_type,
                            'id': entity_id
                        })
                    
                    db.commit()
                    logger.info(f"Article {article_id}: saved {len(saved_entities)} entities")
                    
                except Exception as e:
                    db.rollback()
                    logger.error(f"DB error for article {article_id}: {e}", exc_info=True)
                    continue
                finally:
                    db.close()
                
                output_message = {
                    **article_data,
                    'entities': saved_entities
                }
                await producer.send_and_wait(settings.output_topic, output_message)
                logger.debug(f"Sent to {settings.output_topic}: {len(saved_entities)} entities")
                
            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
                continue
    
    except KeyboardInterrupt:
        logger.info("Stopping NER Service...")
    finally:
        await consumer.stop()
        await producer.stop()
        engine.dispose()
        logger.info("NER Service stopped")