# Database Schema Analysis

## Overview
Based on Alembic migrations in `services/output_module/alembic/versions/`, here's the complete database schema structure.

---

## Table: `post_entities`

### Current Definition
From migration `c1d087f5b63c_first_migration.py`:

```sql
CREATE TABLE post_entities (
    post_id INTEGER NOT NULL,
    entity_id INTEGER NOT NULL,
    PRIMARY KEY (post_id, entity_id),
    FOREIGN KEY (entity_id) REFERENCES named_entities(id) ON DELETE CASCADE,
    FOREIGN KEY (entity_id) REFERENCES named_entities(id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES articles(id) ON DELETE CASCADE
);
```

### Schema Details

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `post_id` | INTEGER | NOT NULL, Foreign Key to `articles(id)`, Primary Key part 1 | References the article |
| `entity_id` | INTEGER | NOT NULL, Foreign Key to `named_entities(id)`, Primary Key part 2 | References the named entity |

### Primary Key Structure
- **Composite Primary Key**: `(post_id, entity_id)`
- This is a junction/association table linking posts/articles to named entities

### Constraints
1. **Primary Key**: `(post_id, entity_id)` - Composite, ensures one entity per post
2. **Foreign Key** on `post_id`: 
   - References `articles.id` (was `posts.id` before migration `b2c3d4e5f6g7`)
   - ON DELETE CASCADE - deletes association when article is deleted
3. **Foreign Key** on `entity_id`:
   - References `named_entities.id`
   - ON DELETE CASCADE - deletes association when entity is deleted

### Evolution
- **Initial creation** (migration `c1d087f5b63c`): Created as junction table between posts and named_entities
- **Table rename** (migration `b2c3d4e5f6g7`): Foreign key updated to reference `articles` instead of `posts`
  - Foreign key name: `post_entities_post_id_fkey`
  - Foreign key name: `post_entities_entity_id_fkey` (implied)

### Purpose
Represents many-to-many relationship: one post/article can have multiple named entities, and one entity can appear in multiple posts.

---

## Table: `risks`

### Current Definition
From migration `b2c3d4e5f6g7_rename_posts_to_articles_add_risk.py`:

```sql
CREATE TABLE risks (
    id INTEGER PRIMARY KEY,
    article_id INTEGER NOT NULL,
    risk_type TEXT NOT NULL,
    confidence FLOAT,
    created_at DATETIME DEFAULT now() NOT NULL,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    INDEX ix_risks_article_id ON (article_id)
);
```

### Schema Details

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | INTEGER | PRIMARY KEY | Auto-incrementing identifier |
| `article_id` | INTEGER | NOT NULL, Foreign Key to `articles(id)`, Unique | References the article (unique - one risk per article) |
| `risk_type` | TEXT | NOT NULL | Type of risk (политический/экономический/социальный, etc.) |
| `confidence` | FLOAT | NULL | Confidence level of the risk classification (0.0-1.0) |
| `created_at` | DATETIME | NOT NULL, DEFAULT now() | Timestamp of risk creation |

### Primary Key Structure
- **Simple Primary Key**: `id` (auto-incrementing integer)

### Constraints
1. **Primary Key**: `id` - Simple auto-increment identifier
2. **Foreign Key** on `article_id`:
   - References `articles.id`
   - ON DELETE CASCADE - deletes risk when article is deleted
   - **UNIQUE**: `article_id` is UNIQUE (only one risk per article)
3. **Index**: `ix_risks_article_id` on `article_id` for query performance

### ORM Model Definition
From `services/risk-classifier/app/storage.py`:

```python
class Risk(Base):
    """Модель таблицы risks"""
    __tablename__ = "risks"
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, unique=True, index=True)
    risk_type = Column(String)
    confidence = Column(Float)
```

### Purpose
Stores risk classification results for articles, with exactly one risk assessment per article. The `unique=True` on `article_id` enforces one-to-one relationship.

---

## Related Tables

### `articles` (formerly `posts`)
```sql
CREATE TABLE articles (
    id INTEGER PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT now() NOT NULL,
    link TEXT,
    pub_date DATETIME,
    updated_at DATETIME DEFAULT now() NOT NULL,
    text TEXT NOT NULL,
    source TEXT NOT NULL,
    UNIQUE (link) -- Added in migration d4e5f6g7h8i9
);
```

### `named_entities`
```sql
CREATE TABLE named_entities (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT now() NOT NULL
);
```

---

## Summary of Key Relationships

1. **post_entities** ← Many-to-Many → **articles** & **named_entities**
   - Composite key ensures unique combinations
   - Cascade delete maintains referential integrity

2. **risks** ← One-to-One → **articles**
   - Unique constraint on `article_id` enforces one risk per article
   - Cascade delete orphans risks when article deleted

---

## Migration History

| Revision | Up Revises | Description | Key Changes |
|----------|-----------|-------------|-------------|
| `c1d087f5b63c` | None | First migration | Creates `posts`, `post_entities`, `named_entities`, `topics`, `post_analysis` |
| `a1b2c3d4e5f6` | `c1d087f5b63c` | Add users table | Creates `users` table with `login` UNIQUE constraint |
| `b2c3d4e5f6g7` | `a1b2c3d4e5f6` | Rename posts to articles, add risks | Renames `posts` → `articles`, adds `risks` table, adds columns (link, pub_date, text, updated_at) |
| `c3d4e5f6g7h8` | `b2c3d4e5f6g7` | Add sentiment columns | Adds `confidence`, `sentiment_label` to `post_analysis` |
| `d4e5f6g7h8i9` | `c3d4e5f6g7h8` | Add UNIQUE on articles.link | Adds unique constraint on `articles(link)` |
| `e5f6g7h8i9j0` | `d4e5f6g7h8i9` | Add UNIQUE on post_analysis.post_id | Adds unique constraint on `post_analysis(post_id)` |
| `f5f6g7h8i9j0` | `e5f6g7h8i9j0` | Make sentiment columns nullable | Changes `emotion`, `tonality`, `relevance` to nullable |
| `003_add_notifications` | `f5f6g7h8i9j0` | Add notification system | Creates notification-related tables |
| `004_add_email_to_users` | `003_add_notifications` | Add email to users | Adds `email` column to `users` with unique index |

---

## Important Notes

1. **No explicit created_at or updated_at on post_entities**: The junction table doesn't track when associations were created
2. **article_id is UNIQUE in risks table**: Only one risk assessment per article
3. **Cascade deletes**: Both tables use CASCADE delete strategy - deleting an article will cascade delete its risks and entity associations
4. **Index on risks.article_id**: Facilitates fast lookups by article
5. **post_entities has no other metadata**: It's a pure junction table with just the two foreign keys
