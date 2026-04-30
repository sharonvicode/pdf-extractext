from fastapi import APIRouter

from app.schemas import TestResponse
from app.services.test_service import guardar

router = APIRouter()

TEST_ENTITY_NAME = "test"
TEST_SUCCESS_MESSAGE = "guardado"


@router.get("/test", response_model=TestResponse)
def save_test_entry():
    guardar(TEST_ENTITY_NAME)
    return {"msg": TEST_SUCCESS_MESSAGE}
