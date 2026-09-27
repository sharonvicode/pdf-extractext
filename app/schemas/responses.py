"""Esquemas Pydantic para las respuestas de la API."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Respuesta del health check."""

    status: str


class TestResponse(BaseModel):
    """Respuesta del endpoint de test."""

    msg: str


class ExtraccionResponse(BaseModel):
    """Respuesta exitosa de extracción de texto PDF."""

    exito: bool
    texto: str
    nombre_archivo: str

class ValidatorResponse(BaseModel):
    """Respuesta del microservicio de validación."""

    valido: bool
    mensaje: str | None = None


class ExtractorResponse(BaseModel):
    """Respuesta del microservicio de extracción."""

    texto: str


class PersistenceResponse(BaseModel):
    """Respuesta del microservicio de persistencia."""

    id: str