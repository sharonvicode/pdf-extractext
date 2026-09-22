"""
Servicio de persistencia de documentos procesados.

Coordina el guardado de un documento (nombre, texto y fecha de
procesamiento) a través del repositorio inyectado. No sabe de dónde
viene el texto ni cómo se extrajo: solo persiste el resultado.
"""

from datetime import UTC, datetime

from app.core.logger import logger
from app.repository.interface import DocumentoRepositoryInterface


def guardar_documento(
    nombre_archivo: str, texto: str, repositorio: DocumentoRepositoryInterface
) -> str:
    """
    Persiste un documento en el repositorio.

    Asigna la fecha y hora actual en UTC como fecha de procesamiento.

    Args:
        nombre_archivo: Nombre original del archivo.
        texto: Texto extraído del documento.
        repositorio: Implementación del repositorio para persistencia.

    Returns:
        str: El ID del documento generado.
    """
    logger.info("Guardando documento %s en el repositorio", nombre_archivo)
    resultado = repositorio.guardar(
        nombre=nombre_archivo,
        texto=texto,
        fecha_procesamiento=datetime.now(UTC),
    )
    logger.info("Documento %s guardado correctamente", nombre_archivo)
    return resultado
