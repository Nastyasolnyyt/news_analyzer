# text_preprocessing_service_kafka.py
import json
import os
import logging
from bs4 import BeautifulSoup
from confluent_kafka import Consumer, Producer
import signal
import sys
from nltk import  word_tokenize, download
import pymystem3
from pymystem3 import Mystem

# --- Настройки из переменных окружения ---
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')

INPUT_TOPIC = os.getenv('INPUT_TOPIC', 'raw_articles') # Можно настроить гибко
OUTPUT_TOPICS = [
    os.getenv('OUTPUT_TOPIC_NER', 'text_for_ner'),
    os.getenv('OUTPUT_TOPIC_RISK', 'text_for_risk'),
    os.getenv('OUTPUT_TOPIC_SENTIMENT', 'text_for_sentiment'),
    os.getenv('OUTPUT_TOPIC_ANOMALY', 'text_for_anomaly'),
    os.getenv('OUTPUT_TOPIC_SYNC', 'text_for_kg_sync')
]

# Конфигурация Kafka Consumer
CONSUMER_CONFIG = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    'group.id': os.getenv('KAFKA_CONSUMER_GROUP', 'text-preprocessing-group'), # Также можно настроить
    'auto.offset.reset': 'latest',
    'enable.auto.commit': False,
}

# Конфигурация Kafka Producer
PRODUCER_CONFIG = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
}

# --- Логирование ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Глобальные переменные для корректного завершения ---
running = True
producer = None

def signal_handler(sig, frame):
    global running
    logger.info("Получен сигнал SIGINT. Завершение работы...")
    running = False

def clean_text(text):
    """Очищает текст: удаляет HTML-теги, приводит к нижнему регистру, убирает лишние пробелы."""
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    clean_text = soup.get_text(separator=" ").lower()
    return " ".join(clean_text.split())

def clean_special_symbol(text:str):
    """Очищает текст: удаляет пунктуацию, спецсимволы."""
    for i in range(len(text)):
        if not(text[i].isalpha() or text[i].isdigit() or text[i] == ' '):
            text = text[:i] + text[i + 1:]
    return text.lower()

def receive_tokens(text:str):
    """Получение массива строк с токенами из оригинального текста нижнего регистра без пробелов, HTML-тегов, лишних пробелов, пунктуации, стоп-слов и спецсимволов"""
    with open('stopwords-ru (1).json', 'r', encoding='utf-8') as f:
        stopwords = json.load(f)

    mystem = Mystem()
    download('punkt')
    sentences = word_tokenize(text)
    words = mystem.lemmatize(sentences)
    try:
        while 1:
            words.remove(' ')
    except:
        for word in words:
            if word in stopwords:
                words.remove(word)
        return words

def delivery_callback(err, msg):
    """Callback функция для проверки успешной доставки сообщения в Kafka."""
    if err is not None:
        logger.error(f'Ошибка доставки сообщения в {msg.topic()}: {err}')
    else:
        logger.debug(f'Сообщение доставлено в {msg.topic()} [{msg.partition()}] на оффсет {msg.offset()}')

def main():
    global producer, running
    signal.signal(signal.SIGINT, signal_handler)

    consumer = Consumer(CONSUMER_CONFIG)
    consumer.subscribe([INPUT_TOPIC])
    logger.info(f"Подписка на топик '{INPUT_TOPIC}' с Kafka: {KAFKA_BOOTSTRAP_SERVERS}...")

    producer = Producer(PRODUCER_CONFIG)

    logger.info(f"Запуск Text Preprocessing Service...")

    try:
        while running:
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                continue
            if msg.error():
                logger.error(f'Ошибка Kafka: {msg.error()}')
                continue

            raw_message = msg.value().decode('utf-8')

            try:
                article_data = json.loads(raw_message)
            except json.JSONDecodeError:
                logger.error(f"Ошибка декодирования JSON: {raw_message[:100]}...")
                consumer.commit(msg)
                continue

            original_text = article_data.get('text', '')
            cleaned_text = clean_text(original_text)
            cleared_text = clean_special_symbol(cleaned_text)
            extracted_tokens = receive_tokens(cleared_text)
            processed_article_data = article_data.copy()
            processed_article_data['text'] = cleaned_text
            processed_article_data['clean_text'] = cleared_text
            processed_article_data['tokens'] = extracted_tokens

            for out_topic in OUTPUT_TOPICS:
                try:
                    message_to_send = json.dumps(processed_article_data, ensure_ascii=False).encode('utf-8')
                    producer.produce(topic=out_topic, value=message_to_send, callback=delivery_callback)
                    logger.debug(f"Сообщение помещено в очередь {out_topic}.")

                except BufferError:
                    logger.error(f'Буфер продюсера переполнен при отправке в {out_topic}. Ожидание...')
                    producer.flush()

            consumer.commit(msg)
            logger.debug(f"Обработано и подтверждено сообщение из {INPUT_TOPIC}")
            producer.poll(0)

    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")

    finally:
        logger.info("Очистка ресурсов...")
        producer.flush()
        consumer.close()
        logger.info("Сервис завершен.")


if __name__ == "__main__":
    main()