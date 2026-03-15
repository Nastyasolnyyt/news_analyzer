## sentiment_analysis microservice

Микросервис для анализа тональности русскоязычных текстов (positive / negative / neutral).

### Назначение

- **Читает** сообщения из Kafka‑топика `text_for_sentiment`.
- **Определяет** тональность текста с помощью модели HuggingFace (по умолчанию `cointegrated/rubert-tiny-sentiment`).
- **Сохраняет** результаты в PostgreSQL в таблицу `sentiments`.

### Быстрый старт

- **Требования**:
  - **Python**: 3.10+
  - **Доступ к интернету** для первой загрузки модели из HuggingFace.
  - **Kafka**: доступен кластер и топик `text_for_sentiment`.
  - **PostgreSQL**: доступна БД с таблицей `sentiments`.

- **Установка зависимостей**:

```bash
pip install -r requirements.txt
```

- **Запуск сервиса**:

```bash
python -m sentiment_analysis.main
```

или

```bash
python sentiment_analysis/main.py
```

### Конфигурация (env‑переменные)

- **KAFKA_BOOTSTRAP_SERVERS** — адреса брокеров Kafka (по умолчанию `localhost:9092`).
- **KAFKA_GROUP_ID** — consumer group (по умолчанию `sentiment-analysis-group`).
- **KAFKA_TOPIC** — имя топика (по умолчанию `text_for_sentiment`).
- **DATABASE_URL** — URL подключения к PostgreSQL.
- **SENTIMENT_MODEL_NAME** — имя модели HuggingFace (по умолчанию `cointegrated/rubert-tiny-sentiment`).
- **LOG_LEVEL** — уровень логирования (`INFO`/`DEBUG`).


### Пример локальной конфигурации Kafka

Ниже приведён минимальный пример `docker-compose.yml` для локального подъёма Kafka
с одним брокером (для разработки):

```yaml
version: "3.8"

services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092,PLAINTEXT_HOST://localhost:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
```

После запуска (`docker compose up -d`) создайте топик `text_for_sentiment` любым
удобным способом (CLI или GUI). Через CLI (внутри контейнера `kafka`):

```bash
kafka-topics --create \
  --bootstrap-server kafka:9092 \
  --replication-factor 1 \
  --partitions 1 \
  --topic text_for_sentiment
```

### Тестовый продьюсер

Для отправки тестового сообщения в Kafka можно использовать скрипт
`kafka_test_producer.py`:

```bash
python kafka_test_producer.py
```

Он сформирует сообщение формата:

```json
{
  "id": 123,
  "title":"Газпром временно остановил поставки",
  "text":"Газпром временно остановил поставки газа в Европу...",
  "clean_text":"газпром временно остановил поставки газа в европу",
  "tokens": ["газпром","временно","остановить","поставка","газ","европа"],
  "source":"ria.ru",
  "pub_date":"2025-02-10T10:00:00Z"
}
```

и отправит его в топик `text_for_sentiment`. При запущенном сервисе
`sentiment_analysis` новая запись должна появиться в таблице `sentiments`.


### Проверка работы сервиса

1. Убедитесь, что PostgreSQL доступен по `DATABASE_URL` и таблица `sentiments`
   создана (как минимум с полями `id`, `article_id`, `sentiment_label`,
   `confidence_score`, `analyzed_at`).
2. Запустите Kafka и создайте топик `text_for_sentiment`.
3. Запустите сервис:

   ```bash
   python -m sentiment_analysis.main
   ```

4. В другом терминале запустите тестовый продьюсер:

   ```bash
   python kafka_test_producer.py
   ```

5. Проверьте логи сервиса — вы должны увидеть успешный анализ тональности и
   сохранение результата.
6. Откройте БД и убедитесь, что в таблице `sentiments` появилась запись с
   `article_id = 123` и заполненными `sentiment_label`, `confidence_score`.



