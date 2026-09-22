"""
Decorador para logging uniforme de errores en los repositorios.

Evita repetir el mismo bloque try/except/log/raise en cada método
de las implementaciones de DocumentoRepositoryInterface.
"""

import functools

from app.core.logger import logger


def registrar_error(mensaje: str):
    """
    Decorador para métodos de repositorio: si la operación lanza una
    excepción, la loguea con `mensaje` y la vuelve a lanzar sin modificarla.
    """

    def decorador(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                logger.error("%s: %s", mensaje, exc)
                raise

        return wrapper

    return decorador
