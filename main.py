"""
PDF ExtraText API - Punto de entrada principal.

Esta aplicación sigue el patrón MVC (Modelo-Vista-Controlador) con principios de Clean Code.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from routes import user_routes, health_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestiona el ciclo de vida de la aplicación."""
    # Startup
    print("Iniciando aplicación...")
    yield
    # Shutdown
    print("Cerrando aplicación...")


def create_application() -> FastAPI:
    """
    Factory para crear la instancia de FastAPI.

    Returns:
        FastAPI: Instancia configurada de la aplicación.
    """
    application = FastAPI(
        title="PDF ExtraText API",
        description="API para extracción y procesamiento de texto de PDFs",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Configuración CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Registro de routers
    _register_routers(application)

    return application


def _register_routers(app: FastAPI) -> None:
    """
    Registra todos los routers de la aplicación.

    Args:
        app: Instancia de FastAPI.
    """
    app.include_router(health_routes.router, prefix="/api/v1", tags=["health"])
    app.include_router(user_routes.router, prefix="/api/v1", tags=["users"])


# Crear instancia de la aplicación
app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
