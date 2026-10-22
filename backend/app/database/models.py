"""SQLAlchemy models for NeuroScan XAI."""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    Boolean,
    DateTime,
    JSON,
    Text,
)
from app.database.session import Base


def generate_uuid() -> str:
    """Generate a random UUID4 as a string."""
    return str(uuid.uuid4())


class AnalysisRecord(Base):
    """Stores inference analysis results and uncertainty metrics."""

    __tablename__ = "analysis_records"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    filename = Column(String(255), nullable=False)
    predicted_class = Column(String(64), nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    probabilities = Column(JSON, nullable=False)  # Dict mapping class names to floats
    entropy = Column(Float, nullable=False)
    normalized_entropy = Column(Float, nullable=False)
    prediction_margin = Column(Float, nullable=False)
    inference_time_ms = Column(Float, nullable=False)
    model_version = Column(String(64), nullable=False, default="efficientnet-b0-v1")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    gradcam_path = Column(String(512), nullable=True)

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "id": self.id,
            "filename": self.filename,
            "predicted_class": self.predicted_class,
            "confidence": self.confidence,
            "probabilities": self.probabilities,
            "entropy": self.entropy,
            "normalized_entropy": self.normalized_entropy,
            "prediction_margin": self.prediction_margin,
            "inference_time_ms": self.inference_time_ms,
            "model_version": self.model_version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "gradcam_path": self.gradcam_path,
        }


class ModelRegistry(Base):
    """Metadata tracking trained models, architectures, and performance."""

    __tablename__ = "model_registry"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    name = Column(String(128), nullable=False, unique=True)
    architecture = Column(String(128), nullable=False)
    num_classes = Column(Integer, nullable=False, default=4)
    class_mapping = Column(JSON, nullable=False)
    dataset_id = Column(String(36), nullable=True)
    checkpoint_path = Column(String(512), nullable=False)
    training_config = Column(JSON, nullable=True)
    metrics = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    def to_dict(self) -> dict:
        """Convert model record to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "architecture": self.architecture,
            "num_classes": self.num_classes,
            "class_mapping": self.class_mapping,
            "dataset_id": self.dataset_id,
            "checkpoint_path": self.checkpoint_path,
            "training_config": self.training_config,
            "metrics": self.metrics,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_active": self.is_active,
        }


class DatasetRegistry(Base):
    """Tracks datasets, class distributions, and validation status."""

    __tablename__ = "dataset_registry"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    name = Column(String(128), nullable=False, unique=True)
    source_url = Column(String(512), nullable=True)
    license = Column(String(128), nullable=True)
    total_images = Column(Integer, default=0, nullable=False)
    class_distribution = Column(JSON, nullable=True)
    splits = Column(JSON, nullable=True)
    validation_status = Column(String(64), default="pending", nullable=False)
    manifest_path = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        """Convert dataset record to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "source_url": self.source_url,
            "license": self.license,
            "total_images": self.total_images,
            "class_distribution": self.class_distribution,
            "splits": self.splits,
            "validation_status": self.validation_status,
            "manifest_path": self.manifest_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ExperimentRecord(Base):
    """Tracks training and evaluation experiments."""

    __tablename__ = "experiment_records"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    name = Column(String(128), nullable=False)
    experiment_type = Column(String(64), nullable=False)
    config = Column(JSON, nullable=True)
    results = Column(JSON, nullable=True)
    model_id = Column(String(36), nullable=True)
    dataset_id = Column(String(36), nullable=True)
    status = Column(String(64), default="created", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    def to_dict(self) -> dict:
        """Convert experiment record to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "experiment_type": self.experiment_type,
            "config": self.config,
            "results": self.results,
            "model_id": self.model_id,
            "dataset_id": self.dataset_id,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class AuditExecution(Base):
    """Tracks fairness and shortcut bias audit executions."""

    __tablename__ = "audit_executions"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    audit_type = Column(String(64), nullable=False)  # 'fairness' or 'shortcut'
    config = Column(JSON, nullable=True)
    results = Column(JSON, nullable=True)
    model_id = Column(String(36), nullable=True)
    dataset_id = Column(String(36), nullable=True)
    status = Column(String(64), default="completed", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    def to_dict(self) -> dict:
        """Convert audit record to dictionary."""
        return {
            "id": self.id,
            "audit_type": self.audit_type,
            "config": self.config,
            "results": self.results,
            "model_id": self.model_id,
            "dataset_id": self.dataset_id,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
