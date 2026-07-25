"""
Configuracion centralizada del sistema de logging.

Proporciona un logger reutilizable para toda la aplicacion.
Uso:
    from app.core.logger import logger
    logger.info("Mensaje informativo")
"""

import logging
import sys


# ==== Formato del log ====
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _configurar_logger() -> logging.Logger:
    """
    Configura y retorna un logger centralizado.

    Returns:
        Logger configurado con formato y nivel establecidos.
    """
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)

        formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        logger.propagate = False

    return logger


# ==== Logger reutilizable ====
logger = _configurar_logger()
