"""
Tests del servicio de extracción usando el puerto ExtractorTexto.

El extractor se inyecta como un fake, así que estos tests no dependen
de pypdf ni de archivos reales.
"""

import pytest

from app.core.config import MIN_TEXT_LENGTH
from app.services.pdf_service import PDFEmptyError, PDFExtractionError, procesar_pdf

TEXTO_SUFICIENTE = "x" * MIN_TEXT_LENGTH


def _extractor_que_devuelve(texto):
    return lambda ruta: texto


def _extractor_que_lanza(exc):
    def extractor(ruta):
        raise exc

    return extractor


def test_devuelve_el_texto_del_extractor_inyectado():
    assert procesar_pdf("doc.pdf", "doc.pdf", _extractor_que_devuelve(TEXTO_SUFICIENTE)) == TEXTO_SUFICIENTE


def test_texto_mas_corto_que_el_minimo_lanza_pdf_empty_error():
    with pytest.raises(PDFEmptyError) as exc_info:
        procesar_pdf("doc.pdf", "doc.pdf", _extractor_que_devuelve("x" * (MIN_TEXT_LENGTH - 1)))

    assert str(MIN_TEXT_LENGTH) in str(exc_info.value)


@pytest.mark.parametrize("error", [FileNotFoundError("no existe"), ValueError("corrupto"), RuntimeError("otro")])
def test_errores_del_extractor_se_traducen_a_pdf_extraction_error(error):
    with pytest.raises(PDFExtractionError):
        procesar_pdf("doc.pdf", "doc.pdf", _extractor_que_lanza(error))
