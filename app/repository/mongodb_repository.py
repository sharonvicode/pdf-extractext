"""
Repositorio de documentos para MongoDB.

Implementa la misma interfaz que DocumentoRepository pero
persiste los datos en MongoDB en lugar de SQLite.
"""

from datetime import datetime
from typing import Optional
from bson import ObjectId

from app.core.db import db


class MongoDBDocumentoRepository:
    """
    Repositorio para persistencia de documentos PDF en MongoDB.

    Implementa la misma interfaz que DocumentoRepository para
    permitir intercambio transparente entre SQLite (testing)
    y MongoDB (producción).
    """

    def __init__(self, collection_name: str = "documentos"):
        self._collection = db[collection_name]

    def guardar(self, nombre: str, texto: str, fecha_procesamiento: datetime) -> str:
        """Guarda un documento y retorna su ID generado."""
        documento = {
            "nombre": nombre,
            "texto": texto,
            "fecha_procesamiento": fecha_procesamiento,
        }
        result = self._collection.insert_one(documento)
        return str(result.inserted_id)

    def obtener_por_id(self, documento_id: str) -> Optional[dict]:
        """Recupera un documento por ID o None si no existe."""
        try:
            from bson.objectid import ObjectId

            doc = self._collection.find_one({"_id": ObjectId(documento_id)})
            if doc:
                return {
                    "id": str(doc["_id"]),
                    "nombre": doc["nombre"],
                    "texto": doc["texto"],
                    "fecha_procesamiento": doc["fecha_procesamiento"],
                }
            return None
        except Exception:
            return None

    def obtener_por_nombre(self, nombre: str) -> Optional[dict]:
        """Recupera un documento por nombre exacto."""
        doc = self._collection.find_one({"nombre": nombre})
        if doc:
            return {
                "id": str(doc["_id"]),
                "nombre": doc["nombre"],
                "texto": doc["texto"],
                "fecha_procesamiento": doc["fecha_procesamiento"],
            }
        return None

    def listar_todos(self) -> list[dict]:
        """Lista todos los documentos ordenados por ID."""
        docs = self._collection.find().sort("_id")
        return [
            {
                "id": str(doc["_id"]),
                "nombre": doc["nombre"],
                "texto": doc["texto"],
                "fecha_procesamiento": doc["fecha_procesamiento"],
            }
            for doc in docs
        ]

    def eliminar(self, documento_id: str) -> bool:
        """Elimina un documento. Retorna True si existía, False si no."""
        try:
            from bson.objectid import ObjectId

            result = self._collection.delete_one({"_id": ObjectId(documento_id)})
            return result.deleted_count > 0
        except Exception:
            return False

    def contar(self) -> int:
        """Cuenta el total de documentos almacenados."""
        return self._collection.count_documents({})
