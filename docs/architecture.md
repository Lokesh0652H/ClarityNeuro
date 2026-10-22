# NeuroScan XAI — Architecture

## System Overview

NeuroScan XAI is a full-stack research platform with three primary subsystems:

1. **Frontend Application** — Next.js with React Three Fiber for 3D visualization
2. **Backend API** — FastAPI serving ML inference, explainability, and auditing
3. **ML Pipeline** — PyTorch-based training, evaluation, and model management

## Component Diagram

```
┌──────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                     │
│                                                          │
│  ┌─────────┐  ┌──────────┐  ┌───────────┐  ┌─────────┐ │
│  │ 3D Hero  │  │ Analysis │  │ Dashboard │  │ Audits  │ │
│  │ Brain    │  │ Workspace│  │ & Charts  │  │ Pages   │ │
│  └─────────┘  └──────────┘  └───────────┘  └─────────┘ │
│                      │                                   │
│              ┌───────┴───────┐                          │
│              │  API Client   │ (lib/api.ts)             │
│              └───────────────┘                          │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP/REST (JSON)
                       ▼
┌──────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                       │
│                                                          │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌────────┐ │
│  │ API      │  │ Services  │  │ ML Engine│  │ Audits │ │
│  │ Routes   │──│ Layer     │──│ Inference│  │ Module │ │
│  └──────────┘  └───────────┘  │ GradCAM++│  └────────┘ │
│                               │ Uncertnt │              │
│  ┌──────────┐                 └──────────┘              │
│  │ Database │ SQLAlchemy + SQLite                       │
│  │ Models   │ (analysis history, experiments, audits)   │
│  └──────────┘                                           │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                   ML Pipeline                            │
│                                                          │
│  download_dataset.py → validate_dataset.py →            │
│  generate_manifest.py → train.py → evaluate.py          │
│                                                          │
│  Dataset: Brain Tumor MRI (Kaggle)                      │
│  Model: EfficientNet-B0 (4 classes)                     │
└──────────────────────────────────────────────────────────┘
```

## Data Flow: MRI Analysis

1. User uploads MRI image via frontend
2. Frontend sends multipart POST to `/api/analyze`
3. Backend validates image (format, size, content)
4. Image preprocessed: Resize(224) → CenterCrop(224) → Normalize(ImageNet)
5. EfficientNet-B0 forward pass produces logits
6. Softmax converts to 4-class probabilities
7. Entropy and uncertainty metrics calculated
8. Result persisted to SQLite
9. JSON response returned to frontend
10. Frontend displays prediction, probabilities chart, uncertainty gauge

## Data Flow: Grad-CAM++ Explanation

1. Frontend sends image to `/api/explain`
2. Backend registers forward/backward hooks on last conv layer
3. Forward pass captures activations
4. Backward pass captures gradients for target class
5. Grad-CAM++ weighting: α = ReLU(∂²Y/∂A²) / (2·∂²Y/∂A² + Σ(Aij·∂³Y/∂A³) + ε)
6. Weighted combination of activation maps
7. ReLU and upsampling to input resolution
8. Heatmap colorization and overlay generation
9. Base64-encoded images returned in response

## Security Boundaries

- Uploaded images are validated and stored temporarily
- No uploaded content is executed
- Database uses parameterized queries (SQLAlchemy ORM)
- CORS restricted to configured origins
- File size limits enforced
- No external API calls for inference (local model only)
