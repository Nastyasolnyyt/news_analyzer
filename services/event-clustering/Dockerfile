FROM news_analyzer-ml-base:latest

# Системные зависимости для pymystem3 и nltk
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

# Скачать данные для nltk
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')" || true

# Скачать и установить Mystem вручную (если pymystem3 не скачает сам)
RUN curl -fsSL https://yandex.ru/dev/mystem/mystem-3.1-linux-64bit.tar.gz -o /tmp/mystem.tar.gz && \
    tar -xzf /tmp/mystem.tar.gz -C /tmp && \
    mv /tmp/mystem-3.1-linux-64bit/mystem /usr/local/bin/mystem && \
    chmod +x /usr/local/bin/mystem && \
    rm -rf /tmp/mystem.tar.gz /tmp/mystem-3.1-linux-64bit

COPY . .

CMD ["python", "event_clustering.py"]