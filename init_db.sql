-- Таблица статей
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title TEXT,
    text TEXT NOT NULL,
    link TEXT,
    pub_date TIMESTAMPTZ,
    source TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Таблица рисков (для Risk Classifier)
CREATE TABLE risks (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    risk_type TEXT NOT NULL,
    confidence REAL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Таблица сущностей (для NER Service)
CREATE TABLE entities (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    type TEXT NOT NULL,
    start_pos INTEGER,
    end_pos INTEGER,
    details JSONB
);

-- Таблица источников
CREATE TABLE sources (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    type TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_scraped_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Таблица пользователей
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Таблица тональности (для Sentiment Analysis)
CREATE TABLE sentiments (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    sentiment_label TEXT NOT NULL,  -- 'positive', 'negative', 'neutral'
    confidence REAL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Таблица кластеров (для Event Clustering)
CREATE TABLE clusters (
    id SERIAL PRIMARY KEY,
    name TEXT,
    description TEXT,
    article_ids INTEGER[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Таблица аномалий (для Anomaly Detection)
CREATE TABLE anomalies (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    entity_id INTEGER REFERENCES entities(id) ON DELETE SET NULL,
    risk_type TEXT,
    anomaly_type TEXT NOT NULL,  -- 'mention_spike', 'sentiment_shift', 'unusual_pair'
    description TEXT,
    severity TEXT DEFAULT 'medium',  -- 'low', 'medium', 'high'
    score REAL,
    detected_at TIMESTAMPTZ DEFAULT NOW()
);

-- Таблица связей между сущностями (для Knowledge Graph Sync)
CREATE TABLE entity_relations (
    id SERIAL PRIMARY KEY,
    entity1_id INTEGER REFERENCES entities(id) ON DELETE CASCADE,
    entity2_id INTEGER REFERENCES entities(id) ON DELETE CASCADE,
    relation_type TEXT DEFAULT 'co-occurrence',
    weight REAL DEFAULT 1.0,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Индексы
CREATE INDEX idx_articles_source ON articles(source);
CREATE INDEX idx_articles_pub_date ON articles(pub_date);
CREATE INDEX idx_risks_article_id ON risks(article_id);
CREATE INDEX idx_entities_article_id ON entities(article_id);
CREATE INDEX idx_sentiments_article_id ON sentiments(article_id);
CREATE INDEX idx_anomalies_article_id ON anomalies(article_id);
CREATE INDEX idx_entity_relations_article_id ON entity_relations(article_id);