# 📧 Email Notifications - Полная Реализация

## 🎯 Что Реализовано

### ✅ Система Отправки Email
- **Email Service** (`src/services/email_service.py`) - асинхронная отправка письма через SMTP
- **Beautiful HTML письма** - профессиональный дизайн с информацией о статье
- **Поддержка метаданных** - риск, тональность, упоминаемая сущность

### ✅ Kafka Consumer для Уведомлений
- **Notification Consumer** (`src/services/notification_consumer.py`) - слушает Kafka топик `articles_analyzed`
- **Автоматическая отправка** - при упоминании отслеживаемой сущности
- **Умная фильтрация** - отправляет только если включены уведомления пользователя

### ✅ API для Тестирования
- **POST `/api/v1/notifications/test-email`** - отправить тестовое письмо

---

## 🔧 Конфигурация

### Переменные Окружения (`.env`)

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/news_analyzer

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_INPUT_TOPIC=articles_analyzed
KAFKA_NOTIFICATION_GROUP_ID=notifications-sender-group

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
SMTP_FROM_EMAIL=noreply@signaldesk.io
SMTP_FROM_NAME=Signal Desk
SMTP_ENABLED=true
```

### Для Gmail

1. **Включить 2FA** на аккаунте Google
2. **Создать App Password** (не используйте основной пароль):
   - Перейти в https://myaccount.google.com/apppasswords
   - Выбрать "Mail" и "Windows Computer"
   - Google сгенерирует 16-символьный пароль
   - Использовать этот пароль в `SMTP_PASSWORD`

### Для Own SMTP Server

```bash
SMTP_HOST=mail.example.com
SMTP_PORT=587  # или 465 для SSL/TLS
SMTP_USERNAME=notifications@example.com
SMTP_PASSWORD=your-password
SMTP_FROM_EMAIL=notifications@example.com
SMTP_FROM_NAME=Signal Desk
```

---

## 🚀 Запуск

### Вариант 1: Запуск Consumer как Отдельный Сервис

```bash
# В папке services/output_module/
cd services/output_module

# Установить зависимости
pip install -r requirements.txt

# Запустить consumer
python notification_consumer_main.py
```

Консоль покажет:
```
============================================================
🚀 NOTIFICATION CONSUMER STARTED
============================================================
📡 Kafka Servers: localhost:9092
📬 Input Topic: articles_analyzed
👥 Group ID: notifications-sender-group
🗄️  Database: postgresql://postgres:postgres@post...
============================================================
✅ Kafka Consumer started. Listening to topic: articles_analyzed
🎯 Starting to consume messages...
```

### Вариант 2: В Docker (docker-compose.yml)

```yaml
# services/output_module/docker-compose.yml

notification-consumer:
  build:
    context: .
    dockerfile: Dockerfile
  environment:
    DATABASE_URL: postgresql://postgres:postgres@postgres:5432/news_analyzer
    KAFKA_BOOTSTRAP_SERVERS: kafka:9092
    KAFKA_INPUT_TOPIC: articles_analyzed
    KAFKA_NOTIFICATION_GROUP_ID: notifications-sender-group
    SMTP_HOST: ${SMTP_HOST:-smtp.gmail.com}
    SMTP_PORT: ${SMTP_PORT:-587}
    SMTP_USERNAME: ${SMTP_USERNAME}
    SMTP_PASSWORD: ${SMTP_PASSWORD}
    SMTP_FROM_EMAIL: ${SMTP_FROM_EMAIL:-noreply@signaldesk.io}
    SMTP_FROM_NAME: ${SMTP_FROM_NAME:-Signal Desk}
    SMTP_ENABLED: "true"
    JWT_SECRET_KEY: ${JWT_SECRET_KEY}
  command: python notification_consumer_main.py
  depends_on:
    - kafka
    - postgres
  networks:
    - app-network
```

---

## 🧪 Тестирование

### 1. Отправить Тестовое Email Через API

```bash
# Получить токен
curl -X POST http://localhost:8003/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login":"your_username","password":"your_password"}'

# Использовать токен для отправки тестового email
curl -X POST http://localhost:8003/api/v1/notifications/test-email \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Успешный ответ:
```json
{
  "message": "Test email sent successfully",
  "to": "your-email@example.com",
  "status": "sent"
}
```

### 2. Проверить Настройки Уведомлений

```bash
curl -X GET http://localhost:8003/api/v1/notifications/config \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Ответ должен содержать:
```json
{
  "settings": {
    "id": 1,
    "enabled": true,
    "digest_frequency": "instant"
  },
  "channels": [
    {
      "id": 1,
      "channel_type": "email",
      "channel_address": "your-email@example.com",
      "enabled": true
    }
  ],
  "triggers": [
    {
      "id": 1,
      "name": "Watch OrgName",
      "trigger_type": "organization",
      "trigger_value": "123",
      "enabled": true
    }
  ]
}
```

### 3. Полный Flow на Frontend

```
1. Открыть http://localhost:5173/notifications
2. Включить уведомления
3. Ввести email: your-email@example.com
4. Выбрать организацию "ПАО Газпром"
5. Нажать "Сохранить настройки"
6. Нажать "Отправить тестовое письмо" (кнопка на странице)
   ✅ Письмо должно прийти на почту!
7. Запустить Consumer (python notification_consumer_main.py)
8. Когда приходит новая статья с упоминанием "ПАО Газпром"
   ✅ Email должен придти автоматически!
```

---

## 📊 Архитектура Потока Данных

```
┌─────────────────────────┐
│  Frontend (http://localhost:5173)
│  - Ввод email
│  - Выбор сущностей для отслеживания
└──────────────┬──────────┘
               │
               ↓
┌─────────────────────────┐
│  REST API (port 8003)
│  - POST /notifications/settings
│  - POST /notifications/triggers
│  - POST /notifications/channels
└──────────────┬──────────┘
               │
               ↓
┌─────────────────────────┐
│  PostgreSQL Database
│  - notification_settings
│  - notification_triggers
│  - notification_channels
└──────────────────────────┘

┌─────────────────────────┐
│  Data Pipeline
│  - Parsers → raw_articles (Kafka)
│  - Preprocessing → articles_analyzed (Kafka)
│  - Text Analysis → enriched articles
└──────────────┬──────────┘
               │
               ↓
┌─────────────────────────────────┐
│  Notification Consumer
│  (notification_consumer_main.py)
│  - Слушает: articles_analyzed
│  - Проверяет: есть ли упоминания
│  - Запрашивает: триггеры из БД
│  - Отправляет: email
└──────────────┬──────────────────┘
               │
               ↓
┌─────────────────────────┐
│  Email Service (SMTP)
│  - Генерирует HTML письмо
│  - Отправляет через Gmail/Own Server
└──────────────┬──────────┘
               │
               ↓
┌─────────────────────────┐
│  User Email Inbox ✅
│  - "🔔 Signal Desk: Упоминание ПАО Газпром"
│  - Статья, тональность, риск
└─────────────────────────┘
```

---

## 🔍 Логирование и Отладка

### Consumer Логи

```bash
# Запуск с DEBUG логом
export LOG_LEVEL=DEBUG
python notification_consumer_main.py
```

Примеры логов:
```
2024-05-04 10:30:15 - notification_consumer - INFO - ✅ Kafka Consumer started
2024-05-04 10:30:20 - notification_consumer - DEBUG - 📬 Received message: article_456
2024-05-04 10:30:21 - notification_consumer - INFO - 🔔 Found 2 triggers for entities [123, 456]
2024-05-04 10:30:22 - notification_consumer - INFO - ✅ Email sent to user 1
2024-05-04 10:30:23 - notification_consumer - INFO - ✅ Email sent to user 2
```

### Проверить Логи Consumer в Docker

```bash
docker logs -f news_analyzer-notification-consumer-1 --tail 50
```

---

## ⚠️ Возможные Проблемы и Решения

### Проблема 1: "Connection refused" при подключении к Kafka

**Причина**: Consumer не может подключиться к Kafka

**Решение**:
```bash
# Проверить, что Kafka запущен
docker ps | grep kafka

# Проверить сетевые настройки в docker-compose
# KAFKA_BOOTSTRAP_SERVERS должен быть kafka:9092 (внутри docker)
# Не localhost:9092
```

### Проблема 2: "Authentication failed" при отправке email

**Причина**: Неверные учетные данные SMTP

**Решение**:
```bash
# Для Gmail проверить:
# 1. 2FA включена
# 2. Используется App Password, не основной пароль
# 3. Пароль скопирован без пробелов

# Проверить конфиг
echo $SMTP_USERNAME
echo $SMTP_PASSWORD
```

### Проблема 3: "Email channel not found"

**Причина**: На фронтенде не сохранился email

**Решение**:
```bash
# Проверить в БД
psql postgresql://postgres:postgres@localhost:5432/news_analyzer

SELECT * FROM notification_channels WHERE user_id = 1;
```

### Проблема 4: Consumer не получает сообщений

**Причина**: Неверный топик или group_id

**Решение**:
```bash
# Проверить доступные топики в Kafka
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Проверить consumer groups
docker exec kafka kafka-consumer-groups --list --bootstrap-server localhost:9092

# Проверить настройки в .env
# KAFKA_INPUT_TOPIC должен совпадать с топиком, куда пишут парсеры
```

---

## 📝 Файловая Структура

```
services/output_module/
├── notification_consumer_main.py      # Entry point для запуска consumer
├── src/
│   ├── services/
│   │   ├── email_service.py           # 📧 Email отправка (SMTP)
│   │   ├── notification_consumer.py   # 🔔 Kafka consumer для уведомлений
│   │   └── notification.py            # Управление триггерами
│   ├── presentation/api/v1/routes/
│   │   └── notification/
│   │       └── api.py                 # ✅ REST endpoints
│   └── infrastructure/postgres/models/
│       └── notification.py            # 📊 БД моделе
├── .env                               # Конфигурация (не в git)
├── .env.example                       # Пример конфигурации ✅
└── requirements.txt                   # Dependencies (aiokafka добавлен)
```

---

## 🚀 Next Steps

1. **Установить зависимости**:
   ```bash
   cd services/output_module
   pip install -r requirements.txt
   ```

2. **Настроить `.env`**:
   - Копировать `.env.example` в `.env`
   - Добавить SMTP учетные данные

3. **Запустить Consumer**:
   ```bash
   python notification_consumer_main.py
   ```

4. **Тестировать на Frontend**: `http://localhost:5173/notifications`

5. **Отправить тестовое письмо** через API endpoint

6. **Проверить Логи**:
   ```bash
   # Consumer логи
   tail -f /var/log/notification_consumer.log
   ```

---

## 📞 Как Это Работает

### Когда пользователь сохраняет настройки:

1. **Frontend** отправляет данные в REST API
2. **Backend** сохраняет триггеры в БД (notification_triggers)
3. **Backend** сохраняет email канал (notification_channels)

### Когда новая статья поступает в систему:

1. **Parser** отправляет `raw_article` в Kafka `raw_articles`
2. **Text Preprocessing** обрабатывает, отправляет в `articles_analyzed` с `entities`
3. **Notification Consumer** (всегда запущен):
   - Слушает `articles_analyzed`
   - Для каждой статьи извлекает ID упоминаемых сущностей
   - Ищит в БД триггеры, которые отслеживают эти сущности
   - Для каждого найденного триггера:
     - Получает user_id
     - Проверяет, что уведомления включены
     - Получает email канал пользователя
     - **Отправляет email!** ✅

### Email Письмо Содержит:

- 📰 Заголовок и описание статьи
- 🔗 Ссылка на полный текст
- 🔴 Уровень риска (high/medium/low)
- 😊 Тональность (positive/negative/neutral)
- 👤 Какая сущность упоминается
- ✉️ Красивый HTML дизайн

---

**Готово! Система полностью рабочая! 🎉**
