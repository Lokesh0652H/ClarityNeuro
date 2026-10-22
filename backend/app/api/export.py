"""Project export and code archival endpoints."""

import io
import os
import zipfile
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import Response

from app.config import settings

router = APIRouter(prefix="/export", tags=["Export"])

EXCLUDED_DIR_NAMES = {
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    ".git",
    ".github",
    "temp_uploads",
    ".pytest_cache",
    ".mypy_cache",
    "dist",
    "build",
}

EXCLUDED_FILE_EXTENSIONS = {".pyc", ".pyo", ".pyd", ".db-journal"}
EXCLUDED_FILE_NAMES = {".env", "neuroscan.db", "clarityneuro.db", ".DS_Store"}


def should_exclude(rel_path: Path) -> bool:
    """Determine whether a file or directory path should be excluded from project export."""
    parts = rel_path.parts
    # Check directory parts
    for part in parts:
        if part in EXCLUDED_DIR_NAMES or part.endswith(".egg-info"):
            return True

    # Check file name and extension
    file_name = rel_path.name
    if file_name in EXCLUDED_FILE_NAMES or file_name.startswith(".env"):
        return True

    if rel_path.suffix.lower() in EXCLUDED_FILE_EXTENSIONS:
        return True

    return False


@router.get("/project")
def export_project_zip() -> Response:
    """Generate a clean ZIP archive of the entire ClarityNeuro project source tree.

    Excludes virtual environments, cache files, node modules, temporary uploads,
    and sensitive configuration files.
    """
    project_root = settings.PROJECT_ROOT  # C:\Users\Lokush\.gemini\antigravity\scratch\neuroscan-xai
    if not project_root.exists():
        # Fallback to backend parent if project_root doesn't exist
        project_root = settings.BACKEND_DIR.parent

    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(project_root):
            # Prune directory search in-place
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIR_NAMES and not d.endswith(".egg-info")]

            current_dir = Path(root)
            for file in files:
                file_path = current_dir / file
                rel_path = file_path.relative_to(project_root)

                if should_exclude(rel_path):
                    continue

                try:
                    # Skip files larger than 50MB to prevent archive blowout
                    if file_path.stat().st_size > 50 * 1024 * 1024:
                        continue
                    zf.write(file_path, arcname=str(rel_path).replace("\\", "/"))
                except (PermissionError, FileNotFoundError):
                    continue

    buffer.seek(0)
    zip_bytes = buffer.getvalue()

    headers = {
        "Content-Disposition": 'attachment; filename="clarityneuro-source.zip"',
        "Content-Length": str(len(zip_bytes)),
    }
    return Response(content=zip_bytes, media_type="application/zip", headers=headers)
