import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
import logging
from typing import List, Optional

from config import POSTGRES_DB_URL, LAST_SYNC_FILE
from models import Article, PostEntity
from elasticsearch_client import ElasticSearchClient, ARTICLES_MAPPING

logger = logging.getLogger(__name__)

class SyncService:
    def __init__(self, index_name: str ):
        try:
            self.engine = create_engine(POSTGRES_DB_URL, echo=True)
            self.client = ElasticSearchClient()

            try:
                with self.engine.connect() as conn:
                    logger.info("Successfully connected to PostgreSQL")
            except Exception as e:
                logger.error(f"Failed to connect to PostgreSQL: {e}")
                raise

            if not self.client.index_exists(index_name):
                self.client.create(index_name, ARTICLES_MAPPING)  # create -> create_index
            else:
                logger.info(f"Index {index_name} already exists") 
        except Exception as e:
            logger.error(f'Error initializing SyncService: {e}')
            raise
        

    def _get_last_sync_time(self) -> datetime:
        try:
            if not os.path.exists(LAST_SYNC_FILE):
                logger.info("Last sync file not found. First run - will index all articles")
                return datetime.min
            
            with open(LAST_SYNC_FILE, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                if not content: 
                    logger.info("Empty sync file - will index all articles")
                    return datetime.min
                
            try:
                last_sync = datetime.fromisoformat(content)
                logger.info(f"Last sync time: {last_sync}")
                return last_sync
            except ValueError:
                logger.error(f"Invalid date format in sync file: {content}")
                return datetime.min
            
        except Exception as e:
            logger.error(f'Error reading last sync time: {e}')
            return datetime.min


    def _save_last_sync_time(self, sync_time: datetime):
        try:
            with open(LAST_SYNC_FILE, 'w', encoding='utf-8') as file:
                file.write(sync_time.isoformat())
                logger.debug(f"Saved last sync time: {sync_time}")
        except Exception as e:
            logger.error(f'File with last sync Not Found: {e}') 


    def get_changed_articles(self, last_sync: datetime) -> List[Article]:
        try:
            with Session(self.engine) as session:
                data = session.query(Article).options(
                    joinedload(Article.risks),
                    joinedload(Article.entities).joinedload(PostEntity.entity) # <-- Изменили эту строку
                ).filter(
                    Article.updated_at >= last_sync
                ).all()
                logger.info(f"Found {len(data)} changed articles")
                return data
        except Exception as e:
            logger.error(f"Error getting changed articles: {e}")
            return []


    # sync.py

    def article_to_doc(self, article):
        # Собираем данные из связанных таблиц (SQLAlchemy relationship)
        # Убедись, что в моделях прописаны отношения!
        
        doc = {
            "id": article.id,
            "title": article.title,
            "text": article.text,
            "source": article.source,
            "link": article.link,
            "pub_date": article.pub_date.isoformat() if article.pub_date else None,
            "updated_at": article.updated_at.isoformat(),
            
            # Подтягиваем аналитику (если она уже готова)
            "risk_level": article.risks[0].risk_type if article.risks else "unknown",
            "risk_confidence": article.risks[0].confidence if article.risks else None,
        }
        
        # Если есть сущности (NER)
        # Если есть сущности (NER)
        if hasattr(article, 'entities') and article.entities:
            doc["entities"] = [
                {"text": e.entity.name, "type": e.entity.type} 
                for e in article.entities if e.entity is not None
            ]
            
        return doc
    
    def sync_articles(self):
        logger.info("Starting articles sync")
        last_sync = self._get_last_sync_time()
        articles = self.get_changed_articles(last_sync)
        
        if not articles:
            logger.info("No new articles to sync")
            return
        
        current_sync = datetime.now()
        
        success_count = 0
        for article in articles:
            try:
                doc = self.article_to_doc(article)
                if self.client.index_doc("articles", doc, article.id):
                    success_count += 1
                else:
                    logger.error(f"Failed to index article {article.id}")
                    
            except Exception as e:
                logger.error(f"Error processing article {article.id}: {e}")
        
        if success_count > 0:
            self._save_last_sync_time(current_sync)
        
        logger.info(f"Sync completed: {success_count}/{len(articles)} articles indexed")