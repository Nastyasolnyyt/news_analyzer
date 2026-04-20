import logging

DB_URL = "postgresql://data_i2d0_user:D49vf1tZSSLWNHmmTxUUVl9Ui6hofFHK@dpg-d7063a7diees73devjt0-a.oregon-postgres.render.com/data_i2d0"
DEFAULT_DAYS = 30
Z_SCORE_THRESHOLD = 2.0

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AnomalyService")