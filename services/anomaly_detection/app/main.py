"""
anomaly_detection/app/main.py
ИСПРАВЛЕНО:
1. Импорты теперь относительные (from analyzer import ...) → работает при запуске через python app/main.py
2. Добавлен вывод статистики БД при каждом цикле для диагностики
"""
import time
import sys
import os
import pandas as pd

# Добавляем путь к директории app в sys.path для корректных импортов
sys.path.insert(0, os.path.dirname(__file__))

from analyzer import AnomalyAnalyzer
from database import get_engine, check_db_structure, save_anomalies, fetch_and_print_all_anomalies
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AnomalyService")


def run_monitoring():
    logger.info("Инициализация сервиса обнаружения аномалий...")

    if not check_db_structure():
        logger.error("Не удалось подготовить БД. Завершение работы.")
        return

    engine = get_engine()
    analyzer = AnomalyAnalyzer(engine)

    logger.info("Цикл мониторинга запущен.")

    while True:
        try:
            logger.info("=" * 50)
            logger.info("Проверка на наличие аномалий...")

            # Выводим статистику для диагностики
            stats = analyzer.get_stats()
            if stats['articles'] == 0:
                logger.warning("База данных пуста, аномалии невозможно обнаружить")
                logger.info("Следующая проверка через 10 минут...")
                time.sleep(600)
                continue

            # Анализируем
            mentions = analyzer.analyze_mentions(days=30)
            risks = analyzer.analyze_risks(days=30)

            all_found = mentions + risks

            if all_found:
                print("\n" + "=" * 80)
                print(f" ОБНАРУЖЕНЫ АНОМАЛИИ ({len(all_found)} шт.)")
                print("=" * 80)
                df_report = pd.DataFrame(all_found)
                print(df_report[['type', 'entity_name', 'score', 'desc']].to_string(index=False))
                print("=" * 80 + "\n")

                save_anomalies(all_found)
                fetch_and_print_all_anomalies()
            else:
                logger.info(
                    f"Аномалий не обнаружено "
                    f"(статей: {stats['articles']}, "
                    f"рисков: {stats['risks']}, "
                    f"сущностей: {stats['entities']})"
                )

            logger.info("Следующая проверка через 10 минут...")
            time.sleep(600)

        except Exception as e:
            logger.error(f"Ошибка в цикле мониторинга: {e}", exc_info=True)
            time.sleep(60)


if __name__ == "__main__":
    run_monitoring()