from fastapi import FastAPI, HTTPException
from .parsers import parse_telegram_channels  
from .kafka_producer import send_article_to_kafka
from .models import Article
from typing import List

app = FastAPI(title="Telegram Parser Service")

@app.post("/parse_telegram", response_model=List[Article])
async def parse_telegram():
    articles = await parse_telegram_channels()
    for article in articles:
        # Явно сериализуем в JSON-compatible dict
        article_dict = article.model_dump()
        # Преобразуем datetime вручную
        if article_dict.get('pub_date') and hasattr(article_dict['pub_date'], 'isoformat'):
            article_dict['pub_date'] = article_dict['pub_date'].isoformat()
        
        await send_article_to_kafka(article_dict)
    return articles

@app.get("/")
async def root():
    return {"message": "Telegram Parser Service is running"}