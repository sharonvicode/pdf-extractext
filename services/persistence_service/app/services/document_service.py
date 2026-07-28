from app.repository.mongodb_repository import DocumentRepository
from app.core.logger import logger


class DocumentService:
    def __init__(self, repository: DocumentRepository):
        self._repository = repository

    def save_document(self, filename: str, content: str, metadata: dict) -> str:
        logger.info("Servicio: guardando documento %s", filename)
        return self._repository.save(filename=filename, content=content, metadata=metadata)

    def get_document(self, document_id: str) -> dict | None:
        return self._repository.get_by_id(document_id)

    def list_documents(self) -> list[dict]:
        return self._repository.list_all()

    def delete_document(self, document_id: str) -> bool:
        return self._repository.delete(document_id)