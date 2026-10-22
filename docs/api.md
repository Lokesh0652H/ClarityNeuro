# API Reference

## Base URL

```
http://localhost:8000
```

## Authentication

No authentication required for local development.

---

## Health & Status

### GET /api/health

System health check.

**Response 200:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "dataset_available": true,
  "database_connected": true,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### GET /api/model/status

Model checkpoint availability and metadata.

**Response 200:**
```json
{
  "available": true,
  "architecture": "efficientnet_b0",
  "num_classes": 4,
  "class_mapping": {"0": "glioma", "1": "meningioma", "2": "pituitary", "3": "notumor"},
  "checkpoint_path": "models/efficientnet_b0_brain_tumor.pth",
  "parameter_count": 5288548
}
```

### GET /api/dataset/status

Dataset availability and statistics.

**Response 200:**
```json
{
  "available": true,
  "total_images": 7023,
  "class_distribution": {"glioma": 1621, "meningioma": 1645, "pituitary": 1757, "notumor": 2000},
  "splits": {"training": 5712, "testing": 1311},
  "validation_status": "validated",
  "source": "kaggle/masoudnickparvar/brain-tumor-mri-dataset"
}
```

---

## Analysis

### POST /api/analyze

Upload and classify a brain MRI image.

**Request:** `multipart/form-data`
- `file`: Image file (JPEG, PNG; max 10MB)

**Response 200:**
```json
{
  "analysis_id": "uuid-string",
  "predicted_class": "glioma",
  "confidence": 0.87,
  "probabilities": {"glioma": 0.87, "meningioma": 0.08, "pituitary": 0.03, "notumor": 0.02},
  "entropy": 0.52,
  "normalized_entropy": 0.37,
  "prediction_margin": 0.79,
  "inference_time_ms": 45.2,
  "model_version": "efficientnet_b0_v1"
}
```

**Response 503:** Model not loaded

### POST /api/analyze/batch

Upload multiple MRI images for batch classification.

**Request:** `multipart/form-data`
- `files`: Multiple image files

### POST /api/explain

Generate Grad-CAM++ visualization.

**Request:** `multipart/form-data`
- `file`: Image file
- `target_class` (optional): Class index to explain (default: predicted class)
- `overlay_alpha` (optional): Heatmap overlay opacity (0.0-1.0, default: 0.4)

**Response 200:**
```json
{
  "predicted_class": "glioma",
  "target_class": "glioma",
  "confidence": 0.87,
  "heatmap_overlay": "base64-encoded-png",
  "heatmap_only": "base64-encoded-png",
  "original_image": "base64-encoded-png"
}
```

### POST /api/uncertainty

Calculate uncertainty metrics for an uploaded image.

**Request:** `multipart/form-data`
- `file`: Image file
- `mc_passes` (optional): Number of Monte Carlo dropout passes (default: 30)

**Response 200:**
```json
{
  "predicted_class": "glioma",
  "probabilities": {"glioma": 0.87, "meningioma": 0.08, "pituitary": 0.03, "notumor": 0.02},
  "entropy": 0.52,
  "normalized_entropy": 0.37,
  "prediction_margin": 0.79,
  "mc_dropout": {
    "mean_probabilities": {"glioma": 0.85, "meningioma": 0.09, "pituitary": 0.04, "notumor": 0.02},
    "std_per_class": {"glioma": 0.03, "meningioma": 0.02, "pituitary": 0.01, "notumor": 0.01},
    "predictive_entropy": 0.55,
    "mutual_information": 0.03,
    "n_passes": 30
  }
}
```

---

## Auditing

### POST /api/audits/fairness

Run fairness audit with subgroup metadata.

**Request:** `multipart/form-data`
- `metadata_file`: CSV with image IDs and subgroup columns
- `subgroup_column`: Column name to stratify by

**Response 200 (with metadata):**
```json
{
  "status": "completed",
  "subgroup_column": "age_group",
  "results": [
    {"group": "young", "sample_count": 150, "accuracy": 0.92, "macro_f1": 0.91},
    {"group": "elderly", "sample_count": 45, "accuracy": 0.84, "macro_f1": 0.82, "warning": "small_sample"}
  ],
  "max_performance_gap": 0.08
}
```

**Response 200 (no metadata):**
```json
{
  "status": "unavailable",
  "message": "Fairness audit unavailable — required subgroup metadata has not been provided."
}
```

### POST /api/audits/shortcut

Run shortcut learning audit.

**Request:** `multipart/form-data`
- `file`: Image file to audit

**Response 200:**
```json
{
  "visual_artifacts": {
    "has_bright_borders": false,
    "has_corner_text": false,
    "border_intensity_mean": 12.5,
    "background_uniformity": 0.95
  },
  "perturbation_results": {
    "original_prediction": "glioma",
    "original_confidence": 0.87,
    "border_masked_confidence": 0.85,
    "corner_masked_confidence": 0.86,
    "prediction_changed": false,
    "max_confidence_drop": 0.02
  }
}
```

---

## Data Access

### GET /api/evaluation

Get persisted evaluation metrics.

### GET /api/datasets

List registered datasets.

### GET /api/models

List registered models.

### GET /api/history

List analysis history.

**Query params:** `page` (int), `per_page` (int), `search` (string)

### GET /api/history/{analysis_id}

Get specific analysis record.

### DELETE /api/history/{analysis_id}

Delete specific analysis record.

### GET /api/experiments

List experiments.

### GET /api/experiments/{experiment_id}

Get specific experiment.

---

## Export

### GET /api/export/project

Download complete project source as ZIP.

**Response 200:** `application/zip` file download
