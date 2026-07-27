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
    procesar_pdf as procesar_pdf_service,
    PDFEmptyError,
    PDFExtractionError,
)

from app.core.dependencies import get_documento_repository
from app.schemas import ExtraccionResponse
from app.utils.validators import FileValidator


DEFAULT_PDF_SUFFIX = ".pdf"

router = APIRouter()


@contextmanager
def _guardar_archivo_temporal(file: UploadFile) -> Generator[Path, None, None]:
    """
    Guarda el archivo subido temporalmente y lo elimina al finalizar.
    """

    suffix = Path(file.filename).suffix if file.filename else DEFAULT_PDF_SUFFIX

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        temp_path = tmp.name

    logger.info(
        "Archivo temporal creado para procesamiento: %s",
        temp_path,
    )

    try:
        yield Path(temp_path)

    finally:
        if os.path.exists(temp_path):
            logger.info(
                "Eliminando archivo temporal: %s",
                temp_path,
            )
            os.remove(temp_path)


def procesar_archivo_pdf(
    file: UploadFile,
    repositorio,
) -> str:
    """
    Lógica interna del endpoint /extraer.

    Valida el archivo, lo guarda temporalmente
    y delega el procesamiento al servicio PDF.
    """

    FileValidator.validate_pdf(file)

    with _guardar_archivo_temporal(file) as temp_path:
        logger.info(
            "Procesando PDF temporal: %s",
            temp_path,
        )

        return procesar_pdf_service(
            temp_path,
            file.filename,
            repositorio,
        )


def _mapear_excepcion_servicio(exc: Exception) -> HTTPException:
    """
    Mapea errores del servicio a respuestas HTTP.
    """

    if isinstance(exc, PDFEmptyError):
        return HTTPException(
            status_code=422,
            detail=str(exc),
        )

    if isinstance(exc, PDFExtractionError):
        return HTTPException(
            status_code=400,
            detail=str(exc),
        )

    return HTTPException(
        status_code=500,
        detail=f"Error interno al procesar el PDF: {exc}",
    )


@router.post(
    "/extraer",
    response_model=ExtraccionResponse,
)
def extraer(
    file: UploadFile = File(...),
    repositorio=Depends(get_documento_repository),
):
    """
    Recibe un archivo PDF y extrae su texto.
    """

    logger.info(
        "Recibiendo petición HTTP POST /extraer para el archivo %s",
        file.filename,
    )

    try:
        texto = procesar_archivo_pdf(
            file,
            repositorio,
        )

    except HTTPException as exc:
        logger.error(
            "Error de validación en /extraer para %s: %s",
            getattr(file, "filename", "sin nombre"),
            str(exc.detail),
        )
        raise

    except Exception as exc:
        logger.error(
            "Error al procesar /extraer para %s: %s",
            getattr(file, "filename", "sin nombre"),
            str(exc),
        )
        raise _mapear_excepcion_servicio(exc)

    logger.info(
        "Procesamiento de /extraer completado exitosamente para %s",
        file.filename,
    )

    return {
        "exito": True,
        "texto": texto,
        "nombre_archivo": file.filename,
    }