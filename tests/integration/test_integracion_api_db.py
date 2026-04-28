"""
Tests de integración completos: API + Extracción + Base de Datos

Este módulo prueba el flujo completo sin mocks ni mocks internos,
verificando que:
- La API responde correctamente
- El texto se extrae de los PDFs reales
- Los datos se persisten en SQLite
- La integridad de datos se mantiene

Principios aplicados:
- KISS: Código simple y directo
- DRY: Fixtures reutilizables
- Independencia: Cada test es autónomo
- Claridad: Nombres descriptivos y assertions explícitas
- Puros: Sin mocks, usando dependencias reales de FastAPI
"""

import io
import sqlite3
from datetime import datetime
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from fpdf import FPDF

from main import create_app
from app.routes.extraer import get_documento_repository
from app.repository.documento_repository import DocumentoRepository


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def db_connection() -> Generator[sqlite3.Connection, None, None]:
    """
    Proporciona una conexión SQLite en memoria con esquema inicializado.
    """
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE documentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            texto TEXT NOT NULL,
            fecha_procesamiento TEXT NOT NULL
        )
        """
    )
    conn.commit()

    yield conn
    conn.close()


@pytest.fixture
def repositorio(db_connection: sqlite3.Connection) -> DocumentoRepository:
    """Proporciona un repositorio inicializado con BD limpia."""
    return DocumentoRepository(db_connection)


def _crear_pdf_temporal(texto: str) -> bytes:
    """
    Crea un PDF temporal con el texto especificado usando fpdf.

    Args:
        texto: Texto a incluir en el PDF

    Returns:
        bytes: Contenido del PDF como bytes
    """

    class PDF(FPDF):
        def header(self):
            pass

        def footer(self):
            pass

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)

    # Manejar caracteres especiales
    try:
        pdf.multi_cell(0, 10, text=texto)
    except UnicodeEncodeError:
        pdf.multi_cell(0, 10, text=texto.encode("latin-1", "replace").decode("latin-1"))

    # output() devuelve bytearray, convertir a bytes
    resultado = pdf.output()
    if isinstance(resultado, bytearray):
        return bytes(resultado)
    return resultado


@pytest.fixture
def pdf_valido() -> bytes:
    """Genera un PDF válido con texto suficiente (>20 caracteres)."""
    return _crear_pdf_temporal(
        "Este es un documento de prueba con suficiente texto para pasar la validacion."
    )


@pytest.fixture
def pdf_otro() -> bytes:
    """Genera otro PDF válido con contenido diferente."""
    return _crear_pdf_temporal(
        "Segundo documento de prueba con contenido unico para verificar integridad."
    )


@pytest.fixture
def pdf_invalido() -> bytes:
    """Genera un archivo que parece PDF pero no lo es."""
    return b"Este no es un PDF valido, solo texto plano con extension pdf"


@pytest.fixture
def pdf_con_poco_texto() -> bytes:
    """Genera un PDF válido pero con menos de 20 caracteres."""
    return _crear_pdf_temporal("Corto")


@pytest.fixture
def client(db_connection: sqlite3.Connection) -> Generator[TestClient, None, None]:
    """
    Proporciona un TestClient con la BD SQLite inyectada via dependency_overrides.

    Usa FastAPI dependency_overrides para reemplazar el repositorio
    con una instancia que usa SQLite en memoria, sin mocks.
    """
    app = create_app()

    # Crear repositorio con la conexión proporcionada
    repo = DocumentoRepository(db_connection)

    # Reemplazar la dependencia usando dependency_overrides de FastAPI
    def override_get_repository():
        return repo

    app.dependency_overrides[get_documento_repository] = override_get_repository

    with TestClient(app) as test_client:
        # Almacenar referencia al repositorio para usar en assertions
        test_client._test_repo = repo  # type: ignore
        yield test_client

    # Limpiar overrides después del test
    app.dependency_overrides.clear()


# =============================================================================
# TESTS DE INTEGRACIÓN
# =============================================================================


class TestFlujoCompleto:
    """
    Tests del flujo completo: request → extracción → guardado → response.
    """

    def test_flujo_completo_exitoso(
        self, client: TestClient, pdf_valido: bytes
    ) -> None:
        """
        Test 1: Flujo completo exitoso.

        Verifica que una request válida resulta en:
        - Response 200 con los datos correctos
        - Texto extraído del PDF
        - Documento guardado en base de datos
        """
        archivo = io.BytesIO(pdf_valido)
        nombre = "documento_prueba.pdf"

        response = client.post(
            "/extraer", files={"file": (nombre, archivo, "application/pdf")}
        )

        # Verificar respuesta de API
        assert response.status_code == 200
        json_response = response.json()
        assert json_response["exito"] is True
        assert json_response["nombre_archivo"] == nombre
        assert len(json_response["texto"]) >= 20  # Texto extraído válido

    def test_persistencia_datos(self, client: TestClient, pdf_valido: bytes) -> None:
        """
        Test 2: Verificar persistencia en base de datos.

        Luego de un POST exitoso, el documento debe existir en la BD
        con todos sus campos correctamente almacenados.
        """
        archivo = io.BytesIO(pdf_valido)
        nombre = "documento_persistencia.pdf"

        # Ejecutar request
        response = client.post(
            "/extraer", files={"file": (nombre, archivo, "application/pdf")}
        )

        assert response.status_code == 200
        texto_extraido = response.json()["texto"]

        # Verificar en base de datos a través del repositorio real
        repo = client._test_repo  # type: ignore
        documento = repo.obtener_por_nombre(nombre)

        assert documento is not None
        assert documento["nombre"] == nombre
        assert documento["texto"] == texto_extraido
        assert isinstance(documento["fecha_procesamiento"], datetime)

    def test_multiples_requests(
        self, client: TestClient, pdf_valido: bytes, pdf_otro: bytes
    ) -> None:
        """
        Test 3: Múltiples requests procesan todos los PDFs correctamente.

        Verifica que varios PDFs subidos secuencialmente se guarden
        correctamente sin interferencia entre ellos.
        """
        nombres_archivos = ["doc_1.pdf", "doc_2.pdf", "doc_3.pdf"]
        pdfs = [pdf_valido, pdf_otro, pdf_valido]

        textos_extraidos = []

        for nombre, pdf_bytes in zip(nombres_archivos, pdfs):
            archivo = io.BytesIO(pdf_bytes)
            response = client.post(
                "/extraer", files={"file": (nombre, archivo, "application/pdf")}
            )

            assert response.status_code == 200
            textos_extraidos.append(response.json()["texto"])

        # Verificar persistencia de todos
        repo = client._test_repo  # type: ignore
        assert repo.contar() == 3

        for nombre, texto in zip(nombres_archivos, textos_extraidos):
            doc = repo.obtener_por_nombre(nombre)
            assert doc is not None
            assert doc["texto"] == texto


class TestManejoErrores:
    """
    Tests de manejo de errores durante el procesamiento.
    """

    def test_error_extraccion_pdf_invalido(
        self, client: TestClient, pdf_invalido: bytes
    ) -> None:
        """
        Test 4: Error de extracción - PDF inválido no se guarda en BD.

        Un archivo que no es un PDF válido debe:
        - Retornar error (400)
        - NO persistirse en la base de datos
        """
        archivo = io.BytesIO(pdf_invalido)
        nombre = "archivo_invalido.pdf"

        # Guardar conteo inicial
        repo = client._test_repo  # type: ignore
        conteo_inicial = repo.contar()

        response = client.post(
            "/extraer", files={"file": (nombre, archivo, "application/pdf")}
        )

        # Verificar error de API
        assert response.status_code == 400

        # Verificar que NO se guardó en BD
        assert repo.contar() == conteo_inicial
        assert repo.obtener_por_nombre(nombre) is None

    def test_error_extraccion_poco_texto(
        self, client: TestClient, pdf_con_poco_texto: bytes
    ) -> None:
        """
        Test adicional: PDF válido pero con poco texto (<20 caracteres).

        Este caso debe ser rechazado por el servicio y no guardarse.
        """
        archivo = io.BytesIO(pdf_con_poco_texto)
        nombre = "poco_texto.pdf"

        repo = client._test_repo  # type: ignore
        conteo_inicial = repo.contar()

        response = client.post(
            "/extraer", files={"file": (nombre, archivo, "application/pdf")}
        )

        # Error de validación (422 Unprocessable Entity)
        assert response.status_code == 422

        # No debe guardarse
        assert repo.contar() == conteo_inicial


class TestRecuperacionDatos:
    """
    Tests de listado y recuperación de documentos guardados.
    """

    def test_listado_recuperacion(self, client: TestClient, pdf_valido: bytes) -> None:
        """
        Test 5: Listado y recuperación de documentos.

        Los documentos guardados deben poder consultarse correctamente
        a través del repositorio.
        """
        # Crear algunos documentos
        nombres = ["alpha.pdf", "beta.pdf", "gamma.pdf"]
        for nombre in nombres:
            archivo = io.BytesIO(pdf_valido)
            response = client.post(
                "/extraer", files={"file": (nombre, archivo, "application/pdf")}
            )
            assert response.status_code == 200

        # Verificar listado completo
        repo = client._test_repo  # type: ignore
        todos = repo.listar_todos()

        assert len(todos) == 3
        nombres_recuperados = {doc["nombre"] for doc in todos}
        assert nombres_recuperados == set(nombres)

        # Verificar orden (por ID, ascendente)
        ids = [doc["id"] for doc in todos]
        assert ids == sorted(ids)

    def test_obtener_por_id(self, client: TestClient, pdf_valido: bytes) -> None:
        """
        Test adicional: Recuperación individual por ID.

        Cada documento debe poder recuperarse por su ID único.
        """
        archivo = io.BytesIO(pdf_valido)
        response = client.post(
            "/extraer", files={"file": ("unico.pdf", archivo, "application/pdf")}
        )

        assert response.status_code == 200

        repo = client._test_repo  # type: ignore
        doc_por_nombre = repo.obtener_por_nombre("unico.pdf")
        assert doc_por_nombre is not None

        # Recuperar por ID
        doc_por_id = repo.obtener_por_id(doc_por_nombre["id"])
        assert doc_por_id is not None
        assert doc_por_id["nombre"] == "unico.pdf"
        assert doc_por_id["texto"] == doc_por_nombre["texto"]


class TestIntegridadDatos:
    """
    Tests de integridad y consistencia de datos.
    """

    def test_integridad_datos_texto_coincide(
        self, client: TestClient, pdf_valido: bytes
    ) -> None:
        """
        Test 6: El texto guardado coincide exactamente con el extraído.

        Verifica que no hay transformaciones o pérdida de datos
        durante el flujo completo.
        """
        archivo = io.BytesIO(pdf_valido)
        nombre = "integridad.pdf"

        response = client.post(
            "/extraer", files={"file": (nombre, archivo, "application/pdf")}
        )

        assert response.status_code == 200
        texto_respuesta = response.json()["texto"]

        # Verificar que el texto en BD es idéntico
        repo = client._test_repo  # type: ignore
        documento = repo.obtener_por_nombre(nombre)

        assert documento is not None
        assert documento["texto"] == texto_respuesta
        assert len(documento["texto"]) >= 20

    def test_fechas_son_datetime(self, client: TestClient, pdf_valido: bytes) -> None:
        """
        Test adicional: Las fechas de procesamiento son objetos datetime válidos.
        """
        archivo = io.BytesIO(pdf_valido)
        nombre = "fecha_test.pdf"

        before = datetime.utcnow()
        response = client.post(
            "/extraer", files={"file": (nombre, archivo, "application/pdf")}
        )
        after = datetime.utcnow()

        assert response.status_code == 200

        repo = client._test_repo  # type: ignore
        documento = repo.obtener_por_nombre(nombre)

        assert documento is not None
        assert isinstance(documento["fecha_procesamiento"], datetime)
        assert before <= documento["fecha_procesamiento"] <= after
