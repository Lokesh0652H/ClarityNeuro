"""
Comprehensive Model Evaluation Suite for Brain Tumor Classification.

NeuroScan XAI - Explainable Brain Tumor MRI Classification Pipeline.
Calculates multi-class clinical performance metrics:
- Accuracy & Balanced Accuracy
- Per-class Precision, Recall, F1-score, and Support
- Macro and Weighted F1-scores
- Confusion Matrix
- Multi-class Log Loss (Cross-Entropy)
- Parameter counts (Total and Trainable)
- Latency profiling (mean, std, p50, p95, p99 ms)
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader

try:
    from sklearn.metrics import (
        accuracy_score,
        balanced_accuracy_score,
        confusion_matrix,
        log_loss,
        precision_recall_fscore_support,
    )
except ImportError:
    accuracy_score = None
    balanced_accuracy_score = None
    confusion_matrix = None
    log_loss = None
    precision_recall_fscore_support = None

try:
    from app.ml.model import CLASS_NAMES, IDX_TO_CLASS
except ImportError:
    from backend.app.ml.model import CLASS_NAMES, IDX_TO_CLASS

logger = logging.getLogger(__name__)


@dataclass
class EvaluationResults:
    """Structured container holding all computed model evaluation metrics."""

    accuracy: float
    balanced_accuracy: float
    macro_f1: float
    weighted_f1: float
    log_loss_value: float
    per_class_metrics: Dict[str, Dict[str, float]]
    confusion_matrix: List[List[int]]
    total_samples: int
    parameter_counts: Dict[str, int]
    latency_stats_ms: Dict[str, float]
    class_names: List[str] = field(default_factory=lambda: list(CLASS_NAMES))

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to a Python dictionary."""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Serialize metrics to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def save_json(self, path: Union[str, Path]) -> None:
        """Save metrics directly to a JSON file."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            f.write(self.to_json())

    def summary(self) -> str:
        """Generate a formatted human-readable evaluation summary."""
        lines = [
            "=" * 70,
            "         NEUROSCAN XAI - MODEL EVALUATION REPORT",
            "=" * 70,
            f"Total Evaluated Samples : {self.total_samples}",
            f"Overall Accuracy        : {self.accuracy * 100:.2f}%",
            f"Balanced Accuracy       : {self.balanced_accuracy * 100:.2f}%",
            f"Macro F1-Score          : {self.macro_f1:.4f}",
            f"Weighted F1-Score       : {self.weighted_f1:.4f}",
            f"Multi-class Log Loss    : {self.log_loss_value:.4f}",
            "-" * 70,
            f"{'Class':<15} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'Support':<10}",
            "-" * 70,
        ]
        for name in self.class_names:
            metrics = self.per_class_metrics.get(name, {})
            p = metrics.get("precision", 0.0)
            r = metrics.get("recall", 0.0)
            f1 = metrics.get("f1_score", 0.0)
            sup = int(metrics.get("support", 0))
            lines.append(f"{name:<15} {p:<12.4f} {r:<12.4f} {f1:<12.4f} {sup:<10}")

        lines.extend(
            [
                "-" * 70,
                f"Total Parameters        : {self.parameter_counts.get('total', 0):,}",
                f"Trainable Parameters    : {self.parameter_counts.get('trainable', 0):,}",
                f"Mean Latency per Batch  : {self.latency_stats_ms.get('mean_batch_ms', 0.0):.2f} ms",
                "=" * 70,
            ]
        )
        return "\n".join(lines)


class ModelEvaluator:
    """
    Evaluates neural network classifiers across clinical validation datasets.
    Calculates exact mathematical metrics using scikit-learn without approximations.
    """

    def __init__(self, class_names: Optional[List[str]] = None) -> None:
        """
        Initialize the evaluator.

        Args:
            class_names: List of class labels in index order.
        """
        self.class_names = class_names or list(CLASS_NAMES)
        self.num_classes = len(self.class_names)

        if accuracy_score is None:
            raise ImportError(
                "scikit-learn is required for ModelEvaluator. Install it via `pip install scikit-learn`."
            )

    @staticmethod
    def count_parameters(model: nn.Module) -> Dict[str, int]:
        """
        Count total and trainable parameters in the model.
        """
        total = sum(p.numel() for p in model.parameters())
        trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
        frozen = total - trainable
        return {
            "total": total,
            "trainable": trainable,
            "frozen": frozen,
        }

    def evaluate(
        self,
        model: nn.Module,
        dataloader: DataLoader,
        device: Optional[Union[str, torch.device]] = None,
    ) -> EvaluationResults:
        """
        Run complete evaluation over a DataLoader.

        Args:
            model: PyTorch model to evaluate.
            dataloader: DataLoader yielding (images, labels) or (images, labels, ...).
            device: Target torch device. If None, auto-detected from model or availability.

        Returns:
            EvaluationResults object containing all calculated metrics.
        """
        if device is None:
            try:
                device = next(model.parameters()).device
            except StopIteration:
                device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        elif isinstance(device, str):
            device = torch.device(device)

        model.to(device)
        model.eval()

        all_preds: List[int] = []
        all_labels: List[int] = []
        all_probs: List[np.ndarray] = []
        batch_latencies: List[float] = []

        with torch.no_grad():
            for batch in dataloader:
                if isinstance(batch, (list, tuple)):
                    images = batch[0]
                    labels = batch[1]
                elif isinstance(batch, dict):
                    images = batch["image"]
                    labels = batch["label"]
                else:
                    raise TypeError(f"Unexpected batch format from dataloader: {type(batch)}")

                images = images.to(device)
                labels = labels.to(device)

                t0 = time.perf_counter()
                logits = model(images)
                # Device synchronization for accurate timing if CUDA
                if device.type == "cuda":
                    torch.cuda.synchronize(device)
                batch_ms = (time.perf_counter() - t0) * 1000.0
                batch_latencies.append(batch_ms)

                probs = F.softmax(logits, dim=1).cpu().numpy()
                preds = np.argmax(probs, axis=1)

                all_probs.append(probs)
                all_preds.extend(preds.tolist())
                all_labels.extend(labels.cpu().numpy().tolist())

        y_true = np.array(all_labels, dtype=np.int64)
        y_pred = np.array(all_preds, dtype=np.int64)
        y_prob = np.concatenate(all_probs, axis=0) if all_probs else np.zeros((0, self.num_classes))

        total_samples = len(y_true)
        if total_samples == 0:
            raise ValueError("Dataloader yielded 0 samples for evaluation.")

        # Compute scikit-learn metrics
        acc = float(accuracy_score(y_true, y_pred))
        bal_acc = float(balanced_accuracy_score(y_true, y_pred))

        precision, recall, f1, support = precision_recall_fscore_support(
            y_true,
            y_pred,
            labels=list(range(self.num_classes)),
            zero_division=0,
        )

        macro_f1 = float(np.mean(f1))
        weighted_f1 = float(
            np.average(f1, weights=support) if np.sum(support) > 0 else 0.0
        )

        # Cross-entropy log loss
        try:
            ce_loss = float(log_loss(y_true, y_prob, labels=list(range(self.num_classes))))
        except Exception as exc:
            logger.warning("Could not calculate log_loss: %s. Defaulting to 0.0", exc)
            ce_loss = 0.0

        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred, labels=list(range(self.num_classes)))
        cm_list = cm.tolist()

        # Per-class dictionary
        per_class: Dict[str, Dict[str, float]] = {}
        for idx, name in enumerate(self.class_names):
            per_class[name] = {
                "precision": float(round(precision[idx], 4)),
                "recall": float(round(recall[idx], 4)),
                "f1_score": float(round(f1[idx], 4)),
                "support": int(support[idx]),
            }

        param_counts = self.count_parameters(model)

        lat_arr = np.array(batch_latencies, dtype=np.float64)
        latency_stats = {
            "mean_batch_ms": float(round(np.mean(lat_arr), 3)),
            "std_batch_ms": float(round(np.std(lat_arr), 3)),
            "p50_batch_ms": float(round(np.percentile(lat_arr, 50), 3)),
            "p95_batch_ms": float(round(np.percentile(lat_arr, 95), 3)),
            "p99_batch_ms": float(round(np.percentile(lat_arr, 99), 3)),
        }

        return EvaluationResults(
            accuracy=round(acc, 4),
            balanced_accuracy=round(bal_acc, 4),
            macro_f1=round(macro_f1, 4),
            weighted_f1=round(weighted_f1, 4),
            log_loss_value=round(ce_loss, 4),
            per_class_metrics=per_class,
            confusion_matrix=cm_list,
            total_samples=total_samples,
            parameter_counts=param_counts,
            latency_stats_ms=latency_stats,
            class_names=self.class_names,
        )
