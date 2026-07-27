from app.repository.documento_repository import MongoDBDocumentoRepository


def get_documento_repository() -> MongoDBDocumentoRepository:
    """
    Proporciona el repositorio de documentos.

    Esta función puede ser sobrescrita en tests mediante dependency_overrides.
    En producción utiliza MongoDB a través de MongoDBDocumentoRepository.
    """
    return MongoDBDocumentoRepository()
