"""
Tests unitarios para la función extraer_texto(ruta_pdf).

Estos tests definen el comportamiento esperado siguiendo TDD (Test Driven Development),
aplicando principios de Clean Code, KISS y SOLID.
"""

import pytest
from pathlib import Path
from fpdf import FPDF
from app.utils.pdf_extractor import extraer_texto


def _crear_pdf_con_texto(ruta: Path, textos: list[str]) -> None:
    """
    Helper para crear un PDF válido con texto.

    Args:
        ruta: Ruta donde se guardará el PDF.
        textos: Lista de textos, uno por página.
    """
    pdf = FPDF()
    for texto in textos:
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        try:
            pdf.multi_cell(0, 10, txt=texto)
        except UnicodeEncodeError:
            pdf.multi_cell(
                0, 10, txt=texto.encode("latin-1", "replace").decode("latin-1")
            )
    pdf.output(str(ruta))


class TestExtraerTextoPDF:
    """Tests para la función extraer_texto que extrae texto de archivos PDF."""

    # ============================================================================
    # CASOS BÁSICOS
    # ============================================================================

    def test_pdf_con_texto_extrae_contenido_correctamente(self, tmp_path):
        """PDF con texto plano debe devolver el contenido extraído."""
        ruta_pdf = tmp_path / "con_texto.pdf"
        _crear_pdf_con_texto(ruta_pdf, ["Hola Mundo"])

        resultado = extraer_texto(str(ruta_pdf))

        assert "Hola" in resultado
        assert "Mundo" in resultado

    def test_pdf_con_multiples_paginas_concatena_texto(self, tmp_path):
        """PDF con múltiples páginas debe concatenar todo el texto."""
        ruta_pdf = tmp_path / "multipagina.pdf"
        _crear_pdf_con_texto(
            ruta_pdf, ["Primera pagina", "Segunda pagina", "Tercera pagina"]
        )

        resultado = extraer_texto(str(ruta_pdf))

        assert "Primera" in resultado
        assert "Segunda" in resultado
        assert "Tercera" in resultado

    def test_pdf_vacio_devuelve_string_vacio(self, tmp_path):
        """PDF vacío (sin contenido) debe devolver string vacío."""
        ruta_pdf = tmp_path / "vacio.pdf"
        ruta_pdf.write_bytes(b"")

        resultado = extraer_texto(str(ruta_pdf))

        assert resultado == ""

    def test_pdf_sin_texto_solo_estructura_devuelve_vacio(self, tmp_path):
        """PDF con páginas vacías pero sin texto debe devolver string vacío."""
        ruta_pdf = tmp_path / "solo_estructura.pdf"
        pdf = FPDF()
        pdf.add_page()
        pdf.output(str(ruta_pdf))

        resultado = extraer_texto(str(ruta_pdf))

        assert resultado == ""

    def test_acepta_objeto_path_como_entrada(self, tmp_path):
        """La función debe aceptar objetos Path de pathlib."""
        ruta_pdf = tmp_path / "documento.pdf"
        _crear_pdf_con_texto(ruta_pdf, ["Texto de prueba"])

        resultado = extraer_texto(ruta_pdf)

        assert "Texto de prueba" in resultado

    def test_ruta_relativa_funciona_correctamente(self, tmp_path, monkeypatch):
        """Debe funcionar con rutas relativas cuando el archivo existe."""
        monkeypatch.chdir(tmp_path)
        ruta_pdf = tmp_path / "relativo.pdf"
        _crear_pdf_con_texto(ruta_pdf, ["Texto relativo"])

        resultado = extraer_texto("relativo.pdf")

        assert "Texto relativo" in resultado

    # ============================================================================
    # CASOS DE ERROR (Parametrizados)
    # ============================================================================

    def test_archivo_inexistente_lanza_filenotfounderror(self):
        """Ruta que no existe debe lanzar FileNotFoundError."""
        ruta_inexistente = "/ruta/que/no/existe/documento.pdf"

        with pytest.raises(FileNotFoundError):
            extraer_texto(ruta_inexistente)

    def test_archivo_no_pdf_lanza_valueerror(self, tmp_path):
        """Archivo de texto con extensión .txt debe lanzar ValueError."""
        ruta_archivo = tmp_path / "documento.txt"
        ruta_archivo.write_text("Este es un archivo de texto")

        with pytest.raises(ValueError) as exc_info:
            extraer_texto(str(ruta_archivo))

        assert "PDF" in str(exc_info.value).upper()

    def test_archivo_corrupto_con_extension_pdf_lanza_valueerror(self, tmp_path):
        """Archivo corrupto con extensión .pdf debe lanzar ValueError."""
        ruta_pdf = tmp_path / "corrupto.pdf"
        ruta_pdf.write_bytes(b"Este no es un PDF valido\nContenido aleatorio")

        with pytest.raises(ValueError) as exc_info:
            extraer_texto(str(ruta_pdf))

        assert "PDF" in str(exc_info.value).upper()

    # ============================================================================
    # INPUTS INVÁLIDOS (Parametrizados)
    # ============================================================================

    @pytest.mark.parametrize(
        "input_invalido",
        [
            None,
            12345,
            ["/ruta/archivo.pdf"],
            {"ruta": "/archivo.pdf"},
        ],
    )
    def test_inputs_invalidos_lanzan_typeerror(self, input_invalido):
        """Inputs que no son string ni Path deben lanzar TypeError o ValueError."""
        with pytest.raises((TypeError, ValueError)):
            extraer_texto(input_invalido)

    # ============================================================================
    # EDGE CASES
    # ============================================================================

    def test_pdf_con_muchas_paginas_extrae_contenido(self, tmp_path):
        """PDF con muchas páginas debe extraer texto de todas."""
        ruta_pdf = tmp_path / "grande.pdf"
        textos = [f"Pagina numero {i}" for i in range(1, 51)]
        _crear_pdf_con_texto(ruta_pdf, textos)

        resultado = extraer_texto(str(ruta_pdf))

        assert "Pagina numero 1" in resultado
        assert "Pagina numero 25" in resultado
        assert "Pagina numero 50" in resultado

    def test_pdf_con_caracteres_especiales_latin1_extrae_texto(self, tmp_path):
        """PDF con caracteres latin-1 debe extraer texto correctamente."""
        ruta_pdf = tmp_path / "especiales.pdf"
        _crear_pdf_con_texto(
            ruta_pdf,
            [
                "Texto con tildes: áéíóú",
                "La eñe: ñ",
                "Mayúsculas: ÁÉÍÓÚ Ñ",
            ],
        )

        resultado = extraer_texto(str(ruta_pdf))

        assert "Texto con tildes" in resultado
        assert "La eñe" in resultado
        assert "Mayúsculas" in resultado

    def test_pdf_con_simbolos_comunes_extrae_texto(self, tmp_path):
        """PDF con símbolos comunes debe extraer texto correctamente."""
        ruta_pdf = tmp_path / "simbolos.pdf"
        _crear_pdf_con_texto(
            ruta_pdf, ["Precio: $100.50", "Porcentaje: 50%", "Numero: #123"]
        )

        resultado = extraer_texto(str(ruta_pdf))

        assert "Precio" in resultado
        assert "Porcentaje" in resultado
        assert "Numero" in resultado

    def test_pdf_solo_firma_sin_contenido_valido_devuelve_vacio(self, tmp_path):
        """PDF que solo tiene firma %PDF- pero contenido corrupto debe devolver vacío."""
        ruta_pdf = tmp_path / "solo_firma.pdf"
        ruta_pdf.write_bytes(b"%PDF-1.4\ncontenido corrupto aqui...")

        resultado = extraer_texto(str(ruta_pdf))

        assert resultado == ""
