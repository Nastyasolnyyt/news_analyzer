from sqlalchemy import create_engine, text, inspect
import pandas as pd
from config import DB_URL, logger

# Инициализация движка для подключения к БД.
engine = create_engine(DB_URL, echo=False)

# Получение движка для работы с БД (можно расширить для поддержки нескольких баз или разных настроек) - в данном случае, просто возвращаем глобальный движок, так как он один и настройки фиксированные
# singleton-подход для простоты, так как в данном проекте достаточно одного подключения к БД. В более сложных случаях можно реализовать полноценный класс-менеджер подключений.
def get_engine():
    return engine

# Проверка структуры БД и создание таблицы anomalies при необходимости
# ? перенести логику в отдельный файл для бд, так как она может расширяться (например, добавление новых таблиц для хранения аномалий разных типов)
# В данном случае, для простоты, оставляем здесь, так как таблица всего одна и логика несложная
# возможен перенос в файл models.py при расширении проекта и использовании ORM
def check_db_structure():
    try:
        inspector = inspect(engine)
        if 'anomalies' not in inspector.get_table_names():
            with engine.begin() as conn:
                conn.execute(text("""
                    CREATE TABLE anomalies (
                        id SERIAL PRIMARY KEY,
                        entity_id INTEGER,
                        risk_type TEXT,
                        anomaly_type TEXT NOT NULL,
                        description TEXT,
                        severity TEXT,
                        score REAL,
                        detected_at TIMESTAMPTZ DEFAULT NOW()
                    );
                """))
            logger.info("Таблица 'anomalies' создана.")
        return True
    except Exception as e:
        logger.error(f"Ошибка БД: {e}")
        return False

# Сохранение найденных аномалий в базу данных + вывод в консоль
def save_anomalies(anomalies_list):
    if not anomalies_list:
        return
    
    df = pd.DataFrame(anomalies_list)
    
    try:
        with engine.connect() as conn:
            # 1. Читаем из базы аномалии, которые УЖЕ были найдены сегодня
            query = "SELECT anomaly_type, description FROM anomalies WHERE DATE(detected_at) = CURRENT_DATE"
            existing_df = pd.read_sql(text(query), conn)
            
        # 2. Фильтруем дубликаты с помощью Pandas
        if not existing_df.empty:
            # Создаем временную колонку 'key' (склеиваем тип и описание) для сравнения
            existing_df['key'] = existing_df['anomaly_type'] + existing_df['description']
            df['key'] = df['anomaly_type'] + df['description']
            
            # Оставляем в df только те строки, ключей которых НЕТ в existing_df
            df = df[~df['key'].isin(existing_df['key'])].drop(columns=['key'])
            
        if df.empty:
            print("\n" + "-" * 60)
            print("Новых аномалий нет (все найденные уже сохранены в базе сегодня).")
            print("-" * 60)
            return

        # 3. Сохраняем только уникальные новые аномалии
        print("\n" + "Найденные НОВЫЕ аномалии:")
        print("-" * 60)
        print(df[['anomaly_type', 'description', 'severity']].to_string(index=False))
        print("-" * 60)

        with engine.begin() as conn:
            df.to_sql('anomalies', con=conn, if_exists='append', index=False)
        logger.info(f"Успешно сохранено в базу: {len(df)} шт.")

    except Exception as e:
        logger.error(f"Ошибка сохранения: {e}")

# вывод содержимого таблицы anomalies в консоль для просмотра
def fetch_and_print_all_anomalies():
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text("SELECT * FROM anomalies ORDER BY detected_at DESC"), conn)
            
            print("\n" + "Полная история аномалий (из бд):")
            if df.empty:
                print("[База данных пока пуста]")
            else:
                pd.set_option('display.max_colwidth', 80)
                print(df[['id', 'anomaly_type', 'description', 'detected_at']].to_string(index=False))
            print("="*90 + "\n")
    except Exception as e:
        logger.error(f"Ошибка чтения таблицы: {e}")

# Удалить все записи из таблицы anomalies (для тестов)
def clear_anomalies_table():
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE anomalies RESTART IDENTITY CASCADE;"))
    print("--Таблица anomalies успешно очищена--")