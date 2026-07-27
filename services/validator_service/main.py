from fastapi import FastAPI

from api.routes import router

app = FastAPI(title="PDF Validator Service")
app.include_router(router)
