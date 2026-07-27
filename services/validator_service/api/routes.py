from fastapi import APIRouter, Depends, File, UploadFile

from core.config import MAX_FILE_SIZE
from schemas.responses import ValidationResponse
from service.pdf_validator_service import PDFValidationService
from validators.content_validator import ContentValidator
from validators.extension_validator import ExtensionValidator
from validators.size_validator import SizeValidator

router = APIRouter()


def _build_service() -> PDFValidationService:
    return PDFValidationService([
        ExtensionValidator(),
        SizeValidator(MAX_FILE_SIZE),
        ContentValidator(),
    ])


@router.post("/validate", response_model=ValidationResponse)
async def validate_pdf(
    file: UploadFile = File(...),
    service: PDFValidationService = Depends(_build_service),
):
    return service.validate(file)
