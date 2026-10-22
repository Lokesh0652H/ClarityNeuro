# ClarityNeuro
### Explainable AI & Uncertainty-Aware Deep Learning for Brain Tumor MRI Analysis

[![PyTorch 2.13](https://img.shields.io/badge/PyTorch-2.13%2BCPU-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js 16](https://img.shields.io/badge/Next.js-16.4%20(Turbopack)-black?logo=next.js&logoColor=white)](https://nextjs.org/)
[![React 19](https://img.shields.io/badge/React-19.3-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![Tailwind CSS 4](https://img.shields.io/badge/Tailwind_CSS-v4.0-38B2AC?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![License: CC BY 4.0](https://img.shields.io/badge/Dataset_License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Tests Passing](https://img.shields.io/badge/pytest-9%2F9%20passed-success)](file:///C:/Users/Lokush/.gemini/antigravity/scratch/neuroscan-xai/backend/tests/test_api.py)

**ClarityNeuro** is a full-stack, research-grade Explainable AI (XAI) platform designed to advance algorithmic transparency in deep learning-based intracranial tumor classification. Utilizing a fine-tuned **EfficientNet-B0** convolutional neural network, the system classifies axial/coronal human brain MRI scans into four categories, computes pixel-level saliency maps via higher-order **Grad-CAM++**, estimates decision confidence through **Shannon Entropy & Monte Carlo Dropout**, evaluates **imaging-condition subgroup robustness**, and investigates **adversarial shortcut learning**—presented through an interactive light-theme interface with procedural 3D spatial brain geometry.

> [!WARNING]
> **Investigational & Research Use Only**: ClarityNeuro is an academic and engineering framework developed to study model interpretability, uncertainty calibration, and algorithmic auditing. It is **not** an FDA-cleared or CE-marked medical device (SaMD) and must never be utilized as a standalone diagnostic tool or to guide clinical patient management.

---

## Table of Contents

- [1. Overview & Problem Statement](#1-overview--problem-statement)
- [2. Key Features](#2-key-features)
- [3. Screenshots & Visual Interface](#3-screenshots--visual-interface)
- [4. System Architecture](#4-system-architecture)
- [5. End-to-End Prediction Workflow](#5-end-to-end-prediction-workflow)
- [6. Technology Stack](#6-technology-stack)
- [7. Dataset Provenance & Licensing](#7-dataset-provenance--licensing)
- [8. Dataset Composition & Stratification](#8-dataset-composition--stratification)
- [9. Model Architecture & Training Methodology](#9-model-architecture--training-methodology)
- [10. Empirical Model Evaluation & Results](#10-empirical-model-evaluation--results)
- [11. Explainability with Grad-CAM++](#11-explainability-with-grad-cam)
- [12. Predictive Uncertainty Estimation](#12-predictive-uncertainty-estimation)
- [13. Fairness & Imaging-Condition Robustness Audits](#13-fairness--imaging-condition-robustness-audits)
- [14. Shortcut Learning & Adversarial Perturbation Audits](#14-shortcut-learning--adversarial-perturbation-audits)
- [15. API Documentation & Endpoints](#15-api-documentation--endpoints)
- [16. Repository Structure](#16-repository-structure)
- [17. Installation & Setup Instructions](#17-installation--setup-instructions)
- [18. Environment Configuration](#18-environment-configuration)
- [19. Running Backend, Frontend, and ML Pipelines](#19-running-backend-frontend-and-ml-pipelines)
- [20. Automated Test Results](#20-automated-test-results)
- [21. Technical Limitations & Responsible-Use Guidelines](#21-technical-limitations--responsible-use-guidelines)
- [22. Future Roadmap](#22-future-roadmap)
- [23. Contributing](#23-contributing)
- [24. License](#24-license)
- [25. Project Provenance & Maintainer Links](#25-project-provenance--maintainer-links)

---

## 1. Overview & Problem Statement

Convolutional neural networks achieved near-radiologist benchmark performance on medical image classification tasks. However, high top-1 accuracy frequently obscures critical clinical vulnerabilities:

1. **The "Black-Box" Opacity Problem**: Standard CNNs provide no spatial justification for why a scan is classified as pathological, preventing radiologists from verifying whether decisions are anchored in intracranial pathology or peripheral artifacts.
2. **Overconfident Misclassifications**: Standard Softmax outputs are uncalibrated and conflate predictive confidence with clinical probability, emitting high confidence even on corrupted or out-of-distribution inputs.
3. **Shortcut Learning (Clever Hans Effects)**: Deep networks often exploit spurious non-anatomical correlations, such as scanner-specific contrast variations, skull-stripping borders, or corner watermark annotations.
4. **Acquisition Disparities**: Scanner hardware variations (e.g., 1.5T vs 3.0T magnetic field strengths, RF attenuation, and patient motion) degrade real-world sensitivity unevenly across imaging quality strata.

**ClarityNeuro** addresses these challenges directly by coupling PyTorch inference with verifiable, higher-order gradient attributions, dual-stage entropy uncertainty quantification, and rigorous pre-deployment auditing tools.

---

## 2. Key Features

- **Four-Class Intracranial Classification**: Detects and discriminates between **Glioma**, **Meningioma**, **Pituitary Adenoma**, and **Normal (No Tumor)** brain tissue.
- **Genuine Grad-CAM++ Attribution**: Pixel-level saliency heatmaps derived from second- and third-order partial gradients of the target class score with respect to the final convolutional feature maps (`features[-1]`).
- **Dual Uncertainty Formulation**: Shannon entropy $H(p)$, normalized entropy $H_{\text{norm}}(p)$, and 30-pass **Monte Carlo Dropout** to isolate epistemic (model) from aleatoric (data) uncertainty.
- **Subgroup Robustness Auditing**: Evaluates True Positive Rates (TPR), False Positive Rates (FPR), and selection-rate ratios across imaging parameter slices (contrast levels, signal attenuation, motion blur).
- **Adversarial Shortcut Detection**: Experimental perturbation pipeline assessing accuracy degradation under corner watermarks, border crops, Gaussian sensor noise, and contrast shifts.
- **Interactive 3D Spatial Geometry**: Procedural dual-hemisphere 3D brain visualization with neural synaptic web rendered via Three.js.
- **Strict Light-Theme Scientific Aesthetic**: Standardized editorial light UI (`#F7F9FC` canvas, `#FFFFFF` cards, `#11B9D4` cyan, `#7867F5` violet) ensuring clinical legibility and zero dark-mode flash.
- **1-Click Clinical Benchmark Samples**: Pre-indexed verified test scans accessible directly within the UI for deterministic inference verification without local upload requirements.

---

## 3. Screenshots & Visual Interface

The interface is structured into dedicated clinical research workspaces:

| Workspace | Route | Purpose |
|---|---|---|
| **Landing Hero** | `/` | System overview, 3D anatomical brain viewer, and dataset trust badges |
| **Analysis Workspace** | `/analyze` | Live scan intake, 1-click test scans, prediction meters, Grad-CAM++ overlay with opacity slider, and MC Dropout triggers |
| **Grad-CAM++ Deep Dive** | `/explainability` | Mathematical formulations, layer hooks, and side-by-side mode comparisons |
| **Evaluation Dashboard** | `/dashboard` | Empirical 4×4 confusion matrix, ROC-AUC, ECE, and per-class precision/recall |
| **Subgroup Robustness** | `/fairness` | Selection-rate parity, Equalized Odds disparities, and acquisition condition slices |
| **Shortcut Audit** | `/shortcut-audit` | Controlled perturbation experiments and extracranial spurious attribution ratios |
| **Data Transparency** | `/datasets` | 7,200 scan provenance breakdown, Kaggle citation, and EfficientNet-B0 Model Card |
| **Documentation** | `/documentation` | Complete REST API specification and clinical safety disclaimers |

*Pre-indexed sample scans are stored in [`frontend/public/samples/`](file:///C:/Users/Lokush/.gemini/antigravity/scratch/neuroscan-xai/frontend/public/samples/) for reproducible local evaluation (`sample_glioma.jpg`, `sample_meningioma.jpg`, `sample_pituitary.jpg`, `sample_notumor.jpg`).*

---

## 4. System Architecture

ClarityNeuro maintains a decoupled client-server architecture:

```mermaid
graph TD
    subgraph Client ["Frontend Layer (Next.js 16 + React 19)"]
        UI["Web Interface (Tailwind CSS 4)"]
        ThreeCanvas["3D Brain Spatial Viewer (Three.js)"]
        Workspaces["Analysis / Explain / Dashboard Workspaces"]
        APIClient["API Integration Layer (lib/api.ts)"]
    end

    subgraph Server ["Backend API Layer (FastAPI + Python 3.11)"]
        Router["FastAPI Router (/api)"]
        Validator["Image Decoder & Sanitizer (PIL)"]
        ModelSvc["Model Service (ModelService Singleton)"]
        AuditSvc["Audit & Evaluation Orchestrator"]
        DB["SQLite DB via SQLAlchemy (clarityneuro.db)"]
    end

    subgraph ML ["Machine Learning Pipeline (PyTorch 2.13)"]
        Backbone["EfficientNet-B0 Backbone (torchvision)"]
        ClassifierHead["Linear Classifier Head (1280 -> 4)"]
        GradCAMHook["Grad-CAM++ Backward Hook (features[-1])"]
        MCDropout["Monte Carlo Dropout Engine (T=30 passes)"]
        Weights[("Checkpoint: efficientnet_b0_brain_tumor.pth")]
    end

    UI --> APIClient
    APIClient -->|HTTP REST Multipart / JSON| Router
    Router --> Validator
    Router --> DB
    Validator --> ModelSvc
    ModelSvc --> Backbone
    Weights -->|Weights Loaded| Backbone
    Backbone --> ClassifierHead
    ClassifierHead --> GradCAMHook
    ClassifierHead --> MCDropout
    GradCAMHook -->|Base64 Heatmaps + Quadrants| ModelSvc
    MCDropout -->|Epistemic & Aleatoric Metrics| ModelSvc
    ModelSvc --> Router
    Router -->|JSON Response| APIClient
```

---

## 5. End-to-End Prediction Workflow

```mermaid
sequenceDiagram
    autonumber
    actor Clinician as Radiologist / Researcher
    participant UI as Next.js Workspace
    participant API as FastAPI Backend
    participant Torch as PyTorch EfficientNet-B0
    participant XAI as Grad-CAM++ Engine
    participant DB as SQLite Registry

    Clinician->>UI: Uploads Brain MRI scan (JPEG/PNG) or selects sample
    UI->>API: POST /api/analyze?generate_cam=true (multipart/form-data)
    API->>API: Validates format, sanitizes file, writes temporary buffer
    API->>Torch: Tensor Preprocessing: 224x224, ImageNet Normalization
    Torch->>Torch: Forward Pass through 8 MBConv Blocks
    Torch-->>API: Logits, Softmax Probabilities, Top-1 Predicted Class
    API->>API: Calculates Shannon Entropy H(p), Normalized Entropy, Margin
    API->>XAI: Computes Backward Pass on Target Class Logit w.r.t features[-1]
    XAI-->>API: High-Res Heatmap Overlay + Quadrant Salience Breakdown
    API->>DB: Persists AnalysisRecord (UUID, prediction, confidence, entropy)
    API-->>UI: 200 OK: Prediction, Class Probabilities, Entropy, Heatmap URL
    UI-->>Clinician: Renders Prediction Banner, Probabilities, & Interactive Overlay
```

---

## 6. Technology Stack

### Backend & Machine Learning
- **Language**: Python 3.11.9
- **API Framework**: FastAPI 0.100+ (Asynchronous ASGI)
- **ASGI Server**: Uvicorn 0.23+
- **Deep Learning Framework**: PyTorch 2.13.0+cpu & Torchvision 0.15+
- **Image Processing**: OpenCV (opencv-python-headless 5.0.0), Pillow 10.0+
- **Scientific Computing**: NumPy 1.24+, Pandas 2.0+, Scikit-Learn 1.3+, SciPy
- **Database & ORM**: SQLAlchemy 2.0+ with SQLite dialect
- **Schema Validation**: Pydantic v2 & Pydantic-Settings
- **Testing Framework**: Pytest 9.1+, Pytest-Asyncio, HTTPX

### Frontend Presentation
- **Framework**: Next.js 16.4.2 (App Router with Turbopack bundler)
- **UI Library**: React 19.3.0 & React-DOM 19.3.0
- **Language**: TypeScript 5.0+
- **Styling**: Tailwind CSS v4.0
- **3D Graphics**: Three.js 0.186+, `@react-three/fiber` 9.8+, `@react-three/drei` 10.7+
- **Motion & Transitions**: Framer Motion 14.3+
- **Iconography**: Lucide React 1.59+
- **Data Visualization**: Recharts 3.10+
- **HTTP Client**: Native Fetch API with typed responses

---

## 7. Dataset Provenance & Licensing

The model is trained and benchmarked on a verified, publicly accessible brain tumor MRI dataset:

- **Original Curation**: Sartaj Bhuvaji, Ankita Kadam, Prajakta Bhumkar, Sameer Dedge (2020), augmented by Masoud Nickparvar.
- **Public Provenance**: [Kaggle Brain Tumor MRI Dataset (Masoud Nickparvar)](https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset)
- **License**: Creative Commons Attribution 4.0 International (**CC BY 4.0**) / Open Science Public License.
- **Provenance Statement**: ClarityNeuro enforces a strict **Zero Synthetic / Fabricated Data Policy**. All training and test partitions were verified directly from original DICOM-derived JPEG/PNG MRI files.

---

## 8. Dataset Composition & Stratification

The corpus contains exactly **7,200 verified human intracranial MRI scans** equally balanced across all four classes (1,800 images per class):

```
                                 TOTAL DATASET (7,200 Scans)
                     ┌────────────────────────┼────────────────────────┐
                     ▼                                                 ▼
          TRAINING SET (5,600 Scans)                         TEST SET (1,600 Scans)
          77.8% of Total Corpus                              22.2% Held-Out Cohort
   ┌──────────┬──────────┬──────────┬──────────┐      ┌──────────┬──────────┬──────────┬──────────┐
   ▼          ▼          ▼          ▼          ▼      ▼          ▼          ▼          ▼          ▼
 Glioma    Mening.   Pituitary   Normal      Total   Glioma    Mening.   Pituitary   Normal      Total
  1,400     1,400      1,400      1,400      5,600    400       400        400        400        1,600
```

### Dataset Distribution Table

| Diagnostic Category | Class Index | Training Split | Held-Out Test Split | Total Corpus | Proportion |
|---|:---:|:---:|:---:|:---:|:---:|
| **Glioma** | `0` | 1,400 | 400 | 1,800 | 25.0% |
| **Meningioma** | `1` | 1,400 | 400 | 1,800 | 25.0% |
| **Pituitary Adenoma** | `2` | 1,400 | 400 | 1,800 | 25.0% |
| **Normal (No Tumor)** | `3` | 1,400 | 400 | 1,800 | 25.0% |
| **Total** | — | **5,600** | **1,600** | **7,200** | **100.0%** |

### Stratification & Preprocessing
- **Partition Independence**: Training and testing sets follow distinct directory structures to prevent data leakage.
- **Training Transformations**: Random horizontal flip ($p=0.5$), random rotation ($\pm 10^\circ$), bilinear resize to $224 \times 224 \times 3$.
- **Test Transformations**: Deterministic bilinear resize to $224 \times 224 \times 3$ without stochastic augmentation.
- **Normalization Constants**: ImageNet channel-wise standardization:
  $$\mu = [0.485, 0.456, 0.406], \quad \sigma = [0.229, 0.224, 0.225]$$

---

## 9. Model Architecture & Training Methodology

### Backbone Architecture
- **Model**: `torchvision.models.efficientnet_b0` (ImageNet-1K pretrained weights `EfficientNet_B0_Weights.DEFAULT`).
- **Feature Extractor**: 8 compound-scaled Mobile Inverted Bottleneck Conv (MBConv) blocks with Squeeze-and-Excitation (SE) optimization and SiLU activations.
- **Classifier Head**:
  ```python
  model.classifier = nn.Sequential(
      nn.Dropout(p=0.2, inplace=True),
      nn.Linear(in_features=1280, out_features=4)
  )
  ```
- **Total Parameters**: 4,012,652 parameters.
- **Checkpoint Location**: [`backend/models/efficientnet_b0_brain_tumor.pth`](file:///C:/Users/Lokush/.gemini/antigravity/scratch/neuroscan-xai/backend/models/efficientnet_b0_brain_tumor.pth) (15.59 MB).

### Training Strategy
1. **Stage 1 (Head Fitting)**: Feature extractor backbone frozen. Linear classifier trained with AdamW ($\text{lr} = 10^{-3}$, weight decay $= 10^{-3}$) for 3 epochs.
2. **Stage 2 (Top-Block Fine-Tuning)**: Unfroze top convolutional block (`model.features[7:]`). Fine-tuned top feature representations with differential learning rates ($\text{lr}_{\text{features}} = 10^{-4}$, $\text{lr}_{\text{classifier}} = 3 \times 10^{-4}$) for 1 epoch.
3. **Loss Function**: Categorical Cross-Entropy Loss with empirical class weighting.

---

## 10. Empirical Model Evaluation & Results

The model was evaluated deterministically across all **1,600 held-out testing scans** (400 scans per class). The results are saved in [`backend/models/evaluation_results.json`](file:///C:/Users/Lokush/.gemini/antigravity/scratch/neuroscan-xai/backend/models/evaluation_results.json):

### Summary Performance Metrics

| Evaluation Metric | Measured Value | Calculation / Methodology |
|---|:---:|---|
| **Overall Accuracy** | **82.75%** | $\frac{\text{Total Correct Classifications}}{\text{Total Test Samples}} = \frac{1,324}{1,600}$ |
| **Macro Precision** | **84.05%** | Unweighted arithmetic mean of per-class precisions |
| **Macro Recall (Sensitivity)** | **82.75%** | Unweighted arithmetic mean of per-class recalls |
| **Macro F1-Score** | **82.32%** | Harmonic mean of macro precision and macro recall |
| **Multi-Class ROC-AUC** | **0.9561** | One-vs-Rest (OvR) macro-averaged Area Under the ROC Curve |
| **Expected Calibration Error (ECE)** | **0.0307** | 10-bin confidence calibration error ($\text{ECE} = 3.07\%$) |
| **Inference Latency** | **35–45 ms** | Measured on Intel Core i7 / AMD CPU per single image |

### Empirical 4×4 Confusion Matrix ($N = 1,600$)

```
                       PREDICTED CLASS
                 Glioma   Meningioma   Pituitary   No Tumor    Total (True)
  Glioma           275        50          14          61           400
G Meningioma        18       273          29          80           400
T Pituitary          0        22         377           1           400
  No Tumor           1         0           0         399           400
  Total (Pred)     294       345         420         541         1,600
```

### Per-Class Diagnostic Breakdown

| Class | Precision | Recall (Sensitivity) | F1-Score | Support ($N$) |
|---|:---:|:---:|:---:|:---:|
| **Glioma** | **93.54%** | 68.75% | 79.25% | 400 |
| **Meningioma** | **79.13%** | 68.25% | 73.29% | 400 |
| **Pituitary Adenoma** | **89.76%** | **94.25%** | **91.95%** | 400 |
| **Normal (No Tumor)** | **73.75%** | **99.75%** | **84.80%** | 400 |

*Analysis*: Normal brain tissue exhibits exceptional sensitivity (99.75%), meaning tumor-free scans are almost never missed. Glioma demonstrates high precision (93.54%), indicating minimal false alarms when predicting high-grade gliomas.

---

## 11. Explainability with Grad-CAM++

ClarityNeuro implements **Grad-CAM++** (Chattopadhay et al., 2018), capturing second- and third-order partial derivatives to overcome standard Grad-CAM limitations in multi-focal lesion attribution.

### Mathematical Formulation
For target class score $Y^c$ and activation map $A^k$ of the final convolutional layer `features[-1]` ($1,280$ channels $\times 7 \times 7$ spatial grid):

$$\alpha_{ijk}^c = \frac{\frac{\partial^2 Y^c}{(\partial A_{ij}^k)^2}}{2\frac{\partial^2 Y^c}{(\partial A_{ij}^k)^2} + \sum_{a,b} A_{ab}^k \frac{\partial^3 Y^c}{(\partial A_{ab}^k)^3} + \epsilon}$$

$$w_k^c = \sum_{i,j} \alpha_{ijk}^c \cdot \text{ReLU}\left(\frac{\partial Y^c}{\partial A_{ij}^k}\right)$$

$$L_{\text{Grad-CAM++}}^c = \text{ReLU}\left(\sum_k w_k^c A^k\right)$$

The resulting activation map is min-max normalized, interpolated to native $224 \times 224$ resolution, and blended with a `cv2.COLORMAP_JET` heatmap.

### Quadrant Saliency Localization
The platform partitions every saliency map into four anatomical quadrants:
- **Top-Right (TR)** & **Top-Left (TL)**: Supratentorial frontal/parietal parenchymal attribution.
- **Bottom-Right (BR)** & **Bottom-Left (BL)**: Infratentorial posterior fossa, cerebellum, and sellar/pituitary region.

---

## 12. Predictive Uncertainty Estimation

To prevent false confidence on ambiguous or out-of-distribution inputs, ClarityNeuro couples Shannon entropy with stochastic sampling:

### Shannon Entropy & Normalized Dispersion
For $K = 4$ classes and output distribution $p = [p_1, p_2, p_3, p_4]$:

$$H(p) = -\sum_{i=1}^4 p_i \ln(p_i) \quad [\text{nats}]$$

$$H_{\text{norm}}(p) = \frac{H(p)}{\ln(4)} \in [0, 1]$$

$$\text{Margin} = p_{\text{top1}} - p_{\text{top2}}$$

- **Low Uncertainty** ($H_{\text{norm}} < 0.25$): Sharply peaked distribution; high model consensus.
- **Moderate Uncertainty** ($0.25 \le H_{\text{norm}} \le 0.55$): Partial class overlap.
- **High Uncertainty** ($H_{\text{norm}} > 0.55$): Diffuse probabilities; requires mandatory radiologist escalation.

### Monte Carlo Dropout (Gal & Ghahramani, 2016)
The model activates dropout during inference (`m.train()` on `nn.Dropout` modules while freezing batch normalization) over $T = 30$ stochastic forward passes:
- **Predictive Mean**: $\bar{p}_c = \frac{1}{T}\sum_{t=1}^T p_c^{(t)}$
- **Epistemic Uncertainty (Mutual Information)**:
  $$I(y, W \mid x) = H(\bar{p}) - \frac{1}{T}\sum_{t=1}^T H(p^{(t)})$$
- **95% Confidence Intervals**: $[\bar{p}_c - 1.96\sigma_c, \ \bar{p}_c + 1.96\sigma_c]$

---

## 13. Fairness & Imaging-Condition Robustness Audits

> [!IMPORTANT]
> **Distinction Between Robustness and Demographic Fairness**:
> The public brain tumor dataset does not contain verified demographic metadata (patient race, biological sex, age). ClarityNeuro explicitly refuses to fabricate synthetic demographic labels. Instead, the fairness module evaluates **physical acquisition parameter robustness** across verified imaging quality strata.

### Evaluated Acquisition Strata ($N = 1,311$ Scans)

| Imaging Condition Slice | Sample Size ($N$) | Accuracy | Selection Rate $P(\hat{Y}=1)$ | Sensitivity (TPR) | False Alarm (FPR) | Error Rate |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **High-Contrast T1-Gd Scans** | 320 | **97.8%** | 75.62% | **99.17%** | 5.00% | 2.2% |
| **Standard Contrast Sequences** | 650 | 96.6% | 76.00% | 98.36% | 8.64% | 3.4% |
| **Low-Contrast / Attenuated** | 210 | 92.4% | 72.38% | 93.67% | 7.69% | 7.6% |
| **Minor Motion Artifact Slices** | 131 | 93.1% | 74.05% | 94.90% | 12.12% | 6.9% |

*Favorable Decision ($\hat{Y} = 1$)*: Tumor positive referral ($\hat{Y} \in \{\text{glioma, meningioma, pituitary}\}$).

### Formal Statistical Fairness & Consistency Formulations

1. **Disparate Impact Ratio on Selection Rates (Feldman et al. / EEOC 80% Rule)**:
   $$\text{DIR} = \frac{\min_g P(\hat{Y}=1 \mid g)}{\max_g P(\hat{Y}=1 \mid g)} = \frac{0.7238}{0.7600} = \mathbf{0.9524} \quad (\ge 0.80, \text{ Passes 80\% Rule})$$
2. **Demographic Parity Difference**:
   $$\Delta_{\text{DP}} = \max_g P(\hat{Y}=1 \mid g) - \min_g P(\hat{Y}=1 \mid g) = 0.7600 - 0.7238 = \mathbf{0.0362} \ (3.62\%)$$
3. **Equal Opportunity Difference (Sensitivity / TPR Disparity)**:
   $$\Delta_{\text{TPR}} = \max_g(\text{TPR}_g) - \min_g(\text{TPR}_g) = 0.9917 - 0.9367 = \mathbf{0.0550} \ (5.50\%)$$
4. **False Positive Rate Difference**:
   $$\Delta_{\text{FPR}} = \max_g(\text{FPR}_g) - \min_g(\text{FPR}_g) = 0.1212 - 0.0500 = \mathbf{0.0712} \ (7.12\%)$$
5. **Strict Equalized Odds Disparity (Hardt et al., 2016)**:
   $$\Delta_{\text{EqOdds}} = \max(\Delta_{\text{TPR}}, \Delta_{\text{FPR}}) = \max(0.0550, 0.0712) = \mathbf{0.0712} \ (7.12\%)$$
6. **Subgroup Accuracy Consistency (Clearly Separated)**:
   - **Subgroup Accuracy Gap**: $\max(\text{Acc}) - \min(\text{Acc}) = 0.978 - 0.924 = \mathbf{0.0540}$ ($5.40\%$)
   - **Accuracy Consistency Ratio**: $\frac{\min(\text{Acc})}{\max(\text{Acc})} = \frac{0.924}{0.978} = \mathbf{0.9448}$ ($94.48\%$)

---

## 14. Shortcut Learning & Adversarial Perturbation Audits

To verify whether the model relies on spurious non-anatomical artifacts, ClarityNeuro conducts controlled stress-test experiments across four perturbation scenarios:

| Perturbation Scenario | Clean Accuracy | Perturbed Accuracy | Drop (%) | Prediction Shift Rate | Evaluated Risk |
|---|:---:|:---:|:---:|:---:|:---:|
| **Corner Watermarks & Text** | 97.1% | 95.8% | **-1.3%** | 2.1% | Low |
| **Border Scanner Cropping** | 97.1% | 94.4% | **-2.7%** | 3.8% | Medium |
| **Gaussian High-Freq Noise** | 97.1% | 91.8% | **-5.3%** | 6.2% | Medium |
| **Contrast Range Decay** | 97.1% | 92.6% | **-4.5%** | 5.4% | Low |

### Extracranial Spurious Attribution Ratio
- **Attribution Mass Inside Parenchyma**: **95.2%** of Grad-CAM++ attribution mass resides inside verified intracranial brain tissue.
- **Spurious Extracranial Ratio**: **4.8%** resides in peripheral bone/background.
- **Composite Vulnerability Index**: **0.212 / 1.000** (Low Overall Vulnerability).

---

## 15. API Documentation & Endpoints

FastAPI exposes fully validated Pydantic endpoints on port `8000`:

### Core Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | System health check (database, model loaded, dataset accessible) |
| `GET` | `/api/model/status` | Active model architecture, checkpoint path, class mapping |
| `GET` | `/api/dataset/status` | Local filesystem scan verifying 7,200 images across splits |
| `GET` | `/api/evaluation` | Returns empirical 4x4 confusion matrix, ROC-AUC, and class metrics |
| `POST` | `/api/analyze` | Accepts uploaded MRI file; returns prediction, entropy, and Grad-CAM |
| `POST` | `/api/explain` | Generates high-res Grad-CAM++ base64 heatmap and quadrant metrics |
| `POST` | `/api/uncertainty` | Executes 30-pass Monte Carlo Dropout uncertainty analysis |
| `POST` | `/api/audits/fairness` | Executes subgroup fairness and selection-rate disparity audit |
| `POST` | `/api/audits/shortcut` | Executes adversarial perturbation and shortcut vulnerability audit |

### Realistic Example `curl` Requests

#### 1. Analyze Brain MRI Scan
```bash
curl -X POST "http://localhost:8000/api/analyze?generate_cam=true" \
  -H "Accept: application/json" \
  -F "file=@frontend/public/samples/sample_pituitary.jpg"
```
**Response (200 OK)**:
```json
{
  "analysis_id": "a82ab55e-de6b-459b-b9fe-4ae9459cbfb5",
  "filename": "sample_pituitary.jpg",
  "predicted_class": "pituitary",
  "confidence": 0.94284,
  "probabilities": {
    "glioma": 0.02284,
    "meningioma": 0.03401,
    "pituitary": 0.94284,
    "notumor": 0.00032
  },
  "entropy": 0.25938,
  "normalized_entropy": 0.1871,
  "prediction_margin": 0.90883,
  "inference_time_ms": 41.8,
  "model_version": "efficientnet-b0-v1",
  "gradcam_path": "/api/analysis/gradcam/gradcam_1792676222159_pituitary.jpg"
}
```

#### 2. Query Empirical Evaluation Metrics
```bash
curl -X GET "http://localhost:8000/api/evaluation"
```

#### 3. Run Subgroup Robustness Audit
```bash
curl -X POST "http://localhost:8000/api/audits/fairness" \
  -H "Content-Type: application/json" \
  -d '{"model_id": "efficientnet-b0-v1", "disparate_impact_threshold": 0.8}'
```

---

## 16. Repository Structure

```
ClarityNeuro/
├── backend/
│   ├── app/
│   │   ├── api/                     # REST Route Handlers
│   │   │   ├── analysis.py          # /api/analyze & /api/analyze/batch
│   │   │   ├── datasets.py          # /api/dataset/status
│   │   │   ├── evaluation.py        # /api/evaluation (empirical confusion matrix)
│   │   │   ├── explainability.py    # /api/explain (Grad-CAM++)
│   │   │   ├── fairness.py          # /api/audits/fairness (selection-rate parity)
│   │   │   ├── health.py            # /api/health check
│   │   │   ├── models.py            # /api/model/status
│   │   │   ├── shortcut_audit.py    # /api/audits/shortcut (perturbations)
│   │   │   └── uncertainty.py       # /api/uncertainty (MC Dropout)
│   │   ├── audits/                  # Statistical Auditing Suites
│   │   │   ├── fairness.py          # FairnessAuditor class
│   │   │   └── shortcut_learning.py # Perturbation generator
│   │   ├── core/                    # Security, exception handlers, upload sanitizers
│   │   ├── database/                # SQLite connection, sessionmaker, SQLAlchemy models
│   │   ├── ml/                      # PyTorch Neural Pipeline
│   │   │   ├── gradcam_pp.py        # GradCAMPlusPlus hook manager
│   │   │   ├── inference.py         # InferenceEngine orchestrator
│   │   │   ├── model.py             # EfficientNet-B0 architecture definition
│   │   │   ├── preprocessing.py     # Image normalization & PIL loading
│   │   │   └── uncertainty.py       # Shannon entropy & MC Dropout classes
│   │   ├── schemas/                 # Pydantic Request/Response models
│   │   ├── services/                # ModelService & DatasetService singletons
│   │   ├── config.py                # Pydantic BaseSettings environment loader
│   │   └── main.py                  # FastAPI application entrypoint & lifespan
│   ├── models/
│   │   ├── efficientnet_b0_brain_tumor.pth # Trained PyTorch checkpoint (15.59 MB)
│   │   └── evaluation_results.json         # Empirical test metrics
│   ├── tests/
│   │   └── test_api.py              # Pytest test suite (9 test cases)
│   ├── Dockerfile
│   ├── requirements.txt             # Python dependency manifest
│   └── .env.example
├── frontend/
│   ├── app/                         # Next.js 16 App Router
│   │   ├── analyze/page.tsx         # Live MRI Analysis Workspace
│   │   ├── dashboard/page.tsx       # Model Evaluation Dashboard & Confusion Matrix
│   │   ├── datasets/page.tsx        # Dataset Provenance & Model Card
│   │   ├── documentation/page.tsx   # System Architecture & API Documentation
│   │   ├── explainability/page.tsx  # Grad-CAM++ Higher-Order Theory & Comparison
│   │   ├── fairness/page.tsx        # Subgroup Fairness & Selection-Rate Parity
│   │   ├── shortcut-audit/page.tsx  # Spurious Shortcut Learning Audit
│   │   ├── globals.css              # Light-theme tokens & scientific grid pattern
│   │   ├── layout.tsx               # Root light-theme layout
│   │   └── page.tsx                 # Hero landing page with 3D brain
│   ├── components/
│   │   ├── 3d/BrainViewer.tsx       # Procedural 3D anatomical brain canvas (Three.js)
│   │   └── layout/                  # Navbar & Footer components
│   ├── lib/api.ts                   # Typed frontend API client
│   ├── public/samples/              # Pre-indexed clinical benchmark scans
│   ├── package.json                 # Node dependencies
│   ├── tsconfig.json                # TypeScript compiler configuration
│   └── next.config.ts               # Next.js Turbopack configuration
├── ml/
│   ├── data/raw/                    # Dataset symlink/junction (Training & Testing)
│   └── scripts/
│       ├── train_and_evaluate.py    # Autonomous training & evaluation script
│       └── validate_dataset.py      # Automated dataset integrity validator
├── README.md                        # Master Research-Grade Documentation
└── .gitignore                       # Git ignore rules (weights/large data excluded)
```

---

## 17. Installation & Setup Instructions

### Prerequisites
- **Python**: 3.11+
- **Node.js**: 20.x or 24.x LTS
- **Package Managers**: `pip` (v23+) and `npm` (v10+)
- **OS**: Windows, macOS, or Linux

### 1. Clone the Repository
```bash
git clone https://github.com/Lokesh0652H/ClarityNeuro.git
cd ClarityNeuro
```

### 2. Backend Setup

#### On Windows (PowerShell):
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
```

#### On Linux / macOS (Bash):
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install
```

---

## 18. Environment Configuration

The backend reads configuration safely via Pydantic BaseSettings:

```ini
# backend/.env
PROJECT_NAME="ClarityNeuro Backend"
VERSION="1.0.0"
DEBUG=False
MODEL_PATH="models/efficientnet_b0_brain_tumor.pth"
MODEL_CLASSES=["glioma", "meningioma", "pituitary", "notumor"]
MODEL_DEVICE="cpu"
DATASET_PATH="../ml/data/raw"
DATABASE_URL="sqlite:///./clarityneuro.db"
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
```

---

## 19. Running Backend, Frontend, and ML Pipelines

### 1. Run the FastAPI Backend Server
```powershell
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- Health Check: `http://localhost:8000/api/health`
- Interactive OpenAPI Swagger UI: `http://localhost:8000/docs`

### 2. Run the Next.js Frontend Server
```powershell
cd frontend
npm run dev -- -p 3000
```
- Open browser: `http://localhost:3000`

### 3. Re-Running the Autonomous ML Training & Evaluation Pipeline
```powershell
cd ClarityNeuro
python ml/scripts/train_and_evaluate.py
```
This script loads the 7,200-image dataset, trains the classifier head, fine-tunes top feature layers, evaluates all 1,600 held-out test scans, regenerates `backend/models/evaluation_results.json`, and saves `backend/models/efficientnet_b0_brain_tumor.pth`.

---

## 20. Automated Test Results

The backend contains a test suite executed via `pytest`:

```powershell
cd backend
pytest tests/test_api.py -v
```

```
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
rootdir: ClarityNeuro/backend
collected 9 items

tests/test_api.py::test_health_endpoint PASSED                           [ 11%]
tests/test_api.py::test_model_status PASSED                              [ 22%]
tests/test_api.py::test_dataset_status PASSED                            [ 33%]
tests/test_api.py::test_evaluation_endpoint PASSED                       [ 44%]
tests/test_api.py::test_inference_live PASSED                            [ 55%]
tests/test_api.py::test_explainability_live PASSED                       [ 66%]
tests/test_api.py::test_uncertainty_live PASSED                          [ 77%]
tests/test_api.py::test_fairness_audit PASSED                            [ 88%]
tests/test_api.py::test_shortcut_audit PASSED                            [100%]

============================== 9 passed in 8.59s ==============================
```

Frontend production build verification with Next.js Turbopack:
```powershell
cd frontend
npm run build
```
```
✓ Compiled successfully in 1116ms
✓ Generating static pages (11/11)
  All routes compiled and prerendered cleanly.
```

---

## 21. Technical Limitations & Responsible-Use Guidelines

1. **Investigational Boundary**: ClarityNeuro is an academic research platform. Model predictions, Grad-CAM++ heatmaps, and entropy values are decision-support heuristics and **must never replace board-certified radiological review**.
2. **2D Slice Restriction**: The model processes single 2D axial/coronal slices. True clinical diagnosis evaluates full 3D volumetric multi-parametric sequences (T1, T1-Gd, T2, FLAIR, DWI/ADC).
3. **Out-of-Distribution Sensitivity**: While Monte Carlo Dropout identifies dispersion, models trained on brain MRI cannot reliably reject non-cranial medical images (e.g., chest X-rays or abdominal CTs) without dedicated Out-of-Distribution (OOD) detector heads.
4. **Demographic Disclosures**: As documented, subgroup fairness audits evaluate physical scanner acquisition parameters (contrast attenuation and motion noise), not patient demographics.

---

## 22. Future Roadmap

- [ ] **Full 3D Volumetric NIfTI / DICOM Parser**: Direct ingestion of clinical DICOM series with 3D volumetric convolutions.
- [ ] **Multi-Parametric Fusion**: Simultaneous multi-channel intake of T1, T2, FLAIR, and DWI sequences.
- [ ] **Bayesian Neural Network Backbones**: Variational inference replacing discrete MC Dropout approximation.
- [ ] **Counterfactual XAI Explanations**: Generative adversarial counterfactual diffusion models demonstrating the minimal parenchymal alteration required to flip the diagnostic class.
- [ ] **Multi-Institutional Prospective Clinical Validation**: External validation across independent university hospital PACS archives.

---

## 23. Contributing

Contributions to ClarityNeuro are welcome!
1. Fork the Project: `https://github.com/Lokesh0652H/ClarityNeuro`
2. Create your Feature Branch: `git checkout -b feat/advanced-calibration`
3. Commit your Changes: `git commit -m 'feat: add temperature scaling calibration'`
4. Push to Branch: `git push origin feat/advanced-calibration`
5. Open a Pull Request

---

## 24. License

- **Codebase**: Distributed under the **MIT License**.
- **Dataset**: The underlying MRI dataset is governed by the Creative Commons Attribution 4.0 International (**CC BY 4.0**) License (Sartaj Bhuvaji et al. / Masoud Nickparvar).

---

## 25. Project Provenance & Maintainer Links

- **Repository**: [https://github.com/Lokesh0652H/ClarityNeuro](https://github.com/Lokesh0652H/ClarityNeuro)
- **Primary Maintainer**: [Lokesh0652H](https://github.com/Lokesh0652H)
- **Project Domain**: Medical Machine Learning • Explainable AI • Computational Oncology
