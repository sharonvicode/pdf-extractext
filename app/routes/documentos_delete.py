"""
Rutas DELETE para documentos.

Expone endpoints para eliminar documentos por ID,
utilizando el repositorio inyectado mediante Depends.
"""

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_documento_repository
from app.core.logger import logger
from app.repository.documento_repository import DocumentoRepository

router = APIRouter()


@router.delete("/documentos/{documento_id}", status_code=204)
def eliminar_documento(
    documento_id: str,
    repositorio: DocumentoRepository = Depends(get_documento_repository),
):
    """Elimina un documento por su ID."""
    logger.info("Recibiendo petición HTTP DELETE /documentos/{documento_id} con id %s", documento_id)
    try:
        eliminado = repositorio.eliminar(documento_id)
        if not eliminado:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        logger.info("Procesamiento de /documentos/{documento_id} completado exitosamente para id %s", documento_id)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error al procesar la petición DELETE /documentos/{documento_id} para id %s: %s", documento_id, str(exc))
        raise HTTPException(status_code=500, detail="Error interno al eliminar el documento")
