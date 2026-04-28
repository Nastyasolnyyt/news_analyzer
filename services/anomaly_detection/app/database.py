"""
anomaly_detection/app/database.py
ИСПРАВЛЕНО:
1. Исправлен импорт config — используем относительный путь вместо абсолютного
2. Добавлено логирование при сохранении аномалий
"""
from sqlalchemy import create_engine, text
import pandas as pd
import logging
import os

logger = logging.getLogger("AnomalyService")

DB_URL = os.getenv("DATABASE_URL")

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
    """Создаёт таблицу аномалий, если её нет."""
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS anomalies (
                    id SERIAL PRIMARY KEY,
                    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
                    entity_id INTEGER REFERENCES named_entities(id) ON DELETE SET NULL,
                    anomaly_type TEXT NOT NULL,
                    entity_name TEXT,
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
        rows = []
        for a in anomalies_list:
            rows.append({
                'anomaly_type': a.get('type', 'unknown'),
                'entity_name': a.get('entity_name', ''),
                'description': a.get('desc', ''),
                'score': a.get('score', 0.0),
                'severity': _score_to_severity(a.get('score', 0.0)),
            })

        df = pd.DataFrame(rows)

        with engine.begin() as conn:
            df.to_sql('anomalies', con=conn, if_exists='append', index=False)

        logger.info(f"Сохранено {len(anomalies_list)} аномалий в БД.")
    except Exception as e:
        logger.error(f"Ошибка сохранения аномалий: {e}")


def _score_to_severity(score: float) -> str:
    """Переводит числовой score в текстовый уровень серьёзности."""
    if score >= 3.0:
        return 'high'
    elif score >= 1.5:
        return 'medium'
    else:
        return 'low'


def fetch_and_print_all_anomalies():
    """Вывод последних записей для контроля."""
    try:
        with engine.connect() as conn:
            df = pd.read_sql(
                text("SELECT * FROM anomalies ORDER BY detected_at DESC LIMIT 5"),
                conn
            )
            if not df.empty:
                print("\n--- ПОСЛЕДНИЕ ЗАПИСИ В ТАБЛИЦЕ ANOMALIES ---")
                print(df[['anomaly_type', 'entity_name', 'description', 'score', 'detected_at']])
            else:
                logger.info("Таблица anomalies пока пуста.")
    except Exception as e:
        logger.error(f"Ошибка при чтении аномалий: {e}")