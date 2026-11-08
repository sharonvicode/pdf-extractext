"""
Tests unitarios para FileValidator.validate_pdf.

Definen el contrato del validador de archivos subidos: un archivo se acepta
solo si es un PDF real, legible, con al menos una página y dentro del tamaño
máximo permitido. Cualquier otro caso se rechaza con ArchivoInvalidoError
(la ruta /extraer lo traduce a HTTP 400).

El validador no depende de FastAPI: se prueba con io.BytesIO.
"""

from io import BytesIO

import pytest
from pypdf import PdfWriter

from app.utils.validators import PDF_CONTENT_TYPE, ArchivoInvalidoError, FileValidator


def _crear_pdf(paginas: int = 1) -> bytes:
    """Genera en memoria un PDF real con la cantidad de páginas indicada."""
    writer = PdfWriter()
    for _ in range(paginas):
        writer.add_blank_page(width=612, height=792)
    buffer = BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def _validar(
    contenido: bytes,
    filename: str | None = "documento.pdf",
    content_type: str = PDF_CONTENT_TYPE,
) -> None:
    FileValidator.validate_pdf(filename, content_type, BytesIO(contenido))


def _assert_rechazado(contenido: bytes, **kwargs) -> None:
    """Verifica que el validador rechace el archivo."""
    with pytest.raises(ArchivoInvalidoError):
        _validar(contenido, **kwargs)


@pytest.fixture
def pdf_valido() -> bytes:
    return _crear_pdf()


class TestValidatePdfCasosValidos:
    """Archivos que el validador debe aceptar."""

    def test_pdf_valido_es_aceptado(self, pdf_valido):
        assert _validar(pdf_valido) is None

    def test_pdf_con_varias_paginas_es_aceptado(self):
        assert _validar(_crear_pdf(paginas=3)) is None

    @pytest.mark.parametrize("filename", ["DOCUMENTO.PDF", "documento.Pdf", "mi.archivo.pdf"])
    def test_extension_pdf_se_acepta_sin_importar_mayusculas_ni_puntos(self, pdf_valido, filename):
        assert _validar(pdf_valido, filename=filename) is None

    def test_pdf_con_tamano_igual_al_maximo_es_aceptado(self, pdf_valido, monkeypatch):
        monkeypatch.setattr("app.utils.validators.MAX_FILE_SIZE", len(pdf_valido))

        assert _validar(pdf_valido) is None

    def test_validacion_deja_el_puntero_al_inicio_para_poder_leer_el_archivo(self, pdf_valido):
        archivo = BytesIO(pdf_valido)

        FileValidator.validate_pdf("documento.pdf", PDF_CONTENT_TYPE, archivo)

        assert archivo.read() == pdf_valido


class TestValidatePdfExtension:
    """El nombre del archivo debe terminar en .pdf."""

    @pytest.mark.parametrize(
        "filename",
        ["documento.txt", "documento", "documento.pdf.exe", "documentopdf", "documento.pdf "],
    )
    def test_extension_distinta_de_pdf_es_rechazada(self, pdf_valido, filename):
        _assert_rechazado(pdf_valido, filename=filename)

    @pytest.mark.parametrize("filename", [None, ""])
    def test_archivo_sin_nombre_es_rechazado(self, pdf_valido, filename):
        _assert_rechazado(pdf_valido, filename=filename)


class TestValidatePdfContentType:
    """El content-type declarado debe ser application/pdf."""

    @pytest.mark.parametrize(
        "content_type",
        ["text/plain", "application/octet-stream", "image/png", ""],
    )
    def test_content_type_distinto_de_pdf_es_rechazado(self, pdf_valido, content_type):
        _assert_rechazado(pdf_valido, content_type=content_type)


class TestValidatePdfContenido:
    """El contenido debe ser un PDF real, legible y con al menos una página."""

    def test_archivo_vacio_es_rechazado(self):
        _assert_rechazado(b"")

    @pytest.mark.parametrize(
        "contenido",
        [
            b"Esto es texto plano, no un PDF",
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR",
            b"PK\x03\x04 contenido de un zip",
        ],
        ids=["texto_plano", "imagen_png", "zip"],
    )
    def test_archivo_que_no_es_pdf_real_es_rechazado(self, contenido):
        _assert_rechazado(contenido)

    def test_pdf_solo_con_cabecera_y_contenido_corrupto_es_rechazado(self):
        _assert_rechazado(b"%PDF-1.4\ncontenido corrupto aqui...")

    def test_pdf_truncado_es_rechazado(self, pdf_valido):
        _assert_rechazado(pdf_valido[: len(pdf_valido) // 2])

    def test_pdf_sin_paginas_es_rechazado(self):
        _assert_rechazado(_crear_pdf(paginas=0))


class TestValidatePdfTamano:
    """El archivo no debe superar MAX_FILE_SIZE."""

    def test_pdf_que_supera_el_tamano_maximo_es_rechazado(self, pdf_valido, monkeypatch):
        monkeypatch.setattr("app.utils.validators.MAX_FILE_SIZE", len(pdf_valido) - 1)

        _assert_rechazado(pdf_valido)
