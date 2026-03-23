FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

# Запускаем Kafka consumer для обработки risk_types_done топика
CMD ["python", "-m", "app.main"]