#!/usr/bin/env python3
"""
Brain Tumor MRI Dataset Downloader.

NeuroScan XAI - Explainable Brain Tumor MRI Classification Pipeline.
Downloads and verifies the Masoud Nickparvar Brain Tumor MRI Dataset from Kaggle.
Dataset ID: masoudnickparvar/brain-tumor-mri-dataset
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

KAGGLE_DATASET_ID = "masoudnickparvar/brain-tumor-mri-dataset"
EXPECTED_CLASSES = ["glioma", "meningioma", "notumor", "pituitary"]
EXPECTED_SPLITS = ["Training", "Testing"]

# Alternative folder names that appear in various dataset releases
CLASS_NAME_ALIASES: Dict[str, str] = {
    "glioma_tumor": "glioma",
    "meningioma_tumor": "meningioma",
    "pituitary_tumor": "pituitary",
    "no_tumor": "notumor",
    "notumor": "notumor",
    "glioma": "glioma",
    "meningioma": "meningioma",
    "pituitary": "pituitary",
}


def check_kaggle_credentials() -> Tuple[bool, str]:
    """
    Check if Kaggle credentials exist on the host system.

    Returns:
        Tuple of (is_configured: bool, description: str).
    """
    # 1. Environment variables
    if os.getenv("KAGGLE_USERNAME") and os.getenv("KAGGLE_KEY"):
        return True, "Kaggle credentials found in environment variables (KAGGLE_USERNAME, KAGGLE_KEY)."

    # 2. Config file in user home directory
    home = Path.home()
    kaggle_json = home / ".kaggle" / "kaggle.json"
    if kaggle_json.is_file():
        # Check that file is non-empty
        if kaggle_json.stat().st_size > 10:
            return True, f"Kaggle token found at {kaggle_json}"

    return False, "No Kaggle credentials found."


def print_kaggle_setup_instructions() -> None:
    """Print actionable instructions for authenticating with Kaggle."""
    instructions = """
================================================================================
  KAGGLE AUTHENTICATION REQUIRED
================================================================================
To automatically download the Brain Tumor MRI dataset, configure your Kaggle API key:

Option 1: Kaggle API Token File (Recommended)
---------------------------------------------
1. Log in to https://www.kaggle.com
2. Navigate to: Account -> Settings -> API section
3. Click 'Create New Token' to download kaggle.json
4. Place the file at:
   Windows : C:\\Users\\<YourUsername>\\.kaggle\\kaggle.json
   Linux/Mac: ~/.kaggle/kaggle.json
5. (On Linux/Mac) Run: chmod 600 ~/.kaggle/kaggle.json

Option 2: Environment Variables
--------------------------------
Set the following environment variables in your terminal:
   $env:KAGGLE_USERNAME = "your_kaggle_username"
   $env:KAGGLE_KEY      = "your_kaggle_api_key"

Option 3: Manual Browser Download
---------------------------------
1. Visit: https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset
2. Click 'Download' (approx. 149 MB zip)
3. Extract the archive into:
   ml/data/raw/
   Expected structure:
     ml/data/raw/Training/{glioma, meningioma, notumor, pituitary}
     ml/data/raw/Testing/{glioma, meningioma, notumor, pituitary}
================================================================================
"""
    print(instructions, file=sys.stderr)


def check_kaggle_cli_installed() -> bool:
    """Check if the `kaggle` command line executable is present in PATH."""
    return shutil.which("kaggle") is not None


def normalize_class_directories(raw_dir: Path) -> None:
    """
    Standardize directory naming if aliases exist (e.g., glioma_tumor -> glioma).
    """
    for split_dir in [raw_dir / "Training", raw_dir / "Testing", raw_dir / "training", raw_dir / "testing"]:
        if not split_dir.is_dir():
            continue
        for child in list(split_dir.iterdir()):
            if child.is_dir():
                clean_name = CLASS_NAME_ALIASES.get(child.name.lower(), child.name.lower())
                target = split_dir / clean_name
                if child.name != clean_name and not target.exists():
                    print(f"Normalizing folder name: {child.name} -> {clean_name}")
                    child.rename(target)


def verify_dataset_structure(target_dir: Path) -> Tuple[bool, Dict[str, Dict[str, int]]]:
    """
    Verify that the dataset directory structure contains expected splits and classes.

    Returns:
        Tuple of (is_valid: bool, counts_dict: dict).
    """
    counts: Dict[str, Dict[str, int]] = {}
    valid = True

    # Check case-insensitive splits
    for split_name in EXPECTED_SPLITS:
        split_path = target_dir / split_name
        if not split_path.is_dir():
            # Check lowercase alternative
            alt_path = target_dir / split_name.lower()
            if alt_path.is_dir():
                split_path = alt_path
            else:
                valid = False
                continue

        counts[split_name] = {}
        for cls in EXPECTED_CLASSES:
            cls_path = split_path / cls
            if not cls_path.is_dir():
                # Check alias
                found = False
                for alias, std_name in CLASS_NAME_ALIASES.items():
                    if std_name == cls and (split_path / alias).is_dir():
                        cls_path = split_path / alias
                        found = True
                        break
                if not found:
                    valid = False
                    counts[split_name][cls] = 0
                    continue

            # Count valid images
            valid_exts = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
            img_count = sum(1 for f in cls_path.iterdir() if f.suffix.lower() in valid_exts)
            counts[split_name][cls] = img_count
            if img_count == 0:
                valid = False

    return valid, counts


def download_dataset(
    output_dir: Path,
    dataset_id: str = KAGGLE_DATASET_ID,
    force: bool = False,
) -> bool:
    """
    Download and extract Kaggle dataset to output_dir.

    Args:
        output_dir: Destination path (e.g. ml/data/raw).
        dataset_id: Kaggle dataset slug.
        force: Overwrite existing files if True.

    Returns:
        True if download and verification succeeded, False otherwise.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Check if already present and valid
    if not force:
        already_valid, existing_counts = verify_dataset_structure(output_dir)
        if already_valid:
            print(f"Dataset already present and verified at {output_dir}")
            for split, classes in existing_counts.items():
                print(f"  {split}: {classes}")
            return True

    # Verify credentials
    has_creds, cred_desc = check_kaggle_credentials()
    if not has_creds:
        print_kaggle_setup_instructions()
        return False

    print(f"Credential status: {cred_desc}")

    # Check CLI
    if not check_kaggle_cli_installed():
        print(
            "The 'kaggle' CLI tool is not found in PATH.\n"
            "Install it with `pip install kaggle` and ensure your Python Scripts folder is in PATH.",
            file=sys.stderr,
        )
        print_kaggle_setup_instructions()
        return False

    print(f"Starting download of '{dataset_id}' to '{output_dir}'...")

    cmd = [
        "kaggle",
        "datasets",
        "download",
        "-d",
        dataset_id,
        "-p",
        str(output_dir),
        "--unzip" if not force else "--unzip",
    ]
    if force:
        cmd.append("--force")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)
    except subprocess.CalledProcessError as exc:
        print(f"Kaggle download command failed:\n{exc.stderr}", file=sys.stderr)
        return False
    except Exception as exc:
        print(f"Unexpected error executing kaggle CLI: {exc}", file=sys.stderr)
        return False

    # Check for any remaining zip files to unpack
    for zip_path in output_dir.glob("*.zip"):
        print(f"Extracting archive: {zip_path.name}...")
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(output_dir)
            zip_path.unlink()  # Remove zip after extraction
        except Exception as exc:
            print(f"Failed to extract zip file {zip_path}: {exc}", file=sys.stderr)
            return False

    # Normalize directory names
    normalize_class_directories(output_dir)

    # Verify extracted structure
    is_valid, counts = verify_dataset_structure(output_dir)
    if not is_valid:
        print(
            f"WARNING: Download completed but expected structure was not fully verified in {output_dir}.\n"
            f"Observed counts: {counts}",
            file=sys.stderr,
        )
        return False

    print("=" * 60)
    print("Dataset successfully downloaded and verified!")
    print("=" * 60)
    for split, classes in counts.items():
        total_split = sum(classes.values())
        print(f"{split} Split (Total: {total_split}):")
        for cls_name, count in classes.items():
            print(f"  - {cls_name:<15}: {count} scans")
    print("=" * 60)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download and verify Kaggle Brain Tumor MRI Dataset for NeuroScan XAI."
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="ml/data/raw",
        help="Target directory to store raw dataset (default: ml/data/raw)",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default=KAGGLE_DATASET_ID,
        help=f"Kaggle dataset slug (default: {KAGGLE_DATASET_ID})",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-download even if dataset directory exists.",
    )

    args = parser.parse_args()
    target_path = Path(args.output_dir).resolve()

    success = download_dataset(target_path, dataset_id=args.dataset, force=args.force)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
