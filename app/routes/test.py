from fastapi import APIRouter

from app.core.logger import logger
from app.schemas import TestResponse
from app.services.test_service import guardar

router = APIRouter()

TEST_ENTITY_NAME = "test"
TEST_SUCCESS_MESSAGE = "guardado"


@router.get("/test", response_model=TestResponse)
def save_test_entry():
    logger.info("Recibiendo petición HTTP GET /test")
    try:
        guardar(TEST_ENTITY_NAME)
        logger.info("Procesamiento de /test completado exitosamente")
        return {"msg": TEST_SUCCESS_MESSAGE}
    except Exception as exc:
        logger.error("Error al procesar la petición /test: %s", str(exc))
        raise
