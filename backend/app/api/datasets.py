"""Dataset information and status inspection endpoints."""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.models import DatasetRegistry
from app.database.session import get_db
from app.schemas.common import DatasetStatus
from app.services.dataset_service import dataset_service

router = APIRouter(prefix="", tags=["Datasets"])


@router.get("/dataset/status", response_model=DatasetStatus)
def get_dataset_status() -> DatasetStatus:
    """Inspect actual local filesystem to verify dataset presence, splits, and counts."""
    status_data = dataset_service.get_status()
    return DatasetStatus(**status_data)


@router.get("/datasets")
def list_datasets(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """List all registered dataset records from the database.

    Automatically syncs filesystem scan if database registry is empty.
    """
    records = db.query(DatasetRegistry).all()
    if not records:
        # Sync with actual filesystem
        synced = dataset_service.sync_with_db(db)
        if synced:
            records = [synced]

    return [r.to_dict() for r in records]
