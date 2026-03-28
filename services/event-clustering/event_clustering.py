# -*- coding: utf-8 -*-
import os
import logging
from typing import List
from datetime import datetime

from sqlalchemy import (
    create_engine, Column, Integer, String, Text, DateTime, 
    ForeignKey, Float, func, select
)
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import insert

# ML и анализ
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("event_clustering")

Base = declarative_base()


class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=True)
    text = Column(Text, nullable=False)
    source = Column(Text, nullable=False)
    link = Column(Text, nullable=True)
    pub_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Topic(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class PostAnalysis(Base):
    __tablename__ = "post_analysis"
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), 
                     nullable=False, unique=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="SET NULL"), 
                      nullable=True)
    emotion = Column(Float, nullable=False, default=0.0)
    tonality = Column(Float, nullable=False, default=0.0)
    relevance = Column(Float, nullable=False, default=0.0)



def generate_topic_name(texts: List[str]) -> str:
    """Генерирует название темы из ключевых слов группы текстов."""
    if not texts:
        return f"Событие от {datetime.now().strftime('%d.%m %H:%M')}"
    
    try:
        # Берём первые 100 символов каждого текста для скорости
        short_texts = [t[:100] for t in texts if t]
        if not short_texts:
            return f"Событие от {datetime.now().strftime('%d.%m %H:%M')}"
            
        vectorizer = TfidfVectorizer(
            max_features=5, 
            stop_words='english',  # можно заменить на русский список
            ngram_range=(1, 2)
        )
        tfidf_matrix = vectorizer.fit_transform(short_texts)
        words = vectorizer.get_feature_names_out()
        return "Событие: " + ", ".join(words[:3])
    except Exception as e:
        logger.warning(f"Не удалось сгенерировать название темы: {e}")
        return f"Событие от {datetime.now().strftime('%d.%m %H:%M')}"


# --- ОСНОВНОЙ КЛАСС ---

class EventClustering:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.embedder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    def run_once(self):
        """Один проход кластеризации: берёт статьи без topic_id, группирует, сохраняет."""
        session = self.SessionLocal()
        try:
            # 1. Берём статьи, у которых ещё нет topic_id в post_analysis
            #    Сначала находим post_id, которые УЖЕ имеют topic_id
            assigned_post_ids = select(PostAnalysis.post_id).where(
                PostAnalysis.topic_id.isnot(None)
            )

            articles = session.query(Article).filter(
                Article.id.notin_(assigned_post_ids)
            ).limit(50).all()
            
            if not articles:
                logger.info("Новых статей для кластеризации нет.")
                return

            logger.info(f"Кластеризуем {len(articles)} статей...")

            # 2. Векторизация текстов
            texts = [f"{a.title or ''} {a.text}" for a in articles]
            embeddings = self.embedder.encode(texts, show_progress_bar=False)
            
            # 3. Кластеризация KMeans
            n_articles = len(articles)
            if n_articles < 2:
                logger.info("Меньше 2 статей для кластеризации, пропускаю")
                return
            n_clusters = max(2, min(10, n_articles // 4))   # адаптивное число кластеров
                        
            kmeans = KMeans(n_clusters=n_clusters, n_init='auto', random_state=42)
            labels = kmeans.fit_predict(embeddings)

            # 4. Создаём темы для каждого кластера
            cluster_map = {}  # label -> topic_id
            for cluster_idx in range(n_clusters):
                cluster_indices = [i for i, l in enumerate(labels) if l == cluster_idx]
                if not cluster_indices:
                    continue
                    
                cluster_texts = [texts[i] for i in cluster_indices]
                topic_name = generate_topic_name(cluster_texts)
                
                new_topic = Topic(name=topic_name)
                session.add(new_topic)
                session.flush()  # чтобы получить id
                cluster_map[cluster_idx] = new_topic.id
                logger.info(f"Создана тема #{new_topic.id}: {topic_name}")

            # 5. Привязываем статьи к темам через UPSERT
            updated_count = 0
            for i, article in enumerate(articles):
                label = labels[i]
                topic_id = cluster_map.get(label)
                if topic_id is None:
                    continue
                    
                stmt = insert(PostAnalysis).values(
                    post_id=article.id,
                    topic_id=topic_id,
                    emotion=0.0,
                    tonality=0.0,
                    relevance=0.0
                ).on_conflict_do_update(
                    index_elements=['post_id'],
                    set_={'topic_id': topic_id}
                )
                session.execute(stmt)
                updated_count += 1
            
            session.commit()
            logger.info(f"Кластеризация завершена: {updated_count} статей привязано к {len(cluster_map)} темам")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Ошибка кластеризации: {e}", exc_info=True)
            raise
        finally:
            session.close()


# --- ТОЧКА ВХОДА ---
if __name__ == "__main__":
    import time
    
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        logger.error("Переменная окружения DATABASE_URL не задана!")
        exit(1)
    
    logger.info("Запуск event_clustering (режим цикла)...")
    clustering = EventClustering(db_url)
    
    # Бесконечный цикл: проверяем новые статьи каждые 5 минут
    while True:
        try:
            clustering.run_once()
        except Exception as e:
            logger.error(f"Ошибка в цикле кластеризации: {e}", exc_info=True)
        
        logger.info("Пауза 300 секунд перед следующим прогоном...")
        time.sleep(300)  # 5 минут между запусками