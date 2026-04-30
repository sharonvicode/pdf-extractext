from pydantic import BaseModel, Field
from typing import Optional


class PDFBase(BaseModel):
    """
    Base común para documentos PDF.
    """
    nombre: str = Field(..., description="Nombre del archivo PDF")


class PDFCreate(PDFBase):
    """
    Schema para crear un documento en la base de datos.
    """
    texto: str = Field(..., description="Texto extraído del PDF")
    checksum: str = Field(..., description="Hash único del archivo")


class PDFInDB(PDFCreate):
    """
    Representa cómo se guarda en la base de datos.
    """
    id: Optional[str] = Field(None, alias="_id")

    class Config:
        populate_by_name = True


class PDFResponse(BaseModel):
    """
    Respuesta exitosa del endpoint.
    """
    nombre_archivo: str
    texto: str
    exito: bool


class PDFError(BaseModel):
    """
    Respuesta de error estándar.
    """
    detail: str