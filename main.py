#Creacion de la aplicacion
from fastapi import FastAPI

from app.routes import health
from app.routes import test
from app.routes import usuario

def create_app() -> FastAPI:
    #Funcion que crea y configura la aplicacion de FastAPI
    app = FastAPI(
        title="PDF Extract API",
        description="A simple FastAPI application",
        version="0.1.0",
    )

    # Incluye el router
    app.include_router(health.router)
    app.include_router(test.router)
    app.include_router(usuario.router)
    return app

app = create_app()