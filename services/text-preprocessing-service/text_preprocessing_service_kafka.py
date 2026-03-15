import json
import os
import logging
import re
from bs4 import BeautifulSoup
from confluent_kafka import Consumer, Producer
import signal
import sys
import nltk
from nltk import word_tokenize
from pymystem3 import Mystem

# --- Инициализация тяжелых ресурсов (ОДИН РАЗ при запуске) ---
nltk.download('punkt', quiet=True)
mystem = Mystem()

# --- Настройки из переменных окружения ---
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
INPUT_TOPIC = os.getenv('INPUT_TOPIC', 'raw_articles')
OUTPUT_TOPICS = [
    os.getenv('OUTPUT_TOPIC_NER', 'text_for_ner'),
    os.getenv('OUTPUT_TOPIC_RISK', 'text_for_risk'),
    os.getenv('OUTPUT_TOPIC_SENTIMENT', 'text_for_sentiment'),
    os.getenv('OUTPUT_TOPIC_ANOMALY', 'text_for_anomaly'),
    os.getenv('OUTPUT_TOPIC_SYNC', 'text_for_kg_sync')
]

CONSUMER_CONFIG = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    'group.id': os.getenv('KAFKA_CONSUMER_GROUP', 'text-preprocessing-group'),
    'auto.offset.reset': 'latest',
    'enable.auto.commit': False,
}

PRODUCER_CONFIG = {'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

running = True
producer = None

def signal_handler(sig, frame):
    global running
    logger.info("Получен сигнал завершения. Останавливаемся...")
    running = False

def clean_text(text):
    if not text: return ""
    soup = BeautifulSoup(text, "html.parser")
    text = soup.get_text(separator=" ").lower()
    return " ".join(text.split())

def clean_special_symbol(text: str):
    """Очистка через регулярные выражения — это быстрее и не ломает индексы."""
    if not text: return ""
    # Оставляем только буквы, цифры и пробелы
    return re.sub(r'[^a-zа-яё0-9\s]', '', text.lower())

# Загружаем стоп-слова один раз
try:
    with open('stopwords-ru.json', 'r', encoding='utf-8') as f:
        stopwords = set(json.load(f)) # set работает в разы быстрее для поиска
except Exception as e:
    logger.error(f"Не удалось загрузить стоп-слова: {e}")
    stopwords = set()

def receive_tokens(text: str, stopwords):
    """Лемматизация и фильтрация."""
    if not text: return []
    
    # Mystem лучше всего работает с целой строкой, а не со списком токенов
    lemmas = mystem.lemmatize(text)
    
    # Оставляем только значимые слова (не пробелы и не стоп-слова)
    tokens = [
        word for word in lemmas 
        if word.strip() and word not in stopwords and len(word) > 1
    ]
    return tokens

def delivery_callback(err, msg):
    if err is not None:
        logger.error(f'Ошибка доставки: {err}')

def main():
    global producer, running
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    consumer = Consumer(CONSUMER_CONFIG)
    consumer.subscribe([INPUT_TOPIC])
    producer = Producer(PRODUCER_CONFIG)

    logger.info(f"Сервис препроцессинга запущен. Слушаем {INPUT_TOPIC}...")

    try:
        while running:
            msg = consumer.poll(timeout=1.0)
            if msg is None: continue
            if msg.error():
                logger.error(f'Ошибка Kafka: {msg.error()}')
                continue

            try:
                raw_message = msg.value().decode('utf-8')
                article_data = json.loads(raw_message)
                
                original_text = article_data.get('text', '')
                
                # Обработка
                cleaned = clean_text(original_text)
                cleared = clean_special_symbol(cleaned)
                tokens = receive_tokens(cleared, stopwords)

                # Собираем результат
                processed_data = article_data.copy()
                processed_data['text'] = cleaned
                processed_data['clean_text'] = cleared
                processed_data['tokens'] = tokens

                # Отправка
                message_bytes = json.dumps(processed_data, ensure_ascii=False).encode('utf-8')
                for out_topic in OUTPUT_TOPICS:
                    producer.produce(topic=out_topic, value=message_bytes, callback=delivery_callback)
                
                producer.poll(0)
                consumer.commit(msg)

            except Exception as e:
                logger.error(f"Ошибка при обработке конкретного сообщения: {e}")
                # Коммитим, чтобы не застрять на «битом» сообщении навсегда
                consumer.commit(msg) 

    finally:
        logger.info("Закрытие соединений...")
        producer.flush()
        consumer.close()

if __name__ == "__main__":
    main()