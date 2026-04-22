from fastapi import APIRouter
from app.services.test_service import guardar

router = APIRouter()

@router.post("/usuario")
def crear():
    return guardar("Juan")