from app.repository.documento_repository import DocumentoRepository


def get_documento_repository() -> DocumentoRepository:
    """
    Proporciona el repositorio de documentos.

    Esta función puede ser sobrescrita en tests mediante dependency_overrides.
    En producción utiliza MongoDB a través del repositorio real.
    """
    return DocumentoRepository()