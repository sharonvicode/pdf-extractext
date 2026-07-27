import sqlite3
from datetime import datetime
from typing import Optional
from app.core.logger import logger
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
            "id": str(row[0]),
            "nombre": row[1],
            "texto": row[2],
            "fecha_procesamiento": datetime.fromisoformat(row[3]),
        }

    def guardar(self, nombre: str, texto: str, fecha_procesamiento: datetime) -> str:
        """Guarda un documento y retorna su ID generado."""
        logger.info("Intentando guardar documento en SQLite: %s", nombre)  # AGREGAR ESTA LÍNEA
        try:  # AGREGAR TRY
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
            id_insertado= str(cursor.lastrowid)
            logger.info("Documento guardado con id %s para: %s", id_insertado, nombre) 
            return id_insertado
        except Exception as exc:
            logger.error("Error al guardar documento en SQLite %s: %s", nombre, str(exc))
            raise


    def obtener_por_id(self, documento_id: str) -> Optional[dict]:
        """Recupera un documento por ID o None si no existe."""
        logger.info("Intentando obtener documento en SQLite por id %s", documento_id)  # AGREGAR
        try:
            cursor = self._conn.cursor()
            cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE id = ?", (documento_id,))
            row = cursor.fetchone()

            if row is None:
                logger.info("No se encontró documento en SQLite para id %s", documento_id)
                return None

            resultado = self._row_to_dict(row)
            logger.info("Documento obtenido de SQLite por id %s", documento_id)  # AGREGAR
            return resultado
        except Exception as exc:  # AGREGAR EXCEPT
            logger.error("Error al consultar documento en SQLite por id %s: %s", documento_id, str(exc))  # AGREGAR
            return None

    def obtener_por_nombre(self, nombre: str) -> Optional[dict]:
        """Recupera un documento por nombre exacto."""
        logger.info("Intentando obtener documento en SQLite por nombre %s", nombre)  # AGREGAR
        try:
            cursor = self._conn.cursor()
            cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE nombre = ?", (nombre,))
            row = cursor.fetchone()

            if row is None:
                logger.info("No se encontró documento en SQLite para nombre %s", nombre)
                return None

            resultado = self._row_to_dict(row)
            logger.info("Documento obtenido de SQLite por nombre %s", nombre)
            return self._row_to_dict(row)
        except Exception as exc:
            logger.error("Error al consultar documento en SQLite por nombre %s: %s", nombre, str(exc))
            return None

        return self._row_to_dict(row)

    def listar_todos(self) -> list[dict]:
        """Lista todos los documentos ordenados por ID."""
        logger.info("Intentando listar todos los documentos en SQLite")  # AGREGAR
        try:
            cursor = self._conn.cursor()
            cursor.execute(f"SELECT * FROM {TABLE_NAME} ORDER BY id")
            rows = cursor.fetchall()

            resultado = [self._row_to_dict(row) for row in rows]
            logger.info("Listado de documentos en SQLite completado: %d documentos", len(resultado))  # AGREGAR
            return resultado
        except Exception as exc:  # AGREGAR EXCEPT
            logger.error("Error al listar documentos en SQLite: %s", str(exc))  # AGREGAR
            raise
        return [self._row_to_dict(row) for row in rows]

    def actualizar(
        self,
        documento_id: str,
        nombre: str,
        texto: str,
        fecha_procesamiento: datetime,
    ) -> bool:
        """Actualiza un documento existente. Retorna True si existía, False si no."""
        logger.info("Intentando actualizar documento en SQLite con id %s", documento_id)  # AGREGAR
        try:
            cursor = self._conn.cursor()
            cursor.execute(
                f"UPDATE {TABLE_NAME} SET nombre = ?, texto = ?, fecha_procesamiento = ? WHERE id = ?",
                (nombre, texto, fecha_procesamiento.isoformat(), documento_id),
            )
            self._conn.commit()
        
            actualizado = cursor.rowcount > 0
            if actualizado:
                logger.info("Documento actualizado en SQLite con id %s", documento_id)  # AGREGAR
            else:
                logger.info("No se encontró documento en SQLite para actualizar id %s", documento_id)  # AGREGAR
            return actualizado
        except Exception as exc:  # AGREGAR EXCEPT
            logger.error("Error al actualizar documento en SQLite con id %s: %s", documento_id, str(exc))  # AGREGAR
            raise

    def eliminar(self, documento_id: str) -> bool:
        """Elimina un documento. Retorna True si existía, False si no."""
        logger.info("Intentando eliminar documento en SQLite con id %s", documento_id)  # AGREGAR
        try:
            cursor = self._conn.cursor()
            cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE id = ?", (documento_id,))
            self._conn.commit()
            eliminado = cursor.rowcount > 0
            if eliminado:
                logger.info("Documento eliminado en SQLite con id %s", documento_id)  # AGREGAR
            else:
                logger.info("No se encontró documento en SQLite para eliminar id %s", documento_id)  # AGREGAR
            return eliminado
        except Exception as exc:  # AGREGAR EXCEPT
            logger.error("Error al eliminar documento en SQLite con id %s: %s", documento_id, str(exc))  # AGREGAR
            raise
    def contar(self) -> int:
        """Cuenta el total de documentos almacenados."""
        logger.info("Intentando contar documentos en SQLite")  # AGREGAR
        try:
            cursor = self._conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
            total = cursor.fetchone()[0]
            return total
        except Exception as exc:  # AGREGAR EXCEPT
            logger.error("Error al contar documentos en SQLite: %s", str(exc))  # AGREGAR
        raise