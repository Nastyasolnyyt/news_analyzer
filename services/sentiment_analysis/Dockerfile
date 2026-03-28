FROM news_analyzer-ml-base:latest

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

COPY . .

CMD ["python", "-m", "sentiment_analysis.main"]