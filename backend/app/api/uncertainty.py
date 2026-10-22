"""Uncertainty quantification endpoints: Shannon entropy and Monte Carlo Dropout."""

from typing import Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.core.exceptions import InvalidImageException, ResourceNotFoundException
from app.core.security import validate_image_file
from app.database.models import AnalysisRecord
from app.database.session import get_db
from app.schemas.analysis import UncertaintyPassResult
from app.services.model_service import model_service

router = APIRouter(prefix="", tags=["Uncertainty"])


@router.post("/uncertainty", response_model=UncertaintyPassResult)
async def quantify_uncertainty(
    file: Optional[UploadFile] = File(None, description="Brain MRI scan to evaluate"),
    analysis_id: Optional[str] = Form(None, description="Existing analysis ID"),
    passes: int = Form(30, ge=2, le=100, description="Number of Monte Carlo stochastic passes"),
    db: Session = Depends(get_db),
) -> UncertaintyPassResult:
    """Compute epistemic and aleatoric uncertainty via Monte Carlo Dropout.

    Executes T stochastic forward passes with active Dropout to estimate
    predictive entropy, expected entropy, mutual information, and 95% confidence intervals.
    """
    image_bytes: bytes

    if file is not None:
        image_bytes, _ = await validate_image_file(file)
    elif analysis_id is not None:
        record = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
        if not record:
            raise ResourceNotFoundException(f"Analysis record '{analysis_id}' not found")

        upload_dir = settings.resolved_upload_dir
        matches = list(upload_dir.glob(f"{analysis_id}_*"))
        if not matches:
            raise ResourceNotFoundException(f"Original image for analysis '{analysis_id}' not found on server")
        with open(matches[0], "rb") as f:
            image_bytes = f.read()
    else:
        raise InvalidImageException("Either 'file' or 'analysis_id' must be provided")

    result = model_service.mc_dropout_predict(image_bytes, passes=passes)

    return UncertaintyPassResult(
        analysis_id=analysis_id,
        passes=result["passes"],
        mean_probabilities=result["mean_probabilities"],
        variance=result["variance"],
        standard_deviation=result["standard_deviation"],
        confidence_interval=result["confidence_interval"],
        predictive_entropy=result["predictive_entropy"],
        expected_entropy=result["expected_entropy"],
        mutual_information=result["mutual_information"],
    )
