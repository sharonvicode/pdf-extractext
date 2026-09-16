"""
Utilidades para manejo uniforme de errores HTTP en las rutas.
"""

import functools
import inspect

from fastapi import HTTPException

from app.core.logger import logger


def manejar_error_interno(mensaje: str):
    """
    Decorador para endpoints: deja pasar los HTTPException ya lanzados
    (por ejemplo un 404 explícito) y convierte cualquier otra excepción
    no controlada en un 500 con `mensaje`, logueando la causa real.

    Funciona tanto con endpoints `def` como `async def`.
    """

    def decorador(func):
        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except HTTPException:
                    raise
                except Exception as exc:
                    logger.error("%s: %s", mensaje, str(exc))
                    raise HTTPException(status_code=500, detail=mensaje)

            return wrapper

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except HTTPException:
                raise
            except Exception as exc:
                logger.error("%s: %s", mensaje, str(exc))
                raise HTTPException(status_code=500, detail=mensaje)

        return wrapper

    return decorador
