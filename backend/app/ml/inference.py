"""
Thread-safe High-Performance Inference Engine for Brain Tumor Classification.

NeuroScan XAI - Explainable Brain Tumor MRI Classification Pipeline.
"""

from __future__ import annotations

import logging
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image

try:
    from app.ml.model import BrainTumorClassifier, IDX_TO_CLASS
    from app.ml.preprocessing import load_image, preprocess_image
except ImportError:
    from backend.app.ml.model import BrainTumorClassifier, IDX_TO_CLASS
    from backend.app.ml.preprocessing import load_image, preprocess_image

logger = logging.getLogger(__name__)


class InferenceEngine:
    """
    Thread-safe inference manager for BrainTumorClassifier models.

    Provides single-image and batched predictions, automatic device placement,
    latency profiling, and probability distributions.
    """

    def __init__(
        self,
        model: BrainTumorClassifier,
        device: Optional[Union[str, torch.device]] = None,
    ) -> None:
        """
        Initialize the inference engine.

        Args:
            model: Trained BrainTumorClassifier instance.
            device: Device to execute inference on (CUDA, CPU, or MPS). If None, auto-detected.
        """
        self.model = model
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        elif isinstance(device, str):
            self.device = torch.device(device)
        else:
            self.device = device

        self.model.to(self.device)
        self.model.eval()

        # Thread lock ensures concurrent API requests do not collide on shared model state
        self._lock = threading.Lock()
        self.idx_to_class = getattr(model, "idx_to_class", IDX_TO_CLASS)

    def predict(
        self,
        image_input: Union[str, Path, bytes, Image.Image, np.ndarray, torch.Tensor],
    ) -> Dict[str, Any]:
        """
        Run inference on a single image.

        Args:
            image_input: Path, bytes, PIL Image, numpy array, or preprocessed PyTorch Tensor.

        Returns:
            Dictionary containing:
                - 'class_name': Top predicted class label (e.g., 'glioma')
                - 'class_idx': Integer class index
                - 'confidence': Softmax probability of top class [0.0, 1.0]
                - 'probabilities': Dict mapping all class names to probabilities
                - 'logits': Raw model output logits for each class
                - 'inference_time_ms': Inference duration in milliseconds
                - 'device': Device on which inference was executed
        """
        if isinstance(image_input, torch.Tensor):
            tensor = image_input
            if tensor.ndim == 3:
                tensor = tensor.unsqueeze(0)
            tensor = tensor.to(self.device)
        else:
            tensor = preprocess_image(image_input, device=self.device)

        start_time = time.perf_counter()

        with self._lock:
            with torch.no_grad():
                logits = self.model(tensor)
                probs = F.softmax(logits, dim=1).squeeze(0)
                logits_cpu = logits.squeeze(0).cpu().numpy().tolist()
                probs_cpu = probs.cpu().numpy()

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        top_idx = int(np.argmax(probs_cpu))
        top_confidence = float(probs_cpu[top_idx])
        top_class = self.idx_to_class.get(top_idx, f"class_{top_idx}")

        probabilities_dict = {
            self.idx_to_class.get(i, f"class_{i}"): float(probs_cpu[i])
            for i in range(len(probs_cpu))
        }

        return {
            "class_name": top_class,
            "class_idx": top_idx,
            "confidence": top_confidence,
            "probabilities": probabilities_dict,
            "logits": logits_cpu,
            "inference_time_ms": round(elapsed_ms, 3),
            "device": str(self.device),
        }

    def predict_batch(
        self,
        batch_inputs: Sequence[Union[str, Path, bytes, Image.Image, np.ndarray, torch.Tensor]],
    ) -> List[Dict[str, Any]]:
        """
        Run batched inference on multiple image inputs.

        Args:
            batch_inputs: Sequence of image paths, images, or tensors.

        Returns:
            List of prediction dictionaries corresponding to each input image.
        """
        if not batch_inputs:
            return []

        # Convert all inputs to individual preprocessed tensors
        tensors: List[torch.Tensor] = []
        for item in batch_inputs:
            if isinstance(item, torch.Tensor):
                t = item if item.ndim == 3 else item.squeeze(0)
                tensors.append(t)
            else:
                t = preprocess_image(item, add_batch_dim=False)
                tensors.append(t)

        stacked_tensor = torch.stack(tensors, dim=0).to(self.device)
        batch_size = stacked_tensor.size(0)

        start_time = time.perf_counter()

        with self._lock:
            with torch.no_grad():
                logits_batch = self.model(stacked_tensor)
                probs_batch = F.softmax(logits_batch, dim=1).cpu().numpy()
                logits_batch_cpu = logits_batch.cpu().numpy().tolist()

        total_elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        per_item_ms = total_elapsed_ms / max(batch_size, 1)

        results: List[Dict[str, Any]] = []
        for i in range(batch_size):
            probs_i = probs_batch[i]
            top_idx = int(np.argmax(probs_i))
            top_class = self.idx_to_class.get(top_idx, f"class_{top_idx}")
            top_conf = float(probs_i[top_idx])

            prob_dict = {
                self.idx_to_class.get(c, f"class_{c}"): float(probs_i[c])
                for c in range(len(probs_i))
            }

            results.append(
                {
                    "class_name": top_class,
                    "class_idx": top_idx,
                    "confidence": top_conf,
                    "probabilities": prob_dict,
                    "logits": logits_batch_cpu[i],
                    "inference_time_ms": round(per_item_ms, 3),
                    "device": str(self.device),
                }
            )

        return results
