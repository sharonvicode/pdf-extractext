from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.logger import logger
from app.routes import (
    documentos_delete,
    documentos_get,
    extraer,
    health,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Servidor iniciando")
    yield
    logger.info("Servidor cerrando")


def create_app():
    app = FastAPI(title="PDF Extract API", lifespan=lifespan)

    app.include_router(health.router)
    app.include_router(extraer.router)
    app.include_router(documentos_get.router)
    app.include_router(documentos_delete.router)

    return app


app = create_app()
