"""
Paquete controllers - Contiene los controladores de la aplicación.

Los controladores actúan como intermediarios entre las rutas (HTTP)
y los servicios de negocio, manejando la lógica de presentación.
"""

from controllers.user_controller import UserController

__all__ = ["UserController"]
