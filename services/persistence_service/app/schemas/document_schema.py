from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DocumentCreate(BaseModel):
    filename: str = Field(..., description="Nombre del archivo")
    content: str = Field(..., description="Contenido del documento")
    metadata: dict = Field(default_factory=dict, description="Metadatos adicionales")


class DocumentResponse(BaseModel):
    document_id: str = Field(..., description="ID del documento creado")


class DocumentOut(BaseModel):
    id: str
    filename: str
    content: str
    metadata: dict
    created_at: datetime


class ErrorResponse(BaseModel):
    detail: str