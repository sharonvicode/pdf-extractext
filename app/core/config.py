"""
Configuración de la aplicación.

Carga variables de entorno y expone configuración centralizada.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# CONFIGURACIÓN GLOBAL (KISS + estándar FastAPI)
# ============================================================================

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

DATABASE_NAME = os.getenv("DATABASE_NAME", "pdf_extractext")

MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))

MIN_TEXT_LENGTH = int(os.getenv("MIN_TEXT_LENGTH", "20"))

HOST = os.getenv("HOST", "0.0.0.0")

PORT = int(os.getenv("PORT", "8000"))