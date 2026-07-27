from fastapi import APIRouter, Depends, File, UploadFile

from app.core.config import MAX_FILE_SIZE
from app.schemas.responses import ValidationResponse
from app.service.pdf_validator_service import PDFValidationService
from app.validators.content_validator import ContentValidator
from app.validators.extension_validator import ExtensionValidator
from app.validators.size_validator import SizeValidator

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
