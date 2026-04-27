from sqlalchemy import create_engine, text
import pandas as pd
from config import DB_URL, logger

# 1. Настройка SSL и параметров устойчивости пула
connect_args = {}
if "render.com" in DB_URL:
    connect_args["sslmode"] = "require"

engine = create_engine(
    DB_URL, 
    connect_args=connect_args,
    pool_pre_ping=True,      # Проверяет живое ли соединение перед использованием
    pool_recycle=300,        # Пересоздает соединение каждые 5 минут (важно для Render)
    pool_size=5,             # Ограничиваем количество соединений
    max_overflow=10          # Запас соединений при пиках
)

def get_engine():
    return engine

def check_db_structure():
    """Проверяет структуру и создает таблицу, если ее нет."""
    try:
        # Используем connect() + commit() вместо begin() для большей стабильности при инициализации
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
        logger.error(f"Ошибка создания/проверки таблицы аномалий: {e}")
        return False

def save_anomalies(anomalies_list):
    """Преобразует данные из анализатора и сохраняет в БД."""
    if not anomalies_list:
        return
    
    try:
        df = pd.DataFrame(anomalies_list)
        
        # Маппинг колонок: из того что дает analyzer.py -> в то, что ждет БД
        # analyzer.py выдает: type, entity_name, score, desc
        mapping = {
            'type': 'anomaly_type',
            'desc': 'description'
        }
        df = df.rename(columns=mapping)
        
        # Если в данных есть entity_name, но нет entity_id, 
        # sqlalchemy может не понять, куда писать. 
        # Оставляем только те колонки, которые реально есть в таблице anomalies
        allowed_cols = ['anomaly_type', 'description', 'score', 'article_id', 'entity_id', 'severity']
        columns_to_save = [c for c in allowed_cols if c in df.columns]
        
        df_to_save = df[columns_to_save]

        with engine.begin() as conn:
            df_to_save.to_sql('anomalies', con=conn, if_exists='append', index=False)
            logger.info(f"Успешно сохранено аномалий: {len(df_to_save)}")
            
    except Exception as e:
        logger.error(f"Ошибка при сохранении аномалий в БД: {e}")

def fetch_and_print_all_anomalies():
    """Служебная функция для отладки — выводит список из БД в консоль."""
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text("SELECT * FROM anomalies ORDER BY detected_at DESC"), conn)
            print("\n" + "="*30)
            print(" СОСТОЯНИЕ ТАБЛИЦЫ АНОМАЛИЙ ")
            print("="*30)
            if not df.empty:
                print(df[['anomaly_type', 'description', 'detected_at']].to_string(index=False))
            else:
                print("[Данные в таблице отсутствуют]")
            print("="*30 + "\n")
    except Exception as e:
        logger.error(f"Ошибка при чтении аномалий для печати: {e}")