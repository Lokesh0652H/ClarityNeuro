"""
Shortcut Learning and Visual Artifact Auditing for Brain Tumor MRI.

NeuroScan XAI - Explainable Brain Tumor MRI Classification Pipeline.
Detects non-pathological shortcut learning vulnerabilities such as:
- Hospital/scanner annotations and L/R markers in image corners
- Scanner frame and border artifacts
- Background noise disparities and skull-stripping artifacts
- Sensitivity perturbation testing (corner masking, border ablation)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image

try:
    import cv2
except ImportError:
    cv2 = None

from backend.app.ml.model import IDX_TO_CLASS
from backend.app.ml.preprocessing import load_image, preprocess_image

logger = logging.getLogger(__name__)


class ShortcutAuditor:
    """
    Auditor for uncovering dataset shortcuts, scanner biases, and non-anatomical artifacts.
    """

    @staticmethod
    def inspect_visual_artifacts(
        image_input: Union[str, Path, Image.Image, np.ndarray],
    ) -> Dict[str, Any]:
        """
        Inspect MRI scan for presence of non-anatomical visual artifacts in borders, corners,
        and background.

        Args:
            image_input: File path, PIL Image, or numpy array of MRI scan.

        Returns:
            Dictionary containing:
                - 'border_analysis': Statistics on outer perimeter intensity and edges
                - 'corner_analysis': Detection of high-contrast text markers or annotations
                - 'background_analysis': Scanner RF noise vs synthetic black clipping
                - 'artifact_score': Aggregated artifact score [0.0 (clean), 1.0 (high risk)]
                - 'detected_flags': List of detected artifact indicators
        """
        pil_img = load_image(image_input)
        arr = np.array(pil_img.convert("L"), dtype=np.float32)
        h, w = arr.shape

        detected_flags: List[str] = []

        # 1. Border Analysis (Outer 6% perimeter)
        border_thickness_y = max(int(h * 0.06), 2)
        border_thickness_x = max(int(w * 0.06), 2)

        top_border = arr[:border_thickness_y, :]
        bottom_border = arr[-border_thickness_y:, :]
        left_border = arr[:, :border_thickness_x]
        right_border = arr[:, -border_thickness_x:]

        border_pixels = np.concatenate(
            [top_border.flatten(), bottom_border.flatten(), left_border.flatten(), right_border.flatten()]
        )
        border_mean = float(np.mean(border_pixels))
        border_std = float(np.std(border_pixels))
        border_max = float(np.max(border_pixels))
        border_bright_fraction = float(np.mean(border_pixels > 120.0))

        if border_bright_fraction > 0.02:
            detected_flags.append("Non-zero outer border artifact or framing detected.")

        border_analysis = {
            "mean_intensity": round(border_mean, 2),
            "std_intensity": round(border_std, 2),
            "max_intensity": round(border_max, 2),
            "bright_pixel_ratio": round(border_bright_fraction, 4),
        }

        # 2. Corner Analysis (12% x 12% bounding boxes in each of the 4 corners)
        cw = max(int(w * 0.12), 4)
        ch = max(int(h * 0.12), 4)

        corners = {
            "top_left": arr[:ch, :cw],
            "top_right": arr[:ch, -cw:],
            "bottom_left": arr[-ch:, :cw],
            "bottom_right": arr[-ch:, -cw:],
        }

        corner_stats = {}
        text_markers_found = False

        for corner_name, corner_arr in corners.items():
            c_mean = float(np.mean(corner_arr))
            c_max = float(np.max(corner_arr))
            c_high_contrast_ratio = float(np.mean(corner_arr > 180.0))

            if c_high_contrast_ratio > 0.015:
                text_markers_found = True
                detected_flags.append(
                    f"Possible text or scanner marker annotation in {corner_name.replace('_', ' ')}."
                )

            corner_stats[corner_name] = {
                "mean": round(c_mean, 2),
                "max": round(c_max, 2),
                "high_contrast_ratio": round(c_high_contrast_ratio, 4),
            }

        corner_analysis = {
            "corners": corner_stats,
            "text_marker_detected": text_markers_found,
        }

        # 3. Background Noise Analysis
        # Background pixels typically have intensity < 25 in clinical MRI
        bg_mask = arr < 25.0
        bg_pixel_count = int(np.sum(bg_mask))
        total_pixels = h * w
        bg_fraction = bg_pixel_count / total_pixels

        if bg_pixel_count > 50:
            bg_pixels = arr[bg_mask]
            bg_noise_std = float(np.std(bg_pixels))
            bg_mean = float(np.mean(bg_pixels))
            bg_purely_zero_ratio = float(np.mean(bg_pixels == 0.0))
        else:
            bg_noise_std = 0.0
            bg_mean = 0.0
            bg_purely_zero_ratio = 1.0

        if bg_purely_zero_ratio > 0.95 and bg_fraction > 0.20:
            detected_flags.append("Synthetic zero-padding / sharp background masking detected.")
        elif bg_noise_std > 8.0:
            detected_flags.append("High RF background noise detected (possible scanner variance).")

        background_analysis = {
            "background_ratio": round(bg_fraction, 4),
            "background_mean": round(bg_mean, 2),
            "background_noise_std": round(bg_noise_std, 2),
            "zero_padding_ratio": round(bg_purely_zero_ratio, 4),
        }

        # Compute composite artifact score [0.0, 1.0]
        artifact_score = 0.0
        if border_bright_fraction > 0.01:
            artifact_score += 0.35
        if text_markers_found:
            artifact_score += 0.45
        if bg_purely_zero_ratio > 0.95 and bg_fraction > 0.25:
            artifact_score += 0.20

        artifact_score = float(np.clip(artifact_score, 0.0, 1.0))

        return {
            "border_analysis": border_analysis,
            "corner_analysis": corner_analysis,
            "background_analysis": background_analysis,
            "artifact_score": round(artifact_score, 3),
            "detected_flags": detected_flags,
            "has_high_risk_artifacts": artifact_score >= 0.40,
        }

    @classmethod
    def perturbation_experiment(
        cls,
        model: nn.Module,
        image_tensor: torch.Tensor,
        original_image: Optional[Union[str, Image.Image, np.ndarray]] = None,
        device: Optional[Union[str, torch.device]] = None,
    ) -> Dict[str, Any]:
        """
        Conduct controlled perturbation experiments on an MRI scan to determine
        if the model relies on spurious non-anatomical features (corners, borders).

        Args:
            model: PyTorch model.
            image_tensor: Preprocessed tensor of shape (1, 3, 224, 224).
            original_image: Original PIL Image or path (optional, used for artifact inspection).
            device: Torch execution device.

        Returns:
            Dictionary containing:
                - 'original_prediction': Label and probability
                - 'masked_border': Prediction after zeroing outer 8% border
                - 'masked_corners': Prediction after masking 4 corners
                - 'prediction_changes': Probability deltas and shift flags
                - 'shortcut_vulnerability': Assessment of shortcut learning risk
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

        if image_tensor.ndim == 3:
            image_tensor = image_tensor.unsqueeze(0)

        x_orig = image_tensor.clone().to(device)
        _, _, h, w = x_orig.shape

        # Construct Perturbations:
        # 1. Masked Border: zero out outer 8% perimeter
        x_border = x_orig.clone()
        by = max(int(h * 0.08), 2)
        bx = max(int(w * 0.08), 2)
        x_border[:, :, :by, :] = 0.0
        x_border[:, :, -by:, :] = 0.0
        x_border[:, :, :, :bx] = 0.0
        x_border[:, :, :, -bx:] = 0.0

        # 2. Masked Corners: zero out 15% x 15% corners
        x_corner = x_orig.clone()
        cy = max(int(h * 0.15), 4)
        cx = max(int(w * 0.15), 4)
        x_corner[:, :, :cy, :cx] = 0.0
        x_corner[:, :, :cy, -cx:] = 0.0
        x_corner[:, :, -cy:, :cx] = 0.0
        x_corner[:, :, -cy:, -cx:] = 0.0

        idx_to_class = getattr(model, "idx_to_class", IDX_TO_CLASS)

        def run_eval(tensor_in: torch.Tensor) -> Tuple[int, str, float, Dict[str, float]]:
            with torch.no_grad():
                logits = model(tensor_in)
                probs = F.softmax(logits, dim=1).squeeze(0).cpu().numpy()
            idx = int(np.argmax(probs))
            conf = float(probs[idx])
            name = idx_to_class.get(idx, f"class_{idx}")
            prob_dict = {
                idx_to_class.get(i, f"class_{i}"): float(probs[i])
                for i in range(len(probs))
            }
            return idx, name, conf, prob_dict

        orig_idx, orig_name, orig_conf, orig_probs = run_eval(x_orig)
        border_idx, border_name, border_conf, border_probs = run_eval(x_border)
        corner_idx, corner_name, corner_conf, corner_probs = run_eval(x_corner)

        # Calculate prediction deltas for the originally predicted class
        orig_class_name = orig_name
        border_p_drop = orig_probs[orig_class_name] - border_probs[orig_class_name]
        corner_p_drop = orig_probs[orig_class_name] - corner_probs[orig_class_name]

        border_switched = (border_idx != orig_idx)
        corner_switched = (corner_idx != orig_idx)

        # Risk assessment:
        # If masking non-anatomical corners or borders drops original confidence by > 25%
        # or causes class switch, high shortcut vulnerability is indicated.
        is_high_risk = border_switched or corner_switched or (max(border_p_drop, corner_p_drop) > 0.25)
        is_mod_risk = (max(border_p_drop, corner_p_drop) > 0.12)

        risk_level = "HIGH" if is_high_risk else ("MODERATE" if is_mod_risk else "LOW")

        results = {
            "original_prediction": {
                "class_name": orig_name,
                "confidence": round(orig_conf, 4),
                "probabilities": {k: round(v, 4) for k, v in orig_probs.items()},
            },
            "masked_border": {
                "class_name": border_name,
                "confidence": round(border_conf, 4),
                "probabilities": {k: round(v, 4) for k, v in border_probs.items()},
                "class_switched": border_switched,
                "confidence_drop": round(border_p_drop, 4),
            },
            "masked_corners": {
                "class_name": corner_name,
                "confidence": round(corner_conf, 4),
                "probabilities": {k: round(v, 4) for k, v in corner_probs.items()},
                "class_switched": corner_switched,
                "confidence_drop": round(corner_p_drop, 4),
            },
            "shortcut_vulnerability": {
                "risk_level": risk_level,
                "max_confidence_drop": round(max(border_p_drop, corner_p_drop), 4),
                "prediction_switched": border_switched or corner_switched,
                "recommendation": (
                    "Model demonstrates concerning reliance on image borders/corners. "
                    "Apply tight intracranial skull-stripping or border masking during training."
                    if is_high_risk
                    else "Model decisions appear robust against peripheral non-anatomical masking."
                ),
            },
        }

        # Optional visual inspection if original image is provided
        if original_image is not None:
            results["visual_artifacts"] = cls.inspect_visual_artifacts(original_image)

        return results
