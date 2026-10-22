"""Analysis Service: Orchestrates image validation, inference, and database persistence."""

import logging
import time
import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.core.exceptions import ResourceNotFoundException, ModelNotAvailableException
from app.core.security import validate_image_file, sanitize_filename
from app.database.models import AnalysisRecord
from app.schemas.analysis import AnalysisResponse, BatchAnalysisResponse
from app.services.model_service import model_service

logger = logging.getLogger(__name__)


class AnalysisService:
    """Orchestrates image upload, validation, ML inference, and persistence."""

    def __init__(self) -> None:
        self.upload_dir: Path = settings.resolved_upload_dir

    async def analyze_file(
        self,
        file: UploadFile,
        db: Session,
        generate_cam: bool = False,
    ) -> AnalysisResponse:
        """Process an uploaded MRI scan file: validate, infer, and persist record."""
        # 1. Validate image format, dimensions, and size
        image_bytes, _ = await validate_image_file(file)
        clean_name = sanitize_filename(file.filename or "mri_scan.jpg")

        # 2. Save temporary upload copy
        scan_id = str(uuid.uuid4())
        saved_filename = f"{scan_id}_{clean_name}"
        saved_file_path = self.upload_dir / saved_filename
        with open(saved_file_path, "wb") as f:
            f.write(image_bytes)

        # 3. Execute inference via model_service
        inference_result = model_service.predict(image_bytes)

        # 4. Optional Grad-CAM generation
        gradcam_path = None
        if generate_cam:
            try:
                cam_res = model_service.generate_gradcam(image_bytes)
                gradcam_path = cam_res.get("heatmap_url")
            except Exception as e:
                logger.warning(f"Failed generating initial Grad-CAM: {e}")

        # 5. Persist record in database
        record = AnalysisRecord(
            id=scan_id,
            filename=clean_name,
            predicted_class=inference_result["predicted_class"],
            confidence=inference_result["confidence"],
            probabilities=inference_result["probabilities"],
            entropy=inference_result["entropy"],
            normalized_entropy=inference_result["normalized_entropy"],
            prediction_margin=inference_result["prediction_margin"],
            inference_time_ms=inference_result["inference_time_ms"],
            model_version=inference_result["model_version"],
            gradcam_path=gradcam_path,
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        return AnalysisResponse(
            analysis_id=record.id,
            filename=record.filename,
            predicted_class=record.predicted_class,
            confidence=record.confidence,
            probabilities=record.probabilities,
            entropy=record.entropy,
            normalized_entropy=record.normalized_entropy,
            prediction_margin=record.prediction_margin,
            inference_time_ms=record.inference_time_ms,
            model_version=record.model_version,
            gradcam_path=record.gradcam_path,
        )

    async def analyze_batch(
        self,
        files: List[UploadFile],
        db: Session,
        generate_cam: bool = False,
    ) -> BatchAnalysisResponse:
        """Process a batch of uploaded MRI scans sequentially."""
        start_time = time.perf_counter()
        results: List[AnalysisResponse] = []

        for file in files:
            res = await self.analyze_file(file, db, generate_cam=generate_cam)
            results.append(res)

        total_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return BatchAnalysisResponse(
            items=results,
            total_processed=len(results),
            total_time_ms=total_time_ms,
        )

    def get_analysis_by_id(self, analysis_id: str, db: Session) -> AnalysisRecord:
        """Fetch analysis record by UUID or raise ResourceNotFoundException."""
        record = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
        if not record:
            raise ResourceNotFoundException(f"Analysis record with ID '{analysis_id}' was not found")
        return record

    def delete_analysis(self, analysis_id: str, db: Session) -> bool:
        """Delete an analysis record and associated temporary files."""
        record = self.get_analysis_by_id(analysis_id, db)
        db.delete(record)
        db.commit()
        return True


# Singleton instance
analysis_service = AnalysisService()
