"""
Tests de integración para la capa de persistencia de documentos PDF.

Este módulo prueba el repositorio de documentos siguiendo:
- TDD: Tests como especificación del comportamiento observable
- SOLID: Interfaz clara como abstracción, tests independientes de implementación
- KISS: Tests concisos, sin duplicación, enfocados en comportamiento real
- Independencia: Fixtures proporcionan BD limpia por test

Las pruebas usan SQLite en memoria para aislamiento completo.
"""

import sqlite3
import pytest
from datetime import datetime, timezone
from typing import Generator, Optional


# ============================================================================
# INTERFAZ DEL REPOSITORIO
# ============================================================================


class DocumentoRepository:
    """
    Repositorio para persistencia de documentos PDF.

    Contrato de la capa de persistencia - los tests verifican este comportamiento.
    """

    def __init__(self, connection: sqlite3.Connection):
        self._conn = connection

    def guardar(self, nombre: str, texto: str, fecha_procesamiento: datetime) -> int:
        """Guarda un documento y retorna su ID generado."""
        cursor = self._conn.cursor()
        cursor.execute(
            "INSERT INTO documentos (nombre, texto, fecha_procesamiento) VALUES (?, ?, ?)",
            (nombre, texto, fecha_procesamiento.isoformat()),
        )
        self._conn.commit()
        return cursor.lastrowid

    def obtener_por_id(self, documento_id: int) -> Optional[dict]:
        """Recupera un documento por ID o None si no existe."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM documentos WHERE id = ?", (documento_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        return {
            "id": row[0],
            "nombre": row[1],
            "texto": row[2],
            "fecha_procesamiento": datetime.fromisoformat(row[3]),
        }

    def obtener_por_nombre(self, nombre: str) -> Optional[dict]:
        """Recupera un documento por nombre exacto."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM documentos WHERE nombre = ?", (nombre,))
        row = cursor.fetchone()

        if row is None:
            return None

        return {
            "id": row[0],
            "nombre": row[1],
            "texto": row[2],
            "fecha_procesamiento": datetime.fromisoformat(row[3]),
        }

    def listar_todos(self) -> list[dict]:
        """Lista todos los documentos ordenados por ID."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM documentos ORDER BY id")
        rows = cursor.fetchall()

        return [
            {
                "id": row[0],
                "nombre": row[1],
                "texto": row[2],
                "fecha_procesamiento": datetime.fromisoformat(row[3]),
            }
            for row in rows
        ]

    def eliminar(self, documento_id: int) -> bool:
        """Elimina un documento. Retorna True si existía, False si no."""
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM documentos WHERE id = ?", (documento_id,))
        self._conn.commit()
        return cursor.rowcount > 0

    def contar(self) -> int:
        """Cuenta el total de documentos almacenados."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM documentos")
        return cursor.fetchone()[0]


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def db_connection() -> Generator[sqlite3.Connection, None, None]:
    """Proporciona conexión SQLite en memoria con esquema limpio."""
    conn = sqlite3.connect(":memory:")
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
    """Proporciona repositorio inicializado con BD limpia."""
    return DocumentoRepository(db_connection)


# ============================================================================
# TESTS: CRUD Básico
# ============================================================================


class TestGuardado:
    """Tests de guardado de documentos."""

    def test_guardar_devuelve_id_valido(self, repositorio: DocumentoRepository) -> None:
        """Guardar documento retorna ID entero positivo."""
        doc_id = repositorio.guardar(
            nombre="doc.pdf",
            texto="contenido",
            fecha_procesamiento=datetime.now(timezone.utc),
        )

        assert isinstance(doc_id, int)
        assert doc_id > 0

    def test_guardar_persiste_datos_correctamente(
        self, repositorio: DocumentoRepository
    ) -> None:
        """Los datos guardados se recuperan sin modificación."""
        fecha = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)

        doc_id = repositorio.guardar(
            nombre="mi_doc.pdf",
            texto="texto de prueba",
            fecha_procesamiento=fecha,
        )

        documento = repositorio.obtener_por_id(doc_id)

        assert documento["nombre"] == "mi_doc.pdf"
        assert documento["texto"] == "texto de prueba"
        assert documento["fecha_procesamiento"] == fecha


class TestRecuperacion:
    """Tests de recuperación de documentos."""

    def test_obtener_por_id_devuelve_documento_correcto(
        self, repositorio: DocumentoRepository
    ) -> None:
        """Recuperar por ID retorna el documento con todos sus campos."""
        doc_id = repositorio.guardar(
            nombre="buscar.pdf",
            texto="texto a recuperar",
            fecha_procesamiento=datetime.now(timezone.utc),
        )

        documento = repositorio.obtener_por_id(doc_id)

        assert documento is not None
        assert documento["id"] == doc_id
        assert documento["nombre"] == "buscar.pdf"
        assert documento["texto"] == "texto a recuperar"

    def test_obtener_por_id_inexistente_devuelve_none(
        self, repositorio: DocumentoRepository
    ) -> None:
        """Buscar ID inexistente retorna None sin excepción."""
        resultado = repositorio.obtener_por_id(9999)

        assert resultado is None

    def test_obtener_por_nombre_devuelve_documento_correcto(
        self, repositorio: DocumentoRepository
    ) -> None:
        """Recuperar por nombre exacto retorna el documento correspondiente."""
        repositorio.guardar(
            nombre="otro.pdf",
            texto="otro",
            fecha_procesamiento=datetime.now(timezone.utc),
        )
        repositorio.guardar(
            nombre="unico.pdf",
            texto="texto único",
            fecha_procesamiento=datetime.now(timezone.utc),
        )

        documento = repositorio.obtener_por_nombre("unico.pdf")

        assert documento is not None
        assert documento["nombre"] == "unico.pdf"
        assert documento["texto"] == "texto único"


class TestListadoYConteo:
    """Tests de operaciones sobre múltiples documentos."""

    def test_listar_todos_devuelve_todos_los_documentos(
        self, repositorio: DocumentoRepository
    ) -> None:
        """Listar retorna todos los documentos guardados."""
        repositorio.guardar(
            nombre="a.pdf", texto="A", fecha_procesamiento=datetime.now(timezone.utc)
        )
        repositorio.guardar(
            nombre="b.pdf", texto="B", fecha_procesamiento=datetime.now(timezone.utc)
        )

        documentos = repositorio.listar_todos()

        assert len(documentos) == 2
        assert {d["nombre"] for d in documentos} == {"a.pdf", "b.pdf"}

    def test_contar_devuelve_total_correcto(
        self, repositorio: DocumentoRepository
    ) -> None:
        """Contar refleja el número exacto de documentos."""
        assert repositorio.contar() == 0

        for i in range(3):
            repositorio.guardar(
                nombre=f"doc{i}.pdf",
                texto=f"texto{i}",
                fecha_procesamiento=datetime.now(timezone.utc),
            )

        assert repositorio.contar() == 3


class TestEliminacion:
    """Tests de eliminación de documentos."""

    def test_eliminar_existente_devuelve_true_y_elimina(
        self, repositorio: DocumentoRepository
    ) -> None:
        """Eliminar documento existente retorna True y el documento desaparece."""
        doc_id = repositorio.guardar(
            nombre="borrar.pdf",
            texto="texto",
            fecha_procesamiento=datetime.now(timezone.utc),
        )

        eliminado = repositorio.eliminar(doc_id)

        assert eliminado is True
        assert repositorio.obtener_por_id(doc_id) is None
        assert repositorio.contar() == 0

    def test_eliminar_inexistente_devuelve_false(
        self, repositorio: DocumentoRepository
    ) -> None:
        """Eliminar ID inexistente retorna False sin error."""
        resultado = repositorio.eliminar(9999)

        assert resultado is False


# ============================================================================
# TESTS: Integridad
# ============================================================================


class TestIntegridad:
    """Tests de integridad de datos."""

    def test_ids_generados_son_unicos(self, repositorio: DocumentoRepository) -> None:
        """Múltiples guardados generan IDs únicos e incrementales."""
        ids = [
            repositorio.guardar(
                nombre=f"doc{i}.pdf",
                texto=f"texto{i}",
                fecha_procesamiento=datetime.now(timezone.utc),
            )
            for i in range(5)
        ]

        assert len(set(ids)) == 5  # Unicidad
        assert ids == sorted(ids)  # Incrementalidad


# ============================================================================
# TESTS: Casos Límite
# ============================================================================


class TestCasosLimite:
    """Tests de casos extremos y edge cases."""

    def test_guardar_con_texto_vacio(self, repositorio: DocumentoRepository) -> None:
        """Guardar texto vacío (string vacío) funciona según esquema."""
        doc_id = repositorio.guardar(
            nombre="vacio.pdf",
            texto="",
            fecha_procesamiento=datetime.now(timezone.utc),
        )

        documento = repositorio.obtener_por_id(doc_id)
        assert documento["texto"] == ""

    def test_guardar_con_caracteres_especiales_unicode(
        self, repositorio: DocumentoRepository
    ) -> None:
        """Unicode y emojis se preservan correctamente."""
        nombre = "doc_ñáéíóú_中文.pdf"
        texto = "Texto con emojis 🎉 y símbolos € £ ¥"

        doc_id = repositorio.guardar(
            nombre=nombre, texto=texto, fecha_procesamiento=datetime.now(timezone.utc)
        )

        documento = repositorio.obtener_por_id(doc_id)
        assert documento["nombre"] == nombre
        assert documento["texto"] == texto

    def test_guardar_con_fecha_extrema(self, repositorio: DocumentoRepository) -> None:
        """Fechas extremas se almacenan correctamente."""
        fecha_max = datetime.max

        doc_id = repositorio.guardar(
            nombre="extremo.pdf", texto="texto", fecha_procesamiento=fecha_max
        )

        documento = repositorio.obtener_por_id(doc_id)
        assert documento["fecha_procesamiento"] == fecha_max
