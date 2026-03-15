FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем скрипт И файл со стоп-словами
COPY text_preprocessing_service_kafka.py .
COPY stopwords-ru.json . 

CMD ["python", "text_preprocessing_service_kafka.py"]