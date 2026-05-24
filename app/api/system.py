from fastapi import APIRouter

from app.schemas.common import ApiResponse


router = APIRouter(prefix="/api/v1", tags=["system"])


@router.get("/healthz")
def healthz() -> ApiResponse:
    return ApiResponse(data={"status": "ok"})
