from telethon import TelegramClient
from .models import Article as ArticleModel
import os

api_id = int(os.getenv("TG_API_ID"))  
api_hash = os.getenv("TG_API_HASH")   
phone = os.getenv("TG_PHONE")        
session = './app/mfin'

channels = ['rbc_news', 'mash']

async def parse_telegram_channels() -> list[ArticleModel]:
    client = TelegramClient(session, api_id, api_hash)

    await client.connect()

    if not await client.is_user_authorized():
        raise Exception("Session is invalid. Re-authentication required.")

    print("Connected to Telegram!")

    articles = []

    for channel_username in channels:
        print(f"Downloading news from {channel_username}")
        try:
            channel_entity = await client.get_entity(channel_username)
            async for post in client.iter_messages(channel_entity, limit=100):
                if post.text:
                    # Формируем ссылку
                    link = f"https://t.me/{channel_username}/{post.id}"
                    # Создаем объект ArticleModel
                    article_model = ArticleModel(
                        title=" ",
                        link=link,
                        text=post.text,
                        pub_date=post.date.isoformat(), 
                        source=f"Telegram: {channel_username}"
                    )
                    articles.append(article_model)

        except Exception as e:
            print(f"Error reading channel {channel_username}: {e}")
            continue  # Переходим к следующему каналу

    await client.disconnect()
    return articles