"""Model Service: Handles PyTorch EfficientNet-B0 loading, inference, Grad-CAM++, and MC Dropout."""

import io
import logging
import math
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms

from app.config import settings
from app.core.exceptions import ModelNotAvailableException, InferenceException

logger = logging.getLogger(__name__)


def get_default_transform() -> transforms.Compose:
    """Standard MRI preprocessing and normalization transform for EfficientNet-B0."""
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ])


class ModelService:
    """Singleton service managing PyTorch EfficientNet-B0 model lifecycle and inference."""

    def __init__(self) -> None:
        self.device = torch.device(
            settings.MODEL_DEVICE if torch.cuda.is_available() and settings.MODEL_DEVICE == "cuda" else "cpu"
        )
        self.model: Optional[nn.Module] = None
        self.is_loaded: bool = False
        self.load_error: Optional[str] = None
        self.classes: List[str] = list(settings.MODEL_CLASSES)
        self.num_classes: int = len(self.classes)
        self.transform = get_default_transform()
        self.model_version: str = "efficientnet-b0-v1"
        self.architecture: str = "EfficientNet-B0"

        # Attempt initial load
        self.load_model()

    def build_architecture(self) -> nn.Module:
        """Instantiate EfficientNet-B0 architecture with the custom classifier head."""
        import torchvision.models as models

        try:
            # Use weights=None for modern torchvision
            base_model = models.efficientnet_b0(weights=None)
        except TypeError:
            base_model = models.efficientnet_b0(pretrained=False)

        # Replace classifier
        in_features = base_model.classifier[1].in_features
        base_model.classifier[1] = nn.Linear(in_features, self.num_classes)
        return base_model

    def load_model(self) -> bool:
        """Load the model weights from the configured checkpoint path.

        Handles missing checkpoints gracefully without crashing the server.
        """
        checkpoint_path = settings.resolved_model_path

        if not checkpoint_path.exists():
            self.model = None
            self.is_loaded = False
            self.load_error = f"Checkpoint file not found at '{checkpoint_path}'"
            logger.warning(f"Model checkpoint not found: {checkpoint_path}. Inference endpoints will return 503.")
            return False

        try:
            logger.info(f"Loading EfficientNet-B0 from checkpoint: {checkpoint_path}")
            model = self.build_architecture()

            # Load checkpoint state dict safely
            checkpoint = torch.load(checkpoint_path, map_location=self.device)

            if isinstance(checkpoint, dict) and "state_dict" in checkpoint:
                state_dict = checkpoint["state_dict"]
            elif isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
                state_dict = checkpoint["model_state_dict"]
            elif isinstance(checkpoint, dict):
                state_dict = checkpoint
            elif isinstance(checkpoint, nn.Module):
                self.model = checkpoint.to(self.device)
                self.model.eval()
                self.is_loaded = True
                self.load_error = None
                return True
            else:
                raise ValueError("Unrecognized checkpoint format")

            # Clean module. prefix if saved from DataParallel
            clean_state_dict = {}
            for k, v in state_dict.items():
                new_key = k[7:] if k.startswith("module.") else k
                clean_state_dict[new_key] = v

            model.load_state_dict(clean_state_dict, strict=False)
            model.to(self.device)
            model.eval()

            self.model = model
            self.is_loaded = True
            self.load_error = None
            logger.info("Successfully loaded EfficientNet-B0 model")
            return True

        except Exception as e:
            self.model = None
            self.is_loaded = False
            self.load_error = f"Failed to load checkpoint: {str(e)}"
            logger.error(f"Error loading model checkpoint: {str(e)}", exc_info=True)
            return False

    def get_status(self) -> Dict[str, Any]:
        """Return real operational status of the inference engine."""
        checkpoint_path = settings.resolved_model_path
        return {
            "available": self.is_loaded and self.model is not None,
            "model_name": "EfficientNet-B0 Brain Tumor Classifier",
            "architecture": self.architecture,
            "device": str(self.device),
            "checkpoint_path": str(checkpoint_path),
            "checkpoint_exists": checkpoint_path.exists(),
            "num_classes": self.num_classes,
            "classes": self.classes,
            "error": self.load_error,
        }

    def preprocess_image(self, image_input: Union[Image.Image, bytes]) -> Tuple[torch.Tensor, Image.Image]:
        """Convert PIL Image or raw bytes into a normalized torch Tensor.

        Returns:
            Tuple of (torch.Tensor [1, 3, 224, 224], original_pil_image RGB)
        """
        if isinstance(image_input, bytes):
            pil_img = Image.open(io.BytesIO(image_input)).convert("RGB")
        elif isinstance(image_input, Image.Image):
            pil_img = image_input.convert("RGB")
        else:
            raise InferenceException("Unsupported image format input")

        tensor = self.transform(pil_img).unsqueeze(0).to(self.device)
        return tensor, pil_img

    def predict(self, image_input: Union[Image.Image, bytes]) -> Dict[str, Any]:
        """Execute deterministic forward inference and return probabilities and metrics.

        Raises:
            ModelNotAvailableException: if model weights are not loaded.
            InferenceException: if inference computation fails.
        """
        if not self.is_loaded or self.model is None:
            raise ModelNotAvailableException(
                f"Model checkpoint not loaded ({self.load_error or 'Weights missing'}). Ensure checkpoint is available."
            )

        start_time = time.perf_counter()
        try:
            tensor, _ = self.preprocess_image(image_input)

            self.model.eval()
            with torch.no_grad():
                logits = self.model(tensor)
                probs = F.softmax(logits, dim=1).squeeze(0).cpu().numpy()

            inference_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

            # Build probability dictionary
            prob_dict: Dict[str, float] = {
                self.classes[i]: float(round(float(probs[i]), 5)) for i in range(self.num_classes)
            }

            # Top class and confidence
            sorted_indices = np.argsort(probs)[::-1]
            top_idx = int(sorted_indices[0])
            predicted_class = self.classes[top_idx]
            confidence = float(round(float(probs[top_idx]), 5))

            # Shannon entropy: H(p) = -sum(p * ln(p))
            eps = 1e-12
            entropy = float(-np.sum(probs * np.log(probs + eps)))
            max_entropy = math.log(self.num_classes)
            normalized_entropy = float(entropy / max_entropy) if max_entropy > 0 else 0.0

            # Prediction margin: p_top1 - p_top2
            if len(sorted_indices) > 1:
                second_idx = int(sorted_indices[1])
                margin = float(probs[top_idx] - probs[second_idx])
            else:
                margin = float(probs[top_idx])

            return {
                "predicted_class": predicted_class,
                "confidence": confidence,
                "probabilities": prob_dict,
                "entropy": round(entropy, 5),
                "normalized_entropy": round(normalized_entropy, 5),
                "prediction_margin": round(margin, 5),
                "inference_time_ms": inference_time_ms,
                "model_version": self.model_version,
            }

        except ModelNotAvailableException:
            raise
        except Exception as e:
            logger.error(f"Inference execution failed: {str(e)}", exc_info=True)
            raise InferenceException(f"Inference failed during prediction: {str(e)}")

    def mc_dropout_predict(
        self, image_input: Union[Image.Image, bytes], passes: Optional[int] = None
    ) -> Dict[str, Any]:
        """Perform Monte Carlo Dropout uncertainty estimation.

        Keeps Dropout layers active during T stochastic forward passes.
        """
        if not self.is_loaded or self.model is None:
            raise ModelNotAvailableException(
                f"Model checkpoint not loaded ({self.load_error or 'Weights missing'})."
            )

        num_passes = passes or settings.MC_DROPOUT_PASSES
        if num_passes < 2:
            num_passes = 2

        try:
            tensor, _ = self.preprocess_image(image_input)

            # Activate Dropout layers while keeping BatchNormalization in eval mode
            self.model.eval()
            for m in self.model.modules():
                if isinstance(m, nn.Dropout):
                    m.train()

            pass_probabilities: List[np.ndarray] = []
            pass_entropies: List[float] = []

            eps = 1e-12
            with torch.no_grad():
                for _ in range(num_passes):
                    logits = self.model(tensor)
                    probs = F.softmax(logits, dim=1).squeeze(0).cpu().numpy()
                    pass_probabilities.append(probs)
                    h_pass = -np.sum(probs * np.log(probs + eps))
                    pass_entropies.append(float(h_pass))

            # Shape: [passes, num_classes]
            stacked_probs = np.array(pass_probabilities)

            # Mean probabilities
            mean_probs = np.mean(stacked_probs, axis=0)
            # Epistemic variance per class
            variance_per_class = np.var(stacked_probs, axis=0)
            std_per_class = np.std(stacked_probs, axis=0)

            # 95% Confidence interval (empirical 2.5th and 97.5th percentiles)
            ci_lower = np.percentile(stacked_probs, 2.5, axis=0)
            ci_upper = np.percentile(stacked_probs, 97.5, axis=0)

            # Predictive Entropy: H(E[p])
            predictive_entropy = float(-np.sum(mean_probs * np.log(mean_probs + eps)))

            # Expected Entropy: E[H(p)] (Aleatoric uncertainty)
            expected_entropy = float(np.mean(pass_entropies))

            # Mutual Information: I(y, w | x) = H(E[p]) - E[H(p)] (Epistemic uncertainty)
            mutual_information = max(0.0, float(predictive_entropy - expected_entropy))

            # Revert model to eval mode
            self.model.eval()

            return {
                "passes": num_passes,
                "mean_probabilities": {
                    self.classes[i]: round(float(mean_probs[i]), 5) for i in range(self.num_classes)
                },
                "variance": {
                    self.classes[i]: round(float(variance_per_class[i]), 6) for i in range(self.num_classes)
                },
                "standard_deviation": {
                    self.classes[i]: round(float(std_per_class[i]), 6) for i in range(self.num_classes)
                },
                "confidence_interval": {
                    self.classes[i]: [round(float(ci_lower[i]), 5), round(float(ci_upper[i]), 5)]
                    for i in range(self.num_classes)
                },
                "predictive_entropy": round(predictive_entropy, 5),
                "expected_entropy": round(expected_entropy, 5),
                "mutual_information": round(mutual_information, 5),
            }

        except Exception as e:
            self.model.eval()
            logger.error(f"MC Dropout uncertainty estimation failed: {str(e)}", exc_info=True)
            raise InferenceException(f"Uncertainty computation failed: {str(e)}")

    def generate_gradcam(
        self,
        image_input: Union[Image.Image, bytes],
        target_class_idx: Optional[int] = None,
        method: str = "gradcam++",
    ) -> Dict[str, Any]:
        """Generate Grad-CAM or Grad-CAM++ saliency heatmap overlay.

        Extracts activation maps from the last convolutional block of EfficientNet-B0.
        """
        if not self.is_loaded or self.model is None:
            raise ModelNotAvailableException(
                f"Model checkpoint not loaded ({self.load_error or 'Weights missing'})."
            )

        try:
            import cv2
            tensor, pil_img = self.preprocess_image(image_input)
            orig_w, orig_h = pil_img.size

            # Target layer for EfficientNet-B0: the last block in model.features
            target_layer = self.model.features[-1]

            activations: List[torch.Tensor] = []
            gradients: List[torch.Tensor] = []

            def forward_hook(module, input, output):
                activations.append(output)

            def backward_hook(module, grad_in, grad_out):
                gradients.append(grad_out[0])

            handle_fwd = target_layer.register_forward_hook(forward_hook)
            handle_bwd = target_layer.register_full_backward_hook(backward_hook)

            self.model.eval()
            logits = self.model(tensor)
            probs = F.softmax(logits, dim=1).squeeze(0)

            if target_class_idx is None or target_class_idx < 0 or target_class_idx >= self.num_classes:
                target_class_idx = int(torch.argmax(probs).item())

            target_class_name = self.classes[target_class_idx]
            target_confidence = float(round(float(probs[target_class_idx].item()), 5))

            # Backward pass on the target class score
            self.model.zero_grad()
            score = logits[0, target_class_idx]
            score.backward(retain_graph=True)

            handle_fwd.remove()
            handle_bwd.remove()

            if not activations or not gradients:
                raise InferenceException("Failed to capture feature maps or gradients for Grad-CAM")

            act = activations[0].detach()  # [1, C, H, W]
            grad = gradients[0].detach()   # [1, C, H, W]

            if method.lower() == "gradcam++":
                # Grad-CAM++ calculation
                # alpha_ijk = grad^2 / (2 * grad^2 + sum(act * grad^3) + eps)
                grad_2 = grad.pow(2)
                grad_3 = grad.pow(3)
                denom = 2 * grad_2 + (act * grad_3).sum(dim=(2, 3), keepdim=True)
                denom = torch.where(denom != 0.0, denom, torch.ones_like(denom))
                alpha = grad_2 / denom
                weights = (alpha * F.relu(grad)).sum(dim=(2, 3), keepdim=True)
                cam = (weights * act).sum(dim=1, keepdim=True)
                cam = F.relu(cam)
            else:
                # Standard Grad-CAM
                weights = grad.mean(dim=(2, 3), keepdim=True)
                cam = (weights * act).sum(dim=1, keepdim=True)
                cam = F.relu(cam)

            # Normalize CAM
            cam_np = cam.squeeze().cpu().numpy()
            cam_min, cam_max = cam_np.min(), cam_np.max()
            if cam_max > cam_min:
                cam_norm = (cam_np - cam_min) / (cam_max - cam_min)
            else:
                cam_norm = np.zeros_like(cam_np)

            # Resize heatmap to original image dimensions
            heatmap_resized = cv2.resize(cam_norm, (orig_w, orig_h), interpolation=cv2.INTER_LINEAR)

            # Quadrant attribution percentages
            h_half, w_half = orig_h // 2, orig_w // 2
            q1 = float(np.sum(heatmap_resized[:h_half, w_half:]))   # Top-Right
            q2 = float(np.sum(heatmap_resized[:h_half, :w_half]))  # Top-Left
            q3 = float(np.sum(heatmap_resized[h_half:, :w_half]))  # Bottom-Left
            q4 = float(np.sum(heatmap_resized[h_half:, w_half:]))  # Bottom-Right
            total_salience = q1 + q2 + q3 + q4 + 1e-12
            quadrants = {
                "top_right": round(q1 / total_salience, 4),
                "top_left": round(q2 / total_salience, 4),
                "bottom_left": round(q3 / total_salience, 4),
                "bottom_right": round(q4 / total_salience, 4),
            }

            # Create colormap overlay
            heatmap_uint8 = np.uint8(255 * heatmap_resized)
            colored_heatmap = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
            colored_heatmap = cv2.cvtColor(colored_heatmap, cv2.COLOR_BGR2RGB)

            original_uint8 = np.array(pil_img)
            overlay = np.uint8(0.4 * colored_heatmap + 0.6 * original_uint8)
            overlay_pil = Image.fromarray(overlay)

            # Save overlay image to upload directory
            upload_dir = settings.resolved_upload_dir
            timestamp_id = f"gradcam_{int(time.time() * 1000)}_{target_class_name}.jpg"
            save_path = upload_dir / timestamp_id
            overlay_pil.save(str(save_path), format="JPEG", quality=90)

            # Convert to base64 buffer for direct response if needed
            buffer = io.BytesIO()
            overlay_pil.save(buffer, format="JPEG", quality=85)
            import base64
            b64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")

            return {
                "target_class": target_class_name,
                "target_class_idx": target_class_idx,
                "confidence": target_confidence,
                "method": method,
                "heatmap_path": str(save_path),
                "heatmap_url": f"/api/analysis/gradcam/{timestamp_id}",
                "heatmap_base64": f"data:image/jpeg;base64,{b64_str}",
                "salient_regions_summary": quadrants,
            }

        except Exception as e:
            logger.error(f"Grad-CAM generation failed: {str(e)}", exc_info=True)
            raise InferenceException(f"Failed to generate explainability heatmap: {str(e)}")


# Singleton instance
model_service = ModelService()
