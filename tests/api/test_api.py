"""
Tests de integración para los endpoints de la API.

Este módulo contiene tests que verifican el comportamiento de los endpoints
HTTP sin depender de la implementación interna de los servicios.
El extractor y el repositorio se reemplazan con app.dependency_overrides
(seam HTTP de CONTEXT.md) para garantizar tests rápidos y deterministas.
"""

import io
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter

from app.core.dependencies import get_documento_repository, get_extractor_texto
from main import create_app


def _extractor_que_devuelve(texto: str):
    """Extractor falso (puerto ExtractorTexto) que siempre devuelve `texto`."""

    def extractor(ruta_pdf):
        return texto

    return extractor


def _extractor_que_lanza(error: Exception):
    """Extractor falso (puerto ExtractorTexto) que siempre lanza `error`."""

    def extractor(ruta_pdf):
        raise error

    return extractor


def _pdf_valido() -> bytes:
    """Genera los bytes de un PDF real de una página en blanco."""
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


@pytest.fixture
def app():
    """Aplicación FastAPI nueva por test, para poder sobrescribir dependencias."""
    return create_app()


@pytest.fixture
def client(app):
    """Fixture que proporciona un TestClient configurado."""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests para el endpoint GET /health/"""

    def test_get_health_returns_status_200(self, client):
        """Verifica que el endpoint health responde con status 200."""
        response = client.get("/health/")

        assert response.status_code == 200

    def test_get_health_returns_ok_status_in_json(self, client):
        """Verifica que el endpoint health devuelve JSON con status ok."""
        response = client.get("/health/")
        json_response = response.json()

        assert json_response == {"status": "ok"}


class TestExtraerEndpoint:
    """Tests para el endpoint POST /extraer"""

    def test_post_extraer_con_pdf_valido_retorna_status_200(self, app, client_con_repo):
        """Verifica que un PDF válido responde con status 200 y datos correctos."""
        contenido_pdf = _pdf_valido()
        nombre_archivo = "documento_valido.pdf"
        texto_extraido = "Texto extraído del documento de prueba"

        archivo = io.BytesIO(contenido_pdf)

        app.dependency_overrides[get_extractor_texto] = lambda: _extractor_que_devuelve(texto_extraido)

        response = client_con_repo.post(
            "/extraer",
            files={"file": (nombre_archivo, archivo, "application/pdf")}
        )

        assert response.status_code == 200
        json_response = response.json()
        assert json_response["exito"] is True
        assert json_response["texto"] == texto_extraido
        assert json_response["nombre_archivo"] == nombre_archivo

    def test_post_extraer_con_archivo_no_pdf_retorna_status_400(self, client):
        """Verifica que un archivo sin extensión PDF responde con status 400."""
        contenido_txt = b"Contenido de texto"
        nombre_archivo = "archivo.txt"

        archivo = io.BytesIO(contenido_txt)

        response = client.post(
            "/extraer",
            files={"file": (nombre_archivo, archivo, "text/plain")}
        )

        assert response.status_code == 400
        json_response = response.json()
        assert ".pdf" in json_response["detail"].lower()

    def test_post_extraer_sin_archivo_retorna_status_422(self, client):
        """Verifica que la petición sin archivo responde con status 422."""
        response = client.post("/extraer")

        assert response.status_code == 422

    def test_post_extraer_con_pdf_vacio_retorna_status_422(self, app, client):
        """Verifica que un PDF vacío responde con status 422."""
        contenido_pdf = _pdf_valido()
        nombre_archivo = "documento_vacio.pdf"

        archivo = io.BytesIO(contenido_pdf)

        # Sin texto extraído, el servicio lanza PDFEmptyError ("no contiene texto suficiente")
        app.dependency_overrides[get_extractor_texto] = lambda: _extractor_que_devuelve("")

        response = client.post(
            "/extraer",
            files={"file": (nombre_archivo, archivo, "application/pdf")}
        )

        assert response.status_code == 422
        json_response = response.json()
        assert "texto" in json_response["detail"].lower() or "PDF" in json_response["detail"]

    def test_post_extraer_con_pdf_invalido_retorna_status_400(self, app, client):
        """Verifica que un PDF inválido responde con status 400."""
        contenido_pdf = b"Contenido corrupto"
        nombre_archivo = "documento_invalido.pdf"

        archivo = io.BytesIO(contenido_pdf)

        # El servicio traduce el ValueError del extractor a PDFExtractionError
        app.dependency_overrides[get_extractor_texto] = lambda: _extractor_que_lanza(
            ValueError("El archivo PDF está corrupto")
        )

        response = client.post(
            "/extraer",
            files={"file": (nombre_archivo, archivo, "application/pdf")}
        )

        assert response.status_code == 400
        json_response = response.json()
        assert "PDF" in json_response["detail"] or "inválido" in json_response["detail"].lower()

    def test_post_extraer_con_error_interno_retorna_status_500(self, app, client_con_repo, mock_documento_repo):
        """Verifica que un error interno responde con status 500."""
        contenido_pdf = _pdf_valido()
        nombre_archivo = "documento.pdf"

        archivo = io.BytesIO(contenido_pdf)

        # Cualquier error del extractor se traduce a PDFExtractionError (400), así que
        # el error inesperado se provoca en el otro paso del flujo: la persistencia.
        app.dependency_overrides[get_extractor_texto] = lambda: _extractor_que_devuelve(
            "Texto extraído del documento de prueba"
        )
        mock_documento_repo.guardar.side_effect = Exception("Error inesperado del sistema")

        response = client_con_repo.post(
            "/extraer",
            files={"file": (nombre_archivo, archivo, "application/pdf")}
        )

        assert response.status_code == 500
        json_response = response.json()
        assert "Error interno" in json_response["detail"]

    def test_post_extraer_valida_estructura_respuesta_json(self, app, client_con_repo):
        """Verifica que la respuesta JSON tiene la estructura esperada."""
        contenido_pdf = _pdf_valido()
        nombre_archivo = "documento.pdf"
        texto_extraido = "Texto de ejemplo extraído"

        archivo = io.BytesIO(contenido_pdf)

        app.dependency_overrides[get_extractor_texto] = lambda: _extractor_que_devuelve(texto_extraido)

        response = client_con_repo.post(
            "/extraer",
            files={"file": (nombre_archivo, archivo, "application/pdf")}
        )

        json_response = response.json()
        assert "exito" in json_response
        assert "texto" in json_response
        assert "nombre_archivo" in json_response
        assert isinstance(json_response["exito"], bool)
        assert isinstance(json_response["texto"], str)
        assert isinstance(json_response["nombre_archivo"], str)


@pytest.fixture
def mock_documento_repo():
    """Proporciona un mock del repositorio de documentos."""
    return MagicMock()


@pytest.fixture
def client_con_repo(app, mock_documento_repo):
    """Proporciona un TestClient con el repositorio de documentos mockeado."""
    app.dependency_overrides[get_documento_repository] = lambda: mock_documento_repo
    return TestClient(app)




class TestDocumentosEndpoints:
    """Tests para los endpoints GET y DELETE /documentos"""

    # -- GET /documentos --

    def test_get_documentos_retorna_200_y_lista_con_elementos(self, client_con_repo, mock_documento_repo):
        """GET /documentos con datos: retorna 200 y lista de documentos."""
        mock_documento_repo.listar_todos.return_value = [
            {
                "id": "1",
                "nombre": "doc1.pdf",
                "texto": "texto extraido",
                "fecha_procesamiento": "2024-01-01T00:00:00",
            }
        ]

        response = client_con_repo.get("/documentos")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == "1"

    def test_get_documentos_retorna_200_y_lista_vacia(self, client_con_repo, mock_documento_repo):
        """GET /documentos sin datos: retorna 200 y lista vacía."""
        mock_documento_repo.listar_todos.return_value = []

        response = client_con_repo.get("/documentos")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_get_documentos_con_error_interno_retorna_500(self, client_con_repo, mock_documento_repo):
        """GET /documentos con error del repositorio: retorna 500."""
        mock_documento_repo.listar_todos.side_effect = Exception("Error de base de datos")

        response = client_con_repo.get("/documentos")

        assert response.status_code == 500

    # -- GET /documentos/{id} --

    def test_get_documento_por_id_exitoso_retorna_200(self, client_con_repo, mock_documento_repo):
        """GET /documentos/{id} existente: retorna 200 y el documento."""
        mock_documento_repo.obtener_por_id.return_value = {
            "id": "1",
            "nombre": "doc1.pdf",
            "texto": "texto extraido",
            "fecha_procesamiento": "2024-01-01T00:00:00",
        }

        response = client_con_repo.get("/documentos/1")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "1"

    def test_get_documento_por_id_no_existente_retorna_404(self, client_con_repo, mock_documento_repo):
        """GET /documentos/{id} inexistente: retorna 404."""
        mock_documento_repo.obtener_por_id.return_value = None

        response = client_con_repo.get("/documentos/999")

        assert response.status_code == 404

    # -- DELETE /documentos/{id} --

    def test_delete_documento_exitoso_retorna_204(self, client_con_repo, mock_documento_repo):
        """DELETE /documentos/{id} existente: retorna 204."""
        mock_documento_repo.eliminar.return_value = True

        response = client_con_repo.delete("/documentos/1")

        assert response.status_code == 204

    def test_delete_documento_no_existente_retorna_404(self, client_con_repo, mock_documento_repo):
        """DELETE /documentos/{id} inexistente: retorna 404."""
        mock_documento_repo.eliminar.return_value = False

        response = client_con_repo.delete("/documentos/999")

        assert response.status_code == 404

