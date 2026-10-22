"""Explainability (XAI) endpoints: Grad-CAM and Grad-CAM++."""

from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.core.exceptions import InvalidImageException, ResourceNotFoundException
from app.core.security import validate_image_file
from app.database.models import AnalysisRecord
from app.database.session import get_db
from app.schemas.analysis import ExplainabilityResponse
from app.services.model_service import model_service

router = APIRouter(prefix="", tags=["Explainability"])


@router.post("/explain", response_model=ExplainabilityResponse)
async def explain_mri(
    file: Optional[UploadFile] = File(None, description="Brain MRI scan file to explain"),
    analysis_id: Optional[str] = Form(None, description="Existing analysis ID to explain"),
    target_class: Optional[str] = Form(None, description="Optional target class for attribution"),
    method: str = Form("gradcam++", description="XAI method: 'gradcam' or 'gradcam++'"),
    db: Session = Depends(get_db),
) -> ExplainabilityResponse:
    """Generate Grad-CAM or Grad-CAM++ visual explanation heatmap for a brain MRI scan.

    Accepts either an uploaded file or the ID of a previously analyzed image.
    Calculates gradient-weighted feature attributions and quadrant localization percentages.
    """
    image_bytes: bytes

    if file is not None:
        image_bytes, _ = await validate_image_file(file)
    elif analysis_id is not None:
        record = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
        if not record:
            raise ResourceNotFoundException(f"Analysis record '{analysis_id}' not found")

        # Find saved image file in upload dir
        upload_dir = settings.resolved_upload_dir
        matches = list(upload_dir.glob(f"{analysis_id}_*"))
        if not matches:
            raise ResourceNotFoundException(f"Original image file for analysis '{analysis_id}' not found on server")
        with open(matches[0], "rb") as f:
            image_bytes = f.read()
    else:
        raise InvalidImageException("Either 'file' or 'analysis_id' must be provided")

    # Map target_class name to index if specified
    target_idx = None
    if target_class:
        target_clean = target_class.strip().lower()
        if target_clean in settings.MODEL_CLASSES:
            target_idx = settings.MODEL_CLASSES.index(target_clean)

    # Compute Grad-CAM
    cam_result = model_service.generate_gradcam(
        image_input=image_bytes,
        target_class_idx=target_idx,
        method=method,
    )

    # Update database record if analysis_id was supplied
    if analysis_id:
        record = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
        if record:
            record.gradcam_path = cam_result["heatmap_url"]
            db.commit()

    return ExplainabilityResponse(
        analysis_id=analysis_id,
        target_class=cam_result["target_class"],
        target_class_idx=cam_result["target_class_idx"],
        confidence=cam_result["confidence"],
        method=cam_result["method"],
        heatmap_path=cam_result["heatmap_path"],
        heatmap_url=cam_result["heatmap_url"],
        heatmap_base64=cam_result["heatmap_base64"],
        salient_regions_summary=cam_result["salient_regions_summary"],
    )
