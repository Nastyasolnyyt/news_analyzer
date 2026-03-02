# -*- coding: utf-8 -*-
import os
import argparse
import logging
from typing import List, Optional, Tuple, Dict
from datetime import datetime, timezone

from sqlalchemy import (
    create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON, Boolean
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_

# Embeddings & clustering
from sentence_transformers import SentenceTransformer
import numpy as np

# Optional algorithms
try:
    import hdbscan
    HAS_HDBSCAN = True
except Exception:
    HAS_HDBSCAN = False
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.feature_extraction.text import TfidfVectorizer

import warnings
warnings.filterwarnings("ignore")


# Optional: for queue (Redis)
try:
    import redis
    HAS_REDIS = True
except Exception:
    HAS_REDIS = False

# %%
# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("event_clustering")

Base = declarative_base()


# %%
# --- SQLAlchemy models (DB-agnostic) ---
class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True)
    external_id = Column(String(255), unique=True, index=True, nullable=True)  # optional id from upstream
    title = Column(String(2000), nullable=True)
    text = Column(Text, nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    processed = Column(Boolean, default=False)  # whether preprocessed
    clustered_at = Column(DateTime(timezone=True), nullable=True)
    cluster_id = Column(Integer, ForeignKey("clusters.id"), nullable=True)
    meta = Column(JSON, nullable=True)

    cluster = relationship("Cluster", back_populates="articles")


# %%
class Entity(Base):
    __tablename__ = "entities"
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey("articles.id"), index=True, nullable=False)
    text = Column(String(500), nullable=False)
    label = Column(String(50), nullable=True)  # PER/ORG/LOC
    external_refs = Column(JSON, nullable=True)



# %%
class Cluster(Base):
    __tablename__ = "clusters"
    id = Column(Integer, primary_key=True)
    name = Column(String(1000), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    algorithm = Column(String(100), nullable=True)
    params = Column(JSON, nullable=True)
    vector_center = Column(JSON, nullable=True)  # centroid/rep vector
    size = Column(Integer, default=0)
    top_terms = Column(JSON, nullable=True)

    articles = relationship("Article", back_populates="cluster")


# %%
# --- DB utility ---
def get_engine(database_url: Optional[str] = None):
    if database_url is None:
        database_url = os.getenv("DATABASE_URL", "sqlite:///./event_clustering.db")
    engine = create_engine(database_url, echo=False, future=True)
    return engine

def create_tables(engine):
    Base.metadata.create_all(engine)


# %%
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0  # стабильность детекции

import re
from nltk.corpus import stopwords as nltk_stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer

from pymystem3 import Mystem

def lemmatize_ru(text: str) -> str:
    return "".join(mystem.lemmatize(text)).replace("\n", " ").strip()

_word_re = re.compile(r"[A-Za-zА-Яа-яёЁ]+", flags=re.U)

# %%
# --- Clustering component ---
class EventClustering:
    def __init__(
        self,
        db_url: Optional[str] = None,
        embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2",
        min_cluster_size: int = 5,
        use_hdbscan: bool = True,
        umap_n_components: int = 5,
        redis_url: Optional[str] = None,
    ):
        # DB / session
        self.engine = get_engine(db_url)
        self.Session = sessionmaker(bind=self.engine, autoflush=False, expire_on_commit=False)

        # Embeddings model (multilingual by default)
        self.embedding_model_name = embedding_model
        self.embedder = SentenceTransformer(embedding_model)

        # clustering params
        self.min_cluster_size = min_cluster_size
        self.use_hdbscan = use_hdbscan and HAS_HDBSCAN
        if use_hdbscan and not HAS_HDBSCAN:
            logger.warning("hdbscan not installed -> fallback to KMeans will be used")
            self.use_hdbscan = False
        self.umap_n_components = umap_n_components

        # optional redis
        self.redis = None
        if redis_url and HAS_REDIS:
            self.redis = redis.from_url(redis_url)

        # --- language tools ---
        # russian lemmatizer
        self.mystem = Mystem()

        # english lemmatizer
        try:
            self.en_lemmatizer = WordNetLemmatizer()
        except Exception:
            self.en_lemmatizer = None

        # stop-words
        try:
            self.stop_en = set(nltk_stopwords.words("english"))
        except Exception:
            self.stop_en = set()
        try:
            self.stop_ru = set(nltk_stopwords.words("russian"))
        except Exception:
            self.stop_ru = set()

    # ---- функция детекции языка ----
    def detect_language(self, text: str) -> str:
        """Возвращает 'ru' или 'en' (fallback 'en')."""
        try:
            lang = detect(text)
            if lang.startswith("ru"):
                return "ru"
            if lang.startswith("en"):
                return "en"
            # fallback: если неизвестно — решить по наличию кириллицы
            if re.search("[а-яА-Я]", text):
                return "ru"
        except Exception:
            pass
        return "en"
    
    def preprocess_for_tfidf(self, text: str, lang: str) -> str:
        """
        Возвращает строку токенов (лемматизированных), готовую для TfidfVectorizer.
        Для RU — pymystem3, для EN — WordNetLemmatizer.
        Убираем короткие токены и стоп-слова.
        """
        text = text.lower()
        tokens = _word_re.findall(text)
        out_tokens = []
        if lang == "ru":
            for t in tokens:
                if len(t) <= 2:
                    continue
                if t in self.stop_ru:
                    continue
                lemma = "".join(self.mystem.lemmatize(t)).strip()
                if lemma and len(lemma) > 1:
                    out_tokens.append(lemma)
        else:  # english
            for t in tokens:
                if len(t) <= 2:
                    continue
                if t in self.stop_en:
                    continue
                lemma = self.en_lemmatizer.lemmatize(t)
                if lemma and len(lemma) > 1:
                    out_tokens.append(lemma)
        return " ".join(out_tokens)

    def fetch_unclustered_articles(self, limit: int = 500) -> List[Article]:
        session = self.Session()
        try:
            q = (
                session.query(Article)
                .filter(Article.text.isnot(None))
                .filter(or_(Article.cluster_id.is_(None), Article.clustered_at.is_(None)))
                .order_by(Article.published_at.desc().nullslast())
                .limit(limit)
            )
            res = q.all()
            logger.info("Fetched %d unclustered articles", len(res))
            return res
        finally:
            session.close()

    def embed_texts(self, texts: List[str], batch_size: int = 64) -> np.ndarray:
        # embed title + text for better signal
        embeddings = self.embedder.encode(texts, show_progress_bar=False, batch_size=batch_size, convert_to_numpy=True)
        # normalize
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0.0] = 1.0
        embeddings = embeddings / norms
        return embeddings
    
    def extract_top_terms(self, texts: List[str], indices: List[int], top_n: int = 10) -> List[str]:
        """
        Делает TF-IDF на лемматизированных текстах (RU/EN).
        Возвращает top_n терминов для набора документов indices.
        """
        if len(indices) == 0:
            return []
        corpus_prepared = []
        for i in indices:
            txt = texts[i]
            lang = self.detect_language(txt)
            prep = self.preprocess_for_tfidf(txt, lang)
            corpus_prepared.append(prep if prep.strip() else txt.lower())
    
        # Используем стандартный векторизатор — наши тексты уже токенизированы/лемматизированы
        vect = TfidfVectorizer(max_features=2000, token_pattern=r"(?u)\b\w+\b")
        X = vect.fit_transform(corpus_prepared)
        # усредняем TF-IDF по документам, берём top_n
        import numpy as np
        scores = np.array(X.mean(axis=0)).ravel()
        if scores.size == 0:
            return []
        top_idx = np.argsort(scores)[-top_n:][::-1]
        terms = [vect.get_feature_names_out()[i] for i in top_idx]
        return terms

    def cluster_embeddings(self, embeddings: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """
        Return labels array and metadata
        """
        meta = {}
        if self.use_hdbscan and embeddings.shape[0] >= self.min_cluster_size:
            # HDBSCAN expects float32
            clusterer = hdbscan.HDBSCAN(min_cluster_size=self.min_cluster_size, metric='euclidean', prediction_data=True)
            labels = clusterer.fit_predict(embeddings)
            meta["algorithm"] = "hdbscan"
            # convert -1 to noise label
            return labels, meta
        else:
            # fallback KMeans: choose k by heuristic: sqrt(n/2) or min_cluster_size
            n = embeddings.shape[0]
            k = max(2, int(max(2, min(n // self.min_cluster_size, int(np.sqrt(n/2)+1)))))
            k = min(k, n)  # cannot exceed n
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(embeddings)
            meta["algorithm"] = "kmeans"
            meta["k"] = k
            return labels, meta

    def persist_clusters(
        self,
        articles: List[Article],
        texts: List[str],
        labels: np.ndarray,
        algo_meta: Dict,
        embeddings: np.ndarray
    ):
        session = self.Session()
        try:
            label2idxs = {}
            for idx, lab in enumerate(labels.tolist()):
                label2idxs.setdefault(int(lab), []).append(idx)
    
            logger.info("persist_clusters: labels present = %s", list(label2idxs.keys()))
            created = 0
    
            for lab, idxs in label2idxs.items():
                if lab == -1:
                    for i in idxs:
                        art = articles[i]
                        art.cluster_id = None
                        art.clustered_at = datetime.now(timezone.utc)
                        session.merge(art)
                    continue
    
                top_terms = self.extract_top_terms(texts, idxs, top_n=10)
                centroid_vec = embeddings[idxs].mean(axis=0).tolist()
    
                cluster = Cluster(
                    name=f"cluster_{int(datetime.now().timestamp())}_{lab}",
                    algorithm=algo_meta.get("algorithm"),
                    params=algo_meta,
                    vector_center=centroid_vec,
                    size=len(idxs),
                    top_terms=top_terms,
                )
                session.add(cluster)
                session.flush()
                logger.info(
                    "persist_clusters: created cluster id=%s, lab=%s, size=%d, top_terms=%s",
                    cluster.id,
                    lab,
                    len(idxs),
                    top_terms,
                )
    
                for i in idxs:
                    art = articles[i]
                    art.cluster_id = cluster.id
                    art.clustered_at = datetime.now(timezone.utc)
                    session.merge(art)
    
                created += 1
    
            session.commit()
            logger.info("Persisted %d clusters (and updated %d articles)", created, len(articles))
        except Exception as e:
            session.rollback()
            logger.exception("Error while persisting clusters: %s", e)
            raise
        finally:
            session.close()

    def run_once(self, limit: int = 500):
        articles = self.fetch_unclustered_articles(limit=limit)
        logger.info("run_once: fetched %d articles to cluster", len(articles))
    
        if not articles:
            logger.info("No articles to cluster")
            return
    
        texts = []
        for a in articles:
            title = (a.title or "").strip()
            text = (a.text or "").strip()
            combined = title + " . " + text if title else text
            texts.append(combined)
    
        logger.info("run_once: prepared %d combined texts", len(texts))
    
        embeddings = self.embed_texts(texts)
        logger.info("run_once: got embeddings shape=%s", embeddings.shape)
    
        labels, meta = self.cluster_embeddings(embeddings)
        unique_labels, counts = np.unique(labels, return_counts=True)
        logger.info(
            "run_once: clustering done, algo=%s, labels=%s, counts=%s",
            meta.get("algorithm"),
            unique_labels.tolist(),
            counts.tolist(),
        )
    
        try:
            if len(set(labels.tolist())) > 1 and len(labels) >= 5:
                sil = silhouette_score(embeddings, labels)
                meta["silhouette"] = float(sil)
                logger.info("run_once: silhouette score = %.4f", sil)
        except Exception:
            logger.exception("run_once: error computing silhouette")
    
        self.persist_clusters(articles, texts, labels, meta, embeddings)

    # utility for testing: populate sample rows
    def create_sample_data(self):
        session = self.Session()
        try:
            session.query(Article).filter(Article.external_id.like("sample_%")).delete()
            sample_texts = [
                ("Bankruptcies sweep across small banks", "Several regional banks reported sudden withdrawals and may file for bankruptcy..."),
                ("Центробанк повысил ставку", "Центробанк поднял ключевую ставку на 50 б.п...."),
                ("Банкротство регионального банка", "Региональный банк объявил о возможном банкротстве..."),
                ("Tech company files for IPO", "The startup announced intention to go public..."),
                ("Political protest downtown", "Thousands rallied in the capital demanding policy changes..."),
                ("Local elections heating up", "Candidates for mayor debate infrastructure and taxes..."),
                ("Major bank merger announced", "Two large banks agreed to merge in a deal worth billions..."),
                ("Reports: CEO of BigCorp resigns", "In an unexpected move, CEO leaves after scandals..."),
                ("Sports: football team wins cup", "Underdogs beat champions in a dramatic final..."),
            ]
            for i, (t, b) in enumerate(sample_texts):
                art = Article(
                    external_id=f"sample_{i}",
                    title=t,
                    text=b,
                    published_at=datetime.now(timezone.utc),
                    processed=True,
                )
                session.add(art)
            session.commit()
            logger.info("Inserted sample %d articles", len(sample_texts))
        finally:
            session.close()

