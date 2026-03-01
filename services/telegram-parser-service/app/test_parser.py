import asyncio
from parsers import parse_telegram_channels

async def test():
    print("🔍 Parsing started...")
    articles = await parse_telegram_channels()
    print(f"✅ Found {len(articles)} articles")
    for i, article in enumerate(articles[:5], 1):  # Показываем первые 5
        print(f"\n[{i}] {article.title}")
        print(f"Link: {article.link}")
        print(f"Source: {article.source}")
        print(f"Text preview: {article.text[:100]}...")

if __name__ == "__main__":
    asyncio.run(test())