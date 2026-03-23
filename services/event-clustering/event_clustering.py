# -*- coding: utf-8 -*-
import os
import logging
from typing import List, Dict
from datetime import datetime

from sqlalchemy import (
    create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Float, func
)
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import insert

# ML и Анализ
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("event_clustering")

Base = declarative_base()

# --- СИНХРОНИЗИРОВАННЫЕ МОДЕЛИ (ОТВЕЧАЮТ OUTPUT_MODEL) ---

class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True)
    author = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False) 
    source = Column(Text, nullable=False)
    link = Column(Text, unique=True, nullable=False)

class Topic(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False) # Сюда запишем ключевые слова
    created_at = Column(DateTime, server_default=func.now())

class PostAnalysis(Base):
    __tablename__ = "articles_analysis"
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, unique=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="SET NULL"), nullable=True)
    emotion = Column(Float, nullable=False, default=0.0)
    tonality = Column(Float, nullable=False, default=0.0)
    relevance = Column(Float, nullable=False, default=0.0)

# --- ЛОГИКА ГЕНЕРАЦИИ НАЗВАНИЙ ---

def generate_topic_name(texts: List[str]) -> str:
    """Извлекает 3 главных слова из группы текстов для названия темы."""
    if not texts:
        return "Неизвестное событие"
    
    vectorizer = TfidfVectorizer(max_features=5, stop_words=None) # Можно добавить стоп-слова
    try:
        tfidf_matrix = vectorizer.fit_transform(texts)
        words = vectorizer.get_feature_names_out()
        return "Событие: " + ", ".join(words[:3])
    except:
        return f"Событие от {datetime.now().strftime('%d.%m %H:%M')}"

# --- ОСНОВНОЙ КЛАСС ---

class EventClustering:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        self.embedder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    def run_once(self):
        session = self.Session()
        try:
            # 1. Берем статьи без темы
            subquery = session.query(PostAnalysis.post_id).filter(PostAnalysis.topic_id.isnot(None))
            articles = session.query(Article).filter(Article.id.not_in(subquery)).limit(50).all()
            
            if not articles:
                logger.info("Новых статей для кластеризации нет.")
                return

            # 2. Векторизация
            texts = [f"{a.title} {a.content}" for a in articles]
            embeddings = self.embedder.encode(texts)
            
            # 3. Кластеризация
            n_clusters = max(2, len(articles) // 4)
            kmeans = KMeans(n_clusters=n_clusters, n_init='auto', random_state=42)
            labels = kmeans.fit_predict(embeddings)

            # 4. Сохранение
            cluster_map = {} # label -> topic_id
            for cluster_idx in range(n_clusters):
                cluster_texts = [texts[i] for i, l in enumerate(labels) if l == cluster_idx]
                if not cluster_texts: continue
                
                # Создаем красивое имя темы
                topic_name = generate_topic_name(cluster_texts)
                new_topic = Topic(name=topic_name)
                session.add(new_topic)
                session.flush()
                cluster_map[cluster_idx] = new_topic.id

            # 5. Привязка статей к темам через UPSERT
            for i, article in enumerate(articles):
                label = labels[i]
                topic_id = cluster_map.get(label)
                
                stmt = insert(PostAnalysis).values(
                    post_id=article.id,
                    topic_id=topic_id,
                    emotion=0.0, tonality=0.0, relevance=0.0
                ).on_conflict_do_update(
                    index_elements=['post_id'],
                    set_={'topic_id': topic_id}
                )
                session.execute(stmt)
            
            session.commit()
            logger.info(f"Кластеризация завершена. Создано {n_clusters} тем.")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Ошибка в работе сервиса: {e}")
        finally:
            session.close()

if __name__ == "__main__":
    url = os.getenv("DATABASE_URL")
    if url:
        EventClustering(url).run_once()
    else:
        logger.error("Переменная DATABASE_URL не найдена!")