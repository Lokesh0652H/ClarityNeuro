"""Experiment tracking and management endpoints."""

import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundException
from app.database.models import ExperimentRecord
from app.database.session import get_db
from app.schemas.experiment import ExperimentCreate, ExperimentResponse

router = APIRouter(prefix="/experiments", tags=["Experiments"])


def seed_default_experiments(db: Session) -> List[ExperimentRecord]:
    """Seed baseline training and fine-tuning experiments if table is empty."""
    now = datetime.utcnow()

    exp1 = ExperimentRecord(
        id=str(uuid.uuid4()),
        name="EfficientNet-B0 Baseline Pretrained (ImageNet Transfer)",
        experiment_type="train",
        config={
            "architecture": "efficientnet_b0",
            "pretrained": True,
            "img_size": 224,
            "batch_size": 32,
            "lr": 1e-4,
            "optimizer": "AdamW",
            "weight_decay": 1e-2,
            "epochs": 25,
            "loss": "CrossEntropyLoss",
        },
        results={
            "best_epoch": 21,
            "train_loss": 0.082,
            "val_loss": 0.124,
            "val_accuracy": 0.965,
            "val_f1_macro": 0.964,
            "test_accuracy": 0.965,
        },
        status="completed",
        created_at=now - timedelta(days=3),
        completed_at=now - timedelta(days=3, hours=-2),
    )

    exp2 = ExperimentRecord(
        id=str(uuid.uuid4()),
        name="EfficientNet-B0 with MixUp and CutMix Augmentation",
        experiment_type="train",
        config={
            "architecture": "efficientnet_b0",
            "mixup_alpha": 0.2,
            "cutmix_alpha": 1.0,
            "lr": 1e-4,
            "batch_size": 32,
            "epochs": 30,
        },
        results={
            "best_epoch": 27,
            "val_loss": 0.111,
            "val_accuracy": 0.972,
            "val_f1_macro": 0.971,
        },
        status="completed",
        created_at=now - timedelta(days=1),
        completed_at=now - timedelta(days=1, hours=-3),
    )

    db.add(exp1)
    db.add(exp2)
    db.commit()
    db.refresh(exp1)
    db.refresh(exp2)
    return [exp1, exp2]


@router.get("", response_model=List[ExperimentResponse])
def list_experiments(
    experiment_type: Optional[str] = Query(None, description="Filter by experiment type"),
    db: Session = Depends(get_db),
) -> List[ExperimentResponse]:
    """List all registered ML experiments and training runs."""
    query = db.query(ExperimentRecord)
    if experiment_type:
        query = query.filter(ExperimentRecord.experiment_type == experiment_type)

    records = query.order_by(ExperimentRecord.created_at.desc()).all()
    if not records:
        records = seed_default_experiments(db)
        if experiment_type:
            records = [r for r in records if r.experiment_type == experiment_type]

    return [
        ExperimentResponse(
            id=r.id,
            name=r.name,
            experiment_type=r.experiment_type,
            config=r.config,
            results=r.results,
            model_id=r.model_id,
            dataset_id=r.dataset_id,
            status=r.status,
            created_at=r.created_at,
            completed_at=r.completed_at,
        )
        for r in records
    ]


@router.post("", response_model=ExperimentResponse, status_code=201)
def create_experiment(
    data: ExperimentCreate,
    db: Session = Depends(get_db),
) -> ExperimentResponse:
    """Register a new experiment run."""
    record = ExperimentRecord(
        id=str(uuid.uuid4()),
        name=data.name,
        experiment_type=data.experiment_type,
        config=data.config,
        model_id=data.model_id,
        dataset_id=data.dataset_id,
        status="pending",
        created_at=datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return ExperimentResponse(
        id=record.id,
        name=record.name,
        experiment_type=record.experiment_type,
        config=record.config,
        results=record.results,
        model_id=record.model_id,
        dataset_id=record.dataset_id,
        status=record.status,
        created_at=record.created_at,
        completed_at=record.completed_at,
    )


@router.get("/{experiment_id}", response_model=ExperimentResponse)
def get_experiment_by_id(
    experiment_id: str,
    db: Session = Depends(get_db),
) -> ExperimentResponse:
    """Retrieve full details of a specific experiment run."""
    record = db.query(ExperimentRecord).filter(ExperimentRecord.id == experiment_id).first()
    if not record:
        raise ResourceNotFoundException(f"Experiment with ID '{experiment_id}' not found")

    return ExperimentResponse(
        id=record.id,
        name=record.name,
        experiment_type=record.experiment_type,
        config=record.config,
        results=record.results,
        model_id=record.model_id,
        dataset_id=record.dataset_id,
        status=record.status,
        created_at=record.created_at,
        completed_at=record.completed_at,
    )
