"""
Image Preprocessing and Validation Pipeline for Brain Tumor MRI.

NeuroScan XAI - Explainable Brain Tumor MRI Classification Pipeline.
"""

from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Optional, Tuple, Union

import numpy as np
import torch
from PIL import Image, ImageOps
from torchvision import transforms

try:
    from app.ml.model import IMAGENET_MEAN, IMAGENET_STD
except ImportError:
    from backend.app.ml.model import IMAGENET_MEAN, IMAGENET_STD

logger = logging.getLogger(__name__)

# Standard MRI evaluation input size
DEFAULT_IMAGE_SIZE = 224


def load_image(image_input: Union[str, Path, bytes, io.BytesIO, Image.Image, np.ndarray]) -> Image.Image:
    """
    Load and convert any supported image input into a verified PIL RGB Image.

    Supports:
        - File system path (str or Path)
        - Raw image bytes or BytesIO stream
        - Existing PIL Image instance
        - Numpy array (H, W), (H, W, 1), (H, W, 3), (H, W, 4)

    Args:
        image_input: Input image in one of the accepted formats.

    Returns:
        Verified PIL Image in RGB format.

    Raises:
        FileNotFoundError: If a provided file path does not exist.
        ValueError: If image input is invalid, corrupted, or unsupported.
    """
    if isinstance(image_input, (str, Path)):
        file_path = Path(image_input)
        if not file_path.is_file():
            raise FileNotFoundError(f"Image file does not exist: {file_path}")
        try:
            with Image.open(file_path) as img:
                img.verify()
            # Re-open after verify() since verify() alters file pointer
            pil_img = Image.open(file_path)
            pil_img.load()
        except Exception as exc:
            raise ValueError(f"Failed to open/verify image at {file_path}: {exc}") from exc

    elif isinstance(image_input, bytes):
        try:
            byte_stream = io.BytesIO(image_input)
            with Image.open(byte_stream) as img:
                img.verify()
            byte_stream.seek(0)
            pil_img = Image.open(byte_stream)
            pil_img.load()
        except Exception as exc:
            raise ValueError(f"Failed to decode image from bytes: {exc}") from exc

    elif isinstance(image_input, io.BytesIO):
        try:
            image_input.seek(0)
            with Image.open(image_input) as img:
                img.verify()
            image_input.seek(0)
            pil_img = Image.open(image_input)
            pil_img.load()
        except Exception as exc:
            raise ValueError(f"Failed to decode image from BytesIO: {exc}") from exc

    elif isinstance(image_input, Image.Image):
        # Create a copy so original object is not modified in-place
        pil_img = image_input.copy()

    elif isinstance(image_input, np.ndarray):
        arr = image_input
        # Validate shape and data type
        if arr.ndim == 2:
            # Grayscale (H, W)
            arr = arr.astype(np.uint8) if arr.dtype != np.uint8 else arr
            pil_img = Image.fromarray(arr, mode="L")
        elif arr.ndim == 3:
            if arr.shape[2] == 1:
                arr = arr.squeeze(2).astype(np.uint8)
                pil_img = Image.fromarray(arr, mode="L")
            elif arr.shape[2] == 3:
                arr = arr.astype(np.uint8) if arr.dtype != np.uint8 else arr
                pil_img = Image.fromarray(arr, mode="RGB")
            elif arr.shape[2] == 4:
                arr = arr.astype(np.uint8) if arr.dtype != np.uint8 else arr
                pil_img = Image.fromarray(arr, mode="RGBA")
            else:
                raise ValueError(f"Unsupported channel dimension: {arr.shape[2]}")
        else:
            raise ValueError(f"Unsupported numpy array dimensions: {arr.ndim}")
    else:
        raise TypeError(f"Unsupported image input type: {type(image_input)}")

    # Standardize image orientation via EXIF if present
    try:
        pil_img = ImageOps.exif_transpose(pil_img)
    except Exception:
        pass

    # Ensure RGB color representation
    if pil_img.mode == "RGBA":
        # Alpha compositing onto clean black background (standard medical MRI background)
        background = Image.new("RGB", pil_img.size, (0, 0, 0))
        background.paste(pil_img, mask=pil_img.split()[3])
        pil_img = background
    elif pil_img.mode != "RGB":
        pil_img = pil_img.convert("RGB")

    # Validate that image has positive dimensions
    width, height = pil_img.size
    if width <= 0 or height <= 0:
        raise ValueError(f"Invalid image dimensions: {width}x{height}")

    return pil_img


def preprocess_image(
    image_input: Union[str, Path, bytes, io.BytesIO, Image.Image, np.ndarray],
    target_size: int = DEFAULT_IMAGE_SIZE,
    add_batch_dim: bool = True,
    device: Optional[Union[str, torch.device]] = None,
) -> torch.Tensor:
    """
    Validate, normalize, and preprocess an MRI image into a PyTorch tensor ready for inference.

    Handles:
        - Format validation and corruption detection
        - Grayscale / Single-channel -> RGB conversion
        - RGBA -> RGB compositing
        - Deterministic resizing and center-cropping
        - ImageNet mean/standard deviation normalization
        - Device transfer and batch dimension addition

    Args:
        image_input: Path, bytes, PIL Image, or numpy array.
        target_size: Target square resolution (default: 224).
        add_batch_dim: Whether to prepend batch dimension (shape: 1, 3, H, W).
        device: PyTorch device to move tensor to (optional).

    Returns:
        torch.Tensor of shape (1, 3, target_size, target_size) if add_batch_dim else (3, target_size, target_size).
    """
    pil_image = load_image(image_input)

    transform_pipeline = transforms.Compose(
        [
            transforms.Resize(256),
            transforms.CenterCrop(target_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ]
    )

    tensor = transform_pipeline(pil_image)

    if add_batch_dim:
        tensor = tensor.unsqueeze(0)

    if device is not None:
        if isinstance(device, str):
            device = torch.device(device)
        tensor = tensor.to(device)

    return tensor


def denormalize_tensor(tensor: torch.Tensor) -> np.ndarray:
    """
    Reverse ImageNet normalization on a (C, H, W) or (1, C, H, W) tensor
    and convert to uint8 numpy array with values in [0, 255] and shape (H, W, C).

    Args:
        tensor: Normalized PyTorch tensor.

    Returns:
        Numpy array (H, W, 3) in RGB order with values in [0, 255].
    """
    if tensor.ndim == 4:
        tensor = tensor.squeeze(0)

    t = tensor.detach().cpu().clone()
    mean = torch.tensor(IMAGENET_MEAN, dtype=t.dtype).view(3, 1, 1)
    std = torch.tensor(IMAGENET_STD, dtype=t.dtype).view(3, 1, 1)

    t = t * std + mean
    t = torch.clamp(t, 0.0, 1.0)
    arr = (t.permute(1, 2, 0).numpy() * 255.0).astype(np.uint8)
    return arr


def tensor_to_pil(tensor: torch.Tensor) -> Image.Image:
    """
    Convert a normalized or unnormalized image tensor into a PIL Image.
    """
    arr = denormalize_tensor(tensor)
    return Image.fromarray(arr, mode="RGB")
