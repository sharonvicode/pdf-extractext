"""
Tests de integración: API + Extracción + Base de Datos
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


@pytest.fixture
def db_connection() -> Generator[sqlite3.Connection, None, None]:
    """Proporciona una conexión SQLite en memoria."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute(
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
def client(db_connection: sqlite3.Connection) -> Generator[TestClient, None, None]:
    """Proporciona un TestClient con BD SQLite inyectada."""
    app = create_app()
    repo = DocumentoRepository(db_connection)

    def override_get_repository():
        return repo

    app.dependency_overrides[get_documento_repository] = override_get_repository

    with TestClient(app) as test_client:
        test_client._test_repo = repo  # type: ignore
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def repo(client: TestClient) -> DocumentoRepository:
    """Proporciona acceso al repositorio del cliente."""
    return client._test_repo  # type: ignore


def _crear_pdf(texto: str) -> bytes:
    """Crea un PDF temporal con el texto especificado."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    try:
        pdf.multi_cell(0, 10, text=texto)
    except UnicodeEncodeError:
        pdf.multi_cell(0, 10, text=texto.encode("latin-1", "replace").decode("latin-1"))
    resultado = pdf.output()
    return bytes(resultado) if isinstance(resultado, bytearray) else resultado


@pytest.fixture
def pdf_valido() -> bytes:
    return _crear_pdf("Documento de prueba con contenido suficiente.")


@pytest.fixture
def pdf_otro() -> bytes:
    return _crear_pdf("Segundo documento con contenido único.")


@pytest.fixture
def pdf_invalido() -> bytes:
    return b"Este no es un PDF valido"


def _post_pdf(client: TestClient, nombre: str, contenido: bytes) -> dict:
    """Helper para hacer POST de un PDF y devolver la respuesta JSON."""
    response = client.post(
        "/extraer", files={"file": (nombre, io.BytesIO(contenido), "application/pdf")}
    )
    return response


class TestFlujoCompleto:
    """Tests del flujo: request → extracción → guardado → response."""

    def test_flujo_completo_exitoso(
        self, client: TestClient, pdf_valido: bytes
    ) -> None:
        response = _post_pdf(client, "doc.pdf", pdf_valido)

        assert response.status_code == 200
        data = response.json()
        assert data["exito"] is True
        assert data["nombre_archivo"] == "doc.pdf"
        assert "Documento de prueba" in data["texto"]

    def test_persistencia_datos(
        self, client: TestClient, repo: DocumentoRepository, pdf_valido: bytes
    ) -> None:
        _post_pdf(client, "persistencia.pdf", pdf_valido)

        doc = repo.obtener_por_nombre("persistencia.pdf")
        assert doc is not None
        assert doc["nombre"] == "persistencia.pdf"
        assert "Documento de prueba" in doc["texto"]
        assert isinstance(doc["fecha_procesamiento"], datetime)

    def test_multiples_requests(
        self,
        client: TestClient,
        repo: DocumentoRepository,
        pdf_valido: bytes,
        pdf_otro: bytes,
    ) -> None:
        _post_pdf(client, "doc1.pdf", pdf_valido)
        _post_pdf(client, "doc2.pdf", pdf_otro)

        assert repo.contar() == 2
        assert repo.obtener_por_nombre("doc1.pdf") is not None
        assert repo.obtener_por_nombre("doc2.pdf") is not None


class TestManejoErrores:
    """Tests de manejo de errores."""

    def test_pdf_invalido_no_se_guarda(
        self, client: TestClient, repo: DocumentoRepository, pdf_invalido: bytes
    ) -> None:
        conteo_inicial = repo.contar()

        response = _post_pdf(client, "invalido.pdf", pdf_invalido)

        assert response.status_code == 400
        assert repo.contar() == conteo_inicial


class TestRecuperacionDatos:
    """Tests de listado y recuperación."""

    def test_listar_documentos(
        self, client: TestClient, repo: DocumentoRepository, pdf_valido: bytes
    ) -> None:
        _post_pdf(client, "alpha.pdf", pdf_valido)
        _post_pdf(client, "beta.pdf", pdf_valido)

        todos = repo.listar_todos()
        assert len(todos) == 2
        assert {doc["nombre"] for doc in todos} == {"alpha.pdf", "beta.pdf"}

    def test_recuperar_por_id(
        self, client: TestClient, repo: DocumentoRepository, pdf_valido: bytes
    ) -> None:
        _post_pdf(client, "por_id.pdf", pdf_valido)

        doc_por_nombre = repo.obtener_por_nombre("por_id.pdf")
        doc_por_id = repo.obtener_por_id(doc_por_nombre["id"])

        assert doc_por_id["nombre"] == "por_id.pdf"
        assert doc_por_id["texto"] == doc_por_nombre["texto"]


class TestIntegridadDatos:
    """Tests de integridad y consistencia."""

    def test_texto_coincide(
        self, client: TestClient, repo: DocumentoRepository, pdf_valido: bytes
    ) -> None:
        response = _post_pdf(client, "integridad.pdf", pdf_valido)
        texto_respuesta = response.json()["texto"]

        doc = repo.obtener_por_nombre("integridad.pdf")
        assert doc["texto"] == texto_respuesta

    def test_fecha_es_datetime_valido(
        self, client: TestClient, repo: DocumentoRepository, pdf_valido: bytes
    ) -> None:
        before = datetime.utcnow()
        _post_pdf(client, "fecha.pdf", pdf_valido)
        after = datetime.utcnow()

        doc = repo.obtener_por_nombre("fecha.pdf")
        assert isinstance(doc["fecha_procesamiento"], datetime)
        assert before <= doc["fecha_procesamiento"] <= after
