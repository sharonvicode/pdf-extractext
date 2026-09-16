"""
Rutas GET para documentos.

Expone endpoints para listar y obtener documentos por ID,
utilizando el repositorio inyectado mediante Depends.
"""

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_documento_repository
from app.core.logger import logger
from app.repository.interface import DocumentoRepositoryInterface
from app.utils.error_handling import manejar_error_interno


router = APIRouter()


@router.get("/documentos")
@manejar_error_interno("Error interno al obtener los documentos")
def listar_documentos(
    repositorio: DocumentoRepositoryInterface = Depends(get_documento_repository),
):
    """Retorna la lista de todos los documentos."""

    logger.info("Recibiendo petición HTTP GET /documentos")

    documentos = repositorio.listar_todos()

    logger.info("Listado de documentos completado exitosamente")

    return documentos


@router.get("/documentos/{documento_id}")
@manejar_error_interno("Error interno al obtener el documento")
def obtener_documento(
    documento_id: str,
    repositorio: DocumentoRepositoryInterface = Depends(get_documento_repository),
):
    """Retorna un documento por su ID."""

    logger.info(
        "Recibiendo petición HTTP GET /documentos/%s",
        documento_id,
    )

    documento = repositorio.obtener_por_id(documento_id)

    if documento is None:
        raise HTTPException(
            status_code=404,
            detail="Documento no encontrado",
        )

    logger.info(
        "Documento obtenido correctamente con id %s",
        documento_id,
    )

    return documento