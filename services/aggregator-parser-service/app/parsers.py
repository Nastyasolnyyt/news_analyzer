import feedparser
from .models import Article
from datetime import datetime

def parse_rss(url: str) -> list[Article]:
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries:
        pub_date = entry.get("published_parsed")
        # Преобразуем struct_time в datetime, если возможно
        pub_date = datetime(*pub_date[:6]) if pub_date else None
        article = Article(
            title=entry.get("title", ""),
            description=entry.get("summary", ""),
            link=entry.get("link", ""),
            pub_date=pub_date,  
            source=url
        )
        articles.append(article)
    return articles
    