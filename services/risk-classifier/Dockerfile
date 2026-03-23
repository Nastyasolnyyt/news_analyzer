FROM python:3.10-slim

# Установка системных зависимостей для psycopg2 и kafka
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY . .

# Устанавливаем PYTHONPATH, чтобы импорты типа "from .models" работали
ENV PYTHONPATH=/app

# Запуск модуля
CMD ["python", "-m", "app.main"]