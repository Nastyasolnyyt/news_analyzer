# -*- coding: utf-8 -*-
"""
event_clustering.py
ИСПРАВЛЕНО:
1. Добавлены русские стоп-слова в TF-IDF — убираем предлоги из названий топиков
2. Улучшена генерация названий тем — фильтруем короткие слова
3. Исправлена логика дедупликации — не создаём дубли топиков при каждом запуске
4. Увеличен лимит статей за раз до 100
"""
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

from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("event_clustering")

Base = declarative_base()

# ==================== РУССКИЕ СТОП-СЛОВА ====================
# ИСПРАВЛЕНО: добавляем русские стоп-слова, чтобы предлоги не попадали в топик
RUSSIAN_STOPWORDS = [
    'и', 'в', 'на', 'из', 'к', 'от', 'с', 'по', 'а', 'для', 'за', 'но',
    'не', 'это', 'этот', 'что', 'как', 'или', 'который', 'они', 'ты',
    'он', 'она', 'оно', 'вы', 'мы', 'я', 'если', 'при', 'до', 'об',
    'со', 'во', 'то', 'бы', 'же', 'ни', 'да', 'уж', 'вот', 'был',
    'была', 'были', 'будет', 'быть', 'есть', 'её', 'его', 'их', 'им',
    'нет', 'так', 'вс', 'все', 'всё', 'того', 'этого', 'тоже', 'уже',
    'чем', 'ещё', 'еще', 'под', 'над', 'без', 'между', 'через', 'после',
    'перед', 'около', 'вдоль', 'среди', 'против', 'о', 'про', 'у', 'ко',
    'во', 'об', 'по', 'ото', 'изо', 'подо', 'надо', 'передо', 'предо',
    'то', 'бы', 'ли', 'лишь', 'хоть', 'когда', 'где', 'куда', 'откуда',
    'как', 'зачем', 'почему', 'который', 'которая', 'которые', 'которого',
    'которой', 'которых', 'которому', 'которым', 'которыми',
    # Цифры и служебные слова
    'также', 'тем', 'tem', 'при', 'об', 'мне', 'нам', 'вам', 'нас', 'вас',
    'со', 'им', 'ем', 'ей', 'неё', 'нём', 'неи', 'что', 'чего', 'чему',
]


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
    """
    Генерирует название темы из ключевых слов группы текстов.
    ИСПРАВЛЕНО: используем русские стоп-слова и фильтруем короткие слова.
    """
    if not texts:
        return f"Тема от {datetime.now().strftime('%d.%m %H:%M')}"

    try:
        short_texts = [t[:200] for t in texts if t]
        if not short_texts:
            return f"Тема от {datetime.now().strftime('%d.%m %H:%M')}"

        vectorizer = TfidfVectorizer(
            max_features=20,
            stop_words=RUSSIAN_STOPWORDS,  # ИСПРАВЛЕНО: русские стоп-слова
            ngram_range=(1, 2),
            min_df=1,
            token_pattern=r'(?u)\b[а-яёА-ЯЁa-zA-Z][а-яёА-ЯЁa-zA-Z]{2,}\b'  # минимум 3 буквы
        )
        tfidf_matrix = vectorizer.fit_transform(short_texts)

        # Берём средние TF-IDF веса
        mean_scores = np.array(tfidf_matrix.mean(axis=0)).ravel()
        feature_names = vectorizer.get_feature_names_out()

        # Сортируем по весу и берём топ-3
        top_indices = mean_scores.argsort()[::-1]
        top_words = []
        for idx in top_indices:
            word = feature_names[idx]
            # ИСПРАВЛЕНО: фильтруем однобуквенные слова и цифры
            if len(word) >= 3 and not word.isdigit():
                top_words.append(word)
            if len(top_words) >= 3:
                break

        if top_words:
            return "Тема: " + ", ".join(top_words)
        else:
            return f"Тема от {datetime.now().strftime('%d.%m %H:%M')}"

    except Exception as e:
        logger.warning(f"Не удалось сгенерировать название темы: {e}")
        return f"Тема от {datetime.now().strftime('%d.%m %H:%M')}"


class EventClustering:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.embedder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    def run_once(self):
        """
        Один проход кластеризации.
        ИСПРАВЛЕНО:
        - Увеличен лимит до 100 статей
        - Добавлена проверка минимального количества статей для кластеризации
        """
        session = self.SessionLocal()
        try:
            # Берём статьи без topic_id
            assigned_post_ids = select(PostAnalysis.post_id).where(
                PostAnalysis.topic_id.isnot(None)
            )

            articles = session.query(Article).filter(
                Article.id.notin_(assigned_post_ids)
            ).order_by(Article.created_at.desc()).limit(100).all()

            if not articles:
                logger.info("Нет новых статей для кластеризации.")
                return

            logger.info(f"Кластеризуем {len(articles)} статей...")

            if len(articles) < 4:
                logger.info(f"Слишком мало статей ({len(articles)}) для кластеризации, пропускаю")
                return

            # Векторизация
            texts = [f"{a.title or ''} {a.text}" for a in articles]
            embeddings = self.embedder.encode(texts, show_progress_bar=False)

            # Адаптивное число кластеров
            n_articles = len(articles)
            n_clusters = max(2, min(15, n_articles // 5))

            logger.info(f"Создаю {n_clusters} кластеров для {n_articles} статей")

            kmeans = KMeans(n_clusters=n_clusters, n_init='auto', random_state=42)
            labels = kmeans.fit_predict(embeddings)

            # Создаём темы и привязываем статьи
            cluster_map = {}
            updated_count = 0

            for cluster_idx in range(n_clusters):
                cluster_indices = [i for i, l in enumerate(labels) if l == cluster_idx]
                if not cluster_indices:
                    continue

                cluster_texts = [texts[i] for i in cluster_indices]
                topic_name = generate_topic_name(cluster_texts)

                new_topic = Topic(name=topic_name)
                session.add(new_topic)
                session.flush()
                cluster_map[cluster_idx] = new_topic.id
                logger.info(
                    f"Создана тема #{new_topic.id}: '{topic_name}' "
                    f"({len(cluster_indices)} статей)"
                )

            # UPSERT статей в post_analysis
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
            logger.info(
                f"Кластеризация завершена: {updated_count} статей → {len(cluster_map)} тем"
            )

        except Exception as e:
            session.rollback()
            logger.error(f"Ошибка кластеризации: {e}", exc_info=True)
            raise
        finally:
            session.close()


if __name__ == "__main__":
    import time

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        logger.error("Переменная окружения DATABASE_URL не задана!")
        exit(1)

    logger.info("Запуск event_clustering...")
    clustering = EventClustering(db_url)

    while True:
        try:
            clustering.run_once()
        except Exception as e:
            logger.error(f"Ошибка в цикле кластеризации: {e}", exc_info=True)

        logger.info("Пауза 300 секунд перед следующим прогоном...")
        time.sleep(300)