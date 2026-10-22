"""File upload validation and path security sanitization."""

import io
import os
import re
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile
from PIL import Image
from app.core.exceptions import InvalidImageException, FileTooLargeException
from app.config import settings

ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/tiff",
    "image/bmp",
}

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp"}


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal and special character attacks."""
    if not filename:
        return "unnamed_scan.png"
    # Extract only the base name (strip any path components)
    clean_name = os.path.basename(filename)
    # Remove directory separators and null bytes
    clean_name = clean_name.replace("/", "").replace("\\", "").replace("\0", "")
    # Allow alphanumeric, dots, underscores, dashes
    clean_name = re.sub(r"[^a-zA-Z0-9._-]", "_", clean_name)
    # Ensure there is an extension
    ext = Path(clean_name).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        clean_name = f"{clean_name}.png"
    return clean_name


async def check_file_size(file: UploadFile, max_size: int = settings.MAX_UPLOAD_SIZE) -> int:
    """Verify that file size does not exceed the allowed threshold.

    Reads chunk-by-chunk to avoid allocating memory for huge files.
    Restores file cursor position afterwards.
    """
    total_size = 0
    chunk_size = 1024 * 64  # 64 KB

    await file.seek(0)
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        total_size += len(chunk)
        if total_size > max_size:
            await file.seek(0)
            raise FileTooLargeException(
                f"File '{file.filename}' exceeds maximum allowed size of {max_size / (1024 * 1024):.1f} MB"
            )

    await file.seek(0)
    return total_size


async def validate_image_file(file: UploadFile) -> Tuple[bytes, Tuple[int, int]]:
    """Validate uploaded file MIME type, magic bytes, and readable image data using Pillow.

    Returns:
        Tuple of (raw_bytes, (width, height))
    """
    if not file.filename:
        raise InvalidImageException("Filename is missing from upload")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise InvalidImageException(
            f"Unsupported file extension '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # Check file size
    await check_file_size(file)

    # Read image contents
    await file.seek(0)
    content = await file.read()
    await file.seek(0)

    if not content:
        raise InvalidImageException("Uploaded file is empty (0 bytes)")

    try:
        # Use Pillow to verify that image stream is genuine and decode dimensions
        with Image.open(io.BytesIO(content)) as img:
            img.verify()

        # Re-open after verify() to fetch format and dimensions
        with Image.open(io.BytesIO(content)) as img:
            dimensions = (img.width, img.height)
            if img.width < 16 or img.height < 16:
                raise InvalidImageException(f"Image dimensions ({img.width}x{img.height}) are too small for MRI processing")
            return content, dimensions
    except Exception as e:
        if isinstance(e, InvalidImageException):
            raise
        raise InvalidImageException(f"Invalid or corrupted image data: {str(e)}")
