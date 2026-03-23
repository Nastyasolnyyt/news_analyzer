# aggregator-parser/app/main.py
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import text as sql_text
from fastapi import FastAPI, HTTPException
from typing import List


from .database import SessionLocal, ArticleORM # Убедись, что пути верные
from .models import Article                   # Убедись, что путь верный
from .parsers import parse_rss                  # Убедись, что путь верный
from .kafka_producer import send_article_to_kafka

app = FastAPI()

@app.post("/parse", response_model=List[Article])
async def parse_aggregator(urls: List[str]):
    all_articles = []
    db = SessionLocal()
    try:
        for url in urls:
            articles = parse_rss(url.strip())
            for art_data in articles:
                # 1. Готовим UPSERT
                stmt = insert(ArticleORM).values(
                    title=art_data.title,
                    content=art_data.text, # Синхронизируем: пишем в content
                    link=art_data.link,
                    source=art_data.source,
                    pub_date=art_data.pub_date
                )
                
                # Если ссылка уже есть, ничего не меняем, но просим вернуть id
                stmt = stmt.on_conflict_do_nothing(index_elements=['link'])
                db.execute(stmt)
                db.commit()

                # 2. Достаем актуальный ID из базы
                existing = db.query(ArticleORM).filter(ArticleORM.link == art_data.link).first()
                
                if existing:
                    # Обновляем объект Pydantic актуальным ID из БД
                    art_data.id = existing.id
                    
                    # 3. ОТПРАВКА В KAFKA (теперь внутри всегда есть правильный ID)
                    await send_article_to_kafka(art_data)
                    all_articles.append(art_data)
        
        return all_articles
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
