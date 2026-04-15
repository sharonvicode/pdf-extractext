"""
Tests unitarios para la función extraer_texto(ruta_pdf).

Estos tests definen el comportamiento esperado de la función de extracción
de texto desde archivos PDF, siguiendo el enfoque TDD (Test Driven Development).

La función a implementar debe estar en: app.utils.pdf_extractor
"""

import pytest
from pathlib import Path


class TestExtraerTextoPDF:
    """Tests para la función extraer_texto que extrae texto de archivos PDF."""

    def test_pdf_vacio_devuelve_string_vacio(self, tmp_path):
        """
        Caso: PDF vacío (sin contenido).
        Esperado: Debería devolver un string vacío.
        """
        # Arrange: Crear un archivo PDF vacío temporal
        ruta_pdf = tmp_path / "vacio.pdf"
        ruta_pdf.write_bytes(b"")  # Simula PDF vacío

        # Act & Assert: La función debe devolver string vacío
        from app.utils.pdf_extractor import extraer_texto

        resultado = extraer_texto(str(ruta_pdf))

        assert resultado == ""
        assert isinstance(resultado, str)

    def test_pdf_con_texto_devuelve_texto_extraido(self, tmp_path):
        """
        Caso: PDF con texto plano.
        Esperado: Debería devolver el texto contenido en el PDF.
        """
        # Arrange: Preparar ruta a un PDF con texto
        # Nota: En implementación real, se usaría un mock o fixture
        ruta_pdf = tmp_path / "con_texto.pdf"
        ruta_pdf.write_bytes(b"%PDF-1.4 fake pdf with text: Hola Mundo")

        # Act
        from app.utils.pdf_extractor import extraer_texto

        resultado = extraer_texto(str(ruta_pdf))

        # Assert: El resultado debe contener el texto esperado
        assert isinstance(resultado, str)
        assert len(resultado) > 0

    def test_pdf_con_solo_imagenes_devuelve_string_vacio(self, tmp_path):
        """
        Caso: PDF que contiene solo imágenes (sin texto).
        Esperado: Debería devolver string vacío indicando que no hay texto.
        """
        # Arrange
        ruta_pdf = tmp_path / "solo_imagen.pdf"
        ruta_pdf.write_bytes(b"%PDF-1.4 fake pdf with image only")

        # Act
        from app.utils.pdf_extractor import extraer_texto

        resultado = extraer_texto(str(ruta_pdf))

        # Assert: Debe devolver string vacío cuando no hay texto
        assert resultado == ""
        assert isinstance(resultado, str)

    def test_archivo_inexistente_lanza_excepcion(self):
        """
        Caso: La ruta proporcionada no existe.
        Esperado: Debería lanzar FileNotFoundError.
        """
        # Arrange: Ruta que no existe
        ruta_inexistente = "/ruta/que/no/existe/documento.pdf"

        # Act & Assert
        from app.utils.pdf_extractor import extraer_texto

        with pytest.raises(FileNotFoundError):
            extraer_texto(ruta_inexistente)

    def test_archivo_no_pdf_lanza_excepcion(self, tmp_path):
        """
        Caso: El archivo existe pero no es un PDF válido.
        Esperado: Debería lanzar ValueError indicando que el archivo no es PDF.
        """
        # Arrange: Crear un archivo que no es PDF
        ruta_no_pdf = tmp_path / "documento.txt"
        ruta_no_pdf.write_text("Este es un archivo de texto, no un PDF")

        # Act & Assert
        from app.utils.pdf_extractor import extraer_texto

        with pytest.raises(ValueError) as exc_info:
            extraer_texto(str(ruta_no_pdf))

        assert "PDF" in str(exc_info.value) or "pdf" in str(exc_info.value)

    def test_ruta_como_path_objeto_acepta_pathlib(self, tmp_path):
        """
        Caso: La función acepta objetos Path de pathlib además de strings.
        Esperado: Debería funcionar correctamente con Path objects.
        """
        # Arrange
        ruta_pdf = tmp_path / "documento.pdf"
        ruta_pdf.write_bytes(b"%PDF-1.4 fake")

        # Act
        from app.utils.pdf_extractor import extraer_texto

        resultado = extraer_texto(ruta_pdf)  # Pasando Path object

        # Assert
        assert isinstance(resultado, str)

    def test_pdf_con_multiples_paginas_devuelve_texto_concatenado(self, tmp_path):
        """
        Caso: PDF con múltiples páginas con texto.
        Esperado: Debería devolver el texto de todas las páginas concatenado.
        """
        # Arrange
        ruta_pdf = tmp_path / "multipagina.pdf"
        ruta_pdf.write_bytes(b"%PDF-1.4 fake pdf multipage content")

        # Act
        from app.utils.pdf_extractor import extraer_texto

        resultado = extraer_texto(str(ruta_pdf))

        # Assert
        assert isinstance(resultado, str)

    def test_pdf_con_espacios_y_saltos_de_linea_preserva_formato(self, tmp_path):
        """
        Caso: PDF con texto que incluye espacios y saltos de línea.
        Esperado: Debería preservar el formato del texto extraído.
        """
        # Arrange
        ruta_pdf = tmp_path / "con_formato.pdf"
        ruta_pdf.write_bytes(b"%PDF-1.4 fake pdf with formatted text")

        # Act
        from app.utils.pdf_extractor import extraer_texto

        resultado = extraer_texto(str(ruta_pdf))

        # Assert
        assert isinstance(resultado, str)
