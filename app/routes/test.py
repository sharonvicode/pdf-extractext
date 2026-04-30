from fastapi import APIRouter

from app.schemas import TestResponse
from app.services.test_service import guardar

router = APIRouter()

@router.get("/test", response_model=TestResponse)
def test():
    guardar("test")
    return {"msg": "guardado"}
