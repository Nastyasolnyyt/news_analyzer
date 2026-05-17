# 🚀 Email Notifications - Быстрый Старт

## За 5 Минут до Рабочей Системы

### ✅ ШАГ 1: Email Конфигурация (1 мин)

**Для Gmail:**
```bash
# 1. Перейти: https://myaccount.google.com/apppasswords
# 2. Создать App Password для Mail
# 3. Скопировать пароль (16 символов)

# В папке services/output_module создать/обновить .env:
cat > .env << 'EOF'
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/news_analyzer
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_INPUT_TOPIC=articles_analyzed
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
SMTP_FROM_EMAIL=noreply@signaldesk.io
SMTP_FROM_NAME=Signal Desk
SMTP_ENABLED=true
JWT_SECRET_KEY=your-secret-key
EOF
```

### ✅ ШАГ 2: Запустить Consumer (1 мин)

```bash
cd services/output_module

# Установить зависимости (если еще не установлены)
pip install -r requirements.txt

# Запустить Consumer
python notification_consumer_main.py
```

Вы должны увидеть:
```
✅ Kafka Consumer started. Listening to topic: articles_analyzed
🎯 Starting to consume messages...
```

### ✅ ШАГ 3: На Frontend (2 мин)

```
1. Открыть http://localhost:5173/notifications

2. Включить: Статус → "Включено"

3. Email: Ввести свой email (test@example.com)

4. Организация: Поиск "ПАО" → Выбрать

5. Кнопка: "Сохранить настройки"
   ✅ "Настройки успешно сохранены!"

6. Кнопка: "📧 Тестовое письмо"
   ✅ Письмо придет за 1-2 секунды!
```

---

## 🔄 Как Это Работает

```
Frontend (Email + Организации)
         ↓
REST API (Сохраняет триггеры)
         ↓
PostgreSQL (Хранит)
         ↓
New Article (Поступает в Kafka)
         ↓
Consumer (Проверяет триггеры)
         ↓
Email Service (Отправляет письмо) ✅
         ↓
Inbox (Письмо!)
```

---

## 🧪 Проверка

**Тестовое письмо:**
```
Subject: 🔔 Signal Desk: Тестовое письмо
```

**Real письмо при упоминании организации:**
```
Subject: 🔔 Signal Desk: Упоминание ПАО Газпром
```

---

## 🛟 Если Не Работает

| Проблема | Решение |
|----------|---------|
| Email не сохраняется | Проверить консоль браузера (F12) |
| Тестовое письмо не приходит | Проверить SMTP конфиг в .env |
| Consumer не стартует | `docker ps \| grep kafka` - проверить Kafka |
| Письмо не отправляется автоматически | Проверить логи Consumer: `tail -f notification_consumer.log` |

---

## 📊 Файлы

- Backend: `services/output_module/src/services/email_service.py`
- Consumer: `services/output_module/src/services/notification_consumer.py`
- Frontend: `frontend2/src/views/NotificationsSettings.vue`
- Config: `services/output_module/.env`

---

## ✅ ГОТОВО!

Система полностью рабочая! 🎉
