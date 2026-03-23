from sqlalchemy import create_engine, text
import pandas as pd
from config import DB_URL, logger

engine = create_engine(DB_URL, echo=False)

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
                    risk_type TEXT,
                    anomaly_type TEXT NOT NULL,
                    description TEXT,
                    severity TEXT DEFAULT 'medium',
                    score REAL,
                    detected_at TIMESTAMPTZ DEFAULT NOW()
                );
            """))
        return True
    except Exception as e:
        logger.error(f"Ошибка БД: {e}")
        return False

def save_anomalies(anomalies_list):
    if not anomalies_list:
        return
    
    df = pd.DataFrame(anomalies_list)
    try:
        with engine.connect() as conn:
            query = "SELECT anomaly_type, description FROM anomalies WHERE detected_at > NOW() - INTERVAL '1 day'"
            existing_df = pd.read_sql(text(query), conn)
            
        if not existing_df.empty:
            existing_df['key'] = existing_df['anomaly_type'] + existing_df['description']
            df['key'] = df['anomaly_type'] + df['description']
            df = df[~df['key'].isin(existing_df['key'])].drop(columns=['key'])
            
        if df.empty:
            logger.info("Новых уникальных аномалий нет.")
            return

        with engine.begin() as conn:
            df.to_sql('anomalies', con=conn, if_exists='append', index=False)
        logger.info(f"Сохранено новых аномалий: {len(df)}")
    except Exception as e:
        logger.error(f"Ошибка сохранения: {e}")

def fetch_and_print_all_anomalies():
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text("SELECT id, anomaly_type, description, detected_at FROM anomalies ORDER BY detected_at DESC"), conn)
            print("\n--- Полная история аномалий ---")
            if df.empty:
                print("[Пусто]")
            else:
                pd.set_option('display.max_colwidth', 80)
                print(df.to_string(index=False))
            print("-" * 31 + "\n")
    except Exception as e:
        logger.error(f"Ошибка чтения: {e}")