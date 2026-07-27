import os

from dotenv import load_dotenv

load_dotenv()

EXTRACTOR_HOST = os.getenv("EXTRACTOR_HOST", "0.0.0.0")
EXTRACTOR_PORT = int(os.getenv("EXTRACTOR_PORT", "8002"))
