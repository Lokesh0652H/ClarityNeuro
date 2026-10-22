# Model Card: EfficientNet-B0 Brain Tumor Classifier

## Model Details

| Field | Value |
|-------|-------|
| **Architecture** | EfficientNet-B0 |
| **Framework** | PyTorch + timm |
| **Task** | 4-class brain MRI classification |
| **Input** | 224×224 RGB image |
| **Output** | 4-class probability vector |
| **Parameters** | ~5.3M |
| **Pretrained Base** | ImageNet-1K |

## Intended Use

- **Primary**: Educational research into brain tumor classification and explainable AI
- **Users**: ML researchers, students, educators exploring medical imaging AI
- **NOT intended for**: Clinical diagnosis, treatment planning, or any medical decision-making

## Classes

| Index | Class | Description |
|-------|-------|-------------|
| 0 | Glioma | Glial cell tumor |
| 1 | Meningioma | Meningeal tumor |
| 2 | Pituitary | Pituitary gland tumor |
| 3 | No Tumor | Normal brain MRI |

## Training

- **Dataset**: Brain Tumor MRI Dataset (Kaggle - masoudnickparvar)
- **Optimizer**: AdamW
- **Learning Rate**: 1e-4 (with cosine annealing)
- **Batch Size**: 32
- **Epochs**: Up to 50 (early stopping patience: 7)
- **Augmentation**: RandomHorizontalFlip, RandomRotation(15°), ColorJitter
- **Loss**: Cross-entropy (with optional class weights)
- **Preprocessing**: Resize(256) → CenterCrop(224) → Normalize(ImageNet mean/std)

## Evaluation

Evaluation metrics are computed on the held-out test set and persisted in the evaluation results. See the Research Dashboard for actual computed values.

**Reported metrics include:**
- Overall accuracy and balanced accuracy
- Per-class precision, recall, F1
- Macro and weighted F1
- Confusion matrix
- Log loss
- Expected calibration error

> **Important**: All metrics come from a single research dataset. They do NOT represent clinical performance or generalization to other scanners, populations, or imaging protocols.

## Limitations

1. **Single dataset**: Trained and evaluated on one Kaggle dataset. Performance may degrade significantly on images from different scanners, institutions, or patient populations.

2. **No clinical validation**: Has not been validated against clinical ground truth or reviewed by medical professionals.

3. **Potential shortcuts**: The model may rely on image artifacts (borders, backgrounds, text markers) rather than genuine tumor features. Use the Shortcut Audit to investigate.

4. **Class imbalance**: The dataset may have unequal class sizes, which can bias the model toward majority classes.

5. **No uncertainty calibration**: Raw softmax outputs are not calibrated probabilities. High confidence does not guarantee correctness.

6. **2D only**: Operates on single 2D MRI slices, not volumetric 3D scans.

## Ethical Considerations

- Model predictions must never be presented to patients as diagnoses
- Fairness across demographic groups cannot be assessed without demographic metadata
- The "No Tumor" class prediction does not rule out pathology
- Attribution maps (Grad-CAM++) show correlation with model output, not causal evidence of tumor presence
