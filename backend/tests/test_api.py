"""
Comprehensive Test Suite for ClarityNeuro Backend.
Tests Health, Inference, Grad-CAM++, Uncertainty, Evaluation, and Audits.
"""

import io
import pytest
from fastapi.testclient import TestClient
from PIL import Image

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app
from app.services.model_service import model_service
from app.services.dataset_service import dataset_service
from app.database.session import init_db

# Initialize database tables for testing
init_db()

client = TestClient(app)

def create_synthetic_test_mri() -> bytes:
    """Create a dummy 224x224 RGB image buffer for API pipeline testing."""
    img = Image.new("RGB", (224, 224), color=(30, 30, 30))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

def test_health_endpoint():
    """Verify health endpoint reports correct operational status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert data["dataset_available"] is True
    assert data["database_connected"] is True

def test_model_status():
    """Verify model status endpoint identifies EfficientNet-B0 and 4 classes."""
    response = client.get("/api/model/status")
    assert response.status_code == 200
    data = response.json()
    assert data["available"] is True
    assert data["architecture"] == "EfficientNet-B0"
    assert data["num_classes"] == 4
    assert "glioma" in data["classes"]
    assert "notumor" in data["classes"]

def test_dataset_status():
    """Verify dataset status endpoint scans and finds real images."""
    response = client.get("/api/dataset/status")
    assert response.status_code == 200
    data = response.json()
    assert data["available"] is True
    assert data["total_images"] == 7200
    assert data["splits"]["training"] == 5600
    assert data["splits"]["testing"] == 1600

def test_evaluation_endpoint():
    """Verify evaluation endpoint returns real empirical metrics and 4x4 matrix."""
    response = client.get("/api/evaluation")
    assert response.status_code == 200
    data = response.json()
    assert data["test_samples"] == 1600
    assert len(data["confusion_matrix"]) == 4
    assert len(data["class_labels"]) == 4
    assert "glioma" in data["class_metrics"]
    assert data["accuracy"] > 0.80

def test_inference_live():
    """Verify /api/analyze endpoint with an uploaded image."""
    img_bytes = create_synthetic_test_mri()
    files = {"file": ("test_scan.jpg", img_bytes, "image/jpeg")}
    response = client.post("/api/analyze?generate_cam=true", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "analysis_id" in data
    assert data["predicted_class"] in ["glioma", "meningioma", "pituitary", "notumor"]
    assert 0.0 <= data["confidence"] <= 1.0
    assert "entropy" in data
    assert "normalized_entropy" in data

def test_explainability_live():
    """Verify /api/explain endpoint generates Grad-CAM++."""
    img_bytes = create_synthetic_test_mri()
    files = {"file": ("test_scan.jpg", img_bytes, "image/jpeg")}
    data_payload = {"method": "gradcam++"}
    response = client.post("/api/explain", files=files, data=data_payload)
    assert response.status_code == 200
    data = response.json()
    assert "heatmap_base64" in data
    assert "salient_regions_summary" in data
    assert "top_right" in data["salient_regions_summary"]

def test_uncertainty_live():
    """Verify /api/uncertainty endpoint calculates MC Dropout."""
    img_bytes = create_synthetic_test_mri()
    files = {"file": ("test_scan.jpg", img_bytes, "image/jpeg")}
    data_payload = {"passes": 5}
    response = client.post("/api/uncertainty", files=files, data=data_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["passes"] == 5
    assert "predictive_entropy" in data
    assert "mutual_information" in data

def test_fairness_audit():
    """Verify fairness audit endpoint returns valid metrics."""
    response = client.post("/api/audits/fairness", json={"model_id": "efficientnet-b0-v1"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert "disparate_impact_ratio" in data
    assert len(data["slices"]) > 0

def test_shortcut_audit():
    """Verify shortcut audit endpoint returns perturbation results."""
    response = client.post("/api/audits/shortcut", json={"model_id": "efficientnet-b0-v1"})
    assert response.status_code == 200
    data = response.json()
    assert "overall_shortcut_risk" in data
    assert len(data["perturbation_results"]) > 0
