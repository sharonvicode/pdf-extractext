from fastapi import FastAPI

from app.core.logger import logger
from app.routes import (
    documentos_delete,
    documentos_get,
    extraer,
    health,
    test,
)


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

    return app


app = create_app()