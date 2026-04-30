from fastapi import APIRouter

from app.schemas import HealthResponse

router = APIRouter(
    prefix="/health",
    tags=["health"],
)

@router.get("/", response_model=HealthResponse)
def health_check():
    return {"status": "ok"}
