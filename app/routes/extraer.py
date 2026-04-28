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
    PDFServiceError,
    PDFEmptyError,
    PDFExtractionError,
)
from app.repository.documento_repository import DocumentoRepository

router = APIRouter()


def get_documento_repository() -> DocumentoRepository:
    """
    Proporciona el repositorio de documentos.

    Esta función se reemplaza mediante app.dependency_overrides en tests.
    Por defecto, creará una nueva instancia con conexión SQLite.
    """
    import sqlite3

    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS documentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            texto TEXT NOT NULL,
            fecha_procesamiento TEXT NOT NULL
        )
        """
    )
    conn.commit()

    return DocumentoRepository(conn)


@router.post("/extraer")
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
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400, detail="El archivo debe tener extensión .pdf"
        )

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file.file.read())
            temp_path = tmp.name

        texto = procesar_pdf(temp_path, file.filename, repositorio)

        return {"exito": True, "texto": texto, "nombre_archivo": file.filename}

    except PDFEmptyError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except PDFExtractionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error interno al procesar el PDF: {e}"
        )
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
