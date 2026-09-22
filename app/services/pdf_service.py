"""
Servicio de extracción de texto desde archivos PDF.

Este módulo contiene la lógica de negocio para extraer texto de un PDF
y validar que el contenido sea utilizable. No conoce la capa de
persistencia: coordina únicamente extracción y validación, lo que
permite tratarlo como un servicio independiente (extracción) separado
del servicio de persistencia de documentos.
"""

from pathlib import Path

from app.core.config import MIN_TEXT_LENGTH
from app.core.logger import logger
from app.utils.pdf_extractor import extraer_texto


class PDFServiceError(Exception):
    """Excepción base para errores del servicio PDF."""

    pass


class PDFEmptyError(PDFServiceError):
    """Excepción cuando el PDF no contiene texto suficiente."""

    pass


class PDFExtractionError(PDFServiceError):
    """Excepción cuando ocurre un error al extraer el PDF."""

    pass


def ejecutar_extraccion(ruta_pdf: str | Path) -> str:
    """
    Ejecuta la extracción de texto desde un archivo PDF.

    Esta función se encarga puramente de interactuar con el extractor
    de texto y manejar las excepciones que puedan surgir durante el
    proceso de extracción.

    Args:
        ruta_pdf: Ruta al archivo PDF a procesar.

    Returns:
        str: El texto extraído del PDF.

    Raises:
        PDFExtractionError: Si ocurre un error durante la extracción,
            incluyendo archivo no encontrado, PDF inválido u otros
            errores inesperados.
    """
    try:
        texto = extraer_texto(ruta_pdf)
    except FileNotFoundError as e:
        logger.error("No se encontró el archivo PDF en la ruta: %s", ruta_pdf)
        raise PDFExtractionError(f"Archivo no encontrado: {e}")
    except ValueError as e:
        logger.warning("El archivo PDF en la ruta %s es inválido", ruta_pdf)
        raise PDFExtractionError(f"Archivo PDF inválido: {e}")
    except Exception as e:
        logger.exception("Error inseperado al extraer texto del PDF: %s", ruta_pdf)
        raise PDFExtractionError(f"Error al extraer texto del PDF: {e}")

    logger.info("Extracción de texto completada para %s", ruta_pdf)
    return texto


def validar_texto_extraido(texto: str) -> None:
    """
    Valida que el texto extraído cumpla con la longitud mínima requerida.

    Esta función se encarga de verificar que el texto extraído de un PDF
    contenga al menos la cantidad mínima de caracteres definida por MIN_TEXT_LENGTH.
    Raises:
        PDFEmptyError: Si el texto tiene menos caracteres que el mínimo
            requerido (MIN_TEXT_LENGTH).
    """
    if len(texto) < MIN_TEXT_LENGTH:
        logger.warning(
            "El texto extraído es demasiado corto (%s caracteres); se rechaza el PDF",
            len(texto),
        )
        raise PDFEmptyError(
            "El PDF no contiene texto suficiente (mínimo 20 caracteres requeridos)"
        )
    

def procesar_pdf(ruta_pdf: str | Path, nombre_archivo: str) -> str:
    """
    Extrae y valida el texto de un PDF.

    No persiste el resultado: quien invoque esta función decide qué hacer
    con el texto extraído (por ejemplo, guardarlo mediante un repositorio).
    Esto mantiene la extracción aislada de la persistencia, para que cada
    una pueda evolucionar o desplegarse de forma independiente.

    Args:
        ruta_pdf: Ruta al archivo PDF temporal.
        nombre_archivo: Nombre original del archivo (solo para logging).

    Returns:
        str: El texto extraído del PDF.

    Raises:
        PDFEmptyError: Si el texto extraído tiene menos de 20 caracteres.
        PDFExtractionError: Si ocurre un error durante la extracción.
    """
    logger.info("Iniciando procesamiento del PDF %s", nombre_archivo)

    texto = ejecutar_extraccion(ruta_pdf)
    validar_texto_extraido(texto)

    logger.info("Procesamiento del PDF %s finalizado correctamente", nombre_archivo)
    return texto
