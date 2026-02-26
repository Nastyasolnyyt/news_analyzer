# kafka_consumer.py
import os
import json
import logging
import time
from confluent_kafka import Consumer, Producer, KafkaError
from .classifier import MistralNeuralClassifier  # ✅ Изменено
from .storage import save_risk_result, settings
from .models import Article

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def consume_from_kafka():
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    input_topic = os.getenv("KAFKA_TOPIC", "text_for_risk")
    output_topic = os.getenv("OUTPUT_TOPIC", "risk_classified")  # Новый топик
    
    # Consumer для чтения сообщений
    consumer = Consumer({
        'bootstrap.servers': bootstrap_servers,
        'group.id': f'risk_classifier_{int(time.time())}',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True,
        'session.timeout.ms': 10000,
    })
    
    # Producer для отправки результатов
    producer = Producer({
        'bootstrap.servers': bootstrap_servers,
        'message.timeout.ms': 5000,
    })
    
    def delivery_callback(err, msg):
        if err:
            logger.error(f"Failed to deliver message to {msg.topic()}: {err}")
        else:
            logger.debug(f"Message delivered to {msg.topic()} [partition {msg.partition()}]")
    
    logger.info(f"Initializing classifier...")
    
    try:
        # ✅ Изменено: используем MistralNeuralClassifier напрямую
        if hasattr(settings, 'openrouter_api_key') and settings.openrouter_api_key:
            classifier = MistralNeuralClassifier(api_key=settings.openrouter_api_key)
        else:
            classifier = MistralNeuralClassifier()
        logger.info("Classifier initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize classifier: {e}")
        return
    
    try:
        consumer.subscribe([input_topic])
        logger.info(f"Subscribed to input topic: {input_topic}")
        logger.info(f"Will send results to: {output_topic}")
        
        message_count = 0
        
        while True:
            msg = consumer.poll(timeout=1.0)
            
            if msg is None:
                continue
            
            if msg.error():
                logger.error(f"Kafka error: {msg.error()}")
                continue
            
            message_count += 1
            logger.info(f"Processing message #{message_count}")
            
            try:
                article_data = json.loads(msg.value().decode('utf-8'))
                
                # Валидация
                article = Article(**article_data)
                
                # Формируем текст для классификации
                full_text = f"{article.title}"
                if article.description:
                    full_text += f" {article.description}"
                
                logger.info(f"Classifying: {article.title[:50]}...")
                
                # Классификация
                result = classifier.classify(full_text)
                
                # Сохраняем в БД
                temp_id = getattr(article, 'id', 0)
                try:
                    save_risk_result(temp_id, result)
                    logger.info(f"Saved to DB: {result.risk_type}")
                except Exception as db_error:
                    logger.error(f"DB error: {db_error}")
                    # Продолжаем даже если БД ошибка
                
                # ========== ОТПРАВКА В ВЫХОДНОЙ ТОПИК ==========
                result_message = {
                    'article_id': temp_id,
                    'original_title': article.title,
                    'risk_type': result.risk_type,
                    'confidence': float(result.confidence),
                    'classified_at': time.time(),
                    'source_topic': input_topic,
                    'text_preview': full_text[:200] if full_text else '',
                }
                
                # Добавляем исходные данные если есть
                if hasattr(article, 'source'):
                    result_message['source'] = article.source
                if hasattr(article, 'url'):
                    result_message['url'] = article.url
                if hasattr(article, 'published_at'):
                    result_message['published_at'] = article.published_at
                
                # Отправка в Kafka
                producer.produce(
                    topic=output_topic,
                    value=json.dumps(result_message, ensure_ascii=False).encode('utf-8'),
                    callback=delivery_callback,
                    key=str(temp_id).encode('utf-8') if temp_id else None
                )
                
                producer.poll(0)  # Обработка callback'ов
                
                logger.info(f"Sent to {output_topic}: {result.risk_type} (conf: {result.confidence:.2f})")
                
                # Периодически сбрасываем producer
                if message_count % 10 == 0:
                    producer.flush()
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
            except Exception as e:
                logger.error(f"Processing error: {e}", exc_info=True)
    
    except KeyboardInterrupt:
        logger.info("Stopping consumer...")
    except Exception as e:
        logger.error(f"Consumer error: {e}", exc_info=True)
    finally:
        producer.flush(30)
        consumer.close()
        logger.info("Consumer and producer closed")