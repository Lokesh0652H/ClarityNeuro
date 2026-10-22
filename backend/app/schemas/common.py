"""Common Pydantic v2 schemas used across endpoints."""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class HealthResponse(BaseModel):
    """System health status response."""
    status: str = Field(..., description="Overall service status ('healthy', 'degraded', 'unhealthy')")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="UTC timestamp of the health check")
    version: str = Field(..., description="Application version")
    database_connected: bool = Field(..., description="Whether the database is reachable and active")
    model_loaded: bool = Field(..., description="Whether the ML inference model is loaded in memory")
    dataset_available: bool = Field(True, description="Whether the brain MRI dataset is accessible on disk")
    environment: str = Field("production", description="Environment stage")

    model_config = ConfigDict(from_attributes=True)


class ModelStatus(BaseModel):
    """Detailed model operational status."""
    available: bool = Field(..., description="True if model is loaded and ready for inference")
    model_name: str = Field(..., description="Name of the model")
    architecture: str = Field(..., description="Network architecture")
    device: str = Field(..., description="Device executing inference (e.g. cpu, cuda)")
    checkpoint_path: str = Field(..., description="Path to model checkpoint")
    checkpoint_exists: bool = Field(..., description="Whether the checkpoint file exists on disk")
    num_classes: int = Field(..., description="Number of target classes")
    classes: List[str] = Field(..., description="List of target class names")
    error: Optional[str] = Field(None, description="Diagnostic error message if model unavailable")

    model_config = ConfigDict(from_attributes=True)


class DatasetStatus(BaseModel):
    """Detailed dataset status and split validation."""
    available: bool = Field(..., description="True if dataset directory exists and contains images")
    dataset_path: str = Field(..., description="Path to the dataset directory")
    exists: bool = Field(..., description="Whether dataset directory exists on disk")
    total_images: int = Field(0, description="Total number of images detected")
    class_distribution: Dict[str, int] = Field(default_factory=dict, description="Image count per class")
    splits: Dict[str, int] = Field(default_factory=dict, description="Image counts per split partition")
    error: Optional[str] = Field(None, description="Diagnostic error if dataset unavailable")

    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic container for paginated query results."""
    items: List[T] = Field(..., description="Page items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Number of items per page")
    total_pages: int = Field(..., ge=0, description="Total calculated pages")


class MessageResponse(BaseModel):
    """Standard generic response with message and status."""
    success: bool = True
    message: str
    detail: Optional[Any] = None
