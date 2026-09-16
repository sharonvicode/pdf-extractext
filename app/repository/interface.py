"""
Contrato común para los repositorios de documentos PDF.

Toda implementación de persistencia (SQLite para tests, MongoDB para
producción) debe cumplir esta interfaz para poder intercambiarse de
forma transparente vía inyección de dependencias.
"""

from abc import ABC, abstractmethod
from datetime import datetime


class DocumentoRepositoryInterface(ABC):
    """Contrato que deben cumplir las implementaciones de persistencia de documentos."""

    @abstractmethod
    def guardar(self, nombre: str, texto: str, fecha_procesamiento: datetime) -> str:
        """Guarda un documento y retorna su ID generado."""
        ...

    @abstractmethod
    def obtener_por_id(self, documento_id: str) -> dict | None:
        """Recupera un documento por ID o None si no existe."""
        ...

    @abstractmethod
    def obtener_por_nombre(self, nombre: str) -> dict | None:
        """Recupera un documento por nombre exacto."""
        ...

    @abstractmethod
    def listar_todos(self) -> list[dict]:
        """Lista todos los documentos."""
        ...

    @abstractmethod
    def eliminar(self, documento_id: str) -> bool:
        """Elimina un documento. Retorna True si existía, False si no."""
        ...

    @abstractmethod
    def contar(self) -> int:
        """Cuenta el total de documentos almacenados."""
        ...
