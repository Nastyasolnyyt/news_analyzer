FROM news_analyzer-ml-base:latest

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

# Скачать данные для nltk (нужно для токенизации)
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')" || true

COPY . .

CMD ["python", "event_clustering.py"]