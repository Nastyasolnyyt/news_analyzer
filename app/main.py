import argparse
from config import logger, DEFAULT_DAYS, Z_SCORE_THRESHOLD
from analyzer import AnomalyAnalyzer
from database import get_engine, check_db_structure, save_anomalies, fetch_and_print_all_anomalies, clear_anomalies_table


def run_service(days, threshold):
    if not check_db_structure():
        return

    # ДЛЯ ОЧИСТКИ ТАБЛИЦЫ ПЕРЕД ЗАПУСКОМ
    # clear_anomalies_table() 

    analyzer = AnomalyAnalyzer(get_engine())
    found = []

    # Запуск алгоритмов
    logger.info("Анализ упоминаний сущностей...")
    found.extend(analyzer.analyze_entity_mentions(days, threshold))

    logger.info("Анализ распределения рисков...")
    found.extend(analyzer.analyze_risk_distribution(days))

    # Сохранение и вывод в консоль найденного
    if found:
        save_anomalies(found)
    else:
        logger.info("Новых аномалий не обнаружено.")

    # Финальный показ ВСЕЙ таблицы из базы
    fetch_and_print_all_anomalies()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--days', type=int, default=DEFAULT_DAYS)
    parser.add_argument('--threshold', type=float, default=Z_SCORE_THRESHOLD)
    args = parser.parse_args()
    
    run_service(args.days, args.threshold)


