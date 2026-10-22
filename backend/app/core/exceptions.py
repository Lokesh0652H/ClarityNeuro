"""Custom exception classes and FastAPI exception handlers."""

import logging
from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class ClarityNeuroException(Exception):
    """Base exception for all ClarityNeuro custom exceptions."""
    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR, detail: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}

NeuroScanException = ClarityNeuroException


class ModelNotAvailableException(NeuroScanException):
    """Raised when the ML model checkpoint is not loaded or unavailable."""
    def __init__(self, message: str = "ML model is not available or checkpoint not found"):
        super().__init__(message=message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


class DatasetNotFoundException(NeuroScanException):
    """Raised when a requested dataset directory or split cannot be found."""
    def __init__(self, message: str = "Dataset or split directory could not be found"):
        super().__init__(message=message, status_code=status.HTTP_404_NOT_FOUND)


class ResourceNotFoundException(NeuroScanException):
    """Raised when an entity by ID does not exist."""
    def __init__(self, message: str = "Requested resource not found"):
        super().__init__(message=message, status_code=status.HTTP_404_NOT_FOUND)


class InvalidImageException(NeuroScanException):
    """Raised when an uploaded file is not a valid or decipherable image."""
    def __init__(self, message: str = "Uploaded file is not a valid image"):
        super().__init__(message=message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class FileTooLargeException(NeuroScanException):
    """Raised when an uploaded file exceeds the configured size limit."""
    def __init__(self, message: str = "File size exceeds the allowed threshold"):
        super().__init__(message=message, status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)


class InferenceException(NeuroScanException):
    """Raised when inference, Grad-CAM, or uncertainty estimation fails."""
    def __init__(self, message: str = "Inference error occurred during processing", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers on the FastAPI application."""

    @app.exception_handler(NeuroScanException)
    async def neuroscan_exception_handler(request: Request, exc: NeuroScanException):
        logger.warning(f"NeuroScanException on {request.url.path}: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.__class__.__name__,
                "message": exc.message,
                "detail": exc.detail,
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled exception on {request.url.path}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "InternalServerError",
                "message": "An unexpected server error occurred.",
                "detail": str(exc),
            },
        )
