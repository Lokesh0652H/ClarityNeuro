"""Pydantic schemas for experiments and tracking."""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class ExperimentCreate(BaseModel):
    """Schema for registering or launching an experiment."""
    name: str = Field(..., max_length=128, description="Human-readable experiment name")
    experiment_type: str = Field(..., description="Type of experiment: 'train', 'fine_tune', 'prune', 'eval'")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Hyperparameters and config dict")
    model_id: Optional[str] = Field(None, description="Optional associated model registry ID")
    dataset_id: Optional[str] = Field(None, description="Optional associated dataset ID")


class ExperimentResponse(BaseModel):
    """Schema for returning experiment record information."""
    id: str = Field(..., description="Experiment UUID")
    name: str = Field(..., description="Experiment name")
    experiment_type: str = Field(..., description="Experiment category")
    config: Optional[Dict[str, Any]] = Field(None, description="Configuration parameters")
    results: Optional[Dict[str, Any]] = Field(None, description="Results and recorded metrics")
    model_id: Optional[str] = Field(None, description="Associated model ID")
    dataset_id: Optional[str] = Field(None, description="Associated dataset ID")
    status: str = Field(..., description="Status: 'pending', 'running', 'completed', 'failed'")
    created_at: datetime = Field(..., description="Creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")

    model_config = ConfigDict(from_attributes=True)
