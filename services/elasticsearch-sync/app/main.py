from dotenv import load_dotenv
import time
import logging

from config import SYNC_INTERVAL_SECONDS
from sync import SyncService

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  
    ]
)

logger = logging.getLogger(__name__)

def main():
    try:
        sync_service = SyncService("articles")
        while True:
            try:
                logger.info(f'Sync is starting')
                sync_service.sync_articles()
                
                logger.info(f'Sync completed, sleeping for {SYNC_INTERVAL_SECONDS} seconds')
                time.sleep(SYNC_INTERVAL_SECONDS)
                
            except KeyboardInterrupt:
                logger.info("Received stop signal, shutting down gracefully...")
                break
            except Exception as e:
                logger.error(f'Sync error: {e}')
                logger.info(f'Waiting {SYNC_INTERVAL_SECONDS} seconds before retry...')
                time.sleep(SYNC_INTERVAL_SECONDS)
    except Exception as e:
        logger.error(f"Failed to initialize sync service: {e}")
        raise

if __name__ == '__main__':
    main()