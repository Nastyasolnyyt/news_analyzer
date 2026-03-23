# telegram-parser/app/main.py
from .models import Article
from sqlalchemy.dialects.postgresql import insert
from .database import SessionLocal, ArticleORM # Создай файл database.py или импортируй ORM
from fastapi import FastAPI
from typing import List
from .models import Article

app = FastAPI()
@app.post("/parse_telegram", response_model=List[Article])
async def parse_telegram():
    articles = await parse_telegram_channels()
    db = SessionLocal()
    processed_articles = []

    try:
        for article in articles:
            # 1. Сохраняем в БД (или получаем существующий ID по ссылке)
            stmt = insert(ArticleORM).values(
                title=article.title or "Telegram Post",
                content=article.text,
                link=article.link,
                source=article.source,
                pub_date=article.pub_date
            ).on_conflict_do_nothing(index_elements=['link'])
            
            db.execute(stmt)
            db.commit()

            # 2. Достаем ID
            existing = db.query(ArticleORM).filter(ArticleORM.link == article.link).first()
            
            if existing:
                # 3. Формируем словарь для Kafka с реальным article_id
                article_dict = {
                    "article_id": existing.id, # ВАЖНО: называем именно так
                    "title": existing.title,
                    "text": existing.content,
                    "link": existing.link,
                    "source": existing.source
                }
                await send_article_to_kafka(article_dict)
                processed_articles.append(article)
        
        return processed_articles
    finally:
        db.close()
