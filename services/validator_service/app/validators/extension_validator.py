from fastapi import UploadFile

from app.validators.interface import ValidatorInterface


class ExtensionValidator(ValidatorInterface):

    def validate(self, file: UploadFile) -> str | None:
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            return "El archivo debe tener extensión .pdf"
        return None
