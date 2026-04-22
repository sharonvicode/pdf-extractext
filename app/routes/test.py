from fastapi import APIRouter
from app.services.test_service import guardar

router = APIRouter()

@router.get("/test")
def test():
    guardar("test")
    return {"msg": "guardado"}
