import time
import pandas as pd
from analyzer import AnomalyAnalyzer
from database import get_engine, check_db_structure, save_anomalies, fetch_and_print_all_anomalies
from config import logger

def run_monitoring():
    # 1. Инициализация: проверяем или создаем таблицу anomalies
    logger.info("Подготовка базы данных...")
    if not check_db_structure():
        logger.error("Критическая ошибка: не удалось подготовить структуру БД. Проверьте подключение.")
        return

    engine = get_engine()
    analyzer = AnomalyAnalyzer(engine)
    
    logger.info("Сервис мониторинга аномалий запущен успешно.")
    
    while True:
        try:
            logger.info("Запуск цикла проверки на наличие аномалий...")
            
            # 2. Собираем данные через анализатор
            mentions = analyzer.analyze_mentions(days=30)
            risks = analyzer.analyze_risks(days=30)
            
            all_found = mentions + risks
            
            if all_found:
                # Печатаем отчет в логи контейнера для наглядности
                print("\n" + "="*80)
                print(f" ОБНАРУЖЕНЫ АНОМАЛИИ (Анализ за последние 30 дней)")
                print("="*80)
                df_print = pd.DataFrame(all_found)
                print(df_print[['type', 'entity_name', 'score', 'desc']].to_string(index=False))
                print("="*80 + "\n")
                
                # 3. Сохраняем найденное в базу данных
                save_anomalies(all_found)
                
                # Опционально: выводим последние 10 записей из БД для подтверждения записи
                fetch_and_print_all_anomalies()
            else:
                logger.info("Аномалий с заданным порогом не найдено.")

            logger.info("Проверка завершена. Следующий запуск через 10 минут...")
            time.sleep(600) 
            
        except Exception as e:
            logger.error(f"Ошибка в цикле мониторинга: {e}")
            # Если произошла ошибка , ждем минуту и пробуем снова
            time.sleep(60)

if __name__ == "__main__":
    run_monitoring()