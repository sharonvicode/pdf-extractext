"""
Rutas para extracción de texto desde archivos PDF.

Este módulo expone endpoints HTTP para recibir archivos PDF
y delegar la extracción de texto al servicio correspondiente.
"""

import os
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.core.logger import logger

from app.services.pdf_service import (
    procesar_pdf,
    PDFEmptyError,
    PDFExtractionError,
)
from app.repository.documento_repository import DocumentoRepository
from app.schemas import ExtraccionResponse
from app.utils.validators import FileValidator

DEFAULT_PDF_SUFFIX = ".pdf"

router = APIRouter()


def get_documento_repository() -> DocumentoRepository:
    """
    Proporciona el repositorio de documentos.

    Esta función puede ser sobrescrita en tests mediante dependency_overrides.
    En producción utiliza MongoDB a través del repositorio real.
    """
    return DocumentoRepository()


@contextmanager
def _guardar_archivo_temporal(file: UploadFile) -> Generator[Path, None, None]:
    """
    Guarda el archivo subido en disco de forma eficiente (por chunks)
    y garantiza su eliminación al finalizar.

    Yields:
        Ruta absoluta del archivo temporal.
    """
    suffix = Path(file.filename).suffix if file.filename else DEFAULT_PDF_SUFFIX

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        temp_path = tmp.name
    logger.info("Archivo temporal creado para procesamiento: %s", temp_path)

    try:
        yield Path(temp_path)
    finally:
        if os.path.exists(temp_path):
            logger.info("Eliminando archivo temporal: %s", temp_path)
            os.remove(temp_path)


def _mapear_excepcion_servicio(exc: Exception) -> HTTPException:
    """
    Mapea excepciones del dominio a respuestas HTTP apropiadas.

    Args:
        exc: Excepción capturada durante el procesamiento.

    Returns:
        HTTPException con el status code y detalle correspondiente.
    """
    if isinstance(exc, PDFEmptyError):
        return HTTPException(status_code=422, detail=str(exc))

    if isinstance(exc, PDFExtractionError):
        return HTTPException(status_code=400, detail=str(exc))

    return HTTPException(
        status_code=500,
        detail=f"Error interno al procesar el PDF: {exc}",
    )


@router.post("/extraer", response_model=ExtraccionResponse)
def extraer(
    file: UploadFile = File(...),
    repositorio: DocumentoRepository = Depends(get_documento_repository),
):
    """
    Recibe un archivo PDF y extrae su texto.

    Args:
        file: Archivo PDF enviado via form-data.
        repositorio: Repositorio de documentos inyectado.

    Returns:
        JSON con el texto extraído o mensaje de error.
    """
    FileValidator.validate_pdf(file)

    logger.info("Recibiendo petición HTTP POST /extraer para el archivo %s", file.filename),

    try:
        FileValidator.validate_pdf(file)
    except HTTPException:
        logger.warning("La validación del archivo %s falló", getattr(file, "filename", "sin nombre"))
        raise

    try:
        with _guardar_archivo_temporal(file) as temp_path:
            logger.info("Procesando PDF temporal: %s", temp_path)
            texto = procesar_pdf(temp_path, file.filename, repositorio)
    except Exception as exc:
        logger.exception("Error al procesar la petición /extraer para %s", file.filename)
        raise _mapear_excepcion_servicio(exc)

    logger.info("Procesamiento de /extraer completado exitosamente para %s", file.filename)

    return {
        "exito": True,
        "texto": texto,
        "nombre_archivo": file.filename,
    }


# Incluir routers adicionales de documentos
from app.routes.documentos_get import router as documentos_get_router
from app.routes.documentos_delete import router as documentos_delete_router

router.include_router(documentos_get_router)
router.include_router(documentos_delete_router)
