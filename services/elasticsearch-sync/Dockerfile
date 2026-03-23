# services/elasticsearch-sync/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Копируем всё содержимое папки elasticsearch-sync/ в /app
COPY . .

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Запускаем main.py из корня /app
CMD ["python", "app/main.py"]