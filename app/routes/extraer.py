"""
Rutas para extracción de texto desde archivos PDF.

Este módulo expone endpoints HTTP para recibir archivos PDF
y delegar la extracción de texto al servicio correspondiente.
"""

import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from app.services.pdf_service import (
    procesar_pdf,
    PDFEmptyError,
    PDFExtractionError,
)
from app.repository.documento_repository import DocumentoRepository
from app.schemas import ExtraccionResponse
from app.utils.validators import FileValidator

router = APIRouter()


def get_documento_repository() -> DocumentoRepository:
    """
    Proporciona el repositorio de documentos.

    Esta función puede ser sobrescrita en tests mediante dependency_overrides.
    En producción utiliza MongoDB a través del repositorio real.
    """
    return DocumentoRepository()


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

    # Validación desacoplada (SOLID)
    FileValidator.validate_pdf(file)

    temp_path = None

    try:
        # Guardar archivo temporalmente para procesamiento
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file.file.read())
            temp_path = tmp.name

        # Procesar PDF
        texto = procesar_pdf(temp_path, file.filename, repositorio)

        return {
            "exito": True,
            "texto": texto,
            "nombre_archivo": file.filename,
        }

    except PDFEmptyError as e:
        raise HTTPException(status_code=422, detail=str(e))

    except PDFExtractionError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al procesar el PDF: {e}",
        )

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)