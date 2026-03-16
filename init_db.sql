-- 1. Таблица статей (Добавлена уникальность ссылки и индексация для поиска)
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title TEXT,
    text TEXT NOT NULL,
    link TEXT UNIQUE NOT NULL, -- КРИТИЧНО: Защита от дубликатов на уровне БД
    pub_date TIMESTAMPTZ,
    source TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Таблица рисков (Изменено на UNIQUE article_id, так как одной статье — одна оценка риска)
CREATE TABLE risks (
    id SERIAL PRIMARY KEY,
    article_id INTEGER UNIQUE REFERENCES articles(id) ON DELETE CASCADE, -- UNIQUE исключает повторный анализ одной новости
    risk_type TEXT NOT NULL, -- Здесь будут наши 'high', 'medium', 'low'
    confidence REAL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Таблица сущностей
CREATE TABLE entities (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    type TEXT NOT NULL,
    start_pos INTEGER,
    end_pos INTEGER,
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Таблица источников (Уже была UNIQUE url, это хорошо)
CREATE TABLE sources (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    type TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_scraped_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Таблица пользователей
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Таблица тональности
CREATE TABLE sentiments (
    id SERIAL PRIMARY KEY,
    article_id INTEGER UNIQUE REFERENCES articles(id) ON DELETE CASCADE, -- Тоже UNIQUE
    sentiment_label TEXT NOT NULL,
    confidence REAL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. Таблица кластеров (Улучшено: использование GIN индекса для массивов)
CREATE TABLE clusters (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    article_ids INTEGER[] NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. Таблица аномалий
CREATE TABLE anomalies (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    entity_id INTEGER REFERENCES entities(id) ON DELETE SET NULL,
    risk_type TEXT,
    anomaly_type TEXT NOT NULL,
    description TEXT,
    severity TEXT DEFAULT 'medium',
    score REAL,
    detected_at TIMESTAMPTZ DEFAULT NOW()
);

-- 9. Таблица связей между сущностями
CREATE TABLE entity_relations (
    id SERIAL PRIMARY KEY,
    entity1_id INTEGER REFERENCES entities(id) ON DELETE CASCADE,
    entity2_id INTEGER REFERENCES entities(id) ON DELETE CASCADE,
    relation_type TEXT DEFAULT 'co-occurrence',
    weight REAL DEFAULT 1.0,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    -- Уникальность связи в рамках одной статьи, чтобы не дублировать граф
    UNIQUE(entity1_id, entity2_id, article_id, relation_type) 
);

--- ИНДЕКСЫ ДЛЯ ПРОИЗВОДИТЕЛЬНОСТИ ---

-- Поиск по ссылке (самый частый запрос при парсинге)
CREATE INDEX idx_articles_link ON articles(link);

-- Полнотекстовый поиск (заказчик оценит возможность искать по тексту)
CREATE INDEX idx_articles_text_gin ON articles USING gin(to_tsvector('russian', text));

-- Оптимизация связей
CREATE INDEX idx_entities_type ON entities(type);
CREATE INDEX idx_clusters_articles ON clusters USING gin(article_ids);