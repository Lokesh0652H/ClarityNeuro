"""
Uncertainty Quantification and Monte Carlo Dropout for Brain Tumor MRI.

NeuroScan XAI - Explainable Brain Tumor MRI Classification Pipeline.
Implements Bayesian Deep Learning uncertainty estimation:
- Predictive Entropy (Total uncertainty)
- Mutual Information (Epistemic / Model uncertainty)
- Expected Entropy (Aleatoric / Data uncertainty)
- Prediction Margin & Normalized Entropy
"""

from __future__ import annotations

import logging
import math
from typing import Any, Dict, List, Optional, Sequence, Union

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

try:
    from app.ml.model import IDX_TO_CLASS
except ImportError:
    from backend.app.ml.model import IDX_TO_CLASS

logger = logging.getLogger(__name__)

EPSILON = 1e-12


class UncertaintyEstimator:
    """
    Quantifies predictive and epistemic uncertainty for neural network classifications.
    """

    @staticmethod
    def calculate_entropy(
        probabilities: Union[np.ndarray, torch.Tensor, Sequence[float]],
        eps: float = EPSILON,
    ) -> float:
        """
        Compute Shannon entropy in bits (base 2).

        H(p) = - sum(p_i * log2(p_i + eps))

        Args:
            probabilities: Probability distribution across classes.
            eps: Numerical epsilon to avoid log(0).

        Returns:
            Shannon entropy as a float >= 0.0.
        """
        if isinstance(probabilities, torch.Tensor):
            probs = probabilities.detach().cpu().numpy().flatten()
        elif isinstance(probabilities, np.ndarray):
            probs = probabilities.flatten()
        else:
            probs = np.array(probabilities, dtype=np.float64)

        # Re-normalize to ensure sum is exactly 1.0
        sum_p = np.sum(probs)
        if sum_p > 0:
            probs = probs / sum_p

        probs = np.clip(probs, eps, 1.0)
        entropy = -float(np.sum(probs * np.log2(probs)))
        return max(0.0, entropy)

    @classmethod
    def calculate_normalized_entropy(
        cls,
        probabilities: Union[np.ndarray, torch.Tensor, Sequence[float]],
        num_classes: int = 4,
        eps: float = EPSILON,
    ) -> float:
        """
        Calculate normalized Shannon entropy bounded strictly in [0.0, 1.0].

        H_norm(p) = H(p) / log2(K) where K is number of classes.

        Args:
            probabilities: Probability vector.
            num_classes: Total class count K.
            eps: Numerical epsilon.

        Returns:
            Normalized entropy value in [0.0, 1.0].
        """
        if num_classes <= 1:
            return 0.0

        raw_entropy = cls.calculate_entropy(probabilities, eps=eps)
        max_possible_entropy = math.log2(num_classes)
        normalized = raw_entropy / max_possible_entropy
        return float(np.clip(normalized, 0.0, 1.0))

    @staticmethod
    def calculate_prediction_margin(
        probabilities: Union[np.ndarray, torch.Tensor, Sequence[float]],
    ) -> float:
        """
        Compute the prediction margin: difference between the top-1 and top-2 probabilities.

        A margin close to 1.0 indicates high certainty, while near 0.0 indicates ambiguity.

        Args:
            probabilities: Probability distribution across classes.

        Returns:
            Margin float in [0.0, 1.0].
        """
        if isinstance(probabilities, torch.Tensor):
            probs = probabilities.detach().cpu().numpy().flatten()
        elif isinstance(probabilities, np.ndarray):
            probs = probabilities.flatten()
        else:
            probs = np.array(probabilities, dtype=np.float64)

        if len(probs) < 2:
            return 1.0

        sorted_probs = np.sort(probs)[::-1]
        margin = float(sorted_probs[0] - sorted_probs[1])
        return float(np.clip(margin, 0.0, 1.0))

    @classmethod
    def mc_dropout_inference(
        cls,
        model: nn.Module,
        input_tensor: torch.Tensor,
        n_passes: int = 30,
        eps: float = EPSILON,
    ) -> Dict[str, Any]:
        """
        Execute Monte Carlo Dropout inference to estimate predictive and epistemic uncertainty.

        Standard medical imaging practice: activates dropout while keeping Batch Normalization
        and other normalization statistics locked in eval mode.

        Args:
            model: PyTorch classification model.
            input_tensor: Preprocessed tensor of shape (1, C, H, W) or (C, H, W).
            n_passes: Number of stochastic forward passes (default: 30).
            eps: Small numerical constant.

        Returns:
            Dictionary containing:
                - 'mean_probs': Dict of class names mapped to average probabilities
                - 'mean_probs_list': List of average probabilities in class index order
                - 'std_per_class': Dict of class names mapped to standard deviation
                - 'std_per_class_list': List of standard deviations in class index order
                - 'predictive_entropy': Total predictive entropy H(mean_p)
                - 'expected_entropy': Average sample entropy (aleatoric uncertainty)
                - 'mutual_information': Epistemic uncertainty I(y, w | x)
                - 'normalized_entropy': Normalized total entropy [0, 1]
                - 'prediction_margin': Margin between top-1 and top-2 mean probabilities
                - 'predicted_class': Predicted class name
                - 'predicted_idx': Predicted class index
                - 'confidence': Mean probability of the top class
                - 'n_passes': Number of MC passes conducted
        """
        if n_passes < 2:
            raise ValueError(f"n_passes must be at least 2 for variance estimation, got {n_passes}")

        if input_tensor.ndim == 3:
            input_tensor = input_tensor.unsqueeze(0)

        device = next(model.parameters()).device
        x = input_tensor.to(device)

        # Record original training mode of modules
        was_training = model.training

        # Set model to eval mode first, then selectively enable dropout layers
        model.eval()
        dropout_modules_found = 0
        for module in model.modules():
            class_name = module.__class__.__name__
            if "Dropout" in class_name or "DropPath" in class_name:
                module.train()
                dropout_modules_found += 1

        if dropout_modules_found == 0:
            logger.warning(
                "No explicit Dropout layers detected in model. MC Dropout will "
                "produce deterministic passes unless stochastic layers exist."
            )

        all_probs_list: List[np.ndarray] = []
        individual_entropies: List[float] = []

        try:
            with torch.no_grad():
                for _ in range(n_passes):
                    logits = model(x)
                    probs = F.softmax(logits, dim=1).squeeze(0).cpu().numpy()
                    all_probs_list.append(probs)
                    individual_entropies.append(cls.calculate_entropy(probs, eps=eps))
        finally:
            # Restore model to its original training state
            model.train(was_training)

        # Stack into matrix of shape (n_passes, num_classes)
        probs_matrix = np.stack(all_probs_list, axis=0)
        num_classes = probs_matrix.shape[1]

        # Calculate statistics
        mean_probs = np.mean(probs_matrix, axis=0)
        std_per_class = np.std(probs_matrix, axis=0, ddof=1)

        # Epistemic / Aleatoric decomposition:
        # Total Uncertainty: H(mean_p)
        predictive_entropy = cls.calculate_entropy(mean_probs, eps=eps)
        # Aleatoric Uncertainty: average entropy of individual passes
        expected_entropy = float(np.mean(individual_entropies))
        # Epistemic Uncertainty: Mutual Information = H(mean_p) - E[H(p)]
        mutual_information = max(0.0, predictive_entropy - expected_entropy)

        normalized_entropy = cls.calculate_normalized_entropy(mean_probs, num_classes=num_classes)
        prediction_margin = cls.calculate_prediction_margin(mean_probs)

        predicted_idx = int(np.argmax(mean_probs))
        confidence = float(mean_probs[predicted_idx])

        idx_to_class = getattr(model, "idx_to_class", IDX_TO_CLASS)
        predicted_class = idx_to_class.get(predicted_idx, f"class_{predicted_idx}")

        mean_probs_dict = {
            idx_to_class.get(i, f"class_{i}"): float(mean_probs[i])
            for i in range(num_classes)
        }
        std_dict = {
            idx_to_class.get(i, f"class_{i}"): float(std_per_class[i])
            for i in range(num_classes)
        }

        return {
            "mean_probs": mean_probs_dict,
            "mean_probs_list": [float(v) for v in mean_probs],
            "std_per_class": std_dict,
            "std_per_class_list": [float(v) for v in std_per_class],
            "predictive_entropy": round(predictive_entropy, 4),
            "expected_entropy": round(expected_entropy, 4),
            "mutual_information": round(mutual_information, 4),
            "normalized_entropy": round(normalized_entropy, 4),
            "prediction_margin": round(prediction_margin, 4),
            "predicted_class": predicted_class,
            "predicted_idx": predicted_idx,
            "confidence": round(confidence, 4),
            "n_passes": n_passes,
        }
