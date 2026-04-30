"""
Módulo para extracción de texto desde archivos PDF.

Este módulo contiene la función extraer_texto que permite extraer
texto plano desde archivos PDF.
"""

from pathlib import Path
from typing import Union

from pypdf import PdfReader

PDF_EXTENSION = ".pdf"
PDF_SIGNATURE = b"%PDF-"
PDF_SIGNATURE_BYTES = len(PDF_SIGNATURE)
PAGE_SEPARATOR = "\n"


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
    # Convertir a Path para manejar tanto strings como objetos Path
    ruta = Path(ruta_pdf)

    # Verificar que el archivo exista
    if not ruta.exists():
        raise FileNotFoundError(f"El archivo no existe: {ruta_pdf}")

    # Verificar que sea un archivo PDF válido (por extensión y firma)
    if not _es_pdf_valido(ruta):
        raise ValueError(f"El archivo no es un PDF válido: {ruta_pdf}")

    # Extraer el texto del PDF
    return _extraer_texto_de_pdf(ruta)


def _es_pdf_valido(ruta: Path) -> bool:
    """
    Verifica si un archivo es un PDF válido.

    Un archivo se considera PDF válido si:
    - Tiene extensión .pdf
    - Es un archivo vacío (caso especial para PDFs vacíos)
    - O tiene la firma mágica %PDF- al inicio

    Args:
        ruta: Ruta al archivo a verificar.

    Returns:
        bool: True si es un PDF válido, False en caso contrario.
    """
    # Verificar la extensión
    if ruta.suffix.lower() != PDF_EXTENSION:
        return False

    # Verificar si es un archivo vacío (caso especial)
    if ruta.stat().st_size == 0:
        return True

    # Verificar la firma mágica del PDF (%PDF-)
    try:
        with open(ruta, "rb") as archivo:
            firma = archivo.read(PDF_SIGNATURE_BYTES)
            return firma.startswith(PDF_SIGNATURE)
    except (IOError, OSError):
        return False


def _extraer_texto_de_pdf(ruta: Path) -> str:
    """
    Extrae el texto contenido en un archivo PDF.

    Args:
        ruta: Ruta al archivo PDF.

    Returns:
        str: El texto extraído del PDF. String vacío si no hay texto
        o si el PDF no tiene una estructura válida.
    """
    # Caso especial: archivo vacío
    if ruta.stat().st_size == 0:
        return ""

    try:
        reader = PdfReader(str(ruta), strict=False)

        # Si no hay páginas, devolver string vacío
        if len(reader.pages) == 0:
            return ""

        # Extraer texto de todas las páginas y concatenar
        texto_paginas = []
        for pagina in reader.pages:
            texto = pagina.extract_text()
            if texto:
                texto_paginas.append(texto)

        # Unir el texto de todas las páginas con saltos de línea entre páginas
        return PAGE_SEPARATOR.join(texto_paginas)

    except Exception:
        # Si ocurre cualquier error al leer el PDF, devolver string vacío
        # Esto cubre el caso de PDFs corruptos, sin estructura válida,
        # o que solo contienen imágenes sin texto extraíble
        return ""
