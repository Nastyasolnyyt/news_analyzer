from fastapi import FastAPI
from .models import Article, RiskResult # Article возьми из своих старых моделей
from .classifier import MistralNeuralClassifier
from .config import settings # Убедись, что в config.py есть api_key

app = FastAPI(title="Risk Category Classifier")

# Инициализируем твой класс
classifier = MistralNeuralClassifier(api_key=settings.openrouter_api_key)

@app.post("/classify", response_model=RiskResult)
async def classify_news(article: dict):
    # Берем текст или заголовок для анализа
    text_to_analyze = article.get('text') or article.get('title', "")
    result = classifier.classify(text_to_analyze)
    return result