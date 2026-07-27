"""
Rutas GET para documentos.

Expone endpoints para listar y obtener documentos por ID,
utilizando el repositorio inyectado mediante Depends.
"""

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_documento_repository
from app.core.logger import logger


router = APIRouter()


@router.get("/documentos")
def listar_documentos(
    repositorio=Depends(get_documento_repository),
):
    """Retorna la lista de todos los documentos."""

    logger.info("Recibiendo petición HTTP GET /documentos")

    try:
        documentos = repositorio.listar_todos()

        logger.info(
            "Listado de documentos completado exitosamente"
        )

        return documentos

    except Exception as exc:
        logger.error(
            "Error al obtener documentos: %s",
            str(exc),
        )

        raise HTTPException(
            status_code=500,
            detail="Error interno al obtener los documentos",
        )


@router.get("/documentos/{documento_id}")
def obtener_documento(
    documento_id: str,
    repositorio=Depends(get_documento_repository),
):
    """Retorna un documento por su ID."""

    logger.info(
        "Recibiendo petición HTTP GET /documentos/%s",
        documento_id,
    )

    try:
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

    except HTTPException:
        raise

    except Exception as exc:
        logger.error(
            "Error al obtener documento con id %s: %s",
            documento_id,
            str(exc),
        )

        raise HTTPException(
            status_code=500,
            detail="Error interno al obtener el documento",
        )