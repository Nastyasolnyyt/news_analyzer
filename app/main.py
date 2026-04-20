import time
import pandas as pd
from analyzer import AnomalyAnalyzer
from database import get_engine
from config import logger

def run_monitoring():
    engine = get_engine()
    analyzer = AnomalyAnalyzer(engine)
    
    logger.info("Проверка базы данных на наличие аномалий...")
    
    while True:
        try:
            # Собираем данные
            mentions = analyzer.analyze_mentions(days=30)
            risks = analyzer.analyze_risks(days=30)
            
            all_found = mentions + risks
            
            if all_found:
                print("\n" + "="*80)
                print(f" ОТЧЕТ ОБ АНОМАЛИЯХ (Анализ за 30 дней от последней записи)")
                print("="*80)
                df = pd.DataFrame(all_found)
                print(df[['type', 'entity_name', 'score', 'desc']].to_string(index=False))
                print("="*80 + "\n")
            else:
                logger.info("Аномалий с заданным порогом не найдено.")

            logger.info("Следующая проверка через 10 минут...")
            time.sleep(600) 
            
        except Exception as e:
            logger.error(f"Ошибка в цикле мониторинга: {e}")
            time.sleep(60)

if __name__ == "__main__":
    run_monitoring()