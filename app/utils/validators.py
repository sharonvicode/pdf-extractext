"""
Validadores de archivos.

Módulo reutilizable para validación de archivos subidos.
"""

import io

from fastapi import HTTPException, UploadFile
from pypdf import PdfReader

from app.core.config import MAX_FILE_SIZE
from app.core.logger import logger

PDF_EXTENSION = ".pdf"
PDF_CONTENT_TYPE = "application/pdf"
PDF_SIGNATURE = b"%PDF-"
PDF_EOF_MARKER = b"%%EOF"


class FileValidator:
    """
    Validador de archivos para la aplicación.

    Proporciona métodos estáticos para validar archivos subidos
    según criterios específicos (nombre, extensión, tipo, tamaño y contenido).
    """

    @staticmethod
    def validate_pdf(file: UploadFile) -> None:
        """
        Valida que un archivo sea un PDF válido.

        Reglas:
        - Debe tener nombre
        - Debe tener extensión .pdf
        - Debe ser tipo application/pdf
        - No debe superar MAX_FILE_SIZE
        - No debe estar vacío
        - Su contenido debe ser un PDF real, legible y con al menos una página
        """

        # Validar que tenga nombre
        if not file.filename:
            logger.warning("Validación de PDF fallida: archivo sin nombre")
            raise HTTPException(
                status_code=400,
                detail="El archivo debe tener un nombre"
            )

        # Validar extensión
        if not file.filename.lower().endswith(PDF_EXTENSION):
            logger.warning("Validación de PDF fallida: extensión no permitida (%s)", file.filename)
            raise HTTPException(
                status_code=400,
                detail="El archivo debe tener extensión .pdf"
            )

        # Validar content-type
        if file.content_type != PDF_CONTENT_TYPE:
            logger.warning("Validación de PDF fallida: tipo de contenido no permitido (%s)", file.content_type)
            raise HTTPException(
                status_code=400,
                detail="El archivo debe ser tipo application/pdf"
            )

        # Validar tamaño sin cargar todo en memoria
        file.file.seek(0, 2)  # ir al final
        file_size = file.file.tell()
        file.file.seek(0)  # volver al inicio

        if file_size > MAX_FILE_SIZE:
            logger.warning(
                "Validación de PDF fallida: archivo demasiado grande (%s bytes)", file_size
            )
            raise HTTPException(
                status_code=400,
                detail=f"El archivo excede el tamaño máximo de {MAX_FILE_SIZE} bytes"
            )

        # Validar que no esté vacío
        if file_size == 0:
            logger.warning("Validación de PDF fallida: archivo vacío")
            raise HTTPException(
                status_code=400,
                detail="El archivo está vacío"
            )

        # Validar el contenido real del PDF
        FileValidator._validate_pdf_content(file)

    @staticmethod
    def _validate_pdf_content(file: UploadFile) -> None:
        """Verifica que el contenido sea un PDF real, completo y con páginas."""
        content = file.file.read()
        file.file.seek(0)  # dejar el archivo listo para quien lo use después

        # Firma y fin de archivo: descarta texto, imágenes, zips y PDFs truncados
        if not content.startswith(PDF_SIGNATURE) or PDF_EOF_MARKER not in content[-1024:]:
            logger.warning("Validación de PDF fallida: el contenido no es un PDF válido")
            raise HTTPException(
                status_code=400,
                detail="El contenido del archivo no es un PDF válido"
            )

        # Estructura: debe poder leerse y tener al menos una página
        try:
            page_count = len(PdfReader(io.BytesIO(content)).pages)
        except Exception:
            logger.warning("Validación de PDF fallida: PDF dañado o ilegible")
            raise HTTPException(
                status_code=400,
                detail="El PDF está dañado o no se puede leer"
            )

        if page_count == 0:
            logger.warning("Validación de PDF fallida: PDF sin páginas")
            raise HTTPException(
                status_code=400,
                detail="El PDF no tiene páginas"
            )