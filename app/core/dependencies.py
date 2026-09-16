from app.repository.interface import DocumentoRepositoryInterface
from app.repository.mongodb_repository import MongoDBDocumentoRepository


def get_documento_repository() -> DocumentoRepositoryInterface:
    """
    Proporciona el repositorio de documentos.

    Esta función puede ser sobrescrita en tests mediante dependency_overrides.
    En producción utiliza MongoDB a través de MongoDBDocumentoRepository.
    """
    return MongoDBDocumentoRepository()
