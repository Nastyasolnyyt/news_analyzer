# app/main.py

from fastapi import FastAPI, HTTPException
from .parsers import parse_rss
from .kafka_producer import send_article_to_kafka 
from .models import Article
from typing import List

app = FastAPI(title="Aggregator Parser Service")

@app.post("/parse", response_model=List[Article])
async def parse_aggregator(urls: List[str]):
    all_articles = []
    for url in urls:
        try:
            clean_url = url.strip()
            articles = parse_rss(clean_url)
            for article in articles:
                
                await send_article_to_kafka(article)
            all_articles.extend(articles)
        except Exception as e:
           
            raise HTTPException(status_code=500, detail=f"Error parsing {url}: {str(e)}")
    return all_articles

