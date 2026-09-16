"""
Rutas DELETE para documentos.

Expone endpoints para eliminar documentos por ID,
utilizando el repositorio inyectado mediante Depends.
"""

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_documento_repository
from app.core.logger import logger
from app.repository.interface import DocumentoRepositoryInterface
from app.utils.error_handling import manejar_error_interno

router = APIRouter()


@router.delete("/documentos/{documento_id}", status_code=204)
@manejar_error_interno("Error interno al eliminar el documento")
def eliminar_documento(
    documento_id: str,
    repositorio: DocumentoRepositoryInterface = Depends(get_documento_repository),
):
    """Elimina un documento por su ID."""
    logger.info("Recibiendo petición HTTP DELETE /documentos/{documento_id} con id %s", documento_id)
    eliminado = repositorio.eliminar(documento_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    logger.info("Documento eliminado exitosamente con id %s", documento_id)
