from sqlalchemy import create_engine, text
import pandas as pd
from config import DB_URL, logger

# 1. Настраиваем SSL для работы с Render
# Для синхронного psycopg2 используется sslmode
connect_args = {}
if "render.com" in DB_URL:
    connect_args["sslmode"] = "require"

engine = create_engine(
    DB_URL, 
    connect_args=connect_args,
    pool_pre_ping=True  # Помогает не терять связь с далеким сервером
)

def get_engine():
    return engine

def check_db_structure():
    try:
        with engine.begin() as conn:
            # 2. Исправляем имена таблиц в FOREIGN KEY
            # Судя по analyzer.py, твои таблицы называются 'articles' и 'named_entities'
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS anomalies (
                    id SERIAL PRIMARY KEY,
                    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
                    entity_id INTEGER REFERENCES named_entities(id) ON DELETE SET NULL,
                    anomaly_type TEXT NOT NULL,
                    description TEXT,
                    severity TEXT DEFAULT 'medium',
                    score REAL,
                    detected_at TIMESTAMPTZ DEFAULT NOW()
                );
            """))
        return True
    except Exception as e:
        logger.error(f"Ошибка создания таблицы аномалий: {e}")
        return False

def save_anomalies(anomalies_list):
    if not anomalies_list:
        return
    
    # Подготавливаем DataFrame под структуру таблицы
    df = pd.DataFrame(anomalies_list)
    
    # Переименовываем колонки из кода анализатора в колонки БД
    # В analyzer.py у тебя 'type' и 'entity_name', а в БД 'anomaly_type' и 'description'
    mapping = {
        'type': 'anomaly_type',
        'desc': 'description',
        'score': 'score'
    }
    df = df.rename(columns=mapping)
    
    # Оставляем только те колонки, что есть в таблице
    allowed_cols = ['anomaly_type', 'description', 'score']
    df = df[[c for c in allowed_cols if c in df.columns]]

    try:
        with engine.begin() as conn:
            df.to_sql('anomalies', con=conn, if_exists='append', index=False)
            logger.info(f"Сохранено аномалий: {len(df)}")
    except Exception as e:
        logger.error(f"Ошибка при сохранении в БД: {e}")

def fetch_and_print_all_anomalies():
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text("SELECT * FROM anomalies ORDER BY detected_at DESC"), conn)
            print("\n--- Найденные аномалии ---")
            if not df.empty:
                # В БД колонка называется anomaly_type, а не type
                print(df[['anomaly_type', 'description']])
            else:
                print("[Пусто]")
    except Exception as e:
        print(f"Ошибка чтения аномалий: {e}")