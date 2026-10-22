"""
Grad-CAM++ (Generalized Gradient-based Visual Explanations) Implementation.

NeuroScan XAI - Explainable Brain Tumor MRI Classification Pipeline.
Reference: Chattopadhay et al., "Grad-CAM++: Generalized Gradient-based Visual
Explanations for Deep Convolutional Networks", WACV 2018.
"""

from __future__ import annotations

import logging
from typing import Any, List, Optional, Tuple, Union

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image

try:
    import cv2
except ImportError:
    cv2 = None

try:
    from app.ml.preprocessing import load_image
except ImportError:
    from backend.app.ml.preprocessing import load_image

logger = logging.getLogger(__name__)


class GradCAMPlusPlus:
    """
    Grad-CAM++ explainability module for deep convolutional neural networks.

    Captures actual gradients and activations from the final feature extraction layer
    to compute localized, class-discriminative saliency heatmaps with higher-order
    gradient weighting.
    """

    def __init__(
        self,
        model: nn.Module,
        target_layer: Optional[nn.Module] = None,
    ) -> None:
        """
        Initialize Grad-CAM++ with the target model and layer.

        Args:
            model: PyTorch model (e.g., BrainTumorClassifier).
            target_layer: Specific convolution layer to hook. If None,
                          automatically resolves the last conv layer from the model.
        """
        self.model = model
        self.model.eval()

        if target_layer is not None:
            self.target_layer = target_layer
        elif hasattr(model, "get_last_conv_layer"):
            self.target_layer = model.get_last_conv_layer()
        elif hasattr(model, "backbone") and hasattr(model.backbone, "conv_head"):
            self.target_layer = model.backbone.conv_head
        elif hasattr(model, "conv_head"):
            self.target_layer = model.conv_head
        else:
            # Fallback: scan modules in reverse order for first Conv2d layer
            conv_layers = [m for m in model.modules() if isinstance(m, nn.Conv2d)]
            if not conv_layers:
                raise ValueError("No Conv2d layers detected in the provided model.")
            self.target_layer = conv_layers[-1]

        self.activations: Optional[torch.Tensor] = None
        self.gradients: Optional[torch.Tensor] = None
        self.hook_handles: List[Any] = []
        self._register_hooks()

    def _register_hooks(self) -> None:
        """Register forward and backward hooks to capture activations and gradients."""
        self.remove_hooks()

        def forward_hook(module: nn.Module, input_tensor: Any, output_tensor: torch.Tensor) -> None:
            self.activations = output_tensor

            # Register backward tensor hook on the activation tensor
            def tensor_backward_hook(grad: torch.Tensor) -> None:
                self.gradients = grad

            if output_tensor.requires_grad:
                output_tensor.register_hook(tensor_backward_hook)

        handle = self.target_layer.register_forward_hook(forward_hook)
        self.hook_handles.append(handle)

        # Fallback module backward hook for PyTorch versions or layers
        def module_backward_hook(module: nn.Module, grad_input: Any, grad_output: Any) -> None:
            if self.gradients is None and len(grad_output) > 0 and grad_output[0] is not None:
                self.gradients = grad_output[0].detach()

        try:
            b_handle = self.target_layer.register_full_backward_hook(module_backward_hook)
            self.hook_handles.append(b_handle)
        except Exception:
            # Full backward hook not available or rejected; tensor hook remains active
            pass

    def remove_hooks(self) -> None:
        """Clean up and detach all active hook handles."""
        for handle in self.hook_handles:
            try:
                handle.remove()
            except Exception:
                pass
        self.hook_handles = []

    def __enter__(self) -> "GradCAMPlusPlus":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.remove_hooks()

    def __del__(self) -> None:
        self.remove_hooks()

    def generate(
        self,
        input_tensor: torch.Tensor,
        target_class: Optional[int] = None,
        eps: float = 1e-10,
    ) -> np.ndarray:
        """
        Generate a 2D Grad-CAM++ heatmap for the specified input tensor and class.

        Args:
            input_tensor: Tensor of shape (1, C, H, W).
            target_class: Class index for which to explain prediction.
                          If None, defaults to the argmax predicted class.
            eps: Small constant for numerical stability during division.

        Returns:
            Normalized 2D numpy array of shape (H, W) with values in [0.0, 1.0].
        """
        if input_tensor.ndim != 4 or input_tensor.size(0) != 1:
            raise ValueError(
                f"input_tensor must have shape (1, C, H, W), got {input_tensor.shape}"
            )

        self.model.zero_grad()
        self.activations = None
        self.gradients = None

        device = next(self.model.parameters()).device
        x = input_tensor.clone().to(device)
        x.requires_grad_(True)

        # Forward pass
        logits = self.model(x)

        if target_class is None:
            target_class = int(torch.argmax(logits, dim=1).item())

        score = logits[0, target_class]

        # Backward pass using retain_graph to capture gradients
        score.backward(retain_graph=True)

        if self.activations is None or self.gradients is None:
            raise RuntimeError(
                "Failed to capture activations or gradients. "
                "Ensure target_layer was executed during forward pass."
            )

        activations = self.activations[0]  # Shape: (C, h, w)
        gradients = self.gradients[0]      # Shape: (C, h, w)

        # Higher-order gradient formulation for Grad-CAM++:
        # grad_2 = gradients^2, grad_3 = gradients^3
        grad_2 = gradients.pow(2)
        grad_3 = gradients.pow(3)

        # sum_spatial(A * grad_3) per channel
        # activations * grad_3 shape: (C, h, w)
        spatial_sum = (activations * grad_3).sum(dim=(1, 2), keepdim=True)

        # alpha_numerator = grad_2
        # alpha_denominator = 2 * grad_2 + spatial_sum
        alpha_denom = 2.0 * grad_2 + spatial_sum
        alpha_denom = torch.where(
            alpha_denom != 0.0,
            alpha_denom,
            torch.ones_like(alpha_denom) * eps,
        )
        alphas = grad_2 / alpha_denom

        # Only positive gradients contribute to evidence for the class
        rel_grad = F.relu(gradients)

        # Channel weights: w_k = sum_{i,j} (alpha_{i,j} * relu(grad_{i,j}))
        weights = (alphas * rel_grad).sum(dim=(1, 2), keepdim=True)  # (C, 1, 1)

        # Heatmap: ReLU(sum_k (w_k * activations_k))
        cam = torch.sum(weights * activations, dim=0, keepdim=True)  # (1, h, w)
        cam = F.relu(cam)

        # Interpolate to match input spatial dimensions (H, W)
        cam = cam.unsqueeze(0)  # (1, 1, h, w)
        cam = F.interpolate(
            cam,
            size=(input_tensor.size(2), input_tensor.size(3)),
            mode="bilinear",
            align_corners=False,
        ).squeeze()  # (H, W)

        heatmap = cam.detach().cpu().numpy()

        # Min-max normalization with numerical guard
        h_min, h_max = heatmap.min(), heatmap.max()
        if h_max - h_min > eps:
            heatmap = (heatmap - h_min) / (h_max - h_min)
        else:
            heatmap = np.zeros_like(heatmap)

        return heatmap.astype(np.float32)

    @staticmethod
    def create_heatmap_only(
        heatmap: np.ndarray,
        colormap: int = 2,  # cv2.COLORMAP_JET
    ) -> Image.Image:
        """
        Convert a 2D normalized heatmap [0, 1] into a colored PIL Image.

        Args:
            heatmap: 2D numpy array with values in [0.0, 1.0].
            colormap: OpenCV colormap enum (default: cv2.COLORMAP_JET).

        Returns:
            RGB PIL Image representation of the colormapped heatmap.
        """
        h_clipped = np.clip(heatmap, 0.0, 1.0)
        h_uint8 = (h_clipped * 255.0).astype(np.uint8)

        if cv2 is not None:
            colored = cv2.applyColorMap(h_uint8, colormap)
            colored_rgb = cv2.cvtColor(colored, cv2.COLOR_BGR2RGB)
            return Image.fromarray(colored_rgb, mode="RGB")
        else:
            # Pure Python/numpy Jet colormap fallback if OpenCV is unavailable
            r = np.clip(1.5 - np.abs(4.0 * h_clipped - 3.0), 0.0, 1.0)
            g = np.clip(1.5 - np.abs(4.0 * h_clipped - 2.0), 0.0, 1.0)
            b = np.clip(1.5 - np.abs(4.0 * h_clipped - 1.0), 0.0, 1.0)
            rgb = (np.stack([r, g, b], axis=-1) * 255.0).astype(np.uint8)
            return Image.fromarray(rgb, mode="RGB")

    @classmethod
    def create_overlay(
        cls,
        original_image: Union[str, Image.Image, np.ndarray],
        heatmap: np.ndarray,
        alpha: float = 0.4,
        colormap: int = 2,
    ) -> Image.Image:
        """
        Blend a Grad-CAM++ heatmap over the original input image.

        Args:
            original_image: PIL Image, path, or numpy array of original MRI.
            heatmap: 2D normalized heatmap [0.0, 1.0].
            alpha: Heatmap blend weight [0.0, 1.0] (default: 0.4).
            colormap: OpenCV colormap constant.

        Returns:
            Blended RGB PIL Image.
        """
        pil_orig = load_image(original_image)
        orig_w, orig_h = pil_orig.size

        # Resize heatmap to match original image dimensions
        heatmap_pil = Image.fromarray(heatmap)
        heatmap_resized = heatmap_pil.resize((orig_w, orig_h), resample=Image.Resampling.BILINEAR)
        resized_arr = np.array(heatmap_resized, dtype=np.float32)

        heatmap_colored = cls.create_heatmap_only(resized_arr, colormap=colormap)
        orig_arr = np.array(pil_orig, dtype=np.float32)
        heat_arr = np.array(heatmap_colored, dtype=np.float32)

        # Alpha blend: (1 - alpha) * original + alpha * heatmap
        alpha = float(np.clip(alpha, 0.0, 1.0))
        blended = (1.0 - alpha) * orig_arr + alpha * heat_arr
        blended_uint8 = np.clip(blended, 0.0, 255.0).astype(np.uint8)

        return Image.fromarray(blended_uint8, mode="RGB")
