# Исправление системы уведомлений

## Проблемы и решения

### 1. ✅ ИСПРАВЛЕНО: Ошибка подключения frontend к backend

**Проблема:** Браузер выводит ошибку:
```
Unexpected end of JSON input
http proxy error: /api/v1/notifications/test-email
AggregateError [ECONNREFUSED]
```

**Причина:** `.env` frontend2 содержал IP адрес внешнего сервера:
```
VITE_API_URL=http://185.130.212.50:8003/api/v1
```

**Решение:** ✅ Изменено на относительный путь:
```
VITE_API_URL=/api/v1
```

Теперь Vite proxy автоматически маршрутизирует запросы:
- Браузер: `http://localhost:5173/api/v1/...`
- Vite proxy перенаправляет на: `http://localhost:8003/...` (в контейнере)

**Статус:** Исправлено в файле `/home/nastya/study/news_analyzer/frontend2/.env`

---

### 2. ✅ ДОБАВЛЕНО: Функция отправки тестового письма

**Проблемы:** Отсутствовала функция отправки тестового письма в API client и кнопка в UI.

**Решение:** 
- ✅ Добавлена функция `sendTestEmail()` в `/home/nastya/study/news_analyzer/frontend2/src/api/client.ts`
- ✅ Добавлена кнопка "📧 Отправить тест" в компонент `NotificationSettings.vue`
- ✅ Добавлена функция `handleSendTestEmail()` в компонент

**Как использовать:**
1. Откройте http://localhost:5173/notifications
2. Убедитесь, что email канал добавлен в конфигурацию
3. Нажмите кнопку "📧 Отправить тест"

---

### 3. ⚠️ ТРЕБУЕТСЯ ДЕЙСТВИЕ: Конфигурация SMTP

**Проблема:** `.env` содержит placeholder SMTP значения:
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com  ← ⚠️ Placeholder!
SMTP_PASSWORD=app-password            ← ⚠️ Placeholder!
SMTP_FROM_EMAIL=noreply@signaldesk.io
SMTP_FROM_NAME=Signal Desk
```

**Решение для Gmail:**

1. Включите "2-Step Verification" на аккаунте Google
2. Создайте "App password":
   - Перейдите в https://myaccount.google.com/apppasswords
   - Выберите "Mail" и "Windows Computer" (или другое)
   - Скопируйте 16-символьный пароль

3. Обновите `.env` (или `.env.production`):
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=ваш-email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
SMTP_FROM_EMAIL=ваш-email@gmail.com
SMTP_FROM_NAME=Signal Desk
SMTP_ENABLED=true
```

4. Перезапустите backend:
```bash
docker compose restart output_module
```

---

### 4. Проверка статуса

**Проверить, работает ли backend:**
```bash
# Проверить логи
docker compose logs output_module --tail=50

# Проверить доступность
curl -I http://localhost:8003/docs
```

**Проверить конфигурацию SMTP в backend:**
```bash
# Проверить переменные окружения в контейнере
docker compose exec output_module env | grep SMTP
```

**Проверить, доступна ли функция test-email:**
```bash
curl -X POST http://localhost:8003/api/v1/notifications/test-email \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

---

## Все исправления

| №  | Описание | Статус | Файл | Действие |
|----|----------|--------|------|----------|
| 1  | Ошибка подключения frontend | ✅ Исправлено | `frontend2/.env` | Изменен URL на `/api/v1` |
| 2  | Функция sendTestEmail | ✅ Добавлено | `frontend2/src/api/client.ts` | Добавлена функция |
| 3  | Кнопка отправки теста | ✅ Добавлено | `frontend2/src/components/NotificationSettings.vue` | Добавлена кнопка и обработчик |
| 4  | SMTP конфигурация | ⚠️ Требуется | `.env` или `.env.production` | Обновить credentials |

---

## Следующие шаги

1. **Обновите SMTP конфигурацию** в `.env` (или `.env.production`)
2. **Перезапустите backend**: `docker compose restart output_module`
3. **Откройте** http://localhost:5173/notifications
4. **Нажмите** "📧 Отправить тест"
5. **Проверьте** почту на наличие тестового письма

---

## Возможные ошибки и решения

### Ошибка: "Email channel not configured"
- Убедитесь, что email канал добавлен в настройках уведомлений
- Email канал должен иметь тип `email` и указан адрес

### Ошибка: "Failed to send test email"
- Проверьте SMTP credentials в `.env`
- Убедитесь, что app password используется (не обычный пароль для Gmail)
- Проверьте логи backend: `docker compose logs output_module`

### Ошибка: "Unexpected end of JSON input"
- Обновите страницу (Ctrl+Shift+R)
- Проверьте консоль браузера (F12) для деталей ошибки
- Убедитесь, что backend доступен: `curl http://localhost:8003/docs`

---

## Тестирование

```bash
# 1. Проверить, что backend работает
curl http://localhost:8003/api/v1/notifications/config \
  -H "Authorization: Bearer YOUR_TOKEN"

# 2. Проверить логи отправки email
docker compose logs output_module -f | grep -i email

# 3. Проверить SMTP подключение
docker compose exec output_module python3 -c "
import smtplib
smtp = smtplib.SMTP('smtp.gmail.com', 587)
smtp.starttls()
try:
    smtp.login('your-email@gmail.com', 'app-password')
    print('✅ SMTP credentials valid')
except Exception as e:
    print(f'❌ SMTP error: {e}')
finally:
    smtp.quit()
"
```
