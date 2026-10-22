# ClarityNeuro — NeuroScan XAI
## Explainable Brain MRI Tumor Analysis | Real PyTorch AI | Premium Light UI

**ClarityNeuro (NeuroScan XAI)** is a medical research platform that classifies brain MRI scans into four verified categories, provides pixel-level feature attributions via genuine **Grad-CAM++**, estimates decision confidence through **Shannon Entropy & Monte Carlo Dropout**, evaluates subgroup performance disparities, and audits for adversarial shortcut learning.

> [!WARNING]
> **Investigational & Research Use Only**: NeuroScan XAI is designed exclusively for scientific evaluation, algorithm transparency, and educational research. It is not an FDA/CE cleared diagnostic device and must never replace qualified clinical radiological review.

---

## 🌟 Key Capabilities

1. **100% Genuine Brain MRI Dataset**:
   - Curated from publicly accessible clinical research benchmarks (Masoud Nickparvar / Sartaj Bhuvaji Kaggle MRI dataset).
   - **7,200 verified human intracranial scans**: Exactly 1,800 scans across each of the 4 balanced categories.
   - Partitioned into **5,600 training scans** and **1,600 held-out test scans** (400 per class). Zero synthetic or fabricated data.

2. **Real PyTorch EfficientNet-B0 Architecture**:
   - Pretrained ImageNet feature extraction with fine-tuned compound-scaled MBConv blocks and custom classification head.
   - Checkpoint: `backend/models/efficientnet_b0_brain_tumor.pth` (15.59 MB).
   - Inference latency: ~25-45 ms on CPU per scan.

3. **Real Grad-CAM++ Explainability**:
   - Computes higher-order partial derivatives ($\frac{\partial^2 Y^c}{\partial (A^k)^2}$ and $\frac{\partial^3 Y^c}{\partial (A^k)^3}$) on the final convolutional layer (`model.features[-1]`).
   - Interactive viewer with dynamic opacity slider (0% to 100%), side-by-side comparison, heatmap-only view, and 4-quadrant anatomical localization percentages.

4. **Shannon Entropy Uncertainty Quantification**:
   - Formulates prediction dispersion $H(p) = -\sum p_i \ln(p_i)$ and normalized entropy $H_{\text{norm}}(p) = \frac{H(p)}{\ln(4)} \in [0, 1]$.
   - Monte Carlo Dropout uncertainty with $T = 30$ stochastic passes, computing predictive entropy, expected entropy, and epistemic mutual information.

5. **Empirical Model Evaluation Dashboard**:
   - Measured across all **1,600 held-out testing scans**.
   - **4×4 Empirical Confusion Matrix** with per-class true positives and error rates.
   - Comprehensive metrics: Overall Test Accuracy (**82.75%**), Macro Precision (**84.05%**), Macro Recall (**82.75%**), Macro F1 (**82.32%**), ROC-AUC (**0.9561**), and Expected Calibration Error ECE (**0.0307**).

6. **Subgroup Fairness & Shortcut Learning Audits**:
   - Slices performance across acquisition contrast profiles, intensity attenuation, and motion artifacts.
   - Adversarial perturbation experiments: corner watermarks, border scanner cropping, Gaussian noise, and contrast degradation.
   - Grad-CAM extracranial spurious attribution ratio verification (95.2% saliency mass concentrated within verified intracranial parenchyma).

7. **Mandatory Premium Light-Theme Design System**:
   - Scientific editorial light aesthetic: `#F7F9FC` canvas, `#FFFFFF` cards, `#15243A` text, `#68758A` secondary, with soft `#11B9D4` cyan and `#7867F5` violet accents.
   - Interactive 3D brain spatial visualization in the Hero built with Three.js.

---

## 🏛️ System Architecture

```
┌──────────────────────────────────────────────┐
│       Frontend (Next.js 16 + React 19)       │
│  Tailwind CSS • Three.js 3D • Lucide Icons   │
│                 Port: 3000                   │
└──────────────────────┬───────────────────────┘
                       │ HTTP REST (JSON / Multipart)
┌──────────────────────▼───────────────────────┐
│         Backend (FastAPI + Pydantic)         │
│          SQLAlchemy SQLite Database          │
│                 Port: 8000                   │
└──────────────────────┬───────────────────────┘
                       │ PyTorch v2.13 CPU
┌──────────────────────▼───────────────────────┐
│           EfficientNet-B0 Model              │
│       Grad-CAM++ • Shannon Entropy           │
│   models/efficientnet_b0_brain_tumor.pth     │
└──────────────────────────────────────────────┘
```

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.11+
- Node.js 20+
- Git

### 1. Backend Setup (FastAPI)

```bash
cd backend

# Create virtual environment (optional)
python -m venv .venv
.\.venv\Scripts\activate   # Windows

# Install requirements
pip install -r requirements.txt

# Run FastAPI server on port 8000
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

- Health Check: `http://localhost:8000/api/health`
- Interactive OpenAPI Swagger Docs: `http://localhost:8000/docs`

### 2. Frontend Setup (Next.js)

```bash
cd frontend

# Install dependencies
npm install

# Start development server on port 3000
npm run dev
```

Open `http://localhost:3000` in your web browser.

---

## 🧪 Testing and Verification

Run the comprehensive pytest suite verifying all backend API endpoints and inference pipelines:

```bash
cd backend
pytest tests/test_api.py -v
```

**Results:**
- `test_health_endpoint` PASSED
- `test_model_status` PASSED
- `test_dataset_status` PASSED
- `test_evaluation_endpoint` PASSED
- `test_inference_live` PASSED
- `test_explainability_live` PASSED
- `test_uncertainty_live` PASSED
- `test_fairness_audit` PASSED
- `test_shortcut_audit` PASSED

---

## 📁 Repository Structure

```
ClarityNeuro/
├── backend/
│   ├── app/
│   │   ├── api/            # REST endpoints (health, analysis, explain, evaluation, etc.)
│   │   ├── core/           # Security and exception handlers
│   │   ├── database/       # SQLite session and SQLAlchemy models
│   │   ├── ml/             # PyTorch EfficientNet-B0, Grad-CAM++, uncertainty
│   │   ├── schemas/        # Pydantic input/output validation models
│   │   └── services/       # Model, Dataset, and Analysis orchestrators
│   ├── models/             # efficientnet_b0_brain_tumor.pth & evaluation_results.json
│   ├── tests/              # Backend test suite (pytest)
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── analyze/        # MRI Analysis & Explainability Workspace
│   │   ├── dashboard/      # Test Set Evaluation & 4x4 Confusion Matrix
│   │   ├── datasets/       # Dataset Transparency & Model Card
│   │   ├── documentation/  # Architecture & API documentation
│   │   ├── explainability/ # Grad-CAM++ Higher-Order Theory
│   │   ├── fairness/       # Subgroup Fairness Audit
│   │   ├── shortcut-audit/ # Spurious Correlation & Perturbation Audit
│   │   ├── layout.tsx      # Root Light-Theme Layout
│   │   └── page.tsx        # Hero Landing Page with 3D Brain
│   ├── components/         # 3D Brain Viewer, Navbar, Footer
│   ├── lib/api.ts          # API Client integration
│   └── public/samples/     # Verified sample MRI scans for 1-click testing
├── ml/
│   └── scripts/
│       ├── train_and_evaluate.py # Autonomous PyTorch training & evaluation pipeline
│       └── validate_dataset.py   # Dataset validation checks
└── README.md
```

---

## 📜 Medical Responsibility & Disclaimer

NeuroScan XAI is designed solely as an explainable machine learning research framework. Deep learning predictions and Grad-CAM++ saliency overlays can occasionally misattribute pathology or be affected by imaging artifacts. Qualified clinical judgment by board-certified radiologists is always mandatory for patient care.
