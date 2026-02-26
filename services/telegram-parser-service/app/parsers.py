from telethon import TelegramClient
from .models import Article as ArticleModel
import os

# --- Настройки ---
api_id = int(os.getenv("TG_API_ID", "34045959"))
api_hash = os.getenv("TG_API_HASH", "b126e73a8a872a5d03704d8f4f777078")
phone = os.getenv("TG_PHONE", "+79196510789")
session = 'mfin'

# --- Общие настройки ---
channels = ['rbc_news', 'mash']

async def parse_telegram_channels() -> list[ArticleModel]:
    client = TelegramClient(session, api_id, api_hash)
    await client.start()  # <-- await

    print("Connected to Telegram!")

    articles = []

    for channel_username in channels:
        print(f"Downloading news from {channel_username}")
        try:
            # Получаем объект канала
            channel_entity = await client.get_entity(channel_username)  # <-- await
            # Используем асинхронный итератор
            async for post in client.iter_messages(channel_entity, limit=100):  # <-- async for
                if post.text:
                    # Формируем ссылку (убраны лишние пробелы)
                    link = f"https://t.me/{channel_username}/{post.id}"
                    # Создаем объект ArticleModel
                    article_model = ArticleModel(
                        title="",
                        link=link,
                        text=post.text,
                        pub_date=post.date,
                        source=f"Telegram: {channel_username}"
                    )
                    articles.append(article_model)

        except Exception as e:
            print(f"Error reading channel {channel_username}: {e}")
            continue  # Переходим к следующему каналу

    await client.disconnect()  # <-- await
    return articles