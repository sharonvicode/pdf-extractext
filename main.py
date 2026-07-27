from fastapi import FastAPI

from app.core.logger import logger
from app.core.dependencies import get_documento_repository

from app.routes import (
    extraer,
    health,
    test,
    documentos_get,
    documentos_delete,
)

from app.repository.mongodb_repository import MongoDBDocumentoRepository


def create_app():

    app = FastAPI(
        title="PDF Extract API"
    )

    @app.on_event("startup")
    async def startup_event():
        logger.info("Servidor iniciando")


    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Servidor cerrando")


    app.include_router(health.router)
    app.include_router(test.router)

    app.include_router(extraer.router)
    app.include_router(documentos_get.router)
    app.include_router(documentos_delete.router)


    # Repositorio usado en producción
    app.dependency_overrides[get_documento_repository] = (
        lambda: MongoDBDocumentoRepository()
    )


    return app


app = create_app()