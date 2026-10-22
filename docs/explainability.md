# Explainability: Grad-CAM++

## What is Grad-CAM++?

Grad-CAM++ (Gradient-weighted Class Activation Mapping Plus Plus) is an improved version of Grad-CAM that provides better visual explanations for CNN predictions. It uses a weighted combination of the positive partial derivatives of the last convolutional layer feature maps with respect to a specific class score to generate a coarse localization map highlighting important regions.

## How It Works in NeuroScan XAI

1. **Forward Pass**: The input MRI image is passed through EfficientNet-B0
2. **Hook Registration**: Forward and backward hooks capture activations and gradients at the last convolutional layer
3. **Backward Pass**: Gradients are computed for the target class score
4. **Weight Calculation**: Grad-CAM++ weights (α) are computed using second and third order derivatives
5. **Map Generation**: Weighted sum of feature maps → ReLU → upsampling to input size
6. **Visualization**: Heatmap coloring and overlay on original image

## Mathematical Formulation

For class c, the Grad-CAM++ weight for feature map k at spatial location (i,j):

$$\alpha_{ij}^{kc} = \frac{\text{ReLU}\left(\frac{\partial^2 S^c}{\partial (A_{ij}^k)^2}\right)}{2 \cdot \frac{\partial^2 S^c}{\partial (A_{ij}^k)^2} + \sum_{a,b} A_{ab}^k \cdot \frac{\partial^3 S^c}{\partial (A_{ij}^k)^3} + \epsilon}$$

The final heatmap:

$$L^c = \text{ReLU}\left(\sum_k w_k^c \cdot A^k\right)$$

where $w_k^c = \sum_{i,j} \alpha_{ij}^{kc} \cdot \text{ReLU}\left(\frac{\partial S^c}{\partial A_{ij}^k}\right)$

## Interpretation Guidelines

> **⚠️ Important**: Attribution maps show regions that the MODEL uses for its prediction. They are NOT:
> - Definitive tumor segmentation masks
> - Proof of clinical correctness
> - Evidence that highlighted regions contain tumors
> - Substitutes for radiological interpretation

**What the heatmap tells you:**
- Warm colors (red/yellow) = high model attention
- Cool colors (blue/green) = low model attention
- The model's prediction may still be wrong even with plausible-looking attention

**What to watch for:**
- Attention on image borders, corners, or text markers (potential shortcut learning)
- Attention on background rather than brain tissue
- Diffuse, unfocused attention (model may be uncertain)
- Attention on clinically irrelevant regions

## API Usage

```bash
curl -X POST http://localhost:8000/api/explain \
  -F "file=@brain_mri.jpg" \
  -F "target_class=0" \
  -F "overlay_alpha=0.4"
```
