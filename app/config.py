import logging

DB_URL = "postgresql://news_db_r386_user:d3RdNiRIt1B1iWzamwc3Tblto5FxDpJz@dpg-d68bevrh46gs73fc7ln0-a.oregon-postgres.render.com/news_db_r386?sslmode=require"
DEFAULT_DAYS = 30
Z_SCORE_THRESHOLD = 2.0

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AnomalyService")