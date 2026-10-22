"""Analysis history management endpoints."""

import math
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundException
from app.database.models import AnalysisRecord
from app.database.session import get_db
from app.schemas.analysis import AnalysisDetail, AnalysisHistoryItem
from app.schemas.common import MessageResponse, PaginatedResponse
from app.services.analysis_service import analysis_service

router = APIRouter(prefix="/history", tags=["History"])


@router.get("", response_model=PaginatedResponse[AnalysisHistoryItem])
def list_history(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    predicted_class: Optional[str] = Query(None, description="Filter by predicted tumor class"),
    db: Session = Depends(get_db),
) -> PaginatedResponse[AnalysisHistoryItem]:
    """Retrieve paginated historical MRI analysis records."""
    query = db.query(AnalysisRecord)

    if predicted_class:
        query = query.filter(AnalysisRecord.predicted_class == predicted_class.strip().lower())

    total = query.count()
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    records = (
        query.order_by(AnalysisRecord.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = [
        AnalysisHistoryItem(
            id=r.id,
            filename=r.filename,
            predicted_class=r.predicted_class,
            confidence=r.confidence,
            entropy=r.entropy,
            normalized_entropy=r.normalized_entropy,
            prediction_margin=r.prediction_margin,
            inference_time_ms=r.inference_time_ms,
            model_version=r.model_version,
            created_at=r.created_at,
            gradcam_path=r.gradcam_path,
        )
        for r in records
    ]

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{analysis_id}", response_model=AnalysisDetail)
def get_history_detail(
    analysis_id: str,
    db: Session = Depends(get_db),
) -> AnalysisDetail:
    """Retrieve full details and probability breakdown for a specific analysis."""
    record = analysis_service.get_analysis_by_id(analysis_id, db)
    return AnalysisDetail(
        id=record.id,
        filename=record.filename,
        predicted_class=record.predicted_class,
        confidence=record.confidence,
        probabilities=record.probabilities,
        entropy=record.entropy,
        normalized_entropy=record.normalized_entropy,
        prediction_margin=record.prediction_margin,
        inference_time_ms=record.inference_time_ms,
        model_version=record.model_version,
        created_at=record.created_at,
        gradcam_path=record.gradcam_path,
    )


@router.delete("/{analysis_id}", response_model=MessageResponse)
def delete_history_item(
    analysis_id: str,
    db: Session = Depends(get_db),
) -> MessageResponse:
    """Delete an analysis record from history."""
    analysis_service.delete_analysis(analysis_id, db)
    return MessageResponse(
        success=True,
        message=f"Analysis record '{analysis_id}' was successfully deleted",
    )
