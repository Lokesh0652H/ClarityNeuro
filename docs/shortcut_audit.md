# Shortcut Learning Audit

## What is Shortcut Learning?

Shortcut learning occurs when a model learns to rely on spurious correlations or artifacts in the training data rather than the intended features. In medical imaging, this can include:

- **Border artifacts**: Bright or dark borders from image processing
- **Text markers**: Patient ID, date, or scanner information burned into images  
- **Background patterns**: Consistent backgrounds correlated with specific labels
- **Image dimensions**: Certain classes having systematically different resolutions
- **Scanner-specific features**: Acquisition parameters creating class-correlated textures

## Audit Components

### 1. Visual Artifact Inspection

Analyzes a single image for common artifacts:

| Check | Description |
|-------|-------------|
| Border intensity | Mean pixel intensity of image borders vs. center |
| Corner analysis | Presence of text or markers in image corners |
| Background uniformity | Standard deviation of background region pixels |
| Dimension analysis | Image aspect ratio and size relative to training set |

### 2. Perturbation Experiments

Tests model sensitivity to image regions that should NOT contain diagnostic information:

| Experiment | Description |
|------------|-------------|
| Border masking | Black out a configurable border region (default: 10% of each edge) |
| Corner masking | Black out all four corners |
| Background masking | Mask non-brain regions (simple thresholding) |

For each perturbation:
- Record original model prediction and confidence
- Record perturbed model prediction and confidence  
- Calculate confidence change
- Flag if predicted class changes

### 3. Dataset-Level Checks

When run over the full dataset:
- Artifact prevalence per class
- Duplicate image detection
- Cross-split duplicate detection (leakage)
- Image dimension distributions per class

## Interpretation

> **⚠️ Important**: These are SCREENING HEURISTICS, not definitive proof.

- A large confidence drop after border masking SUGGESTS the model may use border features, but does not prove it
- Lack of sensitivity to perturbations does NOT prove the model is free of shortcut learning
- Shortcut detection requires careful analysis combining multiple experiments
- Perturbation experiments can introduce their own confounds

## Example Results

```
Original prediction: glioma (87.2%)
Border-masked prediction: glioma (84.1%) → Δ = -3.1%
Corner-masked prediction: glioma (86.5%) → Δ = -0.7%

Assessment: Small confidence changes suggest low reliance on border/corner features.
Note: This does not rule out other forms of shortcut learning.
```

## Recommended Workflow

1. Run visual artifact inspection on a sample of images from each class
2. Run perturbation experiments on correctly classified test images
3. Compare perturbation sensitivity across classes
4. If high sensitivity detected, investigate the training data for systematic artifacts
5. Consider retraining with artifact removal or augmentation
