import json
import os
import logging
import re
import signal
import sys
import httpx  # Для скачивания страниц
from bs4 import BeautifulSoup
from confluent_kafka import Consumer, Producer
from sqlalchemy import create_engine, text as sql_text # Для UPDATE запроса
import nltk
from pymystem3 import Mystem

# --- Инициализация тяжелых ресурсов ---
nltk.download('punkt', quiet=True)
mystem = Mystem()

# --- Настройки из переменных окружения ---
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
INPUT_TOPIC = os.getenv('INPUT_TOPIC', 'raw_articles')
DATABASE_URL = os.getenv('DATABASE_URL') # Обязательно добавь в docker-compose

OUTPUT_TOPICS = [
    os.getenv('OUTPUT_TOPIC_NER', 'text_for_ner'),
    os.getenv('OUTPUT_TOPIC_RISK', 'text_for_risk'),
    os.getenv('OUTPUT_TOPIC_SENTIMENT', 'text_for_sentiment'),
    os.getenv('OUTPUT_TOPIC_ANOMALY', 'text_for_anomaly'),
    os.getenv('OUTPUT_TOPIC_SYNC', 'text_for_kg_sync')
]

# Настройка БД (как в твоем агрегаторе)
engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"},
    pool_pre_ping=True
)

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

# --- Логика очистки (твоя без изменений) ---

def clean_text(text):
    if not text: return ""
    soup = BeautifulSoup(text, "html.parser")
    text = soup.get_text(separator=" ").lower()
    return " ".join(text.split())

def clean_special_symbol(text: str):
    if not text: return ""
    return re.sub(r'[^a-zа-яё0-9\s]', '', text.lower())

try:
    with open('stopwords-ru.json', 'r', encoding='utf-8') as f:
        stopwords = set(json.load(f))
except Exception as e:
    logger.error(f"Не удалось загрузить стоп-слова: {e}")
    stopwords = set()

def receive_tokens(text: str, stopwords):
    if not text: return []
    lemmas = mystem.lemmatize(text)
    tokens = [
        word for word in lemmas 
        if word.strip() and word not in stopwords and len(word) > 1
    ]
    return tokens

# --- НОВАЯ ЛОГИКА: Скрейпинг и БД ---

def fetch_full_article(url: str):
    """Скачивает полную статью по ссылке."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        with httpx.Client(timeout=10.0, headers=headers, follow_redirects=True) as client:
            r = client.get(url)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                # Ищем параграфы (стандарт для большинства новостных сайтов)
                paragraphs = soup.find_all('p')
                if paragraphs:
                    return " ".join([p.get_text() for p in paragraphs])
    except Exception as e:
        logger.error(f"Ошибка скрейпинга {url}: {e}")
    return None

def update_article_in_db(article_id, full_text):
    """Обновляет запись в PostgreSQL."""
    try:
        with engine.begin() as conn:
            conn.execute(
                sql_text("UPDATE articles SET text = :text WHERE id = :id"),
                {"text": full_text, "id": article_id}
            )
            logger.info(f"Статья ID {article_id} успешно обновлена в БД.")
    except Exception as e:
        logger.error(f"Ошибка БД при обновлении ID {article_id}: {e}")

# --- Обработка сигналов и Kafka ---

def signal_handler(sig, frame):
    global running
    logger.info("Остановка...")
    running = False

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

    logger.info(f"Препроцессинг запущен. Режим: Scraper + DB Update. Слушаем {INPUT_TOPIC}...")

    try:
        while running:
            msg = consumer.poll(timeout=1.0)
            if msg is None: continue
            if msg.error():
                logger.error(f'Ошибка Kafka: {msg.error()}')
                continue

            try:
                article_data = json.loads(msg.value().decode('utf-8'))
                article_id = article_data.get('id')
                article_link = article_data.get('link')
                
                # 1. Проверяем, нужно ли скачивать полный текст
                # Если текст короткий (например, только описание из RSS), идем на сайт
                original_text = article_data.get('text', '')
                
                if article_link and len(original_text) < 300:
                    logger.info(f"Скачиваю полную статью для ID {article_id}...")
                    scraped_text = fetch_full_article(article_link)
                    if scraped_text:
                        original_text = scraped_text
                        # 2. СРАЗУ ОБНОВЛЯЕМ БАЗУ ДАННЫХ
                        update_article_in_db(article_id, original_text)

                # 3. Твоя стандартная обработка NLP
                cleaned = clean_text(original_text)
                cleared = clean_special_symbol(cleaned)
                tokens = receive_tokens(cleared, stopwords)

                # Собираем результат
                processed_data = article_data.copy()
                processed_data['text'] = cleaned # В Kafka пойдет уже очищенный полный текст
                processed_data['clean_text'] = cleared
                processed_data['tokens'] = tokens

                # 4. Отправка во все топики-потребители
                message_bytes = json.dumps(processed_data, ensure_ascii=False).encode('utf-8')
                for out_topic in OUTPUT_TOPICS:
                    producer.produce(topic=out_topic, value=message_bytes, callback=delivery_callback)
                
                producer.poll(0)
                consumer.commit(msg)

            except Exception as e:
                logger.error(f"Ошибка при обработке сообщения: {e}")
                consumer.commit(msg) 

    finally:
        producer.flush()
        consumer.close()

if __name__ == "__main__":
    main()