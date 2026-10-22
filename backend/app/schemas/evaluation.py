"""Pydantic schemas for model evaluation and validation benchmarks."""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ClassMetric(BaseModel):
    """Metrics for a single class label."""
    precision: float = Field(..., ge=0.0, le=1.0)
    recall: float = Field(..., ge=0.0, le=1.0)
    f1_score: float = Field(..., ge=0.0, le=1.0)
    support: int = Field(..., ge=0)


class EvaluationResult(BaseModel):
    """Comprehensive test set evaluation metrics."""
    model_id: str = Field(..., description="Model ID evaluated")
    model_name: str = Field(..., description="Human-readable model name")
    dataset_name: str = Field(..., description="Dataset split evaluated on")
    test_samples: int = Field(..., ge=0, description="Total number of evaluated test samples")
    accuracy: float = Field(..., ge=0.0, le=1.0, description="Overall classification accuracy")
    precision: float = Field(..., ge=0.0, le=1.0, description="Macro-averaged precision")
    recall: float = Field(..., ge=0.0, le=1.0, description="Macro-averaged recall")
    f1_score: float = Field(..., ge=0.0, le=1.0, description="Macro-averaged F1 score")
    roc_auc: Optional[float] = Field(None, ge=0.0, le=1.0, description="Macro-averaged ROC AUC score")
    ece: Optional[float] = Field(None, ge=0.0, le=1.0, description="Expected Calibration Error")
    confusion_matrix: List[List[int]] = Field(..., description="Square confusion matrix [actual x predicted]")
    class_labels: List[str] = Field(..., description="Ordered class labels corresponding to matrix rows/cols")
    class_metrics: Dict[str, ClassMetric] = Field(..., description="Detailed metrics broken down by class")
    evaluation_date: datetime = Field(default_factory=datetime.utcnow, description="Evaluation timestamp")

    model_config = ConfigDict(from_attributes=True)
