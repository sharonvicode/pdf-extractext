import httpx

from app.core.config import PERSISTENCE_URL
from app.core.logger import logger


class PersistenceClient:
    def __init__(self, base_url: str = PERSISTENCE_URL):
        self.base_url = base_url

    def save(self, filename: str, content: str, metadata: dict) -> str:
        logger.info("Enviando documento %s a persistence-service", filename)

        response = httpx.post(
            f"{self.base_url}/documents",
            json={
                "filename": filename,
                "content": content,
                "metadata": metadata,
            },
            timeout=30,
        )

        response.raise_for_status()
        document_id = response.json()["document_id"]
        logger.info("Documento persistido con id %s", document_id)
        return document_id