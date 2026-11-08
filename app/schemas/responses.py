"""Esquemas Pydantic para las respuestas de la API."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Respuesta del health check."""

    status: str


class ExtraccionResponse(BaseModel):
    """Respuesta exitosa de extracción de texto PDF."""

    exito: bool
    texto: str
    nombre_archivo: str
