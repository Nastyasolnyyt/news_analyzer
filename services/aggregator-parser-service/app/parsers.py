import feedparser
from .models import Article
from datetime import datetime

def parse_rss(url: str) -> list[Article]:
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries:
        # Извлекаем данные аккуратно
        title_val = entry.get("title", "")
        desc_val = entry.get("summary", "")
        
        article = Article(
            title=title_val,
            description=desc_val,
            text=desc_val,  # Записываем описание в text, чтобы колонка не была пустой
            link=entry.get("link", ""),
            pub_date=datetime(*entry.published_parsed[:6]) if entry.get("published_parsed") else None,
            source=url
        )
        articles.append(article)
    return articles