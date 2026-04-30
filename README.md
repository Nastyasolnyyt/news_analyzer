# Система интеллектуального анализа новостных потоков

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Программный комплекс для автоматизированного сбора новостей, идентификации именованных сущностей (NER), анализа тональности и оценки репутационных рисков. Система обеспечивает полный цикл обработки данных: от парсинга веб-ресурсов до визуализации связей между объектами.

## 📋 Содержание

- [Возможности](#-возможности)
- [Архитектура](#-архитектура)
- [Технологический стек](#-технологический-стек)
- [Структура проекта](#-структура-проекта)
- [Быстрый старт](#-быстрый-старт)
- [Конфигурация](#-конфигурация)
- [Разработка](#-разработка)
- [API Документация](#-api-документация)

## ✨ Возможности

* **Мониторинг источников** — автоматический парсинг новостных сайтов и Telegram-каналов
* **NER (Named Entity Recognition)** — извлечение организаций, персон, локаций из текстов
* **Анализ тональности** — оценка эмоциональной окраски сообщений (score от -1.0 до 1.0)
* **Классификация рисков** — определение уровня репутационной угрозы
* **Кластеризация событий** — группировка связанных новостей
* **Поиск аномалий** — выявление нестандартных паттернов в информационных потоках
* **Визуализация графа знаний** — отображение взаимосвязей между сущностями
* **Экспорт отчетов** — формирование сводных данных в форматах PDF и Excel
* **Real-time обработка** — потоковая обработка данных через Apache Kafka

## 🏗 Архитектура

Система построена по микросервисной архитектуре:

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Scraper   │────▶│ Preprocessing │────▶│     Kafka       │
│  Services   │     │    Service    │     │   Broker        │
└─────────────┘     └──────────────┘     └────────┬────────┘
                                                  │
                    ┌─────────────────────────────┼─────────────────────────────┐
                    │                             │                             │
                    ▼                             ▼                             ▼
           ┌─────────────┐              ┌─────────────────┐          ┌──────────────────┐
           │     NER     │              │   Sentiment     │          │  Risk Classifier │
           │   Service   │              │   Analysis      │          │      Service     │
           └──────┬──────┘              └────────┬────────┘          └────────┬─────────┘
                  │                              │                            │
                  └──────────────────────────────┼────────────────────────────┘
                                                 │
                                                 ▼
                                        ┌─────────────────┐
                                        │  Elasticsearch  │
                                        │  Output Module  │
                                        └────────┬────────┘
                                                 │
                                                 ▼
                                        ┌─────────────────┐
                                        │   Frontend      │
                                        │   (Vue 3)       │
                                        └─────────────────┘
```

### Основные сервисы

| Сервис | Описание |
|--------|----------|
| `aggregator-parser-service` | Агрегация и первичный парсинг источников |
| `news-site-parser-service` | Парсинг новостных веб-сайтов |
| `telegram-parser-service` | Мониторинг Telegram-каналов |
| `text-preprocessing-service` | Очистка и нормализация текстов |
| `ner-service` | Извлечение именованных сущностей |
| `sentiment_analysis` | Анализ тональности текстов |
| `risk-classifier` / `risklevel-classifier` | Классификация уровней риска |
| `event-clustering` | Группировка связанных событий |
| `anomaly_detection` | Обнаружение аномалий в потоках |
| `knowledge-graph-sync` | Синхронизация графа знаний |
| `elasticsearch-sync` | Индексация данных для поиска |
| `output_module` | API для фронтенда и экспорт данных |

## 🛠 Технологический стек

### Backend
* **Python 3.11** — основной язык разработки
* **FastAPI** — REST API фреймворк
* **SQLAlchemy** — ORM для работы с БД
* **Apache Kafka** — брокер сообщений для потоковой обработки
* **Elasticsearch** — поисковый движок и хранилище

### Frontend
* **Vue 3** (Composition API) — реактивный фреймворк
* **TypeScript** — типизированный JavaScript
* **Vite** — сборщик проектов
* **Axios** — HTTP-клиент
* **Vue Router** — маршрутизация

### Базы данных и инфраструктура
* **PostgreSQL 15** — основное хранилище данных
* **Redis 7** — кэширование и очереди
* **Apache Kafka** — обмен сообщениями между сервисами
* **Elasticsearch** — полнотекстовый поиск
* **Docker & Docker Compose** — контейнеризация

### NLP/ML
* Специализированные библиотеки для NER
* Модели анализа тональности
* Алгоритмы кластеризации и детекции аномалий

## 📁 Структура проекта

```
.
├── services/                 # Микросервисы
│   ├── aggregator-parser-service/
│   ├── news-site-parser-service/
│   ├── telegram-parser-service/
│   ├── text-preprocessing-service/
│   ├── ner-service/
│   ├── sentiment_analysis/
│   ├── risk-classifier/
│   ├── risklevel-classifier/
│   ├── event-clustering/
│   ├── anomaly_detection/
│   ├── knowledge-graph-sync/
│   ├── elasticsearch-sync/
│   └── output_module/
├── frontend/                 # Vue 3 приложение
│   ├── src/
│   ├── public/
│   └── package.json
├── docker/                   # Docker конфигурации
├── infra/                    # Инфраструктурные скрипты
├── docker-compose.yml        # Оркестрация сервисов
├── .env                      # Переменные окружения
└── README.md                 # Документация
```

## 🚀 Быстрый старт

### Предварительные требования

* Docker ≥ 20.10
* Docker Compose ≥ 2.0
* Node.js ≥ 18 (для разработки фронтенда)
* Python ≥ 3.11 (для разработки бэкенда)

### Запуск через Docker Compose

1. **Клонировать репозиторий:**
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. **Настроить переменные окружения:**
   ```bash
   cp .env.example .env
   # Отредактируйте .env файл с вашими параметрами
   ```

3. **Запустить все сервисы:**
   ```bash
   docker-compose up -d
   ```

4. **Проверить статус:**
   ```bash
   docker-compose ps
   ```

5. **Остановить систему:**
   ```bash
   docker-compose down
   ```

### Локальная разработка

#### Backend (отдельный сервис)

```bash
cd services/output_module
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

Фронтенд будет доступен по адресу: `http://localhost:5173`

## ⚙️ Конфигурация

### Переменные окружения

Основные параметры настраиваются через файл `.env`:

| Переменная | Описание | Пример |
|------------|----------|--------|
| `DATABASE_URL` | Строка подключения к PostgreSQL | `postgresql://user:pass@db:5432/news_analysis` |
| `KAFKA_BOOTSTRAP_SERVERS` | Адреса Kafka брокеров | `kafka:9092` |
| `REDIS_URL` | Подключение к Redis | `redis://redis:6379` |
| `ELASTICSEARCH_URL` | Адрес Elasticsearch | `http://elasticsearch:9200` |
| `SECRET_KEY` | Секретный ключ для JWT | `your-secret-key` |

### Порты сервисов

| Сервис | Порт | Описание |
|--------|------|----------|
| PostgreSQL | 5432 | База данных |
| Redis | 6379 | Кэш |
| Kafka | 9092 | Брокер сообщений |
| Zookeeper | 2181 | Координация Kafka |
| Output Module API | 8003 | REST API |
| Frontend (dev) | 5173 | Веб-интерфейс |

## 💻 Разработка

### Добавление нового сервиса

1. Создайте директорию в `services/`:
   ```bash
   mkdir services/new-service
   cd services/new-service
   ```

2. Добавьте `requirements.txt` и код сервиса

3. Создайте `Dockerfile`:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   CMD ["python", "main.py"]
   ```

4. Зарегистрируйте сервис в `docker-compose.yml`

### Тестирование

```bash
# Запуск тестов для конкретного сервиса
cd services/<service-name>
pytest

# Линтинг кода
flake8 .
black --check .
```

## 📡 API Документация

После запуска системы документация Swagger доступна по адресу:

* **Output Module API:** `http://localhost:8003/docs`

Основные эндпоинты:

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/api/articles` | Получить список статей |
| GET | `/api/entities` | Получить извлеченные сущности |
| GET | `/api/sentiments` | Получить анализ тональности |
| POST | `/api/sources` | Добавить источник для парсинга |
| GET | `/api/graph` | Получить данные графа знаний |

## 🔍 Диагностика

### Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f sentiment_analysis
```

### Проверка здоровья сервисов

```bash
docker-compose ps
curl http://localhost:8003/health
```

## 📄 Лицензия

Проект распространяется под лицензией [MIT](LICENSE).

---

**Контакты:** Для вопросов и предложений обращайтесь через Issues на GitHub.