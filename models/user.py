"""
Modelos de datos para usuarios.

Este módulo define las entidades y esquemas de validación
para el recurso User siguiendo principios de Clean Code.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    """
    Entidad User - Representa un usuario en el sistema.

    Attributes:
        id: Identificador único del usuario.
        email: Correo electrónico del usuario.
        full_name: Nombre completo del usuario.
        is_active: Indica si el usuario está activo.
        created_at: Fecha de creación del usuario.
        updated_at: Fecha de última actualización.
    """

    id: int
    email: EmailStr
    full_name: str
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Configuración del modelo."""

        frozen = True


class UserCreate(BaseModel):
    """
    Esquema para crear un nuevo usuario.

    Attributes:
        email: Correo electrónico del usuario (obligatorio).
        full_name: Nombre completo del usuario (obligatorio).
        is_active: Estado del usuario (por defecto True).
    """

    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    is_active: bool = True


class UserUpdate(BaseModel):
    """
    Esquema para actualizar un usuario existente.

    Todos los campos son opcionales para permitir actualizaciones parciales.

    Attributes:
        email: Nuevo correo electrónico (opcional).
        full_name: Nuevo nombre completo (opcional).
        is_active: Nuevo estado (opcional).
    """

    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """
    Esquema para la respuesta de usuario.

    Excluye información sensible y formatea los datos para la API.

    Attributes:
        id: Identificador del usuario.
        email: Correo electrónico.
        full_name: Nombre completo.
        is_active: Estado del usuario.
        created_at: Fecha de creación.
    """

    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: datetime

    class Config:
        """Configuración para serialización."""

        from_attributes = True
