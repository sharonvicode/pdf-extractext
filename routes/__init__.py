"""
Paquete routes - Define los endpoints HTTP de la aplicación.

Las rutas manejan las peticiones HTTP y delegan la lógica
a los controladores correspondientes.
"""

from routes import user_routes, health_routes

__all__ = ["user_routes", "health_routes"]
