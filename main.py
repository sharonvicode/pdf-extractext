from fastapi import FastAPI

from app.routes import extraer, health, test

def create_app():
    app = FastAPI(title="PDF Extract API")
    app.include_router(health.router)
    app.include_router(test.router)
    app.include_router(extraer.router)
    return app

app = create_app()
