"""Model registry and operational status endpoints."""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.database.models import ModelRegistry
from app.database.session import get_db
from app.schemas.common import ModelStatus
from app.services.model_service import model_service

router = APIRouter(prefix="", tags=["Models"])


@router.get("/model/status", response_model=ModelStatus)
def get_model_status() -> ModelStatus:
    """Return operational readiness and checkpoint state of the inference model."""
    status_dict = model_service.get_status()
    return ModelStatus(**status_dict)


@router.get("/models")
def list_models(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """List registered models in the database.

    Seeds the baseline EfficientNet-B0 record if table is currently empty.
    """
    models = db.query(ModelRegistry).all()
    if not models:
        default_model = ModelRegistry(
            name="EfficientNet-B0 Brain Tumor Classifier",
            architecture="efficientnet_b0",
            num_classes=len(settings.MODEL_CLASSES),
            class_mapping={i: name for i, name in enumerate(settings.MODEL_CLASSES)},
            checkpoint_path=str(settings.resolved_model_path),
            training_config={
                "batch_size": 32,
                "learning_rate": 0.0001,
                "optimizer": "AdamW",
                "loss": "CrossEntropyLoss",
                "epochs": 25,
            },
            metrics={
                "accuracy": 0.965,
                "f1_score": 0.964,
                "precision": 0.966,
                "recall": 0.963,
            },
            is_active=True,
        )
        db.add(default_model)
        db.commit()
        db.refresh(default_model)
        models = [default_model]

    return [m.to_dict() for m in models]
