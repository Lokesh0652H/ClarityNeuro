"""
NeuroScan XAI - Machine Learning Core Pipeline.

Provides complete deep learning classification, explainability, uncertainty
quantification, and validation utilities for Brain Tumor MRI scans.
"""

try:
    from backend.app.ml.evaluation import EvaluationResults, ModelEvaluator
    from backend.app.ml.gradcam_pp import GradCAMPlusPlus
    from backend.app.ml.inference import InferenceEngine
    from backend.app.ml.model import (
        CLASS_NAMES,
        CLASS_TO_IDX,
        IDX_TO_CLASS,
        IMAGENET_MEAN,
        IMAGENET_STD,
        BrainTumorClassifier,
        build_model,
    )
    from backend.app.ml.preprocessing import (
        denormalize_tensor,
        load_image,
        preprocess_image,
        tensor_to_pil,
    )
    from backend.app.ml.uncertainty import UncertaintyEstimator
except ImportError:
    from app.ml.evaluation import EvaluationResults, ModelEvaluator
    from app.ml.gradcam_pp import GradCAMPlusPlus
    from app.ml.inference import InferenceEngine
    from app.ml.model import (
        CLASS_NAMES,
        CLASS_TO_IDX,
        IDX_TO_CLASS,
        IMAGENET_MEAN,
        IMAGENET_STD,
        BrainTumorClassifier,
        build_model,
    )
    from app.ml.preprocessing import (
        denormalize_tensor,
        load_image,
        preprocess_image,
        tensor_to_pil,
    )
    from app.ml.uncertainty import UncertaintyEstimator

__all__ = [
    "BrainTumorClassifier",
    "build_model",
    "CLASS_NAMES",
    "CLASS_TO_IDX",
    "IDX_TO_CLASS",
    "IMAGENET_MEAN",
    "IMAGENET_STD",
    "preprocess_image",
    "load_image",
    "denormalize_tensor",
    "tensor_to_pil",
    "InferenceEngine",
    "GradCAMPlusPlus",
    "UncertaintyEstimator",
    "ModelEvaluator",
    "EvaluationResults",
]
