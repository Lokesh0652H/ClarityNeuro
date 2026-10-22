# Dataset Documentation

## Primary Dataset

**Name**: Brain Tumor MRI Dataset  
**Source**: https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset  
**Author**: Masoud Nickparvar  
**License**: See dataset page for current license terms  

## Classes

| Class | Description |
|-------|-------------|
| Glioma | Brain tumor arising from glial cells |
| Meningioma | Tumor from the meninges surrounding the brain |
| Pituitary | Tumor of the pituitary gland |
| No Tumor | Normal brain MRI without visible tumor |

## Expected Structure

After download and extraction:

```
ml/data/raw/
├── Training/
│   ├── glioma/        (JPEG brain MRI images)
│   ├── meningioma/    (JPEG brain MRI images)  
│   ├── pituitary/     (JPEG brain MRI images)
│   └── notumor/       (JPEG brain MRI images)
└── Testing/
    ├── glioma/
    ├── meningioma/
    ├── pituitary/
    └── notumor/
```

## Acquisition

### Method 1: Kaggle CLI (Recommended)

```bash
pip install kaggle
# Place kaggle.json in ~/.kaggle/ (Linux/macOS) or %USERPROFILE%\.kaggle\ (Windows)
python ml/scripts/download_dataset.py
```

### Method 2: Manual Download

1. Visit the Kaggle dataset page
2. Click "Download" (requires Kaggle account)
3. Extract the ZIP to `ml/data/raw/`
4. Verify the Training/ and Testing/ directories exist

## Validation

Run the validation script to verify dataset integrity:

```bash
python ml/scripts/validate_dataset.py --data-dir ml/data/raw
```

This will check:
- File counts per class
- Image readability
- Duplicate detection (MD5 hashes)
- Train/test leakage (cross-split duplicates)
- Image dimensions and formats
- Class distribution

## Known Considerations

1. **No patient identifiers**: The dataset does not include patient IDs, making patient-level splitting impossible. This is a known limitation for leakage analysis.

2. **Potential duplicates**: Some versions of the dataset may contain duplicate or near-duplicate images. The validation script checks for exact duplicates via MD5 hashing.

3. **Image provenance**: Images may come from multiple sources and scanners. This could introduce confounding variables that the model might learn as shortcuts.

4. **No demographic metadata**: The dataset does not include age, sex, scanner type, or institution metadata. This limits fairness analysis to class-level evaluation.

5. **License compliance**: The dataset is hosted on Kaggle. Users must accept Kaggle's terms and any dataset-specific terms before use. The dataset is NOT bundled in this repository.

## Data Retention

- Raw dataset files are stored locally in `ml/data/raw/` (gitignored)
- Uploaded MRI images for analysis are stored temporarily and cleaned up
- No images are sent to external services
- Analysis metadata (predictions, metrics) is stored in SQLite
