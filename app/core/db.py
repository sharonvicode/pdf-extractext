from pymongo import MongoClient

from app.core.config import DATABASE_NAME, MONGO_URL
from app.core.logger import logger

client = MongoClient(MONGO_URL)
db = client[DATABASE_NAME]

logger.info("MONGO_URL: %s", MONGO_URL)
logger.info("DATABASE_NAME: %s", DATABASE_NAME)