-- 1. Таблица статей (Синхронизирована с моделью Post)
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    author VARCHAR(255) NOT NULL,          -- Из модели: author
    title VARCHAR(255) NOT NULL,           -- Из модели: title
    content TEXT NOT NULL,                 -- В модели 'content', а не 'text'
    source TEXT NOT NULL,                  -- Из модели: source
    link TEXT UNIQUE NOT NULL,             -- Твоя защита от дубликатов
    pub_date TIMESTAMPTZ,                  -- Твоя колонка даты публикации
    created_at TIMESTAMPTZ DEFAULT NOW(),  -- Из модели: created_at
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Таблица тем (Требуется для PostAnalysis)
CREATE TABLE topics (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,            -- Из модели Topic
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Единая таблица анализа (Синхронизирована с PostAnalysis)
-- 3. Единая таблица анализа (Синхронизирована с PostAnalysis)
CREATE TABLE articles_analysis (
    id SERIAL PRIMARY KEY,
    -- UNIQUE гарантирует, что для одной статьи будет только ОДНА строка анализа
    post_id INTEGER NOT NULL UNIQUE REFERENCES articles(id) ON DELETE CASCADE, 
    topic_id INTEGER REFERENCES topics(id) ON DELETE SET NULL,
    
    -- Классификация
    category TEXT,                         -- 'economic', 'political', 'social'
    
    -- Метрики
    emotion FLOAT NOT NULL DEFAULT 0.0,
    tonality FLOAT NOT NULL DEFAULT 0.0,
    relevance FLOAT NOT NULL DEFAULT 0.0,
    
    -- Риски
    risk_level TEXT DEFAULT 'low',
    confidence REAL DEFAULT 0.0,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Индекс для быстрого поиска аналитики по ID статьи
CREATE INDEX idx_analysis_post_id ON articles_analysis(post_id);

-- 4. Справочник сущностей (Для NamedEntity)
CREATE TABLE named_entities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,            -- Из модели
    entity_type VARCHAR(50) NOT NULL,      -- Из модели
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Связь статей и сущностей (Для PostEntity)
CREATE TABLE articles_entities (
    post_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    entity_id INTEGER REFERENCES named_entities(id) ON DELETE CASCADE,
    PRIMARY KEY (post_id, entity_id)       -- Составной ключ из модели
);

-- 6. Таблица пользователей (Синхронизирована с моделью User)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    login VARCHAR UNIQUE NOT NULL,         -- В модели 'login'
    username VARCHAR UNIQUE NOT NULL,      -- В модели 'username'
    password_hash VARCHAR NOT NULL,        -- Из модели
    name VARCHAR NOT NULL,                 -- Из модели
    role TEXT DEFAULT 'user',              -- Из модели
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. Таблица аномалий (Для интеграции твоей логики)
CREATE TABLE anomalies (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    anomaly_type TEXT NOT NULL,
    description TEXT,
    score REAL,
    detected_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. Источники (Твоя таблица для парсеров)
CREATE TABLE sources (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    type TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_scraped_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

--- ИНДЕКСЫ ---
CREATE INDEX idx_articles_link ON articles(link);
CREATE INDEX idx_articles_content_gin ON articles USING gin(to_tsvector('russian', content));
CREATE INDEX idx_analysis_post ON articles_analysis(post_id);