"use client";

import Link from "next/link";
import { 
  Sparkles, 
  Brain, 
  Layers, 
  ArrowRight, 
  CheckCircle2, 
  AlertTriangle, 
  HelpCircle, 
  Code2, 
  Activity,
  Sliders,
  Eye
} from "lucide-react";

export default function ExplainabilityPage() {
  const comparisonFeatures = [
    {
      feature: "Multiple Object Instances",
      standard: "Often fails or averages out distinct simultaneous lesions",
      plusPlus: "Accurately localizes multifocal lesions with positive weighting",
    },
    {
      feature: "Gradient Formulation",
      standard: "First-order partial derivatives only: ∂Y^c / ∂A^k",
      plusPlus: "Second & third-order partial derivatives: ∂²Y^c / ∂(A^k)² & ∂³Y^c / ∂(A^k)³",
    },
    {
      feature: "Spatial Precision",
      standard: "Coarser heatmaps with diffuse boundary margins",
      plusPlus: "Sharply delineated tumor boundaries and core contrast enhancement",
    },
    {
      feature: "Class Discrimination",
      standard: "Can exhibit saliency overlap between competing classes",
      plusPlus: "High class-specificity, isolating distinct features for each tumor type",
    },
  ];

  return (
    <div className="min-h-screen bg-[#F7F9FC] py-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header */}
        <div className="mb-10">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#11B9D4] mb-2">
            <Sparkles className="w-4 h-4" />
            <span>Explainable AI (XAI) Deep Dive</span>
          </div>
          <h1 className="text-3xl font-extrabold text-[#15243A] tracking-tight">
            Grad-CAM++ Feature Attribution Methodology
          </h1>
          <p className="text-sm text-[#68758A] mt-1 max-w-3xl leading-relaxed">
            NeuroScan XAI utilizes genuine Gradient-Weighted Class Activation Mapping++ (Grad-CAM++) computed on the final convolutional features of EfficientNet-B0 to provide pixel-level diagnostic interpretability.
          </p>
        </div>

        {/* Mathematical Foundation Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          
          {/* Card 1: Mathematical Formulation */}
          <div className="clinical-card p-6 space-y-4">
            <div className="flex items-center gap-2 text-[#11B9D4] font-bold text-sm">
              <Code2 className="w-4 h-4" />
              <span>Higher-Order Gradient Weighting</span>
            </div>
            <h3 className="text-lg font-bold text-[#15243A]">
              Mathematical Formulation of Grad-CAM++
            </h3>
            <p className="text-xs text-[#68758A] leading-relaxed">
              Standard Grad-CAM computes uniform spatial weights by global average pooling first derivatives. Grad-CAM++ derives pixel-wise weighting coefficients using second- and third-order partial gradients of the target class score <code className="bg-[#F0F4F8] px-1 py-0.5 rounded text-[#15243A] font-mono">Y^c</code> with respect to activation map <code className="bg-[#F0F4F8] px-1 py-0.5 rounded text-[#15243A] font-mono">A^k</code>:
            </p>

            {/* Formula Block */}
            <div className="p-4 rounded-xl bg-[#F0F4F8] border border-[#E5EAF1] font-mono text-xs text-[#15243A] space-y-2 overflow-x-auto">
              <div className="font-semibold text-[#7867F5]">Weight Coefficient Formulation:</div>
              <div>α_ijk^c = [ ∂²Y^c / ∂(A_ij^k)² ] / [ 2·∂²Y^c/∂(A_ij^k)² + Σ_ab A_ab^k · ∂³Y^c/∂(A_ab^k)³ ]</div>
              <div className="pt-2 font-semibold text-[#11B9D4]">Class Saliency Map:</div>
              <div>L^c = ReLU( Σ_k [ Σ_ij (α_ijk^c · ReLU(∂Y^c / ∂A_ij^k)) ] · A^k )</div>
            </div>

            <p className="text-xs text-[#68758A]">
              The resulting tensor is rectified with <strong className="text-[#15243A]">ReLU</strong> to retain only positive evidence supporting the target class, and bilinearly interpolated back to native MRI dimensions (224×224).
            </p>
          </div>

          {/* Card 2: Neural Architecture Mapping */}
          <div className="clinical-card p-6 space-y-4">
            <div className="flex items-center gap-2 text-[#7867F5] font-bold text-sm">
              <Layers className="w-4 h-4" />
              <span>Feature Extraction Backbone</span>
            </div>
            <h3 className="text-lg font-bold text-[#15243A]">
              EfficientNet-B0 Layer Attributions
            </h3>
            <p className="text-xs text-[#68758A] leading-relaxed">
              Gradient hooks are attached to <code className="bg-[#F0F4F8] px-1 py-0.5 rounded text-[#15243A] font-mono">model.features[-1]</code> (the final MBConv block with 1,280 channels and 7×7 spatial resolution). This layer captures the highest-level semantic abstractions:
            </p>

            <div className="space-y-2.5 text-xs">
              <div className="p-3 rounded-lg bg-[#F7F9FC] border border-[#E5EAF1] flex items-center justify-between">
                <div>
                  <span className="font-bold text-[#15243A]">Low-Level Blocks (features[0..2]):</span>
                  <span className="text-[#68758A] block text-[11px]">Edges, cranial bone contours, cerebrospinal fluid interfaces</span>
                </div>
                <span className="text-[10px] font-mono text-[#68758A]">112×112 / 56×56</span>
              </div>

              <div className="p-3 rounded-lg bg-[#F7F9FC] border border-[#E5EAF1] flex items-center justify-between">
                <div>
                  <span className="font-bold text-[#15243A]">Mid-Level Blocks (features[3..5]):</span>
                  <span className="text-[#68758A] block text-[11px]">Sulcal anatomy, ventricles, parenchymal textures</span>
                </div>
                <span className="text-[10px] font-mono text-[#68758A]">28×28 / 14×14</span>
              </div>

              <div className="p-3 rounded-lg bg-[#11B9D4]/10 border border-[#11B9D4]/20 flex items-center justify-between">
                <div>
                  <span className="font-bold text-[#11B9D4]">Target Convolutional Layer (features[8]):</span>
                  <span className="text-[#15243A] block text-[11px]">Pathological lesion morphology, contrast enhancement, mass effect</span>
                </div>
                <span className="text-[10px] font-mono font-bold text-[#11B9D4]">7×7 / 1,280 ch</span>
              </div>
            </div>
          </div>

        </div>

        {/* Algorithmic Comparison: Standard Grad-CAM vs Grad-CAM++ */}
        <div className="clinical-card p-8 mb-12">
          <div className="mb-6">
            <h3 className="text-xl font-bold text-[#15243A]">
              Standard Grad-CAM vs. Grad-CAM++ in Neurological MRI
            </h3>
            <p className="text-xs text-[#68758A] mt-1">
              Why higher-order gradient formulations are necessary for brain tumor identification.
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-[#E5EAF1] text-[#68758A]">
                  <th className="pb-3 font-semibold uppercase tracking-wider">Evaluation Dimension</th>
                  <th className="pb-3 font-semibold uppercase tracking-wider">Standard Grad-CAM</th>
                  <th className="pb-3 font-semibold uppercase tracking-wider text-[#11B9D4]">NeuroScan Grad-CAM++</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E5EAF1]">
                {comparisonFeatures.map((row) => (
                  <tr key={row.feature} className="hover:bg-[#F7F9FC]">
                    <td className="py-3.5 font-bold text-[#15243A]">{row.feature}</td>
                    <td className="py-3.5 text-[#68758A]">{row.standard}</td>
                    <td className="py-3.5 font-semibold text-[#15243A] flex items-center gap-1.5">
                      <CheckCircle2 className="w-4 h-4 text-[#10B981] shrink-0" />
                      <span>{row.plusPlus}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Quadrant Localization & Failure Modes */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
          
          {/* Quadrant Localization */}
          <div className="clinical-card p-6 space-y-3">
            <div className="flex items-center gap-2 text-[#10B981] font-bold text-sm">
              <Eye className="w-4 h-4" />
              <span>Quadrant Attribution Metrics</span>
            </div>
            <h4 className="text-base font-bold text-[#15243A]">
              Automated Spatial Quadrant Partitioning
            </h4>
            <p className="text-xs text-[#68758A] leading-relaxed">
              Every Grad-CAM++ heatmap is partitioned into four anatomical quadrants (Top-Right, Top-Left, Bottom-Left, Bottom-Right). This quantifies attribution concentration:
            </p>
            <ul className="text-xs text-[#68758A] space-y-2 list-disc list-inside">
              <li>Identifies lateralization (Right vs. Left hemisphere mass effect)</li>
              <li>Detects supratentorial vs. infratentorial/sellar concentrations</li>
              <li>Flags abnormal attributions focused on cranial periphery or background</li>
            </ul>
          </div>

          {/* Failure Modes & Disclaimers */}
          <div className="clinical-card p-6 space-y-3 border-l-4 border-[#F59E0B]">
            <div className="flex items-center gap-2 text-[#F59E0B] font-bold text-sm">
              <AlertTriangle className="w-4 h-4" />
              <span>Known Technical Limitations</span>
            </div>
            <h4 className="text-base font-bold text-[#15243A]">
              Attribution Interpretation Disclaimers
            </h4>
            <ul className="text-xs text-[#68758A] space-y-2 list-disc list-inside leading-relaxed">
              <li>
                <strong className="text-[#15243A]">Not a Segmentation Mask:</strong> Saliency maps highlight features driving classification score, not microscopic tumor margin boundaries.
              </li>
              <li>
                <strong className="text-[#15243A]">Low-Contrast Scans:</strong> Scans with severe attenuation or poor T1-contrast enhancement can exhibit diffuse heatmaps.
              </li>
              <li>
                <strong className="text-[#15243A]">Resolution Constraint:</strong> Feature maps at 7×7 are bilinearly upsampled to 224×224; sub-millimeter anatomical detail is constrained.
              </li>
            </ul>
          </div>

        </div>

        {/* CTA to live workspace */}
        <div className="text-center py-6">
          <Link
            href="/analyze"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-[#11B9D4] to-[#7867F5] text-white font-semibold text-sm shadow-sm hover:opacity-95 transition-opacity"
          >
            <Brain className="w-4 h-4" />
            <span>Test Grad-CAM++ in MRI Workspace</span>
            <ArrowRight className="w-4 h-4 ml-1" />
          </Link>
        </div>

      </div>
    </div>
  );
}
