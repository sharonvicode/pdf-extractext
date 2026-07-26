"""
Servicio para procesamiento de archivos PDF.

Este módulo contiene la lógica de negocio para extraer texto de PDFs
y persistirlo en la base de datos.
"""

from datetime import datetime
from pathlib import Path
from typing import Union, Protocol
from typing import Any

from app.core.logger import logger
from app.utils.pdf_extractor import extraer_texto


MIN_TEXT_LENGTH = 20


class DocumentoRepositoryInterface(Protocol):
    """Protocolo para el repositorio de documentos."""

    def guardar(self, nombre: str, texto: str, fecha_procesamiento: datetime) -> Any:
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


def ejecutar_extraccion(ruta_pdf: Union[str, Path]) -> str:
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
        logger.warning("El archivo PDF en la ruta %s es inválido: %s", ruta_pdf)
        raise PDFExtractionError(f"Archivo PDF inválido: {e}")
    except Exception as e:
        logger.exception("Error inseperado al extraer texto del PDF: %s", ruta_pdf)
        raise PDFExtractionError(f"Error al extraer texto del PDF: {e}")

    logger.info("Extracción de texto completada para %s", ruta_pdf)
    return texto


def validar_texto_extraido(texto: str) -> bool:
    """
    Valida que el texto extraído cumpla con la longitud mínima requerida.

    Esta función se encarga de verificar que el texto extraído de un PDF
    contenga al menos la cantidad mínima de caracteres definida por
    MIN_TEXT_LENGTH.

    Args:
        texto: El texto extraído del PDF a validar.

    Returns:
        bool: True si el texto cumple con la longitud mínima requerida.

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

    return True


def guardar_documento(
    nombre_archivo: str, texto: str, repositorio: DocumentoRepositoryInterface
) -> Any:
    """
    Persiste un documento en el repositorio.

    Esta función se encarga únicamente de guardar los datos del documento
    utilizando el repositorio proporcionado, asignando la fecha y hora
    actual en UTC como fecha de procesamiento.

    Args:
        nombre_archivo: Nombre original del archivo.
        texto: Texto extraído del documento.
        repositorio: Implementación del repositorio para persistencia.

    Returns:
        Any: El resultado de la operación de guardado (generalmente el ID
            del documento generado).
    """
    logger.info("Guardando documento %s en el repositorio", nombre_archivo)
    resultado = repositorio.guardar(
        nombre=nombre_archivo,
        texto=texto,
        fecha_procesamiento=datetime.utcnow(),
    )
    logger.info("Documento %s guardado correctamente", nombre_archivo)
    return resultado
    
    return repositorio.guardar(
        nombre=nombre_archivo,
        texto=texto,
        fecha_procesamiento=datetime.utcnow(),
    )


def procesar_pdf(
    
    ruta_pdf: Union[str, Path],
    nombre_archivo: str,
    repositorio: DocumentoRepositoryInterface,
) -> str:
    """
    Procesa un archivo PDF: extrae texto y lo guarda mediante el repositorio.

    Esta función actúa como un orquestador local, coordinando secuencialmente
    las operaciones de extracción, validación y persistencia del documento.
    Facilita la futura migración a microservicios al delegar responsabilidades
    específicas en funciones independientes.

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
    logger.info("Iniciando procesamiento del PDF %s", nombre_archivo)
    
    texto = ejecutar_extraccion(ruta_pdf)
    validar_texto_extraido(texto)
    guardar_documento(nombre_archivo, texto, repositorio)

    logger.info("Procesamiento del PDF %s finalizado correctamente", nombre_archivo)
    return texto