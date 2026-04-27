from sqlalchemy import create_engine, text
import pandas as pd
from config import DB_URL, logger

# Настройка SSL для работы с Render
connect_args = {}
if DB_URL and "render.com" in DB_URL:
    connect_args["sslmode"] = "require"

engine = create_engine(
    DB_URL, 
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=300
)

def get_engine():
    return engine

def check_db_structure():
    """Создает таблицу аномалий, если она не существует."""
    try:
        with engine.connect() as conn:
            # ИСПРАВЛЕНО: REFERENCES named_entities(id)
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
            conn.commit()
        logger.info("Проверка структуры БД: таблица 'anomalies' готова.")
        return True
    except Exception as e:
        logger.error(f"Ошибка создания таблицы аномалий: {e}")
        return False

def save_anomalies(anomalies_list):
    """Сохраняет найденные аномалии в базу."""
    if not anomalies_list:
        return
    try:
        df = pd.DataFrame(anomalies_list)
        # Маппинг полей из анализатора в колонки таблицы
        mapping = {'type': 'anomaly_type', 'desc': 'description'}
        df = df.rename(columns=mapping)
        
        with engine.begin() as conn:
            df.to_sql('anomalies', con=conn, if_exists='append', index=False)
        logger.info(f"Успешно сохранено {len(anomalies_list)} аномалий.")
    except Exception as e:
        logger.error(f"Ошибка сохранения аномалий: {e}")

def fetch_and_print_all_anomalies():
    """Вывод последних записей для контроля."""
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text("SELECT * FROM anomalies ORDER BY detected_at DESC LIMIT 5"), conn)
            if not df.empty:
                print("\n--- ПОСЛЕДНИЕ ЗАПИСИ В ТАБЛИЦЕ ANOMALIES ---")
                print(df[['anomaly_type', 'description', 'detected_at']])
    except Exception as e:
        logger.error(f"Ошибка при чтении аномалий: {e}")