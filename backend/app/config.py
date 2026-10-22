"""Application configuration settings for ClarityNeuro Backend.

Uses Pydantic BaseSettings to read environment variables with type safety
and sensible defaults.
"""

from pathlib import Path
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """ClarityNeuro Backend application settings."""

    # Core Settings
    PROJECT_NAME: str = "ClarityNeuro Backend"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_STR: str = "/api"

    # Database
    DATABASE_URL: str = "sqlite:///./clarityneuro.db"

    # Model and Inference Settings
    MODEL_PATH: str = "models/efficientnet_b0_brain_tumor.pth"
    MODEL_CLASSES: List[str] = ["glioma", "meningioma", "pituitary", "notumor"]
    MC_DROPOUT_PASSES: int = 30
    MODEL_DEVICE: str = "cpu"  # 'cpu', 'cuda', or 'mps'

    # Dataset Settings
    DATASET_PATH: str = "../ml/data/raw"

    # Storage and Uploads
    UPLOAD_DIR: str = "temp_uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB in bytes

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # Project Directories
    BACKEND_DIR: Path = Path(__file__).resolve().parent.parent
    PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent.parent

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v  # type: ignore
        raise ValueError(v)

    @field_validator("MODEL_CLASSES", mode="before")
    @classmethod
    def assemble_model_classes(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v  # type: ignore
        raise ValueError(v)

    @property
    def resolved_model_path(self) -> Path:
        """Resolve model path relative to backend dir or absolute."""
        p = Path(self.MODEL_PATH)
        if p.is_absolute():
            return p
        # Check relative to backend dir first
        backend_rel = self.BACKEND_DIR / p
        if backend_rel.exists():
            return backend_rel
        # Check relative to project root
        project_rel = self.PROJECT_ROOT / p
        if project_rel.exists():
            return project_rel
        return backend_rel

    @property
    def resolved_dataset_path(self) -> Path:
        """Resolve dataset path relative to backend dir or absolute."""
        p = Path(self.DATASET_PATH)
        if p.is_absolute():
            return p
        backend_rel = (self.BACKEND_DIR / p).resolve()
        if backend_rel.exists():
            return backend_rel
        project_rel = (self.PROJECT_ROOT / p).resolve()
        if project_rel.exists():
            return project_rel
        return backend_rel

    @property
    def resolved_upload_dir(self) -> Path:
        """Resolve and ensure upload directory exists."""
        p = Path(self.UPLOAD_DIR)
        if not p.is_absolute():
            p = self.BACKEND_DIR / p
        p.mkdir(parents=True, exist_ok=True)
        return p


settings = Settings()
