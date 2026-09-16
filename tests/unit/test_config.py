"""
Test de regresión: la conexión a Mongo debe usar la configuración
centralizada (DATABASE_NAME) y no un nombre de base hardcodeado.
"""

from app.core.config import DATABASE_NAME
from app.core.db import db


def test_db_usa_database_name_de_config():
    assert db.name == DATABASE_NAME
