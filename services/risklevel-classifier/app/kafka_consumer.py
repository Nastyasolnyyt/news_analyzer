# services/risk-classifier/app/kafka_consumer.py
import os
import json
import logging
import time
from confluent_kafka import Consumer, Producer, KafkaError
from .classifier import MistralNeuralClassifier
from .storage import save_risk_result, settings
from .models import Article

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def wait_for_topic(consumer, topic_name, timeout=5.0):
    logger.info(f"Ожидание появления топика '{topic_name}'...")
    while True:
        try:
            metadata = consumer.list_topics(topic=topic_name, timeout=timeout)
            if topic_name in metadata.topics:
                topic_metadata = metadata.topics[topic_name]
                if topic_metadata.error is None:
                    logger.info(f"Топик '{topic_name}' готов!")
                    return True
            time.sleep(5)
        except Exception as e:
            logger.warning(f"Ошибка при проверке топика: {e}")
            time.sleep(5)

def consume_from_kafka():
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    input_topic = os.getenv("KAFKA_TOPIC", "text_for_risk")
    output_topic = os.getenv("OUTPUT_TOPIC", "risk_classified")
    
    consumer = Consumer({
        'bootstrap.servers': bootstrap_servers,
        'group.id': f'risk_classifier_v2_{int(time.time())}', 
        'auto.offset.reset': 'latest', 
        'enable.auto.commit': True,
    })
    
    producer = Producer({'bootstrap.servers': bootstrap_servers})
    
    def delivery_callback(err, msg):
        if err:
            logger.error(f"Ошибка доставки: {err}")

    # Инициализация классификатора
    classifier = MistralNeuralClassifier(api_key=settings.openrouter_api_key)
    
    try:
        if not wait_for_topic(consumer, input_topic): return
        consumer.subscribe([input_topic])
        
        message_count = 0
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None: continue
            if msg.error(): continue

            message_count += 1
            try:
                article_data = json.loads(msg.value().decode('utf-8'))
                article = Article(**article_data)
                
                # Собираем текст для анализа: заголовок + описание + основной текст
                text_parts = [article.title]
                if article.description: text_parts.append(article.description)
                if article.text: text_parts.append(article.text)
                full_text = " ".join(text_parts)
                
                # КЛАССИФИКАЦИЯ (теперь возвращает high/medium/low)
                result = classifier.classify(full_text)
                
                # Сохранение в PostgreSQL через storage.py
                temp_id = article.id or 0
                save_risk_result(temp_id, result)
                
                # Подготовка сообщения для ФРОНТЕНДА (через выходной топик Kafka)
                result_message = {
                    'article_id': temp_id,
                    'title': article.title,
                    'risk': result.risk_type,  # ВАЖНО: поле 'risk' для фронтенда
                    'confidence': float(result.confidence),
                    'source': article.source,
                    'date': article.pub_date.strftime('%d.%m.%Y') if article.pub_date else '',
                    'summary': result.risk_type.upper() + ": Проанализировано системой", # Можно заменить на суммаризацию
                    'url': article.link
                }
                
                # Отправка в Kafka
                producer.produce(
                    topic=output_topic,
                    value=json.dumps(result_message, ensure_ascii=False).encode('utf-8'),
                    callback=delivery_callback,
                    key=str(temp_id).encode('utf-8')
                )
                producer.poll(0)
                
                logger.info(f"Статья {temp_id} классифицирована как: {result.risk_type}")
                
                # Небольшая пауза, чтобы не спамить API OpenRouter слишком быстро
                time.sleep(2) 
                
            except Exception as e:
                logger.error(f"Ошибка обработки: {e}")
    
    finally:
        producer.flush()
        consumer.close()

if __name__ == "__main__":
    consume_from_kafka()