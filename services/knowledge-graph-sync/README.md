# knowledge-graph-sync

Микросервис **синхронизации графа знаний**: читает из Kafka сообщения с сущностями по статьям, строит граф **совместной встречаемости** сущностей в Redis и отдаёт его через HTTP API (FastAPI).

## Назначение

- **Вход:** топик Kafka с JSON-сообщениями вида `{ "article_id": <int>, "entities": [ ... ] }`.
- **Логика:** для каждой статьи берутся уникальные сущности (по полю `id`); для каждой пары сущностей создаётся или усиливается ребро — вес равен числу **разных** статей, в которых эта пара встречалась вместе.
- **Хранилище:** Redis (ключи связей, множества рёбер по сущности, метаданные сущностей).
- **Выход:** REST API для проверки здоровья, списка связей сущности и выгрузки локального подграфа.

## Требования

- Python 3.11+
- Redis 7+ (или совместимый клиент)
- Kafka (совместимый с `aiokafka`)

Для полного контура из репозитория используйте [docker-compose.yml](../../docker-compose.yml) в корне проекта: поднимаются `redis`, `kafka` и этот сервис.

## Запуск через Docker Compose (рекомендуется)

Из корня репозитория `news_analyzer`:

```bash
docker compose up --build
```

Сервис слушает **8200** (`http://localhost:8200`). Переменные `KAFKA_BOOTSTRAP_SERVERS` и `REDIS_*` уже заданы в compose для сети контейнеров.

## Локальный запуск (без Docker образа сервиса)

```bash
cd services/knowledge-graph-sync
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

Убедитесь, что доступны Redis и Kafka, затем задайте переменные окружения (см. ниже) или файл `.env` рядом с процессом. Запуск:

```bash
python -m app.main
```

## Формат сообщения Kafka

Топик по умолчанию: `entities_extracted`.

Каждое значение сообщения — JSON-объект:

| Поле | Тип | Описание |
|------|-----|----------|
| `article_id` | int (обязательно) | Идентификатор статьи |
| `entities` | массив | Сущности статьи |

Элемент `entities` ожидается с полями:

- `id` — числовой идентификатор сущности;
- `text` или `name` — отображаемое имя;
- `type` — тип сущности (по умолчанию `UNKNOWN`).

Статьи с **менее чем двумя** сущностями после дедупликации по `id` игнорируются.

## Переменные окружения

| Переменная | По умолчанию | Описание |
|------------|---------------|----------|
| `KAFKA_BOOTSTRAP_SERVERS` | `kafka:9092` | Bootstrap Kafka |
| `KAFKA_INPUT_TOPIC` | `entities_extracted` | Топик для чтения |
| `KAFKA_GROUP_ID` | `knowledge-graph-sync-group` | Consumer group |
| `KAFKA_CONSUMER_RETRY_INTERVAL_SEC` | `3.0` | Пауза при недоступности Kafka |
| `KAFKA_CONSUMER_MAX_RETRIES` | `0` | `0` — повторять подключение бесконечно |
| `REDIS_HOST` | `redis` | Хост Redis |
| `REDIS_PORT` | `6379` | Порт Redis |
| `REDIS_DB` | `0` | Номер БД |
| `REDIS_PASSWORD` | не задан | Пароль при необходимости |
| `REST_HOST` | `0.0.0.0` | Хост HTTP |
| `REST_PORT` | `8200` | Порт HTTP |
| `MIN_WEIGHT_THRESHOLD` | `1` | Минимальный вес ребра для выдачи в API |
| `MAX_ENTITIES_PER_ARTICLE` | `50` | Ограничение числа сущностей на статью (`0` — без обрезки) |

Имена задаются в **UPPER_SNAKE_CASE** для `pydantic-settings` (как в таблице).

## HTTP API

Базовый URL: `http://<host>:8200`

| Метод | Путь | Описание |
|--------|------|----------|
| `GET` | `/health` | Проверка работоспособности (`{"status":"ok"}`) |
| `GET` | `/entities/{entity_id}/relations?limit=10` | Связанные сущности, отсортированные по весу |
| `GET` | `/graph/entities/{entity_id}/subgraph?depth=1` | Узлы и рёбра вокруг сущности; `depth` 1 или 2 |
| `GET` | `/search/entities?q=...` | Заглушка: пока возвращает пустой список |

Интерактивная схема: `/docs` (Swagger UI).

## Модель данных в Redis (кратко)

- Ребро пары `(e1, e2)` (нормализованный порядок): ключ `relation:{min}:{max}` с JSON (`weight`, `article_ids`, имена и id).
- Множество ключей рёбер для сущности: `entity_relations:{id}`.
- Имя и тип сущности: `entity:{id}:name`, `entity:{id}:type`; индекс по типу: `entities:by_type:{type}`.

## Проверка логики без Redis (скрипт)

В каталоге `scripts/` есть проверка совместной встречаемости на `fakeredis`:

```bash
pip install fakeredis
python scripts/verify_cooccurrence.py
```

## Стек

FastAPI, Uvicorn, aiokafka, redis (async), pydantic-settings.
