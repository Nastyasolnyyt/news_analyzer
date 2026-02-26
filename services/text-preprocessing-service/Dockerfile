# text-preprocessing-service/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY text_preprocessing_service_kafka.py .

CMD ["python", "text_preprocessing_service_kafka.py"]