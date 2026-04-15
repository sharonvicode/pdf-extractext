"""
Módulo para extracción de texto desde archivos PDF.

Este módulo contiene la función extraer_texto que permite extraer
texto plano desde archivos PDF.
"""

from pathlib import Path
from typing import Union


def extraer_texto(ruta_pdf: Union[str, Path]) -> str:
    """
    Extrae texto desde un archivo PDF.

    Args:
        ruta_pdf: Ruta al archivo PDF. Puede ser string o Path de pathlib.

    Returns:
        str: El texto extraído del PDF. Si el PDF no contiene texto
             o está vacío, devuelve un string vacío.

    Raises:
        FileNotFoundError: Si el archivo no existe en la ruta especificada.
        ValueError: Si el archivo no es un PDF válido.

    Example:
        >>> texto = extraer_texto("documento.pdf")
        >>> print(texto)
        "Contenido del PDF..."
    """
    # Verificar que el archivo exista
    if not Path(ruta_pdf).exists():
        raise FileNotFoundError(f"El archivo no existe: {ruta_pdf}")

    # TODO: Implementar el resto de la lógica de extracción
    raise NotImplementedError("La función extraer_texto aún no está implementada")
