from sqlalchemy import create_engine, text
import pandas as pd
from config import DB_URL, logger

# 1. Настройка SSL и параметров устойчивости
connect_args = {}
if "render.com" in DB_URL:
    # Для psycopg2 (синхронного) крайне важно передать sslmode именно так
    connect_args["sslmode"] = "require"

engine = create_engine(
    DB_URL, 
    connect_args=connect_args,
    # Параметры для борьбы с обрывами в Орегоне:
    pool_pre_ping=True,      # Проверять соединение перед каждым использованием
    pool_recycle=300,        # Пересоздавать соединение каждые 5 минут
    pool_timeout=30,         # Увеличиваем время ожидания подключения
    pool_size=5,             # Не открываем слишком много соединений
    max_overflow=0           # Жестко ограничиваем количество подключений
)

def get_engine():
    return engine

def check_db_structure():
    """Создает таблицу аномалий, если она не существует."""
    try:
        # Используем явный коммит для синхронизации структуры на удаленном сервере
        with engine.connect() as conn:
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
        return True
    except Exception as e:
        logger.error(f"Ошибка проверки/создания структуры БД: {e}")
        return False

def save_anomalies(anomalies_list):
    """Сохраняет найденные аномалии в базу."""
    if not anomalies_list:
        return
    
    try:
        df = pd.DataFrame(anomalies_list)
        
        # Маппинг колонок из analyzer.py в таблицу anomalies
        mapping = {
            'type': 'anomaly_type',
            'desc': 'description'
        }
        df = df.rename(columns=mapping)
        
        # Оставляем только те колонки, которые реально есть в вашей таблице
        db_columns = ['anomaly_type', 'description', 'score', 'article_id', 'entity_id', 'severity']
        df_to_save = df[[c for c in db_columns if c in df.columns]]

        with engine.begin() as conn:
            df_to_save.to_sql('anomalies', con=conn, if_exists='append', index=False)
            logger.info(f"Успешно сохранено {len(df_to_save)} аномалий.")
            
    except Exception as e:
        logger.error(f"Ошибка сохранения аномалий: {e}")

def fetch_and_print_all_anomalies():
    """Служебный вывод аномалий для логов контейнера."""
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text("SELECT * FROM anomalies ORDER BY detected_at DESC LIMIT 10"), conn)
            if not df.empty:
                print("\n--- ПОСЛЕДНИЕ АНОМАЛИИ В БД ---")
                print(df[['anomaly_type', 'description', 'detected_at']])
            else:
                print("\n[Таблица аномалий пуста]")
    except Exception as e:
        logger.error(f"Не удалось прочитать таблицу аномалий: {e}")