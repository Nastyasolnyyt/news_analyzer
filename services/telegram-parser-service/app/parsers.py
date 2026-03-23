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
                # Внутри цикла async for post in client.iter_messages...
                if post.text:
                    # Берем первые 80 символов первой строки как заголовок
                    first_line = post.text.split('\n')[0]
                    title = (first_line[:77] + '...') if len(first_line) > 80 else first_line
                    
                    article_model = ArticleModel(
                        title=title, # Вместо " "
                        link=f"https://t.me/{channel_username}/{post.id}",
                        text=post.text,
                        pub_date=post.date, 
                        source=f"Telegram: {channel_username}"
                    )

        except Exception as e:
            print(f"Error reading channel {channel_username}: {e}")
            continue  # Переходим к следующему каналу

    await client.disconnect()
    return articles