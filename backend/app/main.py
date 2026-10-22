"""FastAPI application entry point for NeuroScan XAI Backend."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.config import settings
from app.core.exceptions import register_exception_handlers
from app.database.session import init_db
from app.services.model_service import model_service
from app.services.dataset_service import dataset_service

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("neuroscan")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup and shutdown routines."""
    logger.info("Initializing NeuroScan XAI database...")
    try:
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)

    logger.info("Verifying model checkpoint readiness...")
    model_loaded = model_service.load_model()
    if model_loaded:
        logger.info("EfficientNet-B0 model weights loaded successfully.")
    else:
        logger.warning(
            f"Model weights not loaded on startup: {model_service.load_error}. "
            "Inference requests will return 503 until a valid checkpoint is placed at "
            f"'{settings.resolved_model_path}'."
        )

    # Initial scan of dataset directory
    ds_status = dataset_service.get_status()
    if ds_status["available"]:
        logger.info(f"Detected {ds_status['total_images']} MRI images in dataset.")
    else:
        logger.info(f"Dataset status: {ds_status.get('error') or 'Unavailable'}")

    yield

    logger.info("Shutting down NeuroScan XAI Backend...")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=(
            "Production-grade Explainable AI (XAI) & Uncertainty-Aware Brain Tumor "
            "MRI Classification API using PyTorch and EfficientNet-B0."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register custom exception handlers
    register_exception_handlers(app)

    # Register API routers
    app.include_router(api_router)

    @app.get("/", tags=["Root"])
    def root():
        """Root endpoint returning API identification and documentation links."""
        return {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "docs_url": "/docs",
            "health_url": "/api/health",
            "status": "online",
        }

    return app


app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
