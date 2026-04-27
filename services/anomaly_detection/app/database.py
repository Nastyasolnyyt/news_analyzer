from sqlalchemy import create_engine, text
import pandas as pd
from config import DB_URL, logger

engine = create_engine(DB_URL)

def get_engine():
    return engine

def check_db_structure():
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS anomalies (
                    id SERIAL PRIMARY KEY,
                    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
                    entity_id INTEGER REFERENCES entities(id) ON DELETE SET NULL,
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
    df = pd.DataFrame(anomalies_list)
    with engine.begin() as conn:
        df.to_sql('anomalies', con=conn, if_exists='append', index=False)

def fetch_and_print_all_anomalies():
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM anomalies ORDER BY detected_at DESC"), conn)
        print("\n--- Найденные аномалии ---")
        print(df[['anomaly_type', 'description']] if not df.empty else "[Пусто]")
