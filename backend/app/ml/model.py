"""
Brain Tumor Classifier Architecture using EfficientNet-B0.

NeuroScan XAI - Explainable Brain Tumor MRI Classification Pipeline.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import torch
import torch.nn as nn
from torchvision import models, transforms

logger = logging.getLogger(__name__)

# Standard class mappings for Brain Tumor MRI classification
IDX_TO_CLASS: Dict[int, str] = {
    0: "glioma",
    1: "meningioma",
    2: "pituitary",
    3: "notumor",
}

CLASS_TO_IDX: Dict[str, int] = {v: k for k, v in IDX_TO_CLASS.items()}
CLASS_NAMES = [IDX_TO_CLASS[i] for i in range(len(IDX_TO_CLASS))]

# Standard ImageNet statistics used during EfficientNet pretraining
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


class BrainTumorClassifier(nn.Module):
    """
    EfficientNet-B0 based neural network for 4-class brain tumor MRI classification:
    glioma, meningioma, pituitary, and notumor.

    Supports CPU, CUDA, and MPS devices with seamless checkpoint management
    and torchvision preprocessing transforms.
    """

    def __init__(
        self,
        num_classes: int = 4,
        pretrained: bool = True,
        dropout_rate: float = 0.2,
        model_name: str = "efficientnet_b0",
    ) -> None:
        """
        Initialize the BrainTumorClassifier model.

        Args:
            num_classes: Number of target classes (default: 4).
            pretrained: Whether to load ImageNet pre-trained weights.
            dropout_rate: Dropout rate for classifier head.
            model_name: Architecture name recognized by timm.
        """
        super().__init__()
        self.num_classes = num_classes
        self.model_name = model_name
        self.dropout_rate = dropout_rate

        # Build backbone using torchvision
        if pretrained:
            weights = models.EfficientNet_B0_Weights.DEFAULT
            self.backbone = models.efficientnet_b0(weights=weights)
        else:
            self.backbone = models.efficientnet_b0(weights=None)

        in_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(p=dropout_rate, inplace=True),
            nn.Linear(in_features, num_classes)
        )

        self.class_to_idx: Dict[str, int] = dict(CLASS_TO_IDX)
        self.idx_to_class: Dict[int, str] = dict(IDX_TO_CLASS)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through backbone.

        Args:
            x: Input tensor of shape (batch_size, 3, H, W).

        Returns:
            Logits tensor of shape (batch_size, num_classes).
        """
        return self.backbone(x)

    def get_last_conv_layer(self) -> nn.Module:
        """
        Retrieve the last convolutional layer of the EfficientNet-B0 backbone.
        Useful for Grad-CAM / Grad-CAM++ feature map and gradient extraction.

        Returns:
            The final convolutional layer module.
        """
        return self.backbone.features[-1]

    @staticmethod
    def get_preprocessing_transform(
        is_training: bool = False,
        image_size: int = 224,
    ) -> transforms.Compose:
        """
        Get the standard preprocessing transformation pipeline.

        Args:
            is_training: If True, include data augmentations (flips, rotations, jitter).
                         If False, deterministic evaluation pipeline (Resize, CenterCrop, Normalize).
            image_size: Target square image dimension (default: 224).

        Returns:
            torchvision.transforms.Compose instance.
        """
        if is_training:
            return transforms.Compose(
                [
                    transforms.Resize((int(image_size * 1.14), int(image_size * 1.14))),
                    transforms.RandomResizedCrop(image_size, scale=(0.8, 1.0)),
                    transforms.RandomHorizontalFlip(p=0.5),
                    transforms.RandomRotation(degrees=15),
                    transforms.ColorJitter(brightness=0.1, contrast=0.1),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
                ]
            )
        else:
            return transforms.Compose(
                [
                    transforms.Resize(256),
                    transforms.CenterCrop(image_size),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
                ]
            )

    def save_checkpoint(
        self,
        checkpoint_path: Union[str, Path],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Save model weights and training metadata to disk.

        Args:
            checkpoint_path: Path where checkpoint will be saved.
            metadata: Additional training or evaluation metadata (epoch, metrics, optimizer state).
        """
        path = Path(checkpoint_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        payload: Dict[str, Any] = {
            "model_state_dict": self.state_dict(),
            "model_name": self.model_name,
            "num_classes": self.num_classes,
            "dropout_rate": self.dropout_rate,
            "class_to_idx": self.class_to_idx,
            "idx_to_class": self.idx_to_class,
            "metadata": metadata or {},
        }

        torch.save(payload, path)
        logger.info("Saved checkpoint successfully to %s", path)

    def load_checkpoint(
        self,
        checkpoint_path: Union[str, Path],
        device: Optional[Union[str, torch.device]] = None,
        strict: bool = True,
    ) -> Dict[str, Any]:
        """
        Load weights and metadata from a checkpoint file.

        Args:
            checkpoint_path: Path to checkpoint file.
            device: Target torch device to load tensors onto.
            strict: Whether to enforce strict key matching on state_dict.

        Returns:
            Dictionary containing stored metadata.
        """
        path = Path(checkpoint_path)
        if not path.is_file():
            raise FileNotFoundError(f"Checkpoint not found at: {path}")

        if device is None:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        elif isinstance(device, str):
            device = torch.device(device)

        checkpoint = torch.load(path, map_location=device)

        # Handle both raw state_dicts and wrapped dictionaries
        if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
            state_dict = checkpoint["model_state_dict"]
            metadata = checkpoint.get("metadata", {})
            if "class_to_idx" in checkpoint:
                self.class_to_idx = checkpoint["class_to_idx"]
            if "idx_to_class" in checkpoint:
                self.idx_to_class = checkpoint["idx_to_class"]
        elif isinstance(checkpoint, dict) and "state_dict" in checkpoint:
            state_dict = checkpoint["state_dict"]
            metadata = checkpoint.get("metadata", {})
        else:
            state_dict = checkpoint
            metadata = {}

        # Handle 'module.' prefix if trained with DataParallel / DDP
        clean_state_dict = {}
        for k, v in state_dict.items():
            clean_key = k[7:] if k.startswith("module.") else k
            clean_state_dict[clean_key] = v

        self.load_state_dict(clean_state_dict, strict=strict)
        self.to(device)
        logger.info("Loaded model weights from %s onto %s", path, device)
        return metadata


def build_model(
    num_classes: int = 4,
    pretrained: bool = True,
    device: Optional[Union[str, torch.device]] = None,
) -> BrainTumorClassifier:
    """
    Convenience factory to instantiate BrainTumorClassifier on specified device.
    """
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    elif isinstance(device, str):
        device = torch.device(device)

    model = BrainTumorClassifier(num_classes=num_classes, pretrained=pretrained)
    model.to(device)
    return model
