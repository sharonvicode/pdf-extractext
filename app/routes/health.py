from fastapi import APIRouter

from app.core.logger import logger
from app.schemas import HealthResponse

router = APIRouter(
    prefix="/health",
    tags=["health"],
)

HEALTH_STATUS_OK = "ok"


@router.get("/", response_model=HealthResponse)
def get_health_status():
    logger.info("Recibiendo petición HTTP GET /health/")
    try:
        logger.info("Procesamiento de /health/ completado exitosamente")
        return {"status": HEALTH_STATUS_OK}
    except Exception as exc:
        logger.error("Error al procesar la petición /health/: %s", str(exc))
        raise
