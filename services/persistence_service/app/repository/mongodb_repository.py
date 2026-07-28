from datetime import datetime, UTC
from typing import Optional
from bson import ObjectId

from app.core.db import db
from app.core.logger import logger

DEFAULT_COLLECTION_NAME = "documents"


class DocumentRepository:
    def __init__(self, collection_name: str = DEFAULT_COLLECTION_NAME):
        self._collection = db[collection_name]
        logger.info("Repositorio MongoDB inicializado para la colección %s", collection_name)

    @staticmethod
    def _document_to_dict(doc) -> dict:
        return {
            "id": str(doc["_id"]),
            "filename": doc["filename"],
            "content": doc["content"],
            "metadata": doc.get("metadata", {}),
            "created_at": doc["created_at"],
        }

    def save(self, filename: str, content: str, metadata: dict) -> str:
        logger.info("Guardando documento en MongoDB: %s", filename)
        try:
            document = {
                "filename": filename,
                "content": content,
                "metadata": metadata,
                "created_at": datetime.now(UTC),
            }
            result = self._collection.insert_one(document)
            logger.info("Documento guardado con id %s", str(result.inserted_id))
            return str(result.inserted_id)
        except Exception as exc:
            logger.error("Error al guardar documento %s: %s", filename, str(exc))
            raise

    def get_by_id(self, document_id: str) -> Optional[dict]:
        try:
            doc = self._collection.find_one({"_id": ObjectId(document_id)})
            if doc:
                return self._document_to_dict(doc)
            return None
        except Exception as exc:
            logger.error("Error al consultar documento por id %s: %s", document_id, str(exc))
            raise

    def list_all(self) -> list[dict]:
        try:
            docs = self._collection.find().sort("_id")
            return [self._document_to_dict(doc) for doc in docs]
        except Exception as exc:
            logger.error("Error al listar documentos: %s", str(exc))
            raise

    def delete(self, document_id: str) -> bool:
        try:
            result = self._collection.delete_one({"_id": ObjectId(document_id)})
            return result.deleted_count > 0
        except Exception as exc:
            logger.error("Error al eliminar documento %s: %s", document_id, str(exc))
            raise

    def count(self) -> int:
        try:
            return self._collection.count_documents({})
        except Exception as exc:
            logger.error("Error al contar documentos: %s", str(exc))
            raise