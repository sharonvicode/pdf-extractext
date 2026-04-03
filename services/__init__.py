"""
Paquete services - Contiene la lógica de negocio de la aplicación.

Los servicios encapsulan las operaciones de negocio y reglas
de la aplicación, independientes de la capa de presentación.
"""

from services.user_service import UserService

__all__ = ["UserService"]
