"""Pydantic v2 schemas for MRI analysis, explainability, and uncertainty."""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class AnalysisResponse(BaseModel):
    """Result of inference and uncertainty estimation on an MRI scan."""
    analysis_id: str = Field(..., description="Unique UUID identifier for this analysis")
    filename: str = Field(..., description="Original filename of the analyzed image")
    predicted_class: str = Field(..., description="Predicted diagnosis class")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Highest predicted probability")
    probabilities: Dict[str, float] = Field(..., description="Softmax probability distribution across classes")
    entropy: float = Field(..., ge=0.0, description="Shannon entropy of the probability distribution (in nats)")
    normalized_entropy: float = Field(..., ge=0.0, le=1.0, description="Entropy normalized by log(K)")
    prediction_margin: float = Field(..., ge=0.0, le=1.0, description="Difference between top 2 class probabilities")
    inference_time_ms: float = Field(..., description="Duration taken for inference in milliseconds")
    model_version: str = Field(..., description="Identifier and version of the model used")
    gradcam_path: Optional[str] = Field(None, description="URL or relative path to generated Grad-CAM overlay")

    model_config = ConfigDict(from_attributes=True)


class AnalysisHistoryItem(BaseModel):
    """Summary item for the historical analysis log list."""
    id: str = Field(..., description="Analysis ID")
    filename: str = Field(..., description="Name of analyzed file")
    predicted_class: str = Field(..., description="Predicted class")
    confidence: float = Field(..., description="Prediction confidence")
    entropy: float = Field(..., description="Shannon entropy")
    normalized_entropy: float = Field(..., description="Normalized entropy")
    prediction_margin: float = Field(..., description="Prediction margin")
    inference_time_ms: float = Field(..., description="Inference latency in ms")
    model_version: str = Field(..., description="Model version")
    created_at: datetime = Field(..., description="Timestamp of analysis")
    gradcam_path: Optional[str] = Field(None, description="Path to Grad-CAM heatmap if generated")

    model_config = ConfigDict(from_attributes=True)


class AnalysisDetail(BaseModel):
    """Complete detail of a recorded analysis."""
    id: str = Field(..., description="Analysis ID")
    filename: str = Field(..., description="Filename")
    predicted_class: str = Field(..., description="Predicted class")
    confidence: float = Field(..., description="Prediction confidence")
    probabilities: Dict[str, float] = Field(..., description="Full class probability map")
    entropy: float = Field(..., description="Shannon entropy")
    normalized_entropy: float = Field(..., description="Normalized entropy")
    prediction_margin: float = Field(..., description="Prediction margin")
    inference_time_ms: float = Field(..., description="Inference latency in ms")
    model_version: str = Field(..., description="Model version")
    created_at: datetime = Field(..., description="Timestamp of analysis")
    gradcam_path: Optional[str] = Field(None, description="Grad-CAM visualization path")

    model_config = ConfigDict(from_attributes=True)


class BatchAnalysisResponse(BaseModel):
    """Container for batch analysis of multiple MRI scans."""
    items: List[AnalysisResponse] = Field(..., description="List of individual analysis responses")
    total_processed: int = Field(..., description="Count of successfully analyzed images")
    total_time_ms: float = Field(..., description="Total elapsed processing time in ms")


class ExplainabilityResponse(BaseModel):
    """Grad-CAM / Grad-CAM++ explainability visualization result."""
    analysis_id: Optional[str] = Field(None, description="Associated analysis ID if persisted")
    target_class: str = Field(..., description="Class for which Grad-CAM was computed")
    target_class_idx: int = Field(..., description="Index of target class")
    confidence: float = Field(..., description="Model confidence for target class")
    method: str = Field("gradcam++", description="XAI method used (e.g., 'gradcam', 'gradcam++')")
    heatmap_path: str = Field(..., description="Server path to the generated heatmap/overlay image")
    heatmap_url: str = Field(..., description="API endpoint to download or view the heatmap")
    heatmap_base64: Optional[str] = Field(None, description="Base64 encoded JPEG overlay if requested")
    salient_regions_summary: Optional[Dict[str, float]] = Field(
        None, description="Region attribution percentages (quadrants: Q1, Q2, Q3, Q4)"
    )


class UncertaintyPassResult(BaseModel):
    """Detailed Monte Carlo Dropout uncertainty response."""
    analysis_id: Optional[str] = Field(None, description="Associated analysis ID")
    passes: int = Field(..., description="Number of stochastic forward passes executed")
    mean_probabilities: Dict[str, float] = Field(..., description="Averaged predictive probabilities")
    variance: Dict[str, float] = Field(..., description="Variance per class across stochastic passes")
    standard_deviation: Dict[str, float] = Field(..., description="Standard deviation per class")
    predictive_entropy: float = Field(..., description="Entropy of the mean predictive distribution")
    expected_entropy: float = Field(..., description="Expected entropy across individual passes (aleatoric)")
    mutual_information: float = Field(..., description="Mutual information / Epistemic uncertainty")
    confidence_interval: Dict[str, List[float]] = Field(
        ..., description="95% confidence intervals [lower, upper] per class"
    )
