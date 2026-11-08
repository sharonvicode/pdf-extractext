"""
Conexión a MongoDB.

Crea el cliente a partir de la configuración centralizada (app.core.config)
y expone la base de datos de la aplicación como `database`.
"""

from pymongo import MongoClient

from app.core.config import DATABASE_NAME, MONGO_URL
from app.core.logger import logger

client = MongoClient(MONGO_URL)
database = client[DATABASE_NAME]

logger.info("Conexión MongoDB configurada: %s / base %s", MONGO_URL, DATABASE_NAME)
