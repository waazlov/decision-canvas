from __future__ import annotations

from fastapi import APIRouter

from app.models.base import StrictBaseModel

router = APIRouter(prefix="/system", tags=["system"])


class HealthResponse(StrictBaseModel):
    status: str
    app: str


@router.get("/health", response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    return HealthResponse(status="ok", app="DecisionCanvas API")
