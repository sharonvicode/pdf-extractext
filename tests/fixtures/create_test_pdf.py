"""
Script para generar PDFs de prueba para tests de integración.

Usa fpdf2, que ya está declarado como dependencia de desarrollo:
el fixture no instala nada en tiempo de ejecución.

Ejecutar: uv run python tests/fixtures/create_test_pdf.py
"""

from pathlib import Path

from fpdf import FPDF

from app.core.logger import logger

FIXTURES_DIR = Path(__file__).resolve().parent


def crear_pdf_simple(contenido: str) -> bytes:
    """Crea un PDF con el contenido indicado y lo devuelve como bytes."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    pdf.multi_cell(0, 10, contenido)
    return bytes(pdf.output())


def guardar_pdf(contenido: str, nombre_archivo: str) -> Path:
    """Crea y guarda un PDF de prueba en el directorio fixtures."""
    ruta = FIXTURES_DIR / nombre_archivo
    ruta.write_bytes(crear_pdf_simple(contenido))
    logger.info("PDF generado: %s", ruta)
    return ruta


if __name__ == "__main__":
    guardar_pdf("Este es un documento de prueba para testing de extracción.", "test_valido.pdf")
    guardar_pdf(
        "Documento número uno con contenido suficientemente largo para pasar la validación.",
        "test_documento_1.pdf",
    )
    guardar_pdf(
        "Documento número dos con contenido suficientemente largo para pasar la validación.",
        "test_documento_2.pdf",
    )
