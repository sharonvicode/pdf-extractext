"""
Validadores de archivos.

No depende de FastAPI: recibe datos planos y lanza una excepción de
dominio (ArchivoInvalidoError). La capa HTTP decide cómo traducirla (400).
"""

import io
from typing import BinaryIO

from pypdf import PdfReader

from app.core.config import MAX_FILE_SIZE
from app.core.logger import logger

PDF_EXTENSION = ".pdf"
PDF_CONTENT_TYPE = "application/pdf"
PDF_SIGNATURE = b"%PDF-"
PDF_EOF_MARKER = b"%%EOF"
EOF_SEARCH_WINDOW = 1024


class ArchivoInvalidoError(Exception):
    """El archivo recibido no cumple las reglas para ser procesado como PDF."""


class FileValidator:
    """Valida archivos subidos según nombre, extensión, tipo, tamaño y contenido."""

    @staticmethod
    def validate_pdf(nombre: str | None, content_type: str | None, archivo: BinaryIO) -> None:
        """
        Valida que un archivo sea un PDF aceptable.

        Reglas:
        - Debe tener nombre y extensión .pdf
        - Debe ser tipo application/pdf
        - No debe superar MAX_FILE_SIZE ni estar vacío
        - Su contenido debe ser un PDF real, legible y con al menos una página

        Deja el archivo posicionado al inicio para quien lo lea después.

        Raises:
            ArchivoInvalidoError: si alguna regla no se cumple.
        """
        if not nombre:
            logger.warning("Validación de PDF fallida: archivo sin nombre")
            raise ArchivoInvalidoError("El archivo debe tener un nombre")

        if not nombre.lower().endswith(PDF_EXTENSION):
            logger.warning("Validación de PDF fallida: extensión no permitida (%s)", nombre)
            raise ArchivoInvalidoError("El archivo debe tener extensión .pdf")

        if content_type != PDF_CONTENT_TYPE:
            logger.warning("Validación de PDF fallida: tipo de contenido no permitido (%s)", content_type)
            raise ArchivoInvalidoError("El archivo debe ser tipo application/pdf")

        archivo.seek(0, 2)
        tamanio = archivo.tell()
        archivo.seek(0)

        if tamanio > MAX_FILE_SIZE:
            logger.warning("Validación de PDF fallida: archivo demasiado grande (%s bytes)", tamanio)
            raise ArchivoInvalidoError(f"El archivo excede el tamaño máximo de {MAX_FILE_SIZE} bytes")

        if tamanio == 0:
            logger.warning("Validación de PDF fallida: archivo vacío")
            raise ArchivoInvalidoError("El archivo está vacío")

        FileValidator._validar_contenido_pdf(archivo)

    @staticmethod
    def _validar_contenido_pdf(archivo: BinaryIO) -> None:
        """Verifica que el contenido sea un PDF real, completo y con páginas."""
        contenido = archivo.read()
        archivo.seek(0)

        # Firma y fin de archivo: descarta texto, imágenes, zips y PDFs truncados
        if not contenido.startswith(PDF_SIGNATURE) or PDF_EOF_MARKER not in contenido[-EOF_SEARCH_WINDOW:]:
            logger.warning("Validación de PDF fallida: el contenido no es un PDF válido")
            raise ArchivoInvalidoError("El contenido del archivo no es un PDF válido")

        try:
            cantidad_paginas = len(PdfReader(io.BytesIO(contenido)).pages)
        except Exception as exc:
            logger.warning("Validación de PDF fallida: PDF dañado o ilegible")
            raise ArchivoInvalidoError("El PDF está dañado o no se puede leer") from exc

        if cantidad_paginas == 0:
            logger.warning("Validación de PDF fallida: PDF sin páginas")
            raise ArchivoInvalidoError("El PDF no tiene páginas")
