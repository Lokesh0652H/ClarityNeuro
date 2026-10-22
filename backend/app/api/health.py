"""System health check endpoint."""

from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.database.session import get_db
from app.schemas.common import HealthResponse
from app.services.model_service import model_service

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
def get_health_status(db: Session = Depends(get_db)) -> HealthResponse:
    """Return actual system health, checking database connectivity and model readiness."""
    db_connected = False
    try:
        db.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        db_connected = False

    model_loaded = model_service.is_loaded and model_service.model is not None

    if db_connected and model_loaded:
        status_str = "healthy"
    elif db_connected:
        status_str = "degraded"
    else:
        status_str = "unhealthy"

    from app.services.dataset_service import dataset_service
    ds_status = dataset_service.get_status()
    dataset_avail = ds_status.get("available", False)

    return HealthResponse(
        status=status_str,
        timestamp=datetime.utcnow(),
        version=settings.VERSION,
        database_connected=db_connected,
        model_loaded=model_loaded,
        dataset_available=dataset_avail,
        environment="development" if settings.DEBUG else "production",
    )
