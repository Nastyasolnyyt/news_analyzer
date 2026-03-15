# services/risk-classifier/app/kafka_consumer.py
import os
import json
import logging
import time
from confluent_kafka import Consumer, Producer, KafkaError, TopicPartition
from .classifier import MistralNeuralClassifier
from .storage import save_risk_result, settings
from .models import Article

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
# services/risk-classifier/app/kafka_consumer.py

def wait_for_topic(consumer, topic_name, timeout=5.0):
    """
    Ждет появления топика в Kafka. Возвращает True, только если топик реально создан и готов.
    """
    logger.info(f"Ожидание появления топика '{topic_name}'...")
    
    while True:
        try:
            # Получаем метаданные конкретного топика
            metadata = consumer.list_topics(topic=topic_name, timeout=timeout)
            
            # Проверяем, есть ли такой топик в списке
            if topic_name in metadata.topics:
                topic_metadata = metadata.topics[topic_name]
               
                if topic_metadata.error is not None:
                    logger.warning(
                        f"Топик '{topic_name}' еще не готов. Ошибка брокера: {topic_metadata.error}. Ждем 5 сек..."
                    )
                    time.sleep(5)
                    continue
                
                # Если ошибки нет — значит топик создан и готов к работе
                logger.info(f"Топик '{topic_name}' найден и готов к работе!")
                return True
            else:
                # Топика вообще нет в списке метаданных (редкий случай, но бывает)
                logger.warning(f"Топик '{topic_name}' еще не создан брокером. Ждем 5 сек...")
                time.sleep(5)
                
        except Exception as e:
            # Ловим любые сетевые ошибки или ошибки клиента
            logger.warning(f"Ошибка при проверке топика '{topic_name}': {e}. Ждем 5 сек...")
            time.sleep(5)

def consume_from_kafka():
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    input_topic = os.getenv("KAFKA_TOPIC", "text_for_risk")
    output_topic = os.getenv("OUTPUT_TOPIC", "risk_classified")
    
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
        if hasattr(settings, 'openrouter_api_key') and settings.openrouter_api_key:
            classifier = MistralNeuralClassifier(api_key=settings.openrouter_api_key)
        else:
            classifier = MistralNeuralClassifier()
        logger.info("Classifier initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize classifier: {e}")
        return
    
    try:
        if not wait_for_topic(consumer, input_topic):
            logger.error(f"Не удалось дождаться топика {input_topic}")
            return

        # Подписываемся только когда топик точно есть
        consumer.subscribe([input_topic])
        logger.info(f"Успешно подписан на '{input_topic}'. Ожидание сообщений...")
        logger.info(f"Результаты будут отправлены в: {output_topic}")
        
        message_count = 0
        
        while True:
            msg = consumer.poll(timeout=1.0)
            
            if msg is None:
                continue
            
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    
                    continue
                logger.error(f"Kafka error: {msg.error()}")
                # Если топик вдруг пропал, можно попробовать переподписаться
                time.sleep(5)
                continue
            
            message_count += 1
            logger.info(f"Processing message #{message_count}")
            
            try:
                article_data = json.loads(msg.value().decode('utf-8'))
                
                # Валидация
                article = Article(**article_data)
                
                # Формируем текст для классификации
                full_text = f"{article.title}"
                if hasattr(article, 'description') and article.description:
                    full_text += f" {article.description}"
                elif hasattr(article, 'text') and article.text:
                    full_text += f" {article.text}"
                
                logger.info(f"Classifying: {article.title[:50] if article.title else 'No title'}...")
                
                # Классификация
                result = classifier.classify(full_text)
                
                # Сохраняем в БД
                temp_id = getattr(article, 'id', 0)
                try:
                    save_risk_result(temp_id, result)
                    logger.info(f"Saved to DB: {result.risk_type}")
                except Exception as db_error:
                    logger.error(f"DB error: {db_error}")
                
                #отправка в выходной топик
                result_message = {
                    'article_id': temp_id,
                    'original_title': article.title if hasattr(article, 'title') else '',
                    'risk_type': result.risk_type,
                    'confidence': float(result.confidence),
                    'classified_at': time.time(),
                    'source_topic': input_topic,
                    'text_preview': full_text[:200] if full_text else '',
                }
                
                if hasattr(article, 'source'):
                    result_message['source'] = article.source
                if hasattr(article, 'url'):
                    result_message['url'] = article.url
                if hasattr(article, 'published_at'):
                    result_message['published_at'] = article.published_at
                
                producer.produce(
                    
                    topic=output_topic,
                    value=json.dumps(result_message, ensure_ascii=False).encode('utf-8'),
                    callback=delivery_callback,
                    key=str(temp_id).encode('utf-8') if temp_id else None
                )
                
                producer.poll(0)
                
                logger.info(f"Sent to {output_topic}: {result.risk_type} (conf: {result.confidence:.2f})")
                
                time.sleep(8)
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
        logger.info("Flushing producer...")
        producer.flush(30)
        logger.info("Closing consumer...")
        consumer.close()
        logger.info("Consumer and producer closed")