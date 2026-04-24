"""
Rutas para extracción de texto desde archivos PDF.

Este módulo expone endpoints HTTP para recibir archivos PDF
y delegar la extracción de texto al servicio correspondiente.
"""

import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.pdf_service import (
    procesar_pdf,
    PDFServiceError,
    PDFEmptyError,
    PDFExtractionError
)

router = APIRouter()


@router.post("/extraer")
def extraer(file: UploadFile = File(...)):
    """
    Recibe un archivo PDF y extrae su texto.

    Args:
        file: Archivo PDF enviado via form-data.

    Returns:
        JSON con el texto extraído o mensaje de error.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="El archivo debe tener extensión .pdf"
        )

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file.file.read())
            temp_path = tmp.name

        texto = procesar_pdf(temp_path, file.filename)

        return {
            "exito": True,
            "texto": texto,
            "nombre_archivo": file.filename
        }

    except PDFEmptyError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except PDFExtractionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al procesar el PDF: {e}"
        )
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
