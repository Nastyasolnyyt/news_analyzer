from fastapi import FastAPI, HTTPException
from .parsers import parse_telegram_channels  
from .kafka_producer import send_article_to_kafka
from .models import Article
from typing import List

app = FastAPI(title="Telegram Parser Service")

@app.post("/parse_telegram", response_model=List[Article])
async def parse_telegram():
    try:
        articles = await parse_telegram_channels()  
        for article in articles:
            await send_article_to_kafka(article.model_dump())
        return articles
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Telegram Parser Service is running"}