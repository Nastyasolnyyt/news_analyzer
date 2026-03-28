# services/risk-classifier/Dockerfile
FROM news_analyzer-ml-base:latest

# Системные зависимости (если нужны дополнительные)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем только специфичные зависимости (без torch/transformers!)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

# Копируем код
COPY . .

# Запускаем
CMD ["python", "-m", "app.main"]