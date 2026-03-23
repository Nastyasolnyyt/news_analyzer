FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Сначала обновляем pip и инструменты
RUN pip install --no-cache-dir --upgrade pip setuptools

# Увеличиваем таймаут и пробуем установить зависимости
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

# Устанавливаем переменную, чтобы избежать некоторых ошибок соеднения
ENV HF_HUB_OFFLINE=0

# Пробуем предзагрузку еще раз с принудительным обновлением кэша
RUN python -c "from transformers import pipeline; pipeline('sentiment-analysis', model='cointegrated/rubert-tiny-sentiment', trust_remote_code=True)"

COPY . ./sentiment_analysis/

CMD ["python", "-m", "sentiment_analysis.main"]
