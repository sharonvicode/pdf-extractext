"""
Rutas GET para documentos.

Expone endpoints para listar y obtener documentos por ID,
utilizando el repositorio inyectado mediante Depends.
"""

from fastapi import APIRouter, Depends, HTTPException

from app.routes.extraer import get_documento_repository
from app.repository.documento_repository import DocumentoRepository

router = APIRouter()


@router.get("/documentos")
def listar_documentos(
    repositorio: DocumentoRepository = Depends(get_documento_repository),
):
    """Retorna la lista de todos los documentos."""
    try:
        return repositorio.listar_todos()
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno al obtener los documentos")


@router.get("/documentos/{documento_id}")
def obtener_documento(
    documento_id: str,
    repositorio: DocumentoRepository = Depends(get_documento_repository),
):
    """Retorna un documento por su ID."""
    documento = repositorio.obtener_por_id(documento_id)
    if documento is None:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return documento
