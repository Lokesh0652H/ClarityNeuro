#!/usr/bin/env python3
"""
Dataset Manifest Generator for NeuroScan XAI.

NeuroScan XAI - Explainable Brain Tumor MRI Classification Pipeline.
Scans raw MRI directories, catalogues every image with resolution, channels,
file size, MD5 checksum, split, and canonical class label, and serializes
a verified dataset manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

from PIL import Image

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}

CLASS_NORMALIZATION = {
    "glioma": "glioma",
    "glioma_tumor": "glioma",
    "meningioma": "meningioma",
    "meningioma_tumor": "meningioma",
    "pituitary": "pituitary",
    "pituitary_tumor": "pituitary",
    "notumor": "notumor",
    "no_tumor": "notumor",
}


def compute_md5(file_path: Path, block_size: int = 65536) -> str:
    """Compute MD5 checksum of a file."""
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        while chunk := f.read(block_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def generate_manifest(data_root: Path, output_file: Path, pretty: bool = True) -> Dict[str, Any]:
    """
    Scan data_root, build image records, and write manifest JSON.
    """
    if not data_root.is_dir():
        raise FileNotFoundError(f"Data root directory does not exist: {data_root}")

    logger.info("Generating manifest for images in: %s", data_root)

    images: List[Dict[str, Any]] = []
    split_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    corrupted_images: List[str] = []

    files = sorted(
        [p for p in data_root.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS]
    )

    logger.info("Found %d image files. Extracting metadata...", len(files))

    for p in files:
        rel_path = p.relative_to(data_root)
        parts = rel_path.parts

        if len(parts) >= 3:
            split = parts[0]
            raw_class = parts[1].lower()
        elif len(parts) == 2:
            split = "unknown"
            raw_class = parts[0].lower()
        else:
            split = "unknown"
            raw_class = "unknown"

        canonical_class = CLASS_NORMALIZATION.get(raw_class, raw_class)

        try:
            with Image.open(p) as img:
                w, h = img.size
                mode = img.mode

            file_size = p.stat().st_size
            md5_hash = compute_md5(p)

            images.append(
                {
                    "path": str(rel_path).replace("\\", "/"),
                    "split": split,
                    "class": canonical_class,
                    "raw_class_folder": raw_class,
                    "width": w,
                    "height": h,
                    "mode": mode,
                    "size_bytes": file_size,
                    "md5": md5_hash,
                }
            )
            split_counts[split][canonical_class] += 1

        except Exception as exc:
            logger.error("Failed to read image %s: %s", p, exc)
            corrupted_images.append(str(rel_path).replace("\\", "/"))

    manifest_data = {
        "dataset_name": "Brain Tumor MRI Dataset",
        "data_root": str(data_root),
        "total_images": len(images),
        "corrupted_images_count": len(corrupted_images),
        "corrupted_images": corrupted_images,
        "split_summary": {k: dict(v) for k, v in split_counts.items()},
        "images": images,
    }

    output_file.parent.mkdir(parents=True, exist_ok=True)
    indent = 2 if pretty else None
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=indent)

    logger.info("Successfully wrote manifest with %d items to: %s", len(images), output_file)
    return manifest_data


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate dataset manifest for NeuroScan XAI.")
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
        help="Path to save generated manifest (default: ml/data/manifest.json)",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        default=True,
        help="Pretty-print JSON output with indentation",
    )

    args = parser.parse_args()
    data_dir = Path(args.data_dir).resolve()
    output_manifest = Path(args.output_manifest).resolve()

    try:
        generate_manifest(data_dir, output_manifest, pretty=args.pretty)
    except Exception as exc:
        logger.error("Failed to generate manifest: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
