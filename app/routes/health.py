from fastapi import APIRouter

from app.schemas import HealthResponse

router = APIRouter(
    prefix="/health",
    tags=["health"],
)

HEALTH_STATUS_OK = "ok"


@router.get("/", response_model=HealthResponse)
def get_health_status():
    return {"status": HEALTH_STATUS_OK}
