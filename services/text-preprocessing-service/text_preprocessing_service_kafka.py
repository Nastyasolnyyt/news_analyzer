# services/text-preprocessing-service/text_preprocessing_service_kafka_FIXED.py
"""
Исправленный text-preprocessing сервис.
Очищает текст, скрейпит полные статьи, отправляет в Kafka.
"""

import json
import os
import logging
import re
import signal
import sys
import httpx
from bs4 import BeautifulSoup
from confluent_kafka import Consumer, Producer
from sqlalchemy import create_engine, text as sql_text
import nltk
from pymystem3 import Mystem

# Инициализация логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("text-preprocessing")

# Скачиваем punkt только если его нет
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

# ==================== КОНФИГ ====================

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
INPUT_TOPIC = os.getenv('INPUT_TOPIC', 'raw_articles')
DATABASE_URL = os.getenv('DATABASE_URL')
OUTPUT_TOPICS = [
    os.getenv('OUTPUT_TOPIC_NER', 'text_for_ner'),
    os.getenv('OUTPUT_TOPIC_RISK', 'text_for_risk'),
    os.getenv('OUTPUT_TOPIC_SENTIMENT', 'text_for_sentiment'),
    os.getenv('OUTPUT_TOPIC_ANOMALY', 'text_for_anomaly'),
    os.getenv('OUTPUT_TOPIC_SYNC', 'text_for_kg_sync'),
    os.getenv('OUTPUT_TOPIC_RISKLEV', 'risk_final_ready')
]

CONSUMER_CONFIG = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    'group.id': 'text-preprocessing-group',
    'auto.offset.reset': 'latest',
    'enable.auto.commit': False,
}

PRODUCER_CONFIG = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS
}

# ==================== БД ====================

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False
)

# ==================== NLP ИНСТРУМЕНТЫ ====================

logger.info("Инициализирую NLP инструменты...")
mystem = Mystem()
logger.info("✅ Mystem инициализирована")

# Стоп-слова для русского
STOPWORDS_RU = {
    'и', 'в', 'на', 'из', 'к', 'от', 'с', 'по', 'а', 'для', 'за', 'но',
    'не', 'это', 'этот', 'что', 'это', 'как', 'или', 'что-то', 'который',
    'они', 'ты', 'он', 'она', 'оно', 'вы', 'мы', 'я', 'если', 'при',
    'наш', 'ваш', 'новый', 'новости', 'медиа', 'vedomosti', 'ru', 'tass',
    'ria', 'interfax', 'gazeta', 'telegraph', 'livejournal', 'habr',
}

running = True
producer = None


def signal_handler(sig, frame):
    """Обработчик сигнала SIGINT (Ctrl+C)"""
    global running
    logger.info("Получен сигнал остановки...")
    running = False


def clean_html(text: str) -> str:
    """Удаляет HTML теги и сущности."""
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    text = soup.get_text(separator=" ").lower()
    # Заменяем HTML сущности
    text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
    return " ".join(text.split())


def remove_special_chars(text: str) -> str:
    """Удаляет специальные символы, оставляя буквы, цифры и пробелы."""
    if not text:
        return ""
    # Оставляем кириллицу, латиницу, цифры и пробелы
    text = re.sub(r'[^а-яёА-ЯЁa-zA-Z0-9\s\.\,\!\?\-]', '', text)
    return text


def tokenize_and_lemmatize(text: str) -> list:
    """Токенизирует и лемматизирует текст."""
    if not text or len(text) < 3:
        return []
    
    try:
        # Лемматизация
        lemmas = mystem.lemmatize(text)
        # Фильтруем
        tokens = [
            word for word in lemmas
            if word.strip()
            and word.lower() not in STOPWORDS_RU
            and len(word) > 1
        ]
        return tokens
    except Exception as e:
        logger.warning(f"Ошибка при лемматизации: {e}")
        return []


def fetch_full_article(url: str) -> str:
    """Скачивает полный текст статьи с URL."""
    if not url:
        return ""
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        with httpx.Client(timeout=10.0, headers=headers, follow_redirects=True) as client:
            response = client.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                # Ищем параграфы
                paragraphs = soup.find_all('p')
                if paragraphs:
                    text = " ".join([p.get_text() for p in paragraphs])
                    logger.debug(f"   ✅ Скачан текст с {url} ({len(text)} символов)")
                    return text
    except Exception as e:
        logger.debug(f"   ⚠️  Ошибка скрейпинга {url}: {e}")
    
    return ""


def update_article_in_db(article_id: int, full_text: str) -> bool:
    """Обновляет текст статьи в БД."""
    if not full_text or not article_id:
        return False
    
    try:
        with engine.begin() as conn:
            query = sql_text(
                "UPDATE articles SET text = :text WHERE id = :id"
            )
            conn.execute(query, {"text": full_text[:5000], "id": article_id})
            logger.info(f"   ✅ Обновлена статья ID={article_id} в БД ({len(full_text)} символов)")
            return True
    except Exception as e:
        logger.error(f"   ❌ Ошибка при обновлении БД: {e}")
        return False


def delivery_callback(err, msg):
    """Коллбэк доставки сообщения в Kafka."""
    if err is not None:
        logger.error(f'Ошибка доставки: {err}')


def main():
    """Основной цикл обработки."""
    global producer, running
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    consumer = Consumer(CONSUMER_CONFIG)
    consumer.subscribe([INPUT_TOPIC])
    producer = Producer(PRODUCER_CONFIG)
    
    logger.info(f"✅ Сервис запущен. Слушаю топик: {INPUT_TOPIC}")
    logger.info(f"   Отправляю в топики: {', '.join(OUTPUT_TOPICS)}")
    
    message_count = 0
    
    try:
        while running:
            # Получаем сообщение из Kafka (не блокирующий режим)
            msg = consumer.poll(1.0)
            
            if msg is None:
                continue
            
            if msg.error():
                logger.error(f"Ошибка Kafka: {msg.error()}")
                continue
            
            message_count += 1
            
            try:
                # Парсим JSON
                article_data = json.loads(msg.value().decode('utf-8'))
                article_id = article_data.get('article_id') or article_data.get('id')
                article_link = article_data.get('link')
                original_text = article_data.get('text') or article_data.get('description') or ''
                
                logger.info(f"📝 Обрабатываю сообщение #{message_count}: ID={article_id}")
                
                # 1️⃣ Скрейпим полный текст, если текст короткий
                if article_link and len(original_text) < 200:
                    logger.info(f"   → Скачиваю полный текст с {article_link}...")
                    scraped_text = fetch_full_article(article_link)
                    if scraped_text:
                        original_text = scraped_text
                        # Обновляем в БД
                        update_article_in_db(article_id, original_text)
                
                # 2️⃣ Очищаем текст
                logger.debug(f"   → Очищаю текст...")
                cleaned_html = clean_html(original_text)
                cleaned_special = remove_special_chars(cleaned_html)
                tokens = tokenize_and_lemmatize(cleaned_special)
                
                # 3️⃣ Подготавливаем данные для аналитических сервисов
                processed_data = {
                    'article_id': article_id,
                    'id': article_id,
                    'text': cleaned_special,
                    'title': article_data.get('title', ''),
                    'link': article_link,
                    'source': article_data.get('source', 'unknown'),
                    'tokens': tokens,  # Для анализа
                }
                
                # 4️⃣ Отправляем в аналитические топики
                logger.debug(f"   → Отправляю в {len(OUTPUT_TOPICS)} топиков...")
                message_bytes = json.dumps(processed_data, ensure_ascii=False).encode('utf-8')
                
                for output_topic in OUTPUT_TOPICS:
                    try:
                        producer.produce(
                            topic=output_topic,
                            value=message_bytes,
                            callback=delivery_callback
                        )
                    except Exception as e:
                        logger.warning(f"   ⚠️  Ошибка отправки в {output_topic}: {e}")
                
                producer.flush()
                consumer.commit(msg)
                logger.info(f"   ✅ Сообщение обработано и отправлено")
                
            except json.JSONDecodeError as e:
                logger.error(f"   ❌ Ошибка парсинга JSON: {e}")
                consumer.commit(msg)
                continue
            except Exception as e:
                logger.error(f"   ❌ Ошибка при обработке: {e}", exc_info=True)
                consumer.commit(msg)
                continue
    
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)
    
    finally:
        logger.info("Закрываю соединения...")
        consumer.close()
        producer.flush()
        logger.info("✅ Сервис остановлен")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Получен Ctrl+C, выходжу...")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        sys.exit(1)