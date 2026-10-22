#!/usr/bin/env python3
"""
Deep Learning Training Script for Brain Tumor MRI Classification.

NeuroScan XAI - Explainable Brain Tumor MRI Classification Pipeline.
Trains an EfficientNet-B0 backbone with:
- Pretrained ImageNet feature representations
- Medically compatible augmentations on training set only
- Weighted Cross-Entropy loss for class imbalance compensation
- AdamW optimizer with Cosine Annealing learning rate schedule
- Early stopping on validation accuracy
- Comprehensive metric logging and checkpoint persistence
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import os
import random
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.app.ml.model import (
    CLASS_NAMES,
    CLASS_TO_IDX,
    IDX_TO_CLASS,
    IMAGENET_MEAN,
    IMAGENET_STD,
    BrainTumorClassifier,
)
from backend.app.ml.preprocessing import load_image

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SUPPORTED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}

# Class aliases mapping to canonical classes
CLASS_ALIASES = {
    "glioma": "glioma",
    "glioma_tumor": "glioma",
    "meningioma": "meningioma",
    "meningioma_tumor": "meningioma",
    "pituitary": "pituitary",
    "pituitary_tumor": "pituitary",
    "notumor": "notumor",
    "no_tumor": "notumor",
}


def set_seed(seed: int = 42) -> None:
    """Set global random seeds for deterministic reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


class BrainTumorDataset(Dataset):
    """
    Robust Dataset for Brain Tumor MRI scans guaranteeing canonical class index mapping:
        0: glioma, 1: meningioma, 2: pituitary, 3: notumor
    """

    def __init__(
        self,
        split_dir: Union[str, Path],
        transform: Optional[transforms.Compose] = None,
    ) -> None:
        self.split_dir = Path(split_dir)
        self.transform = transform
        self.samples: List[Tuple[Path, int, str]] = []

        if not self.split_dir.is_dir():
            raise FileNotFoundError(f"Split directory not found: {self.split_dir}")

        for child in self.split_dir.iterdir():
            if not child.is_dir():
                continue

            folder_name = child.name.lower()
            canonical_class = CLASS_ALIASES.get(folder_name)
            if canonical_class is None or canonical_class not in CLASS_TO_IDX:
                logger.warning("Skipping unrecognized folder: %s", child.name)
                continue

            class_idx = CLASS_TO_IDX[canonical_class]

            for file_path in child.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_IMAGE_EXTS:
                    self.samples.append((file_path, class_idx, canonical_class))

        if not self.samples:
            raise ValueError(f"No valid MRI images discovered in {self.split_dir}")

        logger.info(
            "Loaded split [%s]: %d images across %d classes.",
            self.split_dir.name,
            len(self.samples),
            len(set(s[1] for s in self.samples)),
        )

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        file_path, class_idx, _ = self.samples[idx]
        pil_img = load_image(file_path)

        if self.transform is not None:
            image_tensor = self.transform(pil_img)
        else:
            default_t = transforms.Compose(
                [
                    transforms.Resize((224, 224)),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
                ]
            )
            image_tensor = default_t(pil_img)

        return image_tensor, class_idx

    def get_class_counts(self) -> Dict[str, int]:
        """Return counts of images per canonical class name."""
        counts = {name: 0 for name in CLASS_NAMES}
        for _, _, cname in self.samples:
            counts[cname] += 1
        return counts


def compute_class_weights(counts: Dict[str, int], device: torch.device) -> torch.Tensor:
    """
    Compute balanced class weights inversely proportional to class frequencies:
    w_j = total_samples / (num_classes * count_j)
    """
    total = sum(counts.values())
    n_classes = len(counts)
    weights = []

    for name in CLASS_NAMES:
        c = counts.get(name, 0)
        if c > 0:
            w = total / (n_classes * c)
        else:
            w = 1.0
        weights.append(w)

    w_tensor = torch.tensor(weights, dtype=torch.float32, device=device)
    # Normalize weights so mean is 1.0
    w_tensor = w_tensor / w_tensor.mean()
    return w_tensor


def resolve_split_path(root_dir: Path, split_name: str) -> Path:
    """Find split folder handling casing differences (e.g., Training vs training)."""
    target = root_dir / split_name
    if target.is_dir():
        return target
    target_lower = root_dir / split_name.lower()
    if target_lower.is_dir():
        return target_lower
    target_upper = root_dir / split_name.capitalize()
    if target_upper.is_dir():
        return target_upper
    raise FileNotFoundError(f"Could not locate split '{split_name}' in {root_dir}")


def train_one_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    optimizer: optim.Optimizer,
    device: torch.device,
) -> Tuple[float, float]:
    """Train model for a single epoch."""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in dataloader:
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        optimizer.zero_grad()
        logits = model(images)
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)
        preds = torch.argmax(logits, dim=1)
        correct += torch.sum(preds == labels).item()
        total += images.size(0)

    epoch_loss = running_loss / max(total, 1)
    epoch_acc = correct / max(total, 1)
    return epoch_loss, epoch_acc


def validate_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> Tuple[float, float, float]:
    """Validate model and calculate loss, accuracy, and balanced accuracy."""
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0

    all_preds: List[int] = []
    all_targets: List[int] = []

    with torch.no_grad():
        for images, labels in dataloader:
            images = images.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)

            logits = model(images)
            loss = criterion(logits, labels)

            running_loss += loss.item() * images.size(0)
            preds = torch.argmax(logits, dim=1)
            correct += torch.sum(preds == labels).item()
            total += images.size(0)

            all_preds.extend(preds.cpu().numpy().tolist())
            all_targets.extend(labels.cpu().numpy().tolist())

    val_loss = running_loss / max(total, 1)
    val_acc = correct / max(total, 1)

    # Compute balanced accuracy
    y_true = np.array(all_targets)
    y_pred = np.array(all_preds)
    recalls = []
    for c in range(len(CLASS_NAMES)):
        mask = y_true == c
        if np.sum(mask) > 0:
            recalls.append(float(np.mean(y_pred[mask] == c)))
    balanced_acc = float(np.mean(recalls)) if recalls else val_acc

    return val_loss, val_acc, balanced_acc


def train_pipeline(args: argparse.Namespace) -> None:
    """Main training orchestration routine."""
    set_seed(args.seed)

    # Device selection
    if args.device:
        device = torch.device(args.device)
    else:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    logger.info("Using device: %s", device)

    data_root = Path(args.data_dir).resolve()
    train_dir = resolve_split_path(data_root, "Training")
    val_dir = resolve_split_path(data_root, "Testing")

    # Transforms
    train_transform = BrainTumorClassifier.get_preprocessing_transform(is_training=True, image_size=args.image_size)
    val_transform = BrainTumorClassifier.get_preprocessing_transform(is_training=False, image_size=args.image_size)

    # Datasets and Loaders
    train_dataset = BrainTumorDataset(train_dir, transform=train_transform)
    val_dataset = BrainTumorDataset(val_dir, transform=val_transform)

    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.num_workers,
        pin_memory=(device.type == "cuda"),
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=(device.type == "cuda"),
    )

    # Model instantiation
    logger.info("Initializing BrainTumorClassifier with %s...", args.model_name)
    model = BrainTumorClassifier(
        num_classes=len(CLASS_NAMES),
        pretrained=args.pretrained,
        dropout_rate=args.dropout,
        model_name=args.model_name,
    )
    model.to(device)

    # Loss function with optional class weighting
    if args.use_class_weights:
        class_counts = train_dataset.get_class_counts()
        weights = compute_class_weights(class_counts, device=device)
        logger.info("Applying balanced class weights: %s", weights.cpu().numpy().tolist())
        criterion = nn.CrossEntropyLoss(weight=weights)
    else:
        criterion = nn.CrossEntropyLoss()

    # Optimizer & Scheduler
    optimizer = optim.AdamW(
        model.parameters(),
        lr=args.lr,
        weight_decay=args.weight_decay,
    )

    scheduler = CosineAnnealingLR(
        optimizer,
        T_max=args.epochs,
        eta_min=args.min_lr,
    )

    # Output directory
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    best_checkpoint_path = output_dir / "best_model.pt"
    last_checkpoint_path = output_dir / "last_model.pt"

    history: List[Dict[str, Any]] = []
    best_val_acc = 0.0
    best_epoch = 0
    patience_counter = 0

    logger.info("Commencing training for %d epochs...", args.epochs)

    for epoch in range(1, args.epochs + 1):
        t0 = time.time()
        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc, val_bal_acc = validate_epoch(model, val_loader, criterion, device)
        scheduler.step()
        elapsed = time.time() - t0

        current_lr = float(optimizer.param_groups[0]["lr"])

        epoch_record = {
            "epoch": epoch,
            "train_loss": round(train_loss, 4),
            "train_acc": round(train_acc, 4),
            "val_loss": round(val_loss, 4),
            "val_acc": round(val_acc, 4),
            "val_balanced_acc": round(val_bal_acc, 4),
            "lr": current_lr,
            "elapsed_sec": round(elapsed, 2),
        }
        history.append(epoch_record)

        logger.info(
            "Epoch [%02d/%02d] (%.1fs) | Train Loss: %.4f, Acc: %.2f%% | Val Loss: %.4f, Acc: %.2f%% (Bal: %.2f%%) | LR: %.6f",
            epoch,
            args.epochs,
            elapsed,
            train_loss,
            train_acc * 100,
            val_loss,
            val_acc * 100,
            val_bal_acc * 100,
            current_lr,
        )

        # Checkpoint if best validation accuracy achieved
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_epoch = epoch
            patience_counter = 0

            meta = {
                "epoch": epoch,
                "best_val_acc": best_val_acc,
                "val_balanced_acc": val_bal_acc,
                "val_loss": val_loss,
                "train_acc": train_acc,
                "train_loss": train_loss,
                "args": vars(args),
            }
            model.save_checkpoint(best_checkpoint_path, metadata=meta)
            logger.info("--> Saved new best checkpoint to %s (Val Acc: %.2f%%)", best_checkpoint_path, val_acc * 100)
        else:
            patience_counter += 1
            if patience_counter >= args.patience:
                logger.info(
                    "Early stopping triggered after %d epochs without improvement (Patience: %d).",
                    epoch,
                    args.patience,
                )
                break

    # Save last checkpoint
    last_meta = {
        "epoch": len(history),
        "val_acc": history[-1]["val_acc"] if history else 0.0,
        "best_val_acc": best_val_acc,
        "best_epoch": best_epoch,
        "args": vars(args),
    }
    model.save_checkpoint(last_checkpoint_path, metadata=last_meta)

    # Save history JSON
    history_path = output_dir / "training_history.json"
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "best_epoch": best_epoch,
                "best_val_acc": best_val_acc,
                "epochs_completed": len(history),
                "history": history,
            },
            f,
            indent=2,
        )

    logger.info("Training complete. Best Val Acc: %.2f%% (Epoch %d)", best_val_acc * 100, best_epoch)
    logger.info("Saved models and logs to %s", output_dir)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train NeuroScan XAI Brain Tumor Classifier."
    )
    parser.add_argument("--data-dir", type=str, default="ml/data/raw", help="Path to raw dataset root")
    parser.add_argument("--output-dir", type=str, default="ml/checkpoints", help="Path to save checkpoints")
    parser.add_argument("--model-name", type=str, default="efficientnet_b0", help="timm model architecture")
    parser.add_argument("--image-size", type=int, default=224, help="Input image dimension")
    parser.add_argument("--batch-size", type=int, default=32, help="Mini-batch size")
    parser.add_argument("--epochs", type=int, default=30, help="Total training epochs")
    parser.add_argument("--lr", type=float, default=3e-4, help="Initial learning rate")
    parser.add_argument("--min-lr", type=float, default=1e-6, help="Minimum cosine learning rate")
    parser.add_argument("--weight-decay", type=float, default=1e-2, help="AdamW weight decay")
    parser.add_argument("--dropout", type=float, default=0.2, help="Head dropout rate")
    parser.add_argument("--patience", type=int, default=7, help="Early stopping patience")
    parser.add_argument("--num-workers", type=int, default=0, help="DataLoader worker processes")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--pretrained", action="store_true", default=True, help="Load ImageNet weights")
    parser.add_argument("--use-class-weights", action="store_true", default=True, help="Use balanced class weights")
    parser.add_argument("--device", type=str, default=None, help="Explicit device override (cpu, cuda, cuda:0)")

    args = parser.parse_args()
    train_pipeline(args)


if __name__ == "__main__":
    main()
