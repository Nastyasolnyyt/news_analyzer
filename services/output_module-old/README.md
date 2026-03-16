# Output Module Backend

Backend API для модуля вывода данных с аутентификацией, управлением пользователями и фильтрацией постов.

## Описание проекта

Проект представляет собой REST API на базе FastAPI для управления постами, сущностями и пользователями. Система включает:

- JWT-аутентификацию с access и refresh токенами
- Управление пользователями с ролевой моделью (superadmin, admin, user)
- Фильтрацию, сортировку и пагинацию постов
- Поиск упоминаний сущностей с фильтрацией по датам

## Требования

- Python 3.10+
- Docker и Docker Compose
- PostgreSQL 15+
- Redis 7+

## Технологии

- **FastAPI** - веб-фреймворк
- **SQLAlchemy** - ORM
- **Alembic** - миграции БД
- **PostgreSQL** - база данных
- **Redis** - кэш
- **JWT** (python-jose) - аутентификация
- **bcrypt** - хэширование паролей
- **Dishka** - dependency injection

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd output_module_backend
```

### 2. Настройка окружения

Создайте файл `.env` в корне проекта со следующим содержимым:

```env
# PostgreSQL
PG_HOST=postgres
PG_PORT=5432
PG_DATABASE=your_database
PG_USERNAME=your_username
PG_PASSWORD=your_password

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB_INDEX=0
REDIS_USERNAME=your_redis_user
REDIS_PASSWORD=your_redis_password

# App
APP_PORT=8000
APP_API_KEY=your_api_key_for_legacy_endpoints

# JWT
JWT_SECRET_KEY=your_jwt_secret_key_here_very_long_and_random
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Super Admin Init
SUPERADMIN_INIT_TOKEN=your_pre_shared_secret_token_for_superadmin_init
```

### 3. Запуск через Docker Compose

```bash
docker-compose up --build
```

Приложение будет доступно по адресу: `http://localhost:8000`

### 4. Применение миграций

```bash
docker-compose exec app alembic upgrade head
```

Или если запускаете локально:

```bash
alembic upgrade head
```

## Документация API

После запуска приложения документация доступна по адресам:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Эндпоинты

### Аутентификация

#### POST `/api/v1/auth/login`
Вход в систему.

**Запрос:**
```json
{
  "login": "user@example.com",
  "password": "password123"
}
```

**Ответ:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

**Пример curl:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"login": "admin", "password": "password123"}'
```

#### POST `/api/v1/auth/refresh`
Обновление access токена.

**Запрос:**
```json
{
  "refresh_token": "eyJ..."
}
```

#### POST `/api/v1/auth/superadmin/init`
Инициализация супер-админа (только при первом запуске).

**Заголовки:**
```
X-Auth-Token: your_pre_shared_secret_token
```

**Запрос:**
```json
{
  "login": "superadmin",
  "password": "secure_password",
  "name": "Super Admin",
  "role": "superadmin"
}
```

**Пример curl:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/superadmin/init" \
  -H "Content-Type: application/json" \
  -H "X-Auth-Token: your_pre_shared_secret_token" \
  -d '{
    "login": "superadmin",
    "password": "secure_password",
    "name": "Super Admin",
    "role": "superadmin"
  }'
```

### Управление пользователями

Все эндпоинты требуют авторизации через `Authorization: Bearer <token>`.

#### POST `/api/v1/users`
Создание пользователя (только для superadmin).

**Запрос:**
```json
{
  "login": "newuser",
  "password": "password123",
  "name": "New User",
  "role": "user"
}
```

#### GET `/api/v1/users`
Список пользователей с фильтрацией и пагинацией.

**Query параметры:**
- `role` - фильтр по роли (superadmin, admin, user)
- `login` - поиск по login (частичное совпадение)
- `page` - номер страницы (по умолчанию: 1)
- `page_size` - размер страницы (по умолчанию: 20, максимум: 100)

**Пример:**
```bash
curl -X GET "http://localhost:8000/api/v1/users?role=user&page=1&page_size=20" \
  -H "Authorization: Bearer <token>"
```

#### GET `/api/v1/users/{user_id}`
Получение информации о пользователе.

#### PATCH `/api/v1/users/{user_id}`
Обновление информации о пользователе.

**Запрос:**
```json
{
  "name": "Updated Name",
  "role": "admin",
  "password": "new_password"
}
```

### Посты

#### GET `/api/v1/posts`
Список постов с фильтрацией, сортировкой и пагинацией.

**Query параметры:**
- `topic_id` - фильтр по ID темы
- `emotion` - фильтр по эмоции (float)
- `tonality` - фильтр по тональности (float)
- `relevance` - фильтр по релевантности (float)
- `entity_id` - фильтр по ID сущности
- `sort` - поле для сортировки (id, created_at, emotion, tonality, relevance)
- `order` - порядок сортировки (asc, desc)
- `page` - номер страницы
- `page_size` - размер страницы

**Пример:**
```bash
curl -X GET "http://localhost:8000/api/v1/posts?topic_id=1&sort=created_at&order=desc&page=1&page_size=20" \
  -H "X-Auth-Token: your_api_key"
```

#### GET `/api/v1/posts/{post_id}`
Получение поста по ID с полной информацией (analysis, entities).

**Пример:**
```bash
curl -X GET "http://localhost:8000/api/v1/posts/1" \
  -H "X-Auth-Token: your_api_key"
```

### Упоминания сущностей

#### GET `/api/v1/entities/{entity_id}/mentions`
Получение упоминаний сущности с фильтрацией по датам.

**Query параметры:**
- `start` - начальная дата (ISO format: 2025-01-01T00:00:00)
- `end` - конечная дата (ISO format: 2025-01-31T23:59:59)

**Пример:**
```bash
curl -X GET "http://localhost:8000/api/v1/entities/1/mentions?start=2025-01-01T00:00:00&end=2025-01-31T23:59:59" \
  -H "X-Auth-Token: your_api_key"
```

**Ответ:**
```json
[
  {
    "entity": {
      "id": 1,
      "name": "Entity Name",
      "entity_type": "PERSON",
      "created_at": "2025-01-01T00:00:00"
    },
    "mentioned_at": "2025-01-15T10:30:00"
  }
]
```

## Роли пользователей

- **superadmin** - полный доступ, может создавать пользователей
- **admin** - может просматривать и обновлять всех пользователей
- **user** - может просматривать и обновлять только свой профиль

## Безопасность

- Пароли хранятся в хэшированном виде (bcrypt)
- JWT токены с ограниченным временем жизни
- Refresh токены для обновления access токенов
- Защита эндпоинтов через JWT авторизацию
- Инициализация superadmin только через pre-shared token

## Структура проекта

```
output_module_backend/
├── alembic/              # Миграции БД
├── src/
│   ├── application/      # Схемы, энумы, ошибки
│   ├── core/            # Конфигурация, логирование
│   ├── infrastructure/  # Модели, репозитории, БД
│   ├── presentation/    # API routes, middleware
│   └── services/        # Бизнес-логика
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Разработка

### Локальная разработка без Docker

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Настройте переменные окружения в `.env`

3. Запустите PostgreSQL и Redis локально или через Docker

4. Примените миграции:
```bash
alembic upgrade head
```

5. Запустите сервер:
```bash
uvicorn src.main:app --reload
```

### Создание миграций

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```
