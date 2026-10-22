"""
Fairness, Bias, and Subgroup Performance Auditing Suite for Clinical MRI Models.

NeuroScan XAI - Explainable Brain Tumor MRI Classification Pipeline.
Evaluates algorithmic fairness across patient demographic or clinical acquisition
subgroups (e.g., age bracket, sex, scanner manufacturer, magnetic field strength).
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    from sklearn.metrics import accuracy_score, f1_score
except ImportError:
    accuracy_score = None
    f1_score = None

logger = logging.getLogger(__name__)

MINIMUM_STATISTICAL_SAMPLE_COUNT = 30


@dataclass
class SubgroupMetrics:
    """Performance metrics for an individual patient or scanner subgroup."""

    subgroup_name: str
    sample_count: int
    accuracy: float
    sensitivity: float
    specificity: float
    macro_f1: float
    insufficient_samples: bool
    warning: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FairnessResults:
    """Comprehensive algorithmic fairness audit results."""

    status: str  # 'completed', 'unavailable', or 'failed'
    subgroup_column: Optional[str] = None
    subgroups: Dict[str, SubgroupMetrics] = field(default_factory=dict)
    disparities: Dict[str, float] = field(default_factory=dict)
    flagged_issues: List[str] = field(default_factory=list)
    reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "subgroup_column": self.subgroup_column,
            "subgroups": {k: v.to_dict() for k, v in self.subgroups.items()},
            "disparities": self.disparities,
            "flagged_issues": self.flagged_issues,
            "reason": self.reason,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def summary(self) -> str:
        if self.status != "completed":
            return f"Fairness Audit Status: {self.status.upper()} (Reason: {self.reason})"

        lines = [
            "=" * 75,
            f"       FAIRNESS & SUBGROUP AUDIT REPORT: [{self.subgroup_column}]",
            "=" * 75,
            f"{'Subgroup':<20} {'Samples':<10} {'Accuracy':<12} {'Sensitivity':<12} {'Specificity':<12} {'Macro F1':<10}",
            "-" * 75,
        ]
        for name, m in self.subgroups.items():
            warn = " [!]" if m.insufficient_samples else ""
            lines.append(
                f"{name + warn:<20} {m.sample_count:<10} {m.accuracy * 100:<11.2f}% "
                f"{m.sensitivity:<12.4f} {m.specificity:<12.4f} {m.macro_f1:<10.4f}"
            )
        lines.extend(
            [
                "-" * 75,
                f"Max Accuracy Disparity      : {self.disparities.get('max_accuracy_disparity', 0.0) * 100:.2f}%",
                f"Max Sensitivity Disparity   : {self.disparities.get('max_sensitivity_disparity', 0.0) * 100:.2f}%",
                f"Disparate Impact Ratio      : {self.disparities.get('disparate_impact_ratio', 1.0):.4f}",
                "=" * 75,
            ]
        )
        if self.flagged_issues:
            lines.append("Flagged Fairness Alerts:")
            for issue in self.flagged_issues:
                lines.append(f"  * {issue}")
            lines.append("=" * 75)
        return "\n".join(lines)


class FairnessAuditor:
    """
    Conducts disparity and algorithmic bias audits across metadata subgroups.
    """

    def __init__(self, min_sample_threshold: int = MINIMUM_STATISTICAL_SAMPLE_COUNT) -> None:
        self.min_sample_threshold = min_sample_threshold

    @staticmethod
    def _calculate_macro_sensitivity_specificity(
        y_true: np.ndarray,
        y_pred: np.ndarray,
        num_classes: int,
        eps: float = 1e-10,
    ) -> Tuple[float, float]:
        """
        Calculate macro-averaged sensitivity and specificity for multi-class predictions.
        """
        sensitivities = []
        specificities = []

        for c in range(num_classes):
            tp = np.sum((y_true == c) & (y_pred == c))
            fn = np.sum((y_true == c) & (y_pred != c))
            fp = np.sum((y_true != c) & (y_pred == c))
            tn = np.sum((y_true != c) & (y_pred != c))

            sens = tp / (tp + fn + eps)
            spec = tn / (tn + fp + eps)

            sensitivities.append(sens)
            specificities.append(spec)

        return float(np.mean(sensitivities)), float(np.mean(specificities))

    def audit(
        self,
        model: nn.Module,
        dataloader: DataLoader,
        metadata_df: Optional[Any] = None,
        subgroup_column: Optional[str] = None,
        device: Optional[Union[str, torch.device]] = None,
    ) -> FairnessResults:
        """
        Execute fairness audit on model predictions across designated metadata subgroups.

        If metadata is missing, unavailable, or lacks the requested column,
        an honest 'unavailable' FairnessResults instance is returned without synthetic fabrication.

        Args:
            model: PyTorch model to audit.
            dataloader: DataLoader with test/validation samples.
            metadata_df: pandas DataFrame containing sample metadata aligned with dataloader.
            subgroup_column: Column name in metadata_df defining subgroup categories.
            device: Torch device for model execution.

        Returns:
            FairnessResults object.
        """
        # Validate metadata availability
        if metadata_df is None:
            return FairnessResults(
                status="unavailable",
                subgroup_column=subgroup_column,
                reason="No patient or scanner demographic metadata DataFrame was provided.",
            )

        if pd is not None and not isinstance(metadata_df, pd.DataFrame):
            try:
                metadata_df = pd.DataFrame(metadata_df)
            except Exception as exc:
                return FairnessResults(
                    status="unavailable",
                    subgroup_column=subgroup_column,
                    reason=f"Provided metadata could not be converted to DataFrame: {exc}",
                )

        if not subgroup_column or subgroup_column not in metadata_df.columns:
            available_cols = list(metadata_df.columns) if hasattr(metadata_df, "columns") else []
            return FairnessResults(
                status="unavailable",
                subgroup_column=subgroup_column,
                reason=(
                    f"Subgroup column '{subgroup_column}' not found in metadata. "
                    f"Available columns: {available_cols}"
                ),
            )

        if device is None:
            try:
                device = next(model.parameters()).device
            except StopIteration:
                device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        elif isinstance(device, str):
            device = torch.device(device)

        model.to(device)
        model.eval()

        # Collect model predictions
        all_preds: List[int] = []
        all_labels: List[int] = []

        with torch.no_grad():
            for batch in dataloader:
                if isinstance(batch, (list, tuple)):
                    images, labels = batch[0], batch[1]
                elif isinstance(batch, dict):
                    images, labels = batch["image"], batch["label"]
                else:
                    raise TypeError(f"Unsupported batch format: {type(batch)}")

                images = images.to(device)
                logits = model(images)
                preds = torch.argmax(logits, dim=1).cpu().numpy()

                all_preds.extend(preds.tolist())
                all_labels.extend(labels.cpu().numpy().tolist())

        total_preds = len(all_preds)
        if total_preds == 0:
            return FairnessResults(
                status="failed",
                subgroup_column=subgroup_column,
                reason="DataLoader produced 0 samples for evaluation.",
            )

        # Check alignment length
        subgroup_series = metadata_df[subgroup_column].values
        n_eval = min(total_preds, len(subgroup_series))
        if n_eval < total_preds:
            logger.warning(
                "Metadata count (%d) is smaller than dataloader count (%d). Truncating evaluation.",
                len(subgroup_series),
                total_preds,
            )

        y_true = np.array(all_labels[:n_eval], dtype=np.int64)
        y_pred = np.array(all_preds[:n_eval], dtype=np.int64)
        groups = subgroup_series[:n_eval]

        unique_groups = np.unique(groups)
        num_classes = len(np.unique(y_true))

        subgroup_metrics_dict: Dict[str, SubgroupMetrics] = {}
        group_accuracies: List[float] = []
        group_sensitivities: List[float] = []
        flagged_issues: List[str] = []

        for grp in unique_groups:
            grp_str = str(grp)
            mask = groups == grp
            grp_true = y_true[mask]
            grp_pred = y_pred[mask]
            count = len(grp_true)

            if count == 0:
                continue

            acc = float(accuracy_score(grp_true, grp_pred)) if accuracy_score else 0.0
            macro_f1 = (
                float(f1_score(grp_true, grp_pred, average="macro", zero_division=0))
                if f1_score
                else 0.0
            )

            sens, spec = self._calculate_macro_sensitivity_specificity(
                grp_true, grp_pred, num_classes=num_classes
            )

            insufficient = count < self.min_sample_threshold
            warn_msg = (
                f"Sample size ({count}) is under minimum recommended threshold "
                f"({self.min_sample_threshold}) for reliable statistical inference."
                if insufficient
                else None
            )

            if insufficient:
                flagged_issues.append(f"Subgroup '{grp_str}' has insufficient sample count: {count} < {self.min_sample_threshold}")

            m = SubgroupMetrics(
                subgroup_name=grp_str,
                sample_count=count,
                accuracy=round(acc, 4),
                sensitivity=round(sens, 4),
                specificity=round(spec, 4),
                macro_f1=round(macro_f1, 4),
                insufficient_samples=insufficient,
                warning=warn_msg,
            )
            subgroup_metrics_dict[grp_str] = m
            group_accuracies.append(acc)
            group_sensitivities.append(sens)

        # Calculate disparity metrics
        disparities: Dict[str, float] = {}
        if group_accuracies:
            max_acc = max(group_accuracies)
            min_acc = min(group_accuracies)
            acc_disp = max_acc - min_acc
            disparities["subgroup_accuracy_disparity"] = round(acc_disp, 4)
            disparities["accuracy_consistency_ratio"] = round(min_acc / max_acc if max_acc > 0 else 1.0, 4)
            disparities["disparate_impact_ratio"] = round(min_acc / max_acc if max_acc > 0 else 1.0, 4)

            if acc_disp > 0.10:
                flagged_issues.append(
                    f"Substantial accuracy disparity detected: {acc_disp * 100:.2f}% gap between highest and lowest subgroup."
                )

        if group_sensitivities:
            max_sens = max(group_sensitivities)
            min_sens = min(group_sensitivities)
            sens_disp = max_sens - min_sens
            disparities["equal_opportunity_difference"] = round(sens_disp, 4)
            disparities["equalized_odds_disparity"] = round(sens_disp, 4)

            if sens_disp > 0.10:
                flagged_issues.append(
                    f"Substantial sensitivity disparity detected: {sens_disp * 100:.2f}% gap between subgroups."
                )

        return FairnessResults(
            status="completed",
            subgroup_column=subgroup_column,
            subgroups=subgroup_metrics_dict,
            disparities=disparities,
            flagged_issues=flagged_issues,
            reason=None,
        )
