"""
Validadores de archivos.

Módulo reutilizable para validación de archivos subidos.
"""

from fastapi import UploadFile, HTTPException
from app.core.config import MAX_FILE_SIZE


class FileValidator:
    """
    Validador de archivos para la aplicación.

    Proporciona métodos estáticos para validar archivos subidos
    según criterios específicos (extensión, tipo, tamaño).
    """

    @staticmethod
    async def validate_pdf(file: UploadFile) -> None:
        """
        Valida que un archivo sea un PDF válido.

        Reglas:
        - Debe tener extensión .pdf
        - Debe ser tipo application/pdf
        - No debe superar MAX_FILE_SIZE
        """

        # Validar extensión
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="El archivo debe tener extensión .pdf"
            )

        # Validar content-type
        if file.content_type != "application/pdf":
            raise HTTPException(
                status_code=400,
                detail="El archivo debe ser tipo application/pdf"
            )

        # Validar tamaño sin cargar todo en memoria
        file.file.seek(0, 2)  # ir al final
        file_size = file.file.tell()
        file.file.seek(0)  # volver al inicio

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"El archivo excede el tamaño máximo de {MAX_FILE_SIZE} bytes"
            )