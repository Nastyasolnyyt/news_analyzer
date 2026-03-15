from fastapi import FastAPI
from .models import Article, RiskResult
from pydantic_settings import BaseSettings
from .classifier import MistralNeuralClassifier
import os

# 1. Сначала определяем настройки
class Settings(BaseSettings):
    openrouter_api_key: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# 2. Создаем экземпляр настроек
settings = Settings()

# 3. Создаем приложение FastAPI
app = FastAPI(title="Risk Classifier Service")

# 4. Инициализируем классификатор (используем правильное имя класса)
classifier = MistralNeuralClassifier(api_key=settings.openrouter_api_key)

@app.post("/classify", response_model=RiskResult)
async def classify_risk(article: Article):
    # Используем article.text или article.title как запасной вариант
    # Убедись, что в models.py ты добавила поле text!
    text_to_classify = getattr(article, 'text', None) or article.title
    result = classifier.classify(text_to_classify)
    return result

@app.get("/")
async def root():
    return {"message": "Risk Classifier Service is running"}