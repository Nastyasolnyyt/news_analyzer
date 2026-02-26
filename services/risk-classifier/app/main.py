from fastapi import FastAPI
from .classifier import HFRiskClassifier
from .models import Article, RiskResult
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
     openrouter_api_key: str

class Config:
        env_file = ".env"

settings = Settings()
app = FastAPI(title="Risk Classifier Service")
classifier = HFRiskClassifier( openrouter_api_key=settings.openrouter_api_key)

@app.post("/classify", response_model=RiskResult)
async def classify_risk(article: Article):
    result = classifier.classify(article.text)
    return result

@app.get("/")
async def root():
    return {"message": "Risk Classifier Service is running"}