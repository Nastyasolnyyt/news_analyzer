import argparse
import schedule
import time
from config import logger, DEFAULT_DAYS, Z_SCORE_THRESHOLD
from analyzer import AnomalyAnalyzer
from database import get_engine, check_db_structure, save_anomalies, fetch_and_print_all_anomalies

def run_service(days, threshold):
    if not check_db_structure():
        return

    analyzer = AnomalyAnalyzer(get_engine())
    found = []

    logger.info("Запуск анализа...")
    found.extend(analyzer.analyze_entity_mentions(days, threshold))
    found.extend(analyzer.analyze_risk_distribution(days))
    found.extend(analyzer.analyze_unusual_pairs())
    found.extend(analyzer.analyze_sentiment_shifts())

    save_anomalies(found)
    fetch_and_print_all_anomalies()

if __name__ == "__main__":
    engine = get_engine()
    # with engine.connect() as conn:
    #     conn.execute(text("TRUNCATE TABLE anomalies RESTART IDENTITY CASCADE;"))
    #     conn.commit()
    #     logger.info("Таблица аномалий очищена.")

    parser = argparse.ArgumentParser()
    parser.add_argument('--days', type=int, default=DEFAULT_DAYS)
    parser.add_argument('--threshold', type=float, default=Z_SCORE_THRESHOLD)
    parser.add_argument('--interval', type=int, default=3) # Интервал
    args = parser.parse_args()
    
    logger.info(f"Старт фонового сервиса. Интервал: {args.interval} минут.")
    
    # 1. Запуск сразу при старте
    run_service(args.days, args.threshold)
    
    # 2. Планирование регулярных запусков
    schedule.every(args.interval).minutes.do(run_service, days=args.days, threshold=args.threshold)
    
    # 3. Бесконечный цикл ожидания
    while True:
        schedule.run_pending()
        time.sleep(1)