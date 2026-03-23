FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .


RUN pip install --no-cache-dir --upgrade pip setuptools


RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

ENV HF_HUB_OFFLINE=0

COPY . ./sentiment_analysis/

CMD ["python", "-m", "sentiment_analysis.main"]
