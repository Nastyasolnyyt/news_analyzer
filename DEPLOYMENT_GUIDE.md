# 🚀 РАЗВЕРТЫВАНИЕ - Email Notifications System

## 📋 Содержание
1. [Для Разработчиков](#-для-разработчиков-локальная-разработка)
2. [Для Production](#-для-production)
3. [Проверка](#-проверка-работоспособности)

---

## 💻 Для Разработчиков (Локальная Разработка)

### Требования
- Python 3.9+
- PostgreSQL запущена
- Kafka запущена
- Redis (опционально)

### Установка

**1. Клонировать и перейти**
```bash
cd services/output_module
```

**2. Создать виртуальное окружение**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
.\venv\Scripts\activate  # Windows
```

**3. Установить зависимости**
```bash
pip install -r requirements.txt
```

**4. Создать `.env` файл**
```bash
# Скопировать пример
cp .env.example .env

# Отредактировать .env:
# - DATABASE_URL
# - SMTP_USERNAME и SMTP_PASSWORD
# - KAFKA_BOOTSTRAP_SERVERS
# - JWT_SECRET_KEY

nano .env  # или используйте редактор
```

**5. Запустить миграции БД** (если нужно)
```bash
# Если таблицы уже созданы, пропустить
alembic upgrade head
```

**6. Запустить Consumer**
```bash
python notification_consumer_main.py
```

Вы должны увидеть:
```
✅ NOTIFICATION CONSUMER STARTED
✅ Kafka Consumer started
🎯 Starting to consume messages...
```

**7. В отдельном терминале запустить Backend API**
```bash
# Из папки services/output_module
python -m uvicorn src.main:app --host 0.0.0.0 --port 8003 --reload
```

**8. В отдельном терминале запустить Frontend**
```bash
cd frontend2
npm run dev
```

**9. Открыть Frontend**
```
http://localhost:5173/notifications
```

---

## 🐳 Для Production (Docker)

### Подготовка

**1. Переменные окружения**

Создать файл `.env.production` в корне проекта:
```bash
# Database
DATABASE_URL=postgresql://postgres:YOUR_SECURE_PASSWORD@postgres:5432/news_analyzer

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_INPUT_TOPIC=articles_analyzed
KAFKA_NOTIFICATION_GROUP_ID=notifications-sender-group

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
SMTP_FROM_EMAIL=noreply@yourdomain.io
SMTP_FROM_NAME=Your Company
SMTP_ENABLED=true

# JWT
JWT_SECRET_KEY=your-very-secure-random-key-change-me

# API
ENVIRONMENT=production
```

**2. Dockerfile для Consumer**

Если его еще нет, создать `services/output_module/Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установить зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Скопировать код
COPY . .

# Запустить Consumer
CMD ["python", "notification_consumer_main.py"]
```

**3. Docker Compose Update**

Добавить в `docker-compose.yml`:
```yaml
services:
  # ... существующие сервисы ...

  notification-consumer:
    build:
      context: ./services/output_module
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: ${DATABASE_URL}
      KAFKA_BOOTSTRAP_SERVERS: kafka:9092
      KAFKA_INPUT_TOPIC: articles_analyzed
      KAFKA_NOTIFICATION_GROUP_ID: notifications-sender-group
      SMTP_HOST: ${SMTP_HOST}
      SMTP_PORT: ${SMTP_PORT}
      SMTP_USERNAME: ${SMTP_USERNAME}
      SMTP_PASSWORD: ${SMTP_PASSWORD}
      SMTP_FROM_EMAIL: ${SMTP_FROM_EMAIL}
      SMTP_FROM_NAME: ${SMTP_FROM_NAME}
      SMTP_ENABLED: "true"
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
    depends_on:
      - kafka
      - postgres
    networks:
      - app-network
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Развертывание

**1. Собрать образы**
```bash
docker-compose build notification-consumer
```

**2. Запустить систему**
```bash
docker-compose up -d
```

**3. Проверить логи**
```bash
docker logs -f news_analyzer-notification-consumer-1
```

**4. Проверить что все запущено**
```bash
docker ps | grep news_analyzer
# Должно быть: notification-consumer, output_module, kafka, postgres, etc.
```

---

## ✅ Проверка Работоспособности

### Шаг 1: Проверить что Consumer стартовал

```bash
# Локально
ps aux | grep notification_consumer

# Docker
docker logs notification-consumer | grep "Kafka Consumer started"
```

Должно быть:
```
✅ Kafka Consumer started. Listening to topic: articles_analyzed
```

### Шаг 2: Проверить SMTP

```bash
# Локально
python -c "
import smtplib
import os
smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
smtp_port = int(os.getenv('SMTP_PORT', 587))
username = os.getenv('SMTP_USERNAME')
password = os.getenv('SMTP_PASSWORD')

try:
    s = smtplib.SMTP(smtp_host, smtp_port, timeout=5)
    s.starttls()
    s.login(username, password)
    print('✅ SMTP Connection OK')
    s.quit()
except Exception as e:
    print(f'❌ SMTP Error: {e}')
"
```

### Шаг 3: Проверить Kafka

```bash
# Локально
kafka-topics --list --bootstrap-server localhost:9092 | grep articles_analyzed

# Docker
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092 | grep articles_analyzed
```

Должно быть:
```
articles_analyzed
```

### Шаг 4: Проверить БД

```bash
psql postgresql://postgres:password@localhost:5432/news_analyzer

-- Проверить триггеры
SELECT * FROM notification_triggers LIMIT 1;

-- Проверить каналы
SELECT * FROM notification_channels LIMIT 1;

-- Проверить настройки
SELECT * FROM notification_settings LIMIT 1;
```

### Шаг 5: Тестовое письмо через Frontend

```
1. http://localhost:5173/notifications
2. Ввести email: test@gmail.com
3. Нажать "📧 Тестовое письмо"
✅ Письмо должно прийти за 1-2 сек
```

---

## 🔍 Мониторинг и Логирование

### Consumer Логи (Локально)

```bash
# Просмотр логов в реальном времени
tail -f notification_consumer.log

# Фильтр по уровню ошибок
grep "❌" notification_consumer.log

# Подсчет отправленных писем
grep "✅ Email sent" notification_consumer.log | wc -l
```

### Consumer Логи (Docker)

```bash
# Просмотр последних 50 строк
docker logs -n 50 notification-consumer

# Просмотр в реальном времени
docker logs -f notification-consumer

# Сохранить логи в файл
docker logs notification-consumer > consumer.log 2>&1
```

### Мониторинг Производительности

```bash
# Docker stats
docker stats notification-consumer

# Проверить память
docker ps --format "table {{.Names}}\t{{.MemUsage}}"
```

---

## 🚨 Troubleshooting

### Consumer не стартует

```bash
# Проверить логи
docker logs notification-consumer

# Если "Connection refused":
docker ps | grep kafka
docker logs kafka

# Если "Database connection failed":
docker ps | grep postgres
docker logs postgres
```

### Письма не отправляются

```bash
# Проверить логи
docker logs notification-consumer | grep "Email sent"

# Проверить SMTP конфиг
docker exec notification-consumer env | grep SMTP

# Проверить что Consumer читает из Kafka
docker logs notification-consumer | grep "Received message"
```

### High CPU/Memory Usage

```bash
# Проверить размер логов
du -sh notification_consumer.log

# Ротация логов (добавить в docker-compose)
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"

# Перезагрузить
docker-compose restart notification-consumer
```

---

## 📊 Performance Tuning

### Если письма отправляются медленно

**Option 1: Увеличить pool_size в БД**
```python
# src/services/notification_consumer.py
self.engine = create_async_engine(
    self.database_url,
    pool_size=10,  # ← увеличить (default: 5)
    max_overflow=20,
)
```

**Option 2: Запустить несколько Consumer'ов**
```bash
# В разных окнах/контейнерах
python notification_consumer_main.py  # Instance 1
python notification_consumer_main.py  # Instance 2
# Kafka автоматически распределит сообщения

# Или в docker-compose с реплика
services:
  notification-consumer:
    # ... конфиг
    deploy:
      replicas: 3  # 3 экземпляра
```

**Option 3: Оптимизировать SQL запросы**
```python
# Добавить индексы в БД
CREATE INDEX idx_notification_triggers_value 
ON notification_triggers(trigger_value);

CREATE INDEX idx_notification_triggers_type 
ON notification_triggers(trigger_type);

CREATE INDEX idx_notification_channels_user 
ON notification_channels(user_id, channel_type);
```

---

## 🔐 Безопасность

### Для Production

**1. Не коммитить .env**
```bash
# Уже в .gitignore? Проверить
grep "\.env" .gitignore
```

**2. Использовать Security Secrets**
```bash
# AWS Secrets Manager
# или
# Kubernetes Secrets
# или
# HashiCorp Vault
```

**3. HTTPS для API**
```bash
# Использовать reverse proxy (nginx)
# или
# Let's Encrypt SSL certificates
```

**4. Rotate JWT Secret Key**
```bash
# Периодически менять в production
JWT_SECRET_KEY=new-random-key-every-6-months
```

---

## 📝 Checklist Развертывания

### Перед Production

- [ ] `.env.production` создан и заполнен
- [ ] SMTP testing пройден успешно
- [ ] PostgreSQL миграции выполнены
- [ ] Kafka topics созданы (articles_analyzed)
- [ ] Docker образы собраны
- [ ] docker-compose.yml обновлен
- [ ] Логирование настроено
- [ ] Мониторинг настроен
- [ ] Backup базы данных настроен
- [ ] SSL сертификаты установлены

### После Production Запуска

- [ ] Consumer логирует сообщения
- [ ] Письма отправляются успешно
- [ ] Нет ошибок в логах
- [ ] Performance мониторится
- [ ] Alerts настроены
- [ ] Documentation обновлена
- [ ] Team обучен

---

## 🎯 Результат

Успешное развертывание означает:
```
✅ Consumer запущен и слушает Kafka
✅ SMTP подключение работает
✅ Frontend отправляет тестовое письмо
✅ Письма приходят на email
✅ Автоматические уведомления работают
✅ Логирование показывает все действия
```

---

**Готово! Система в Production! 🚀**
