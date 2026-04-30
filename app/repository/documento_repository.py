import sqlite3
from datetime import datetime
from typing import Optional

# ============================================================================
# CONSTANTES
# ============================================================================

TABLE_NAME = "documentos"

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

    @staticmethod
    def _row_to_dict(row) -> dict:
        """Convierte una fila SQLite a diccionario."""
        return {
            "id": row[0],
            "nombre": row[1],
            "texto": row[2],
            "fecha_procesamiento": datetime.fromisoformat(row[3]),
        }

    def guardar(self, nombre: str, texto: str, fecha_procesamiento: datetime) -> int:
        """Guarda un documento y retorna su ID generado."""
        cursor = self._conn.cursor()
        cursor.execute(
            f"""
            INSERT INTO {TABLE_NAME}
            (nombre, texto, fecha_procesamiento)
            VALUES (?, ?, ?)
            """,
            (nombre, texto, fecha_procesamiento.isoformat()),
        )



        self._conn.commit()
        return cursor.lastrowid

    def obtener_por_id(self, documento_id: int) -> Optional[dict]:
        """Recupera un documento por ID o None si no existe."""
        cursor = self._conn.cursor()
        cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE id = ?", (documento_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_dict(row)

    def obtener_por_nombre(self, nombre: str) -> Optional[dict]:
        """Recupera un documento por nombre exacto."""
        cursor = self._conn.cursor()
        cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE nombre = ?", (nombre,))
        row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_dict(row)

    def listar_todos(self) -> list[dict]:
        """Lista todos los documentos ordenados por ID."""
        cursor = self._conn.cursor()
        cursor.execute(f"SELECT * FROM {TABLE_NAME} ORDER BY id")
        rows = cursor.fetchall()

        return [self._row_to_dict(row) for row in rows]

    def actualizar(
        self,
        documento_id: int,
        nombre: str,
        texto: str,
        fecha_procesamiento: datetime,
    ) -> bool:
        """Actualiza un documento existente. Retorna True si existía, False si no."""
        cursor = self._conn.cursor()
        cursor.execute(
            f"UPDATE {TABLE_NAME} SET nombre = ?, texto = ?, fecha_procesamiento = ? WHERE id = ?",
            (nombre, texto, fecha_procesamiento.isoformat(), documento_id),
        )
        self._conn.commit()
        return cursor.rowcount > 0

    def eliminar(self, documento_id: int) -> bool:
        """Elimina un documento. Retorna True si existía, False si no."""
        cursor = self._conn.cursor()
        cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE id = ?", (documento_id,))
        self._conn.commit()
        return cursor.rowcount > 0

    def contar(self) -> int:
        """Cuenta el total de documentos almacenados."""
        cursor = self._conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
        return cursor.fetchone()[0]
