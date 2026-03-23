FROM python:3.10-slim

RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем всё из текущей папки (news_analyzer) в /app контейнера
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Указываем путь к main.py внутри папки app
CMD ["python", "app/main.py"]