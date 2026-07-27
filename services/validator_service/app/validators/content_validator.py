from fastapi import UploadFile

from app.validators.interface import ValidatorInterface


class ContentValidator(ValidatorInterface):

    PDF_SIGNATURE = b"%PDF-"

    def validate(self, file: UploadFile) -> str | None:
        file.file.seek(0)
        header = file.file.read(len(self.PDF_SIGNATURE))
        file.file.seek(0)
        if not header or not header.startswith(self.PDF_SIGNATURE):
            return "El archivo no es un PDF válido (firma de contenido incorrecta)"
        return None
