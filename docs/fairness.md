# Fairness Audit

## Purpose

The fairness audit evaluates whether the brain tumor classifier performs equitably across different subgroups of the evaluation data. Disparities in model performance can indicate bias that may affect certain patient populations disproportionately.

## Methodology

### Subgroup Evaluation

When subgroup metadata is available (e.g., age group, sex, scanner type), the audit:

1. Joins metadata with evaluation data using stable image identifiers
2. Stratifies predictions by the specified subgroup column
3. Calculates per-group performance metrics
4. Compares performance across groups
5. Flags groups with insufficient sample sizes (< 30)

### Metrics Per Subgroup

| Metric | Description |
|--------|-------------|
| Sample Count | Number of images in the subgroup |
| Accuracy | Overall classification accuracy |
| Sensitivity | True positive rate (per-class) |
| Specificity | True negative rate (per-class) |
| Macro F1 | Unweighted mean of per-class F1 scores |
| False Positive Rate | Proportion of negatives incorrectly classified |
| False Negative Rate | Proportion of positives incorrectly classified |

### Performance Gap Analysis

- Absolute difference in accuracy between best and worst performing groups
- Per-class recall disparity
- Confidence intervals where sample sizes permit

## Limitations

1. **No demographic metadata in the base dataset**: The Brain Tumor MRI dataset does not include patient demographics. Fairness auditing requires external metadata that maps image identifiers to subgroup attributes.

2. **Metadata must be user-provided**: Users must supply a CSV file with documented schema. The system does NOT infer demographics from MRI images.

3. **Small subgroups**: Metrics from groups with fewer than 30 samples should be interpreted with extreme caution.

4. **Single-dataset evaluation**: Fairness findings apply only to the evaluated data and may not generalize.

5. **Not regulatory compliance**: This audit is a research tool. It does not constitute a formal bias assessment required by medical device regulations.

## When Metadata Is Unavailable

If no subgroup metadata is provided, the fairness audit page will display:

> **Fairness audit unavailable** — required subgroup metadata has not been provided.

This is honest behavior. The system does not fabricate demographic data or claim the model is fair simply because the audit feature exists.

## Providing Metadata

Prepare a CSV file with:

```csv
image_id,label,age_group,sex,scanner
img_001.jpg,glioma,adult,female,siemens
img_002.jpg,meningioma,elderly,male,ge
```

Required columns:
- `image_id`: Filename matching images in the evaluation set
- `label`: Ground truth class

Optional subgroup columns (specify one for each audit run):
- `age_group`, `sex`, `scanner`, `institution`, or any categorical field
