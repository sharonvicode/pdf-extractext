"""
chequear si la API funciona.
"""

from fastapi import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["health"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "message": "API is running!"}