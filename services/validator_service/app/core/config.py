import os

from dotenv import load_dotenv

load_dotenv()

VALIDATOR_HOST = os.getenv("VALIDATOR_HOST", "0.0.0.0")
VALIDATOR_PORT = int(os.getenv("VALIDATOR_PORT", "8001"))
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))
