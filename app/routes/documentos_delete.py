"""
Rutas DELETE para documentos.

Expone endpoints para eliminar documentos por ID,
utilizando el repositorio inyectado mediante Depends.
"""

from fastapi import APIRouter, Depends, HTTPException

from app.routes.extraer import get_documento_repository
from app.repository.documento_repository import DocumentoRepository

router = APIRouter()


@router.delete("/documentos/{documento_id}", status_code=204)
def eliminar_documento(
    documento_id: str,
    repositorio: DocumentoRepository = Depends(get_documento_repository),
):
    """Elimina un documento por su ID."""
    eliminado = repositorio.eliminar(documento_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
