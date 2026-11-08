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
    return {"status": HEALTH_STATUS_OK}
