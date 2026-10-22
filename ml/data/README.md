# NeuroScan XAI - Brain Tumor MRI Dataset

## 1. Overview
The NeuroScan XAI pipeline uses the consolidated **Brain Tumor MRI Dataset** curated by Masoud Nickparvar. This benchmark aggregates scans from Sartaj, Br35H, and Figshare repositories, providing a standardized multiclass diagnostic dataset across four categories:

1. **Glioma (`glioma`)**: Infiltrative glial neoplasms originating in brain parenchymal tissue.
2. **Meningioma (`meningioma`)**: Typically benign, extra-axial tumors originating from the arachnoid layer of the meninges.
3. **Pituitary (`pituitary`)**: Sellar / suprasellar endocrine neoplasms affecting the pituitary gland.
4. **No Tumor (`notumor`)**: Healthy control axial/coronal/sagittal T1/T2 MRI brain slices.

### Dataset Citation & Source
- **Kaggle Dataset Identifier**: `masoudnickparvar/brain-tumor-mri-dataset`
- **URL**: [https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset](https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset)
- **Image Modalities**: Contrast-enhanced T1-weighted (T1c), T2-weighted, and FLAIR MRI acquisitions.

---

## 2. Directory Structure

```
ml/data/
├── README.md               # This documentation file
├── manifest.json           # Certified file-level metadata & MD5 checksum manifest
├── raw/                    # Raw uncompressed dataset directory
│   ├── Training/           # Training split (~5,712 images)
│   │   ├── glioma/
│   │   ├── meningioma/
│   │   ├── notumor/
│   │   └── pituitary/
│   └── Testing/            # Evaluation test split (~1,311 images)
│       ├── glioma/
│       ├── meningioma/
│       ├── notumor/
│       └── pituitary/
└── processed/              # (Optional) Preprocessed / cached tensor artifacts
```

---

## 3. Acquisition & Setup Instructions

### Method A: Automated Download Script (Recommended)
Configure your Kaggle API key (either via `~/.kaggle/kaggle.json` or environment variables `KAGGLE_USERNAME` and `KAGGLE_KEY`), then run:
```bash
python ml/scripts/download_dataset.py --output-dir ml/data/raw
```

### Method B: Kaggle CLI
```bash
kaggle datasets download -d masoudnickparvar/brain-tumor-mri-dataset -p ml/data/raw --unzip
```

### Method C: Manual Browser Download
1. Navigate to [Kaggle Brain Tumor MRI Dataset](https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset).
2. Download `archive.zip` (~149 MB).
3. Extract the contents directly into `ml/data/raw/`.

---

## 4. Verification and Integrity Audits

To ensure zero image corruption, inspect class balance, and verify absence of cross-split data leakage:
```bash
# Full dataset validation & integrity check
python ml/scripts/validate_dataset.py --data-dir ml/data/raw --output-manifest ml/data/manifest.json

# Or generate a detailed file-by-file manifest
python ml/scripts/generate_manifest.py --data-dir ml/data/raw --output-manifest ml/data/manifest.json
```

---

## 5. Clinical Caveats, Biases, and Shortcut Risks

When deploying medical imaging models trained on this benchmark, be aware of the following known caveats:

1. **Peripheral Annotations & Scanner Artifacts**:
   - Some MRI slices contain hospital timestamps, patient orientation letters (`L`/`R`), or contrast agent indicators embedded directly in the scan corners.
   - NeuroScan XAI provides the `ShortcutAuditor` (`backend.app.audits.shortcut_learning`) to detect whether the network relies on corner or border cues rather than brain pathology.

2. **Skull-Stripping Disparities**:
   - `notumor` control scans frequently originate from different institutional registries than tumor scans, causing subtle differences in background thermal noise and field-of-view cropping.
   - Balanced data augmentation and background masking are implemented in `train.py` to mitigate these shortcut paths.

3. **Slice Correlation (Patient Overlap)**:
   - Slices from the same 3D MRI volume may appear within the same folder.
   - Cross-validation splits must ideally be partitioned by patient identifier when volumetric DICOM metadata is available.
