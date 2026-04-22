"""
Módulo para extraer texto de archivos PDF.
"""

import os

def extraer_texto(ruta_pdf):
    """
    Extrae texto de un archivo PDF.

    Args:
        ruta_pdf: Ruta al archivo PDF.

    Returns:
        str: El texto extraído del PDF.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si el archivo no es un PDF válido.
    """
    if not os.path.exists(ruta_pdf):
        raise FileNotFoundError(f"El archivo no existe: {ruta_pdf}")

    # TODO: Implementar extracción de texto para archivos que sí existen
    return ""
