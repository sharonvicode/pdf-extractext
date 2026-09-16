from pymongo import MongoClient

from app.core.config import MONGO_URL, DATABASE_NAME
from app.core.logger import logger

client = MongoClient(MONGO_URL)
db = client[DATABASE_NAME]

logger.info("MONGO_URL: %s", MONGO_URL)
logger.info("DATABASE_NAME: %s", DATABASE_NAME)