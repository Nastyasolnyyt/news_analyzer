from fastapi import FastAPI
from .parsers import parse_habr_news
from .models import Article as ArticleModel

app = FastAPI(title="News Site Parser Service")

@app.get("/parse-habr")
async def parse_habr(start_page: int = 1, end_page: int = 2):
    articles = parse_habr_news(start_page=start_page, end_page=end_page)
    return {"articles": [article.model_dump() for article in articles]}

@app.get("/")
async def root():
    return {"message": "News Site Parser Service is running"}