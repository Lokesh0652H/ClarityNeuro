#!/usr/bin/env python3
"""
Model Evaluation and Benchmark Execution Script.

NeuroScan XAI - Explainable Brain Tumor MRI Classification Pipeline.
Loads a trained model checkpoint and evaluates it on the test partition, computing:
- Accuracy, Balanced Accuracy, and Multi-class Log Loss
- Per-class Precision, Recall, and F1-scores
- Confusion Matrix
- Latency and throughput profiles
- Generates certified evaluation report JSON
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import torch
from torch.utils.data import DataLoader

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.app.ml.evaluation import ModelEvaluator
from backend.app.ml.model import BrainTumorClassifier
from ml.scripts.train import BrainTumorDataset, resolve_split_path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def evaluate_checkpoint(
    checkpoint_path: Path,
    data_dir: Path,
    output_report_path: Path,
    batch_size: int = 32,
    device_str: str = None,
) -> None:
    """
    Evaluate checkpoint on test data split and persist results.
    """
    if not checkpoint_path.is_file():
        raise FileNotFoundError(f"Model checkpoint not found at: {checkpoint_path}")

    if device_str:
        device = torch.device(device_str)
    else:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    logger.info("Evaluating on device: %s", device)

    # Resolve test directory
    test_dir = resolve_split_path(data_dir, "Testing")
    val_transform = BrainTumorClassifier.get_preprocessing_transform(is_training=False)

    test_dataset = BrainTumorDataset(test_dir, transform=val_transform)
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0,
    )

    # Initialize model architecture and load checkpoint weights
    logger.info("Loading model weights from %s...", checkpoint_path)
    model = BrainTumorClassifier(num_classes=4, pretrained=False)
    meta = model.load_checkpoint(checkpoint_path, device=device)
    logger.info("Loaded checkpoint metadata: %s", meta)

    # Run evaluation suite
    logger.info("Running evaluation suite across %d test samples...", len(test_dataset))
    evaluator = ModelEvaluator()
    results = evaluator.evaluate(model, test_loader, device=device)

    # Print summary table
    print("\n" + results.summary() + "\n")

    # Save results to JSON file
    output_report_path.parent.mkdir(parents=True, exist_ok=True)
    results.save_json(output_report_path)
    logger.info("Evaluation results saved to: %s", output_report_path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate NeuroScan XAI Brain Tumor Classifier on test dataset."
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        default="ml/checkpoints/best_model.pt",
        help="Path to trained model checkpoint (default: ml/checkpoints/best_model.pt)",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="ml/data/raw",
        help="Path to dataset root folder containing Testing/ split (default: ml/data/raw)",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default="ml/reports/evaluation_results.json",
        help="Path to save evaluation JSON results (default: ml/reports/evaluation_results.json)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="DataLoader batch size (default: 32)",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Explicit device override (e.g., cpu, cuda, cuda:0)",
    )

    args = parser.parse_args()

    checkpoint_path = Path(args.checkpoint).resolve()
    data_dir = Path(args.data_dir).resolve()
    output_report = Path(args.output_file).resolve()

    try:
        evaluate_checkpoint(
            checkpoint_path=checkpoint_path,
            data_dir=data_dir,
            output_report_path=output_report,
            batch_size=args.batch_size,
            device_str=args.device,
        )
    except Exception as exc:
        logger.error("Evaluation failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
