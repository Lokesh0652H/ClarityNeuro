"""Inference and scan analysis endpoints."""

from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.core.exceptions import ResourceNotFoundException
from app.database.session import get_db
from app.schemas.analysis import AnalysisResponse, BatchAnalysisResponse
from app.services.analysis_service import analysis_service

router = APIRouter(prefix="", tags=["Analysis"])


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_mri_scan(
    file: UploadFile = File(..., description="Brain MRI scan image (JPEG, PNG, TIFF, WebP)"),
    generate_cam: bool = Query(False, description="Whether to also generate a Grad-CAM heatmap"),
    db: Session = Depends(get_db),
) -> AnalysisResponse:
    """Analyze a single brain MRI scan image.

    Validates file, performs deep learning inference using EfficientNet-B0,
    computes Shannon entropy & prediction margin, and persists record to database.
    """
    return await analysis_service.analyze_file(file=file, db=db, generate_cam=generate_cam)


@router.post("/analyze/batch", response_model=BatchAnalysisResponse)
async def analyze_mri_batch(
    files: List[UploadFile] = File(..., description="Multiple brain MRI scan images"),
    generate_cam: bool = Query(False, description="Whether to generate Grad-CAM for each image"),
    db: Session = Depends(get_db),
) -> BatchAnalysisResponse:
    """Batch analyze multiple MRI scans sequentially and return aggregated results."""
    return await analysis_service.analyze_batch(files=files, db=db, generate_cam=generate_cam)


@router.get("/analysis/gradcam/{image_filename}")
async def get_gradcam_image(image_filename: str):
    """Retrieve a previously generated Grad-CAM saliency map image."""
    file_path = settings.resolved_upload_dir / image_filename
    if not file_path.exists() or not file_path.is_file():
        raise ResourceNotFoundException(f"Grad-CAM image '{image_filename}' not found")
    return FileResponse(path=str(file_path), media_type="image/jpeg")
