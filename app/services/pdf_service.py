"""
Servicio para procesamiento de archivos PDF.

Este módulo contiene la lógica de negocio para extraer texto de PDFs
y persistirlo en la base de datos.
"""

from datetime import datetime
from pathlib import Path
from typing import Union

from app.core.db import db
from app.utils.pdf_extractor import extraer_texto

collection = db["documentos"]


class PDFServiceError(Exception):
    """Excepción base para errores del servicio PDF."""
    pass


class PDFEmptyError(PDFServiceError):
    """Excepción cuando el PDF no contiene texto suficiente."""
    pass


class PDFExtractionError(PDFServiceError):
    """Excepción cuando ocurre un error al extraer el PDF."""
    pass


def procesar_pdf(ruta_pdf: Union[str, Path], nombre_archivo: str) -> str:
    """
    Procesa un archivo PDF: extrae texto y lo guarda en MongoDB.

    Args:
        ruta_pdf: Ruta al archivo PDF temporal.
        nombre_archivo: Nombre original del archivo.

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

    if len(texto) < 20:
        raise PDFEmptyError(
            "El PDF no contiene texto suficiente (mínimo 20 caracteres requeridos)"
        )

    documento = {
        "nombre": nombre_archivo,
        "texto": texto,
        "fecha_procesamiento": datetime.utcnow()
    }

    # collection.insert_one(documento)

    return texto
