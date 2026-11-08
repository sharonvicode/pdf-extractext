"""
Módulo para extracción de texto desde archivos PDF.

Este módulo contiene la función extraer_texto que permite extraer
texto plano desde archivos PDF.
"""

from pathlib import Path

from pypdf import PdfReader

from app.core.logger import logger

PDF_EXTENSION = ".pdf"
PDF_SIGNATURE = b"%PDF-"
PDF_SIGNATURE_BYTES = len(PDF_SIGNATURE)
PAGE_SEPARATOR = "\n"


def extraer_texto(ruta_pdf: str | Path) -> str:
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
    logger.info("Intentando extraer texto del archivo PDF: %s", ruta_pdf)
    ruta = Path(ruta_pdf)

    if not ruta.exists():
        logger.error("No se encontró el archivo PDF: %s", ruta_pdf)
        raise FileNotFoundError(f"El archivo no existe: {ruta_pdf}")

    if ruta.suffix.lower() != PDF_EXTENSION:
        logger.warning("Archivo rechazado por extensión no válida: %s", ruta_pdf)
        raise ValueError(f"El archivo no es un PDF válido: {ruta_pdf}")

    if ruta.stat().st_size == 0:
        logger.info("Se devuelve texto vacío para el PDF vacío: %s", ruta_pdf)
        return ""

    if not _tiene_firma_pdf(ruta):
        logger.warning("El archivo no tiene la firma %%PDF-: %s", ruta_pdf)
        raise ValueError(f"El archivo no es un PDF válido: {ruta_pdf}")

    return _extraer_texto_de_pdf(ruta)


def _tiene_firma_pdf(ruta: Path) -> bool:
    """Indica si el archivo empieza con la firma mágica %PDF-."""
    try:
        with open(ruta, "rb") as archivo:
            return archivo.read(PDF_SIGNATURE_BYTES).startswith(PDF_SIGNATURE)
    except OSError:
        return False


def _extraer_texto_de_pdf(ruta: Path) -> str:
    """
    Extrae el texto de un PDF no vacío y con firma válida.

    Raises:
        ValueError: Si pypdf no puede leer el archivo (PDF corrupto).
    """
    try:
        reader = PdfReader(str(ruta), strict=False)

        # Si no hay páginas, devolver string vacío
        if len(reader.pages) == 0:
            logger.warning("El PDF %s no contiene páginas extraíbles", ruta)
            return ""
        
        # Extraer texto de todas las páginas y concatenar
        texto_paginas = []
        for pagina in reader.pages:
            texto = pagina.extract_text()
            if texto:
                texto_paginas.append(texto)

        logger.info("Texto extraído correctamente del PDF: %s", ruta)
        # Unir el texto de todas las páginas con saltos de línea entre páginas
        return PAGE_SEPARATOR.join(texto_paginas)

    except Exception as e:
        logger.exception("Error al leer el PDF: %s", ruta)
        raise ValueError(f"PDF corrupto o ilegible: {ruta}") from e