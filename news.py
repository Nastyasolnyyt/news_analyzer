import sys
import types
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import time

# --- МАГИЧЕСКАЯ ЗАПЛАТКА ДЛЯ PYTHON 3.12+ (ОБЯЗАТЕЛЬНО ОСТАВИТЬ!) ---
# Этот блок обходит проблему с удаленным модулем 'imp' в новых версиях Python.
if 'imp' not in sys.modules:
    sys.modules['imp'] = types.ModuleType('imp')
# -------------------------------------------------------------------

# --- НАСТРОЙКИ ---
OUTPUT_FILENAME = "news_output.csv" # Меняем на CSV
CSV_DELIMITER = "|"                  # Выбираем разделитель (например, вертикальная черта)
START_PAGE = 1
END_PAGE = 4  # Указываем, сколько страниц Хабра нужно обработать (с 1 по 4)

# --- ГЛАВНАЯ ЛОГИКА ---
try:
    print(f"Начинаю сбор новостей с Хабра (страницы {START_PAGE}-{END_PAGE})...")

    # Открываем файл для записи. 'w' - перезаписывает файл при каждом запуске.
    with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
        
        # Цикл для перебора страниц
        for page_num in range(START_PAGE, END_PAGE + 1):
            
            # Формирование URL для текущей страницы
            if page_num == 1:
                page_url = 'https://habr.com/ru/articles/'
            else:
                page_url = f'https://habr.com/ru/articles/page{page_num}/'
            
            print(f"\n--- ОБРАБАТЫВАЮ СТРАНИЦУ №{page_num} ({page_url}) ---")
            
            # Скачиваем страницу
            response = requests.get(page_url).text
            data = BeautifulSoup(response, 'html.parser')

            # Собираем ссылки с ленты (селекторы для Хабра)
            articles_on_page = data.find_all('h2', class_='tm-title tm-title_h2')
            
            if not articles_on_page:
                print("Достигнут конец ленты или страница пуста.")
                break
            
            for i, item in enumerate(articles_on_page, 1):
                link = 'https://habr.com' + item.a['href']
                
                try:
                    # Создаем и парсим статью с помощью newspaper3k
                    article = Article(link)
                    article.download()
                    article.parse()
                    
                    # Запись в файл
                    # Записываем Заголовок | URL | Текст
                    # Заменяем все переносы строк в тексте на пробел, чтобы не испортить формат CSV.
                    cleaned_text = article.text.replace('\n', ' ').replace('\r', '') 

                    f.write(f'"{article.title}"{CSV_DELIMITER}"{link}"{CSV_DELIMITER}"{cleaned_text}"\n')

                    print(f"  [+] Сохранено: {article.title[:50]}...")
                    time.sleep(1) # Пауза между статьями
                    
                except Exception as e:
                    # Если конкретная статья не парсится, переходим к следующей
                    print(f"  [!] Ошибка при обработке статьи {link}: {e}")

            time.sleep(5) # Большая пауза между страницами
            
    print(f"\nВСЕГО ОБРАБОТАНО СТРАНИЦ: {page_num}. Результат в {OUTPUT_FILENAME}")

except Exception as global_e:
    print(f"\nГЛОБАЛЬНАЯ ОШИБКА (проверьте интернет или URL): {global_e}")