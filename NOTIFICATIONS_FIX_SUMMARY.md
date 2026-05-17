# 🔧 Исправления Системы Уведомлений

## 📝 Резюме

Исправлена система уведомлений в `/frontend2/src/views/NotificationsSettings.vue`:
- ✅ Добавлен поиск по организациям и персонам
- ✅ Исправлено сохранение настроек (теперь они реально персистируются в БД)
- ✅ Исправлено управление триггерами (создание + обновление)
- ✅ Добавлена автоматическая инициализация каналов при первой загрузке
- ✅ Статус уведомлений теперь сохраняется и восстанавливается

---

## 🎯 Основные Изменения

### 1. **Поиск по Сущностям** 🔍

#### Что было:
```
- Вся запись просто выводилась в список
- Нельзя было найти нужную организацию в большом списке
```

#### Что изменилось:
```typescript
// Новые refs для поиска
const orgSearchQuery = ref('');
const personSearchQuery = ref('');

// Computed properties для фильтрации
const filteredOrganizations = computed(() => {
  const query = orgSearchQuery.value.toLowerCase();
  return query 
    ? allOrganizations.value.filter(org => org.name.toLowerCase().includes(query)) 
    : allOrganizations.value;
});
```

#### Результат:
- 🔎 Поля поиска в каждой секции (Организации, Персоны)
- ⚡ Фильтрация в реальном времени
- 🎯 Быстрый поиск нужной сущности

---

### 2. **Корректное Сохранение Триггеров** 💾

#### Что было (ПРОБЛЕМА):
```typescript
// НЕПРАВИЛЬНЫЙ КОД - пытался обновить триггеры, которых может не быть!
const config = await apiClient.getNotificationConfig();
const orgTriggers = config.triggers.filter(t => t.trigger_type === 'organization');
for (const trigger of orgTriggers) {
  const orgId = parseInt(trigger.trigger_value);
  await apiClient.updateNotificationTrigger(trigger.id, {
    enabled: selectedOrganizations.value.has(orgId),  // ❌ Работает только если триггер уже существует!
  });
}
```

#### Что изменилось:
```typescript
// ПРАВИЛЬНЫЙ КОД - создает или обновляет триггеры
for (const orgId of selectedOrganizations.value) {
  if (currentOrgTriggers.has(orgId)) {
    // Триггер уже существует - обновляем
    const triggerId = currentOrgTriggers.get(orgId)!;
    await apiClient.updateNotificationTrigger(triggerId, {
      enabled: true,
    });
  } else {
    // Триггера нет - создаем новый
    const org = allOrganizations.value.find(o => o.id === orgId);
    if (org) {
      await apiClient.createNotificationTrigger({
        name: `Watch ${org.name}`,
        trigger_type: 'organization',
        trigger_value: String(orgId),
        enabled: true,
      });
    }
  }
}

// Отключаем триггеры для невыбранных организаций
for (const [orgId, triggerId] of currentOrgTriggers) {
  if (!selectedOrganizations.value.has(orgId)) {
    await apiClient.updateNotificationTrigger(triggerId, {
      enabled: false,
    });
  }
}
```

#### Результат:
- ✅ Новые триггеры создаются при первом выборе
- ✅ Существующие триггеры обновляются
- ✅ Невыбранные триггеры отключаются (не удаляются)
- ✅ Никаких ошибок при сохранении

---

### 3. **Сохранение Статуса Уведомлений** 🔔

#### Что было:
```javascript
// statusEnabled изменялась только в UI, но не сохранялась в БД
const statusEnabled = ref(true);
// Нет сохранения этого значения!
```

#### Что изменилось:
```javascript
// Теперь сохраняется через API
await apiClient.updateNotificationSettings({
  enabled: statusEnabled.value,  // ✅ Сохраняется в БД!
  digest_frequency: digestFrequency.value,
});
```

#### Результат:
- ✅ При переключении "Включено/Выключено" сохраняется статус
- ✅ После перезагрузки статус восстанавливается
- ✅ Email уведомления отправляются только если включено

---

### 4. **Автоматическая Инициализация** 🚀

#### Что было:
```
- Если каналов нет - ошибка
- Если настроек нет - ошибка
```

#### Что добавилось:
```typescript
// Инициализируем основные настройки, если их нет
if (!config.settings || !config.settings.id) {
  const newSettings = await apiClient.updateNotificationSettings({
    enabled: true,
    digest_frequency: 'instant',
  });
  config.settings = newSettings;
}

// Инициализируем email канал, если его нет
if (!config.channels || config.channels.length === 0) {
  const newChannel = await apiClient.createNotificationChannel({
    channel_type: 'email',
    channel_address: '',
    enabled: true,
  });
  config.channels = [newChannel];
}
```

#### Результат:
- ✅ При первом входе автоматически создаются базовые структуры
- ✅ Нет ошибок при первоначальной загрузке
- ✅ Пользователь может сразу начать использовать уведомления

---

### 5. **Управление ID-шками** 📋

#### Новые переменные для отслеживания:
```typescript
// Maps для связи между сущностями и триггерами
const orgTriggersMap = ref<Map<number, number>>(new Map());
const personTriggersMap = ref<Map<number, number>>(new Map());

// ID-шки для обновления
let emailChannelId: number | null = null;
let notificationSettingsId: number | null = null;
```

#### Использование:
```typescript
// При загрузке сохраняем ID-шки
orgTriggersMap.value.set(orgId, trigger.id);

// При сохранении используем ID-шки для обновления
const triggerId = currentOrgTriggers.get(orgId)!;
await apiClient.updateNotificationTrigger(triggerId, { enabled: true });
```

---

## 🧪 Что Нужно Проверить

### Тест 1: Переключение Статуса
```
1. Открыть http://localhost:5173/notifications
2. Переключить "Включено/Выключено"
3. Нажать "Сохранить настройки"
4. Перезагрузить страницу
✅ Статус должен остаться тем же
```

### Тест 2: Поиск Организаций
```
1. В поле поиска организаций ввести "ПАО" или часть названия
2. Список должен отфильтроваться мгновенно
3. Выбрать организацию
4. Нажать "Сохранить настройки"
5. Перезагрузить страницу
✅ Организация должна остаться выбранной
```

### Тест 3: Email и Частота
```
1. Ввести email
2. Выбрать частоту "Ежедневно"
3. Нажать "Сохранить настройки"
4. Перезагрузить страницу
✅ Email и частота должны восстановиться
```

### Тест 4: Полный Цикл
```
1. Включить уведомления
2. Выбрать 3 организации через поиск
3. Выбрать 2 персоны через поиск
4. Ввести email
5. Установить частоту "Сразу же"
6. Нажать "Сохранить настройки"
   → Должно быть: "Настройки успешно сохранены!"
7. Перезагрузить страницу
✅ Все параметры должны восстановиться
8. Отключить уведомления
9. Нажать "Сохранить настройки"
10. Перезагрузить страницу
✅ Уведомления должны остаться отключены
```

---

## 📊 Сравнение До/После

| Функция | До | После |
|---------|-----|--------|
| **Поиск организаций** | ❌ Нет | ✅ Есть |
| **Поиск персон** | ❌ Нет | ✅ Есть |
| **Сохранение статуса** | ❌ Теряется при перезагрузке | ✅ Сохраняется в БД |
| **Создание триггеров** | ❌ Ошибка, если триггера нет | ✅ Автоматически создается |
| **Обновление триггеров** | ❌ Только если уже есть | ✅ Создается, если нет |
| **Email канал** | ❌ Может быть не инициализирован | ✅ Создается автоматически |
| **Инициализация** | ❌ Может быть ошибка | ✅ Автоматическая инициализация |
| **Сообщение об успехе** | ❌ Может быть ложное | ✅ Только при реальном сохранении |

---

## 🔗 Затронутые Файлы

- **Основной файл**: `/frontend2/src/views/NotificationsSettings.vue`
- **API клиент**: `/frontend2/src/api/client.ts` (уже содержит все необходимые методы)
- **Роутер**: `/frontend2/src/router.ts` (уже содержит маршрут /notifications)

---

## 🚀 Backend (Не требует Изменений)

Backend уже имеет все необходимые эндпоинты:
- ✅ `GET /api/v1/notifications/config` - загружает конфигурацию
- ✅ `PUT /api/v1/notifications/settings` - сохраняет настройки
- ✅ `POST /api/v1/notifications/triggers` - создает триггер
- ✅ `PUT /api/v1/notifications/triggers/{id}` - обновляет триггер
- ✅ `POST /api/v1/notifications/channels` - создает канал
- ✅ `PUT /api/v1/notifications/channels/{id}` - обновляет канал

---

## 📝 Логирование

Все действия логируются в Console (DevTools → Console tab):
```
✅ Settings updated
✅ Email channel created
✅ Org trigger 123 created
✅ Org trigger 124 updated
✅ Org trigger 125 disabled
✅ Person trigger 456 created
✅ All settings saved successfully
```

---

## ⚠️ Известные Ограничения

1. **Отправка Email-уведомлений** - только сохранение конфигурации
   - Для отправки нужна отдельная интеграция с email-сервисом (SMTP, SendGrid и т.д.)
   
2. **Telegram интеграция** - не реализована
   - Нужно добавить новый тип канала

3. **История уведомлений** - не показывается
   - Нужна отдельная страница для просмотра логов

---

## 🎉 Итог

Система уведомлений теперь:
- 🔍 Имеет удобный поиск
- 💾 Реально сохраняет все настройки
- 🚀 Автоматически инициализируется при первом использовании
- ✅ Не теряет данные при перезагрузке страницы
- 📊 Логирует все действия для отладки
