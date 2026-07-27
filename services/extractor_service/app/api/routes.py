import os
import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.extractors.pypdf_extractor import PyPDFExtractor
from app.schemas.responses import ExtractionResponse
from app.service.pdf_extractor_service import PDFExtractorService

router = APIRouter()


def _build_service() -> PDFExtractorService:
    return PDFExtractorService(PyPDFExtractor())


@router.post("/extract", response_model=ExtractionResponse)
async def extract_text(
    file: UploadFile = File(...),
    service: PDFExtractorService = Depends(_build_service),
):
    suffix = Path(file.filename).suffix if file.filename else ".pdf"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        temp_path = tmp.name

    try:
        text = service.extract(Path(temp_path))
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Error al extraer texto del PDF: {exc}",
        )
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return ExtractionResponse(
        success=True,
        text=text,
        filename=file.filename or "documento.pdf",
    )
