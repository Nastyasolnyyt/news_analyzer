FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

CMD ["python", "-c", "from app.kafka_consumer import consume_from_kafka; consume_from_kafka()"]