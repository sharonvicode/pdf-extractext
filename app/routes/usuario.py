from fastapi import APIRouter
from app.services.test_service import crear_usuario

router = APIRouter()

@router.post("/usuario")
def crear():
    return crear_usuario("Juan")