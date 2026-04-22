from fastapi import APIRouter
from app.services.test_service import guardar

router = APIRouter()

@router.post("/extraer")
def crear():
    return guardar("pdf1")
