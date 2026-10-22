"""Dataset Service: Inspects local filesystem, scans brain MRI data, and validates class balance."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.config import settings
from app.database.models import DatasetRegistry

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".webp"}


class DatasetService:
    """Service for scanning, validating, and managing MRI datasets."""

    def __init__(self, root_path: Optional[Path] = None) -> None:
        self.root_path = root_path or settings.resolved_dataset_path

    def get_status(self) -> Dict[str, Any]:
        """Check filesystem existence and scan MRI dataset structure."""
        path = self.root_path
        if not path.exists():
            return {
                "available": False,
                "dataset_path": str(path),
                "exists": False,
                "total_images": 0,
                "class_distribution": {},
                "splits": {},
                "error": f"Directory does not exist at '{path}'",
            }

        try:
            total_images = 0
            class_counts: Dict[str, int] = {c: 0 for c in settings.MODEL_CLASSES}
            splits_counts: Dict[str, int] = {}

            # Check subdirectories for splits: train, val, test (or Testing, Training)
            subdirs = [p for p in path.iterdir() if p.is_dir()]
            split_candidates = {"train", "training", "val", "validation", "test", "testing"}
            found_splits = [d for d in subdirs if d.name.lower() in split_candidates]

            if found_splits:
                # Structure: dataset_path / <split> / <class_name> / <images>
                for split_dir in found_splits:
                    split_name = split_dir.name.lower()
                    splits_counts[split_name] = 0

                    for class_dir in split_dir.iterdir():
                        if class_dir.is_dir():
                            c_name = class_dir.name.lower()
                            # Find matched target class
                            matched_class = next((c for c in settings.MODEL_CLASSES if c in c_name or c_name in c), c_name)
                            count = sum(1 for f in class_dir.iterdir() if f.suffix.lower() in IMAGE_EXTENSIONS)
                            splits_counts[split_name] += count
                            total_images += count
                            class_counts[matched_class] = class_counts.get(matched_class, 0) + count
            else:
                # Flat structure: dataset_path / <class_name> / <images>
                for class_dir in subdirs:
                    c_name = class_dir.name.lower()
                    matched_class = next((c for c in settings.MODEL_CLASSES if c in c_name or c_name in c), c_name)
                    count = sum(1 for f in class_dir.iterdir() if f.suffix.lower() in IMAGE_EXTENSIONS)
                    total_images += count
                    class_counts[matched_class] = class_counts.get(matched_class, 0) + count

            available = total_images > 0
            error = None if available else "Dataset directory exists but contains 0 images"

            return {
                "available": available,
                "dataset_path": str(path),
                "exists": True,
                "total_images": total_images,
                "class_distribution": class_counts,
                "splits": splits_counts,
                "error": error,
            }

        except Exception as e:
            logger.error(f"Error scanning dataset path: {str(e)}", exc_info=True)
            return {
                "available": False,
                "dataset_path": str(path),
                "exists": True,
                "total_images": 0,
                "class_distribution": {},
                "splits": {},
                "error": f"Failed scanning dataset: {str(e)}",
            }

    def get_sample_files(
        self, split: Optional[str] = None, class_name: Optional[str] = None, limit: int = 10
    ) -> List[Path]:
        """Retrieve real sample image file paths from the dataset for testing/auditing."""
        path = self.root_path
        if not path.exists():
            return []

        results: List[Path] = []
        for p in path.rglob("*"):
            if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS:
                if split and split.lower() not in str(p).lower():
                    continue
                if class_name and class_name.lower() not in str(p).lower():
                    continue
                results.append(p)
                if len(results) >= limit:
                    break
        return results

    def sync_with_db(self, db: Session) -> Optional[DatasetRegistry]:
        """Synchronize current scanned filesystem state into DatasetRegistry database table."""
        status = self.get_status()
        existing = db.query(DatasetRegistry).filter_by(name="Brain Tumor MRI Primary").first()

        if existing:
            existing.total_images = status["total_images"]
            existing.class_distribution = status["class_distribution"]
            existing.splits = status["splits"]
            existing.validation_status = "validated" if status["available"] else "missing"
            db.commit()
            db.refresh(existing)
            return existing
        else:
            new_reg = DatasetRegistry(
                name="Brain Tumor MRI Primary",
                source_url="https://www.kaggle.com/datasets/masoudnickparamb/brain-tumor-mri-dataset",
                license="CC BY-SA 4.0",
                total_images=status["total_images"],
                class_distribution=status["class_distribution"],
                splits=status["splits"],
                validation_status="validated" if status["available"] else "missing",
                manifest_path=str(self.root_path),
            )
            db.add(new_reg)
            db.commit()
            db.refresh(new_reg)
            return new_reg


# Singleton instance
dataset_service = DatasetService()
