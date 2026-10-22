# NeuroScan XAI

## Explainable Brain MRI Classification & Model Trust Auditing

NeuroScan XAI is a full-stack AI research platform that classifies brain MRI images into four categories, explains model predictions using Grad-CAM++, measures prediction uncertainty, investigates fairness across subgroups, and audits for shortcut learning — all through an immersive 3D web interface.

> **⚠️ Research & Education Only**: This platform is NOT a clinically validated diagnostic system. Model outputs should never be used as definitive medical diagnoses or to make treatment decisions.

---

## Features

- **Brain MRI Classification**: EfficientNet-B0 classifying Glioma, Meningioma, Pituitary Tumor, and No Tumor
- **Grad-CAM++ Explainability**: Real gradient-based attribution maps showing which image regions influenced predictions
- **Uncertainty Quantification**: Predictive entropy, normalized entropy, prediction margin, and Monte Carlo dropout
- **Fairness Auditing**: Subgroup-level performance evaluation when metadata is available
- **Shortcut Learning Detection**: Visual artifact inspection and perturbation experiments
- **Immersive 3D Interface**: Interactive brain visualization with scroll-driven storytelling
- **Persistent History**: SQLite-backed analysis records with search, export, and deletion
- **Project Export**: Download the complete source code as a ZIP archive

## Architecture

```
┌─────────────────┐     HTTP/REST      ┌──────────────────┐
│   Next.js App   │ ◄────────────────► │  FastAPI Backend  │
│  React + Three  │                    │  PyTorch + SQLite │
│   Port: 3000    │                    │   Port: 8000      │
└─────────────────┘                    └──────────────────┘
                                              │
                                     ┌────────┴────────┐
                                     │  EfficientNet-B0 │
                                     │  Trained Model   │
                                     └─────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- npm 10+

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

Verify: http://localhost:8000/api/health
API Docs: http://localhost:8000/docs

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open: http://localhost:3000

### Dataset Setup

1. Install Kaggle CLI: `pip install kaggle`
2. Configure credentials: Place `kaggle.json` in `~/.kaggle/`
3. Download dataset:
   ```bash
   python ml/scripts/download_dataset.py
   ```
4. Validate dataset:
   ```bash
   python ml/scripts/validate_dataset.py
   ```

### Model Training

```bash
python ml/scripts/train.py --data-dir ml/data/raw --output-dir backend/models --epochs 20
```

### Evaluation

```bash
python ml/scripts/evaluate.py --checkpoint backend/models/efficientnet_b0_brain_tumor.pth --data-dir ml/data/raw/Testing
```

## Technology Stack

### Frontend
- Next.js 14 (App Router)
- React 18 + TypeScript
- Tailwind CSS
- React Three Fiber + Three.js + Drei
- GSAP + ScrollTrigger
- Framer Motion
- Recharts
- Lucide Icons
- Zod

### Backend
- Python 3.11
- FastAPI + Uvicorn
- PyTorch + timm (EfficientNet-B0)
- SQLAlchemy + SQLite
- Pydantic v2
- scikit-learn
- OpenCV + Pillow

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | System health check |
| GET | `/api/model/status` | Model checkpoint availability |
| GET | `/api/dataset/status` | Dataset availability and stats |
| POST | `/api/analyze` | Upload and classify an MRI image |
| POST | `/api/explain` | Generate Grad-CAM++ visualization |
| POST | `/api/uncertainty` | Calculate uncertainty metrics |
| POST | `/api/audits/fairness` | Run fairness audit |
| POST | `/api/audits/shortcut` | Run shortcut learning audit |
| GET | `/api/evaluation` | Get model evaluation metrics |
| GET | `/api/history` | List analysis history |
| GET | `/api/export/project` | Download project source ZIP |

## Project Structure

```
neuroscan-xai/
├── frontend/          # Next.js application
├── backend/           # FastAPI application  
│   ├── app/
│   │   ├── api/       # Route handlers
│   │   ├── ml/        # Model, inference, Grad-CAM++
│   │   ├── audits/    # Fairness & shortcut auditing
│   │   ├── database/  # SQLAlchemy models & session
│   │   ├── schemas/   # Pydantic response models
│   │   └── services/  # Business logic
│   └── tests/         # pytest test suite
├── ml/                # Training & data pipeline
│   ├── scripts/       # Download, validate, train, evaluate
│   ├── data/          # Dataset storage (gitignored)
│   └── configs/       # Training configurations
├── docs/              # Project documentation
└── docker-compose.yml # Container deployment
```

## Known Limitations

1. **CPU-only inference**: Training and inference on CPU is slow. GPU (CUDA) recommended for training.
2. **Dataset requires Kaggle account**: The brain tumor MRI dataset requires Kaggle authentication to download.
3. **No clinical validation**: Model performance metrics are from a single research dataset and are NOT clinically validated.
4. **Fairness audit requires metadata**: Subgroup fairness analysis requires external CSV metadata with patient demographics. The MRI dataset alone does not include this information.
5. **Shortcut learning heuristics**: Artifact detection and perturbation experiments are screening tools, not definitive proof of shortcut reliance.

## License

This project is for educational and research purposes. The brain tumor MRI dataset has its own license terms — see [docs/dataset.md](docs/dataset.md).

## Documentation

- [Architecture](docs/architecture.md)
- [Dataset](docs/dataset.md)
- [Model Card](docs/model_card.md)
- [API Reference](docs/api.md)
- [Explainability](docs/explainability.md)
- [Fairness](docs/fairness.md)
- [Shortcut Audit](docs/shortcut_audit.md)
- [Privacy](docs/privacy.md)
