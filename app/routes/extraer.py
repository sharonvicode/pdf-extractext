"""
Rutas para extracción de texto desde archivos PDF.

Este módulo expone endpoints HTTP para recibir archivos PDF
y delegar la extracción de texto al servicio correspondiente.
"""

import os
import shutil
import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.dependencies import get_documento_repository, get_extractor_texto
from app.core.logger import logger
from app.repository.interface import DocumentoRepositoryInterface
from app.schemas import ExtraccionResponse
from app.services.documento_service import guardar_documento
from app.services.pdf_service import (
    ExtractorTexto,
    PDFEmptyError,
    PDFExtractionError,
)
from app.services.pdf_service import (
    procesar_pdf as procesar_pdf_service,
)
from app.utils.validators import ArchivoInvalidoError, FileValidator

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
    repositorio: DocumentoRepositoryInterface,
    extractor: ExtractorTexto,
) -> str:
    """
    Lógica interna del endpoint /extraer.

    Valida el archivo, lo guarda temporalmente, delega la extracción al
    servicio de PDF y luego persiste el resultado mediante el repositorio.
    Esta función es quien orquesta ambos pasos: ninguno de los dos
    servicios conoce al otro.
    """

    FileValidator.validate_pdf(file.filename, file.content_type, file.file)

    with _guardar_archivo_temporal(file) as temp_path:
        logger.info(
            "Procesando PDF temporal: %s",
            temp_path,
        )

        texto = procesar_pdf_service(temp_path, file.filename, extractor)
        guardar_documento(file.filename, texto, repositorio)
        return texto


def _mapear_excepcion_servicio(exc: Exception) -> HTTPException:
    """
    Mapea errores del servicio a respuestas HTTP.
    """

    if isinstance(exc, ArchivoInvalidoError):
        return HTTPException(
            status_code=400,
            detail=str(exc),
        )

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
    repositorio: DocumentoRepositoryInterface = Depends(get_documento_repository),
    extractor: ExtractorTexto = Depends(get_extractor_texto),
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
            extractor,
        )

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