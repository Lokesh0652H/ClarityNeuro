"""API router aggregation module."""

from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.analysis import router as analysis_router
from app.api.datasets import router as datasets_router
from app.api.models import router as models_router
from app.api.evaluation import router as evaluation_router
from app.api.explainability import router as explainability_router
from app.api.uncertainty import router as uncertainty_router
from app.api.fairness import router as fairness_router
from app.api.shortcut_audit import router as shortcut_audit_router
from app.api.history import router as history_router
from app.api.experiments import router as experiments_router
from app.api.export import router as export_router

api_router = APIRouter(prefix="/api")

# Register all endpoint routers under /api
api_router.include_router(health_router)
api_router.include_router(analysis_router)
api_router.include_router(datasets_router)
api_router.include_router(models_router)
api_router.include_router(evaluation_router)
api_router.include_router(explainability_router)
api_router.include_router(uncertainty_router)
api_router.include_router(fairness_router)
api_router.include_router(shortcut_audit_router)
api_router.include_router(history_router)
api_router.include_router(experiments_router)
api_router.include_router(export_router)

__all__ = ["api_router"]
