from pymongo import MongoClient
import os
from dotenv import load_dotenv

from app.core.logger import logger

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

MONGO_DATABASE = os.getenv( "MONGO_DATABASE", "mi_base")


client = MongoClient(MONGO_URL)
db = client["mi_base"]

logger.info("MONGO_URL: %s", MONGO_URL)