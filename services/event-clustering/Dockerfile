FROM news_analyzer-ml-base:latest

# Доп. системные зависимости для pymystem3
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmystem-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

# Скачать данные для nltk и mystem
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')" || true

COPY . .

CMD ["python", "event_clustering.py"]