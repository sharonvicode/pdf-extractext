"""
Repositorio de documentos para MongoDB.

Implementa la misma interfaz que DocumentoRepository pero
persiste los datos en MongoDB en lugar de SQLite.
"""

from datetime import datetime
from typing import Optional
from bson import ObjectId

from app.core.db import db
from app.core.logger import logger

DEFAULT_COLLECTION_NAME = "documentos"


class MongoDBDocumentoRepository:
    """
    Repositorio para persistencia de documentos PDF en MongoDB.

    Implementa la misma interfaz que DocumentoRepository para
    permitir intercambio transparente entre SQLite (testing)
    y MongoDB (producción).
    """

    def __init__(self, collection_name: str = DEFAULT_COLLECTION_NAME):
        self._collection = db[collection_name]
        logger.info("Repositorio MongoDB inicializado para la colección %s", collection_name)

    @staticmethod
    def _documento_to_dict(doc) -> dict:
        return {
            "id": str(doc["_id"]),
            "nombre": doc["nombre"],
            "texto": doc["texto"],
            "fecha_procesamiento": doc["fecha_procesamiento"],
        }

    def guardar(self, nombre: str, texto: str, fecha_procesamiento: datetime) -> str:
        """Guarda un documento y retorna su ID generado."""
        logger.info("Intentando guardar documento en MongoDB: %s", nombre)
        try:
            documento = {
                "nombre": nombre,
                "texto": texto,
                "fecha_procesamiento": fecha_procesamiento,
            }
            result = self._collection.insert_one(documento)
            logger.info("Documento guardado en MongoDB con id %s", str(result.inserted_id))
            return str(result.inserted_id)
        except Exception as exc:
            logger.error("Error al guardar documento en MongoDB %s: %s", nombre, str(exc))
            raise

    def obtener_por_id(self, documento_id: str) -> Optional[dict]:
        """Recupera un documento por ID o None si no existe."""
        logger.info("Intentando obtener documento en MongoDB por id %s", documento_id)
        try:
            doc = self._collection.find_one({"_id": ObjectId(documento_id)})
            if doc:
                logger.info("Documento obtenido de MongoDB por id %s", documento_id)
                return self._documento_to_dict(doc)
            logger.info("No se encontró documento en MongoDB para id %s", documento_id)
            return None
        except Exception as exc:
            logger.error("Error al consultar documento en MongoDB por id %s: %s", documento_id, str(exc))
            return None

    def obtener_por_nombre(self, nombre: str) -> Optional[dict]:
        """Recupera un documento por nombre exacto."""
        logger.info("Intentando obtener documento en MongoDB por nombre %s", nombre)
        try:
            doc = self._collection.find_one({"nombre": nombre})
            if doc:
                logger.info("Documento obtenido de MongoDB por nombre %s", nombre)
                return self._documento_to_dict(doc)
            logger.info("No se encontró documento en MongoDB por nombre %s", nombre)
            return None
        except Exception as exc:
            logger.error("Error al consultar documento en MongoDB por nombre %s: %s", nombre, str(exc))
            return None

    def listar_todos(self) -> list[dict]:
        """Lista todos los documentos ordenados por ID."""
        logger.info("Intentando listar todos los documentos en MongoDB")
        try:
            docs = self._collection.find().sort("_id")
            resultado = [self._documento_to_dict(doc) for doc in docs]
            logger.info("Listado de documentos en MongoDB completado: %d documentos", len(resultado))
            return resultado
        except Exception as exc:
            logger.error("Error al listar documentos en MongoDB: %s", str(exc))
            raise

    def eliminar(self, documento_id: str) -> bool:
        """Elimina un documento. Retorna True si existía, False si no."""
        logger.info("Intentando eliminar documento en MongoDB por id %s", documento_id)
        try:
            result = self._collection.delete_one({"_id": ObjectId(documento_id)})
            eliminado = result.deleted_count > 0
            logger.info("Eliminación en MongoDB para id %s completada: eliminado=%s", documento_id, eliminado)
            return eliminado
        except Exception as exc:
            logger.error("Error al eliminar documento en MongoDB por id %s: %s", documento_id, str(exc))
            raise

    def contar(self) -> int:
        """Cuenta el total de documentos almacenados."""
        logger.info("Intentando contar documentos en MongoDB")
        try:
            total = self._collection.count_documents({})
            logger.info("Conteo de documentos en MongoDB completado: %d documentos", total)
            return total
        except Exception as exc:
            logger.error("Error al contar documentos en MongoDB: %s", str(exc))
            raise
