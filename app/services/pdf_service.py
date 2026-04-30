"""
Servicio para procesamiento de archivos PDF.

Este módulo contiene la lógica de negocio para extraer texto de PDFs
y persistirlo en la base de datos.
"""

from datetime import datetime
from pathlib import Path
from typing import Union, Protocol

from app.utils.pdf_extractor import extraer_texto


MIN_TEXT_LENGTH = 20


class DocumentoRepositoryInterface(Protocol):
    """Protocolo para el repositorio de documentos."""

    def guardar(self, nombre: str, texto: str, fecha_procesamiento: datetime) -> int:
        """Guarda un documento y retorna su ID generado."""
        ...


class PDFServiceError(Exception):
    """Excepción base para errores del servicio PDF."""

    pass


class PDFEmptyError(PDFServiceError):
    """Excepción cuando el PDF no contiene texto suficiente."""

    pass


class PDFExtractionError(PDFServiceError):
    """Excepción cuando ocurre un error al extraer el PDF."""

    pass


def procesar_pdf(
    ruta_pdf: Union[str, Path],
    nombre_archivo: str,
    repositorio: DocumentoRepositoryInterface,
) -> str:
    """
    Procesa un archivo PDF: extrae texto y lo guarda mediante el repositorio.

    Args:
        ruta_pdf: Ruta al archivo PDF temporal.
        nombre_archivo: Nombre original del archivo.
        repositorio: Implementación del repositorio para persistencia.

    Returns:
        str: El texto extraído del PDF.

    Raises:
        PDFEmptyError: Si el texto extraído tiene menos de 20 caracteres.
        PDFExtractionError: Si ocurre un error durante la extracción.
    """
    try:
        texto = extraer_texto(ruta_pdf)
    except FileNotFoundError as e:
        raise PDFExtractionError(f"Archivo no encontrado: {e}")
    except ValueError as e:
        raise PDFExtractionError(f"Archivo PDF inválido: {e}")
    except Exception as e:
        raise PDFExtractionError(f"Error al extraer texto del PDF: {e}")

    if len(texto) < MIN_TEXT_LENGTH:
        raise PDFEmptyError(
            "El PDF no contiene texto suficiente (mínimo 20 caracteres requeridos)"
        )

    repositorio.guardar(
        nombre=nombre_archivo,
        texto=texto,
        fecha_procesamiento=datetime.utcnow(),
    )

    return texto
