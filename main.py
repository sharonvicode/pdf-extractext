from fastapi import FastAPI

from app.routes import extraer, health, test
from app.routes.extraer import get_documento_repository
from app.repository.mongodb_repository import MongoDBDocumentoRepository


def create_app():
    app = FastAPI(title="PDF Extract API")
    app.include_router(health.router)
    app.include_router(test.router)
    app.include_router(extraer.router)

    # Configurar dependencia por defecto: usar MongoDB en producción
    app.dependency_overrides[get_documento_repository] = lambda: (
        MongoDBDocumentoRepository()
    )

    return app


app = create_app()
