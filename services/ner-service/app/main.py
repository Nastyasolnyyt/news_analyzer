# services/ner-service/app/main.py
import asyncio
import logging
from .kafka_worker import consume_and_extract

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    logger.info("🚀 Starting NER Service...")
    try:
        await consume_and_extract()
    except Exception as e:
        logger.error(f"❌ Critical error: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())