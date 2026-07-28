from fastapi import UploadFile, HTTPException

from app.core.config import MAX_FILE_SIZE
from app.core.logger import logger

PDF_EXTENSION = ".pdf"
PDF_CONTENT_TYPE = "application/pdf"


class FileValidator:
    @staticmethod
    def validate_pdf(file: UploadFile) -> None:
        if not file.filename.lower().endswith(PDF_EXTENSION):
            logger.warning("Validación fallida: extensión no permitida (%s)", file.filename)
            raise HTTPException(status_code=400, detail="El archivo debe tener extensión .pdf")

        if file.content_type != PDF_CONTENT_TYPE:
            logger.warning("Validación fallida: content-type no permitido (%s)", file.content_type)
            raise HTTPException(status_code=400, detail="El archivo debe ser tipo application/pdf")

        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

        if file_size > MAX_FILE_SIZE:
            logger.warning("Validación fallida: archivo demasiado grande (%s bytes)", file_size)
            raise HTTPException(
                status_code=400,
                detail=f"El archivo excede el tamaño máximo de {MAX_FILE_SIZE} bytes",
            )