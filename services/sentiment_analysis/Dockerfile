FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Увеличиваем таймаут до 1000 секунд
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

# Предзагрузка легкой модели (она скачается быстро)
RUN python -c "from transformers import pipeline; pipeline('sentiment-analysis', model='cointegrated/rubert-tiny-sentiment')"

COPY . ./sentiment_analysis/

CMD ["python", "-m", "sentiment_analysis.main"]