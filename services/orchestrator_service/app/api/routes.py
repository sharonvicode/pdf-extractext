import os
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.core.logger import logger
from app.schemas import ExtraccionResponse
from app.utils.validators import FileValidator
from app.services.orchestrator_service import (
    OrchestratorService,
    PDFEmptyError,
    PDFExtractionError,
)
from app.clients.extractor_client import ExtractorClient
from app.clients.validator_client import ValidatorClient
from app.clients.persistence_client import PersistenceClient


DEFAULT_PDF_SUFFIX = ".pdf"

router = APIRouter()

_orchestrator = OrchestratorService(
    extractor=ExtractorClient(),
    validator=ValidatorClient(),
    persistence=PersistenceClient(),
)


@contextmanager
def _guardar_archivo_temporal(file: UploadFile) -> Generator[Path, None, None]:
    suffix = Path(file.filename).suffix if file.filename else DEFAULT_PDF_SUFFIX

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        temp_path = tmp.name

    logger.info("Archivo temporal creado: %s", temp_path)

    try:
        yield Path(temp_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
            logger.info("Archivo temporal eliminado: %s", temp_path)


def procesar_archivo_pdf(file: UploadFile) -> str:
    FileValidator.validate_pdf(file)

    with _guardar_archivo_temporal(file) as temp_path:
        logger.info("Procesando PDF temporal: %s", temp_path)
        return _orchestrator.execute(str(temp_path), file.filename)


def _mapear_excepcion_servicio(exc: Exception) -> HTTPException:
    if isinstance(exc, PDFEmptyError):
        return HTTPException(status_code=422, detail=str(exc))

    if isinstance(exc, PDFExtractionError):
        return HTTPException(status_code=400, detail=str(exc))

    return HTTPException(status_code=500, detail=f"Error interno al procesar el PDF: {exc}")


@router.post("/extraer", response_model=ExtraccionResponse)
def extraer(file: UploadFile = File(...)):
    logger.info("Recibiendo petición POST /extraer para %s", file.filename)

    try:
        texto = procesar_archivo_pdf(file)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error en /extraer para %s: %s", file.filename, str(exc))
        raise _mapear_excepcion_servicio(exc)

    logger.info("Procesamiento de /extraer completado para %s", file.filename)

    return {
        "exito": True,
        "texto": texto,
        "nombre_archivo": file.filename,
    }


@router.get("/health")
def health_check():
    return {"status": "ok"}