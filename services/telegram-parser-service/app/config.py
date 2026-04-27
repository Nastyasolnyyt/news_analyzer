import os

KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "raw_articles")
TG_API_ID = int(os.getenv("TG_API_ID")) 
TG_API_HASH = os.getenv("TG_API_HASH")   
TG_PHONE = os.getenv("TG_PHONE")        
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
PARSE_INTERVAL = int(os.getenv("PARSE_INTERVAL", 1800))