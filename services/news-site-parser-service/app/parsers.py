import sys
import types
import requests
from bs4 import BeautifulSoup
import time
from .models import Article as ArticleModel



def get_article_content(url: str) -> str:
    """
    Получает текст статьи с указанного URL с помощью requests + BeautifulSoup.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Пример: ищем основной контент статьи на Хабре
        # Класс может изменяться, проверьте актуальный HTML
        article_body = soup.find('div', class_='tm-article-body')
        if article_body:
            return article_body.get_text(separator=' ', strip=True)
        else:
            # Если не нашли, ищем более общий контент
            sel = soup.find('article')
            if sel:
                return sel.get_text(separator=' ', strip=True)
            else:
                return "Текст статьи не найден."

    except Exception as e:
        print(f"  [!] Ошибка при получении текста статьи {url}: {e}")
        return f"Ошибка получения текста: {e}"

def parse_habr_news(start_page: int = 1, end_page: int = 4) -> list[ArticleModel]:
    articles = []
    for page_num in range(start_page, end_page + 1):
        if page_num == 1:
            page_url = 'https://habr.com/ru/articles/'
        else:
            page_url = f'https://habr.com/ru/articles/page{page_num}/'

        print(f"\n--- ОБРАБАТЫВАЮ СТРАНИЦУ №{page_num} ({page_url}) ---")

        try:
            response = requests.get(page_url)
            response.raise_for_status()
            data = BeautifulSoup(response.text, 'html.parser')

            articles_on_page = data.find_all('h2', class_='tm-title tm-title_h2')

            if not articles_on_page:
                print("Достигнут конец ленты или страница пуста.")
                break

            for i, item in enumerate(articles_on_page, 1):
                link = 'https://habr.com' + item.a['href']

                try:
                    text = get_article_content(link)

                    # Создаем объект ArticleModel
                    article_model = ArticleModel(
                        title=item.a.get_text(strip=True),
                        link=link,
                        text=text,
                        source="Habr"
                    )
                    articles.append(article_model)

                    print(f"  [+] Собрано: {article_model.title[:50]}...")
                    time.sleep(1)

                except Exception as e:
                    print(f"  [!] Ошибка при обработке статьи {link}: {e}")

            time.sleep(5)

        except Exception as e:
            print(f"  [!] Ошибка при обработке страницы {page_num}: {e}")
            continue

    return articles