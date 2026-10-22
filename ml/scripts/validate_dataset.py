#!/usr/bin/env python3
"""
Dataset Validation, Data Leakage Detection, and Integrity Scanner.

NeuroScan XAI - Explainable Brain Tumor MRI Classification Pipeline.
Performs comprehensive scientific audits on raw medical image datasets:
- Scans and verifies every individual image file
- Detects corrupted, unreadable, or truncated files
- Computes MD5 checksums for exact duplicate identification
- Detects Train/Test Data Leakage (identical images across splits)
- Calculates class distributions and imbalance ratios
- Audits dimensional statistics (resolutions, aspect ratios, color modes)
- Generates a certified dataset manifest JSON file
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np
from PIL import Image

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


def compute_file_md5(file_path: Path, chunk_size: int = 65536) -> str:
    """Compute MD5 checksum of a file efficiently in binary chunks."""
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


@dataclass
class ImageRecord:
    file_path: str
    relative_path: str
    split: str
    class_name: str
    width: int
    height: int
    mode: str
    file_size_bytes: int
    md5: str
    is_valid: bool
    error: Optional[str] = None


class DatasetValidator:
    """
    Scans physical disk directory to validate dataset integrity, corruption,
    and train/test leakage.
    """

    def __init__(self, data_root: Path) -> None:
        self.data_root = data_root.resolve()

    def run_validation(self) -> Dict[str, Any]:
        """
        Execute full validation scan across the data root.

        Returns:
            Dictionary containing audit results and manifest.
        """
        if not self.data_root.is_dir():
            raise FileNotFoundError(f"Dataset root directory does not exist: {self.data_root}")

        logger.info("Scanning dataset root at %s...", self.data_root)

        records: List[ImageRecord] = []
        corrupted_files: List[Dict[str, str]] = []
        md5_to_records: Dict[str, List[ImageRecord]] = defaultdict(list)

        # Collect all candidate image files
        all_candidate_files = [
            p for p in self.data_root.rglob("*")
            if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
        ]

        if not all_candidate_files:
            logger.warning("No image files found in %s with extensions %s", self.data_root, SUPPORTED_EXTENSIONS)

        logger.info("Found %d candidate image files. Verifying integrity...", len(all_candidate_files))

        widths: List[int] = []
        heights: List[int] = []
        modes_count: Dict[str, int] = defaultdict(int)

        for file_path in all_candidate_files:
            rel_path = file_path.relative_to(self.data_root)
            parts = rel_path.parts

            # Infer split and class from directory hierarchy
            if len(parts) >= 3:
                split = parts[0]
                class_name = parts[1].lower()
            elif len(parts) == 2:
                split = "unknown"
                class_name = parts[0].lower()
            else:
                split = "unknown"
                class_name = "unknown"

            # Normalize common naming aliases
            if class_name in ("no_tumor", "notumor"):
                class_name = "notumor"
            elif class_name in ("glioma_tumor", "glioma"):
                class_name = "glioma"
            elif class_name in ("meningioma_tumor", "meningioma"):
                class_name = "meningioma"
            elif class_name in ("pituitary_tumor", "pituitary"):
                class_name = "pituitary"

            file_size = file_path.stat().st_size

            # Check file readability and image corruption
            try:
                with Image.open(file_path) as img:
                    img.verify()

                # Reopen to read dimensions and mode
                with Image.open(file_path) as img:
                    w, h = img.size
                    mode = img.mode
                    widths.append(w)
                    heights.append(h)
                    modes_count[mode] += 1

                md5_sum = compute_file_md5(file_path)
                rec = ImageRecord(
                    file_path=str(file_path),
                    relative_path=str(rel_path).replace("\\", "/"),
                    split=split,
                    class_name=class_name,
                    width=w,
                    height=h,
                    mode=mode,
                    file_size_bytes=file_size,
                    md5=md5_sum,
                    is_valid=True,
                )
                records.append(rec)
                md5_to_records[md5_sum].append(rec)

            except Exception as exc:
                err_msg = str(exc)
                logger.error("Corrupted image detected: %s (%s)", file_path, err_msg)
                corrupted_files.append({"file": str(file_path), "error": err_msg})
                records.append(
                    ImageRecord(
                        file_path=str(file_path),
                        relative_path=str(rel_path).replace("\\", "/"),
                        split=split,
                        class_name=class_name,
                        width=0,
                        height=0,
                        mode="unknown",
                        file_size_bytes=file_size,
                        md5="",
                        is_valid=False,
                        error=err_msg,
                    )
                )

        # Split and Class Distribution Counts
        split_class_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        class_totals: Dict[str, int] = defaultdict(int)

        for r in records:
            if r.is_valid:
                split_class_counts[r.split][r.class_name] += 1
                class_totals[r.class_name] += 1

        # Class Imbalance Calculation
        total_valid = len(widths)
        imbalance_ratios: Dict[str, float] = {}
        if class_totals:
            max_c = max(class_totals.values())
            min_c = min(class_totals.values())
            imbalance_ratio = float(max_c / min_c) if min_c > 0 else 0.0
            imbalance_ratios["overall_imbalance_ratio"] = round(imbalance_ratio, 2)
            imbalance_ratios["min_class_count"] = min_c
            imbalance_ratios["max_class_count"] = max_c

        # Data Leakage and Duplicate Detection
        duplicates_within_splits: List[Dict[str, Any]] = []
        data_leakage_cases: List[Dict[str, Any]] = []

        for md5, dup_records in md5_to_records.items():
            if len(dup_records) > 1:
                splits_involved = set(r.split for r in dup_records)
                classes_involved = set(r.class_name for r in dup_records)
                paths = [r.relative_path for r in dup_records]

                # If the same identical image is present across different splits
                if len(splits_involved) > 1:
                    data_leakage_cases.append(
                        {
                            "md5": md5,
                            "splits": list(splits_involved),
                            "classes": list(classes_involved),
                            "files": paths,
                            "count": len(dup_records),
                        }
                    )
                else:
                    duplicates_within_splits.append(
                        {
                            "md5": md5,
                            "split": list(splits_involved)[0],
                            "files": paths,
                            "count": len(dup_records),
                        }
                    )

        # Dimension statistics
        dim_stats = {}
        if widths and heights:
            w_arr = np.array(widths)
            h_arr = np.array(heights)
            dim_stats = {
                "min_width": int(np.min(w_arr)),
                "max_width": int(np.max(w_arr)),
                "mean_width": float(round(np.mean(w_arr), 1)),
                "min_height": int(np.min(h_arr)),
                "max_height": int(np.max(h_arr)),
                "mean_height": float(round(np.mean(h_arr), 1)),
                "color_modes": dict(modes_count),
            }

        # Build validation summary
        summary = {
            "dataset_root": str(self.data_root),
            "total_candidate_files": len(all_candidate_files),
            "total_valid_scans": total_valid,
            "corrupted_count": len(corrupted_files),
            "corrupted_files": corrupted_files,
            "splits": {k: dict(v) for k, v in split_class_counts.items()},
            "class_totals": dict(class_totals),
            "imbalance_metrics": imbalance_ratios,
            "dimension_statistics": dim_stats,
            "duplicate_count_within_splits": len(duplicates_within_splits),
            "data_leakage_count": len(data_leakage_cases),
            "data_leakage_cases": data_leakage_cases,
            "passed_validation": len(corrupted_files) == 0 and len(data_leakage_cases) == 0 and total_valid > 0,
        }

        return {
            "summary": summary,
            "records": [asdict(r) for r in records],
        }


def print_validation_report(summary: Dict[str, Any]) -> None:
    """Print clean terminal report of dataset validation results."""
    print("=" * 70)
    print("           NEUROSCAN XAI - DATASET INTEGRITY REPORT")
    print("=" * 70)
    print(f"Dataset Root       : {summary['dataset_root']}")
    print(f"Total Valid Images : {summary['total_valid_scans']}")
    print(f"Corrupted Images   : {summary['corrupted_count']}")
    print(f"Data Leakage Items : {summary['data_leakage_count']}")
    print("-" * 70)

    print("Distribution by Split & Class:")
    for split_name, cls_map in summary["splits"].items():
        subtotal = sum(cls_map.values())
        print(f"  [{split_name}] Total: {subtotal}")
        for cname, cnt in cls_map.items():
            print(f"    - {cname:<15}: {cnt}")

    if summary.get("imbalance_metrics"):
        imb = summary["imbalance_metrics"]
        print("-" * 70)
        print(f"Class Imbalance Ratio: {imb.get('overall_imbalance_ratio', 1.0):.2f}:1")

    if summary.get("dimension_statistics"):
        dims = summary["dimension_statistics"]
        print("-" * 70)
        print("Image Dimensions:")
        print(f"  Width  : min={dims.get('min_width')}, mean={dims.get('mean_width')}, max={dims.get('max_width')}")
        print(f"  Height : min={dims.get('min_height')}, mean={dims.get('mean_height')}, max={dims.get('max_height')}")
        print(f"  Modes  : {dims.get('color_modes')}")

    if summary["data_leakage_cases"]:
        print("-" * 70)
        print(f"WARNING: DATA LEAKAGE DETECTED! ({len(summary['data_leakage_cases'])} cases)")
        for leak in summary["data_leakage_cases"][:5]:
            print(f"  MD5 {leak['md5']}: {leak['files']}")
        if len(summary["data_leakage_cases"]) > 5:
            print(f"  ... and {len(summary['data_leakage_cases']) - 5} more leakage cases.")

    print("=" * 70)
    status_str = "PASSED CERTIFICATION" if summary["passed_validation"] else "FAILED CERTIFICATION"
    print(f"OVERALL STATUS: {status_str}")
    print("=" * 70)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit and validate Brain Tumor MRI dataset integrity."
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="ml/data/raw",
        help="Path to dataset root folder (default: ml/data/raw)",
    )
    parser.add_argument(
        "--output-manifest",
        type=str,
        default="ml/data/manifest.json",
        help="Path to save generated manifest JSON (default: ml/data/manifest.json)",
    )

    args = parser.parse_args()
    data_path = Path(args.data_dir).resolve()
    manifest_path = Path(args.output_manifest).resolve()

    validator = DatasetValidator(data_path)
    try:
        results = validator.run_validation()
    except Exception as exc:
        logger.error("Dataset validation failed: %s", exc)
        sys.exit(1)

    print_validation_report(results["summary"])

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    logger.info("Saved dataset manifest to %s", manifest_path)
    sys.exit(0 if results["summary"]["passed_validation"] else 1)


if __name__ == "__main__":
    main()
