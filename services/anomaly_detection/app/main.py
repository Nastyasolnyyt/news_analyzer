import time
import pandas as pd
from analyzer import AnomalyAnalyzer
from database import get_engine, check_db_structure, save_anomalies, fetch_and_print_all_anomalies
from config import logger

def run_monitoring():
    # 1. Сначала подготавливаем таблицу
    logger.info("Инициализация сервиса...")
    if not check_db_structure():
        logger.error("Не удалось подготовить БД. Завершение работы.")
        return

    engine = get_engine()
    analyzer = AnomalyAnalyzer(engine)
    
    logger.info("Цикл мониторинга запущен.")
    
    while True:
        try:
            logger.info("Проверка на наличие аномалий...")
            
            # Собираем данные
            mentions = analyzer.analyze_mentions(days=30)
            risks = analyzer.analyze_risks(days=30)
            
            all_found = mentions + risks
            
            if all_found:
                # Печатаем в консоль
                print("\n" + "="*80)
                print(f" ОБНАРУЖЕНЫ АНОМАЛИИ")
                print("="*80)
                df_report = pd.DataFrame(all_found)
                print(df_report[['type', 'entity_name', 'score', 'desc']].to_string(index=False))
                print("="*80 + "\n")
                
                # 2. Сохраняем в БД
                save_anomalies(all_found)
                
                # 3. Проверяем, что сохранилось
                fetch_and_print_all_anomalies()
            else:
                logger.info("Аномалий не обнаружено.")

            logger.info("Следующая проверка через 10 минут...")
            time.sleep(600) 
            
        except Exception as e:
            logger.error(f"Ошибка в цикле мониторинга: {e}")
            time.sleep(60)

if __name__ == "__main__":
    run_monitoring()