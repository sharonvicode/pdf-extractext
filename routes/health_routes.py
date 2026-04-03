"""
Rutas de health check - Monitoreo del sistema.

Este módulo define endpoints para verificar el estado
de la aplicación y sus dependencias.
"""

from datetime import datetime
from typing import Dict

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Verifica el estado de la aplicación.

    Returns:
        Información del estado del sistema.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "pdf-extractext-api",
    }


@router.get("/ping")
async def ping() -> Dict[str, str]:
    """
    Endpoint simple para verificar que el servicio responde.

    Returns:
        Respuesta pong.
    """
    return {"message": "pong"}
