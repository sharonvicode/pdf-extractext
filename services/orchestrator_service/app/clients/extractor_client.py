import httpx
from pathlib import Path

from app.core.config import EXTRACTOR_URL
from app.core.logger import logger


class ExtractorClient:
    def __init__(self, base_url: str = EXTRACTOR_URL):
        self.base_url = base_url

    def extract(self, file_path: str, filename: str) -> str:
        logger.info("Enviando archivo %s a extractor-service", filename)

        with open(file_path, "rb") as f:
            files = {"file": (filename, f, "application/pdf")}
            response = httpx.post(
                f"{self.base_url}/extract",
                files=files,
                timeout=120,
            )

        response.raise_for_status()
        texto = response.json()["text"]
        logger.info("Texto recibido de extractor-service (%d caracteres)", len(texto))
        return texto