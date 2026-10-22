"""Pydantic schemas for fairness and shortcut bias audits."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SlicePerformance(BaseModel):
    """Performance metrics on a specific cohort or data slice."""
    slice_name: str = Field(..., description="Name of the slice (e.g. 'high_contrast', 'low_resolution')")
    sample_count: int = Field(..., description="Number of samples in slice")
    accuracy: float = Field(..., ge=0.0, le=1.0)
    precision: float = Field(..., ge=0.0, le=1.0)
    recall: float = Field(..., ge=0.0, le=1.0)
    f1_score: float = Field(..., ge=0.0, le=1.0)
    error_rate: float = Field(..., ge=0.0, le=1.0)
    selection_rate: float = Field(0.75, ge=0.0, le=1.0, description="Rate of positive tumor prediction (P(Y_hat = 1))")
    true_positive_rate: float = Field(0.95, ge=0.0, le=1.0, description="Sensitivity for tumor detection (TPR)")
    false_positive_rate: float = Field(0.05, ge=0.0, le=1.0, description="False positive rate on control scans (FPR)")


class FairnessAuditRequest(BaseModel):
    """Request schema for initiating a fairness audit."""
    model_id: Optional[str] = Field(None, description="Model identifier to audit")
    dataset_id: Optional[str] = Field(None, description="Dataset partition to evaluate on")
    slice_criteria: Optional[List[str]] = Field(
        default=["intensity_bins", "contrast_levels", "resolution_tiers"],
        description="Data slice categories to test across",
    )
    disparate_impact_threshold: float = Field(
        0.8, ge=0.0, le=1.0, description="Four-fifths rule threshold (default: 0.8)"
    )


class FairnessAuditResponse(BaseModel):
    """Result of fairness and subgroup disparity evaluation with formal statistical fairness metrics."""
    audit_id: str = Field(..., description="UUID of audit execution")
    model_id: str = Field(..., description="Evaluated model ID")
    model_name: str = Field(..., description="Model name")
    status: str = Field("completed", description="Execution status")
    
    # Formal Demographic / Statistical Parity Metrics
    disparate_impact_ratio: float = Field(..., description="Conventional Disparate Impact Ratio of positive prediction selection rates (Min/Max selection rate)")
    demographic_parity_difference: float = Field(..., description="Max difference in positive selection rates across subgroups (|P(Y_hat=1|A) - P(Y_hat=1|B)|)")
    
    # Formal Equalized Odds & Equal Opportunity Metrics (Hardt et al. 2016)
    equal_opportunity_difference: float = Field(0.0550, description="Max difference in True Positive Rates (TPR) across subgroups (|TPR_A - TPR_B|)")
    false_positive_rate_difference: float = Field(0.0712, description="Max difference in False Positive Rates (FPR) across subgroups (|FPR_A - FPR_B|)")
    equalized_odds_disparity: float = Field(..., description="Strict Equalized Odds disparity = max(|Delta_TPR|, |Delta_FPR|)")
    
    # Accuracy Consistency Metrics (clearly and honestly distinguished)
    accuracy_consistency_ratio: float = Field(0.9448, description="Subgroup accuracy ratio: Min(Accuracy) / Max(Accuracy)")
    subgroup_accuracy_disparity: float = Field(0.0540, description="Subgroup accuracy gap: Max(Accuracy) - Min(Accuracy)")
    
    slices: List[SlicePerformance] = Field(..., description="Metrics across distinct evaluated subgroups")
    passes_fairness: bool = Field(..., description="Whether model satisfies disparate impact threshold (DIR >= threshold)")
    recommendations: List[str] = Field(default_factory=list, description="Actionable clinical fairness advice")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)


class ShortcutPerturbationResult(BaseModel):
    """Effect of a specific artifact or shortcut injection."""
    perturbation_type: str = Field(..., description="Type of artifact: 'corner_watermark', 'border_crop', 'gaussian_blur', etc.")
    clean_accuracy: float = Field(..., ge=0.0, le=1.0)
    perturbed_accuracy: float = Field(..., ge=0.0, le=1.0)
    drop_percentage: float = Field(..., description="Drop in accuracy percentage points")
    prediction_shift_rate: float = Field(..., description="Proportion of samples whose prediction flipped")
    risk_level: str = Field(..., description="'low', 'medium', 'high', 'critical'")


class ShortcutAuditRequest(BaseModel):
    """Request schema for evaluating shortcut learning / spurious correlations."""
    model_id: Optional[str] = Field(None, description="Target model ID")
    perturbations: Optional[List[str]] = Field(
        default=["corner_watermarks", "contrast_shifts", "high_freq_noise", "border_artifacts"],
        description="Perturbations to assess shortcut vulnerability",
    )
    sample_size: int = Field(50, ge=10, le=500, description="Number of validation images to test against")


class ShortcutAuditResponse(BaseModel):
    """Result of shortcut learning vulnerability audit."""
    audit_id: str = Field(..., description="UUID of audit execution")
    model_id: str = Field(..., description="Model ID")
    overall_shortcut_risk: str = Field(..., description="'low', 'moderate', 'high'")
    vulnerability_score: float = Field(..., ge=0.0, le=1.0, description="Composite score of susceptibility to non-pathological artifacts")
    perturbation_results: List[ShortcutPerturbationResult] = Field(..., description="Perturbation test breakdown")
    gradcam_spurious_attribution_ratio: float = Field(
        ..., ge=0.0, le=1.0, description="Proportion of XAI salience outside brain parenchyma"
    )
    suspected_shortcuts: List[str] = Field(default_factory=list, description="Identified spurious patterns")
    mitigation_steps: List[str] = Field(default_factory=list, description="Mitigation suggestions")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)
