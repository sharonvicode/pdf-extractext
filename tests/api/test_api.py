"""
Tests de integración para los endpoints de la API.

Este módulo contiene tests que verifican el comportamiento de los endpoints
HTTP sin depender de la implementación interna de los servicios.
Los servicios son mockeados para garantizar tests rápidos y deterministas.
"""

import io
import pytest
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient

from main import create_app
from app.routes.extraer import get_documento_repository


@pytest.fixture
def client():
    """Fixture que proporciona un TestClient configurado."""
    app = create_app()
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

    def test_post_extraer_con_pdf_valido_retorna_status_200(self, client):
        """Verifica que un PDF válido responde con status 200 y datos correctos."""
        contenido_pdf = b"Contenido simulado de PDF"
        nombre_archivo = "documento_valido.pdf"
        texto_extraido = "Texto extraído del documento de prueba"

        archivo = io.BytesIO(contenido_pdf)

        with patch("app.routes.extraer.procesar_pdf") as mock_procesar:
            mock_procesar.return_value = texto_extraido

            response = client.post(
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

    def test_post_extraer_con_pdf_vacio_retorna_status_422(self, client):
        """Verifica que un PDF vacío responde con status 422."""
        contenido_pdf = b"Contenido"
        nombre_archivo = "documento_vacio.pdf"

        archivo = io.BytesIO(contenido_pdf)

        with patch("app.routes.extraer.procesar_pdf") as mock_procesar:
            from app.services.pdf_service import PDFEmptyError
            mock_procesar.side_effect = PDFEmptyError(
                "El PDF no contiene texto suficiente"
            )

            response = client.post(
                "/extraer",
                files={"file": (nombre_archivo, archivo, "application/pdf")}
            )

        assert response.status_code == 422
        json_response = response.json()
        assert "texto" in json_response["detail"].lower() or "PDF" in json_response["detail"]

    def test_post_extraer_con_pdf_invalido_retorna_status_400(self, client):
        """Verifica que un PDF inválido responde con status 400."""
        contenido_pdf = b"Contenido corrupto"
        nombre_archivo = "documento_invalido.pdf"

        archivo = io.BytesIO(contenido_pdf)

        with patch("app.routes.extraer.procesar_pdf") as mock_procesar:
            from app.services.pdf_service import PDFExtractionError
            mock_procesar.side_effect = PDFExtractionError(
                "El archivo PDF está corrupto"
            )

            response = client.post(
                "/extraer",
                files={"file": (nombre_archivo, archivo, "application/pdf")}
            )

        assert response.status_code == 400
        json_response = response.json()
        assert "PDF" in json_response["detail"] or "inválido" in json_response["detail"].lower()

    def test_post_extraer_con_error_interno_retorna_status_500(self, client):
        """Verifica que un error interno responde con status 500."""
        contenido_pdf = b"Contenido"
        nombre_archivo = "documento.pdf"

        archivo = io.BytesIO(contenido_pdf)

        with patch("app.routes.extraer.procesar_pdf") as mock_procesar:
            mock_procesar.side_effect = Exception("Error inesperado del sistema")

            response = client.post(
                "/extraer",
                files={"file": (nombre_archivo, archivo, "application/pdf")}
            )

        assert response.status_code == 500
        json_response = response.json()
        assert "Error interno" in json_response["detail"]

    def test_post_extraer_valida_estructura_respuesta_json(self, client):
        """Verifica que la respuesta JSON tiene la estructura esperada."""
        contenido_pdf = b"Contenido de prueba"
        nombre_archivo = "documento.pdf"
        texto_extraido = "Texto de ejemplo extraído"

        archivo = io.BytesIO(contenido_pdf)

        with patch("app.routes.extraer.procesar_pdf") as mock_procesar:
            mock_procesar.return_value = texto_extraido

            response = client.post(
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
def client_con_repo(mock_documento_repo):
    """Proporciona un TestClient con el repositorio de documentos mockeado."""
    app = create_app()
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
