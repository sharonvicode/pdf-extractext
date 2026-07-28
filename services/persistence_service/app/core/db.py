from pymongo import MongoClient

from app.core.config import MONGO_URL, DATABASE_NAME
from app.core.logger import logger

client = MongoClient(MONGO_URL)
db = client[DATABASE_NAME]

logger.info("Conectado a MongoDB: %s, base de datos: %s", MONGO_URL, DATABASE_NAME)