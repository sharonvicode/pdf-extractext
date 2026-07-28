import os
from dotenv import load_dotenv

load_dotenv()

MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))

EXTRACTOR_URL = os.getenv("EXTRACTOR_URL", "http://localhost:8002")
VALIDATOR_URL = os.getenv("VALIDATOR_URL", "http://localhost:8001")
PERSISTENCE_URL = os.getenv("PERSISTENCE_URL", "http://localhost:8003")

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8004"))