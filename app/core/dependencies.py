"""
Composition root: arma las implementaciones concretas que usan las rutas.

Cada función puede sobrescribirse en tests mediante app.dependency_overrides.
"""

from app.core.mongo import database
from app.repository.interface import DocumentoRepositoryInterface
from app.repository.mongodb_repository import MongoDBDocumentoRepository
from app.services.pdf_service import ExtractorTexto
from app.utils.pdf_extractor import extraer_texto

DOCUMENTOS_COLLECTION = "documentos"


def get_documento_repository() -> DocumentoRepositoryInterface:
    """Repositorio de documentos de producción (MongoDB)."""
    return MongoDBDocumentoRepository(database[DOCUMENTOS_COLLECTION])


def get_extractor_texto() -> ExtractorTexto:
    """Implementación concreta del puerto de extracción (pypdf)."""
    return extraer_texto
