import logging
import os
DB_URL = os.getenv("DATABASE_URL")
DEFAULT_DAYS = 30
Z_SCORE_THRESHOLD = 2.0

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AnomalyService")