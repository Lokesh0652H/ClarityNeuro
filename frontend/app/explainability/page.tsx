"use client";

import Link from "next/link";
import { 
  Sparkles, 
  Brain, 
  Layers, 
  ArrowRight, 
  CheckCircle2, 
  AlertTriangle, 
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
    <div className="min-h-screen bg-[#FAFAFD] text-[#0F172A] py-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header */}
        <div className="mb-8">
          <span className="text-[11px] font-bold tracking-wider uppercase text-indigo-600">
            EXPLAINABLE AI (XAI)
          </span>
          <h1 className="font-serif text-3xl sm:text-4xl font-bold text-[#0F172A] mt-1 tracking-tight">
            Grad-CAM++ Feature Attribution Methodology
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1 max-w-3xl leading-relaxed">
            NeuroScan XAI utilizes genuine Gradient-Weighted Class Activation Mapping++ (Grad-CAM++) computed on the final convolutional features of EfficientNet-B0 to provide pixel-level diagnostic interpretability.
          </p>
        </div>

        {/* Mathematical Foundation Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          
          {/* Card 1: Mathematical Formulation */}
          <div className="bg-white rounded-2xl border border-slate-100 p-6 shadow-xs space-y-4">
            <div className="flex items-center gap-2 text-indigo-600 font-bold text-xs">
              <Code2 className="w-4 h-4" />
              <span>Higher-Order Gradient Weighting</span>
            </div>
            <h3 className="font-serif text-lg font-bold text-slate-900">
              Mathematical Formulation of Grad-CAM++
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Standard Grad-CAM computes uniform spatial weights by global average pooling first derivatives. Grad-CAM++ derives pixel-wise weighting coefficients using second- and third-order partial gradients of the target class score <code className="bg-slate-100 px-1 py-0.5 rounded text-slate-900 font-mono text-[11px]">Y^c</code> with respect to activation map <code className="bg-slate-100 px-1 py-0.5 rounded text-slate-900 font-mono text-[11px]">A^k</code>:
            </p>

            {/* Formula Block */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 font-mono text-xs text-slate-900 space-y-2 overflow-x-auto">
              <div className="font-semibold text-indigo-600">Weight Coefficient Formulation:</div>
              <div>α_ijk^c = [ ∂²Y^c / ∂(A_ij^k)² ] / [ 2·∂²Y^c/∂(A_ij^k)² + Σ_ab A_ab^k · ∂³Y^c/∂(A_ab^k)³ ]</div>
              <div className="pt-2 font-semibold text-blue-600">Class Saliency Map:</div>
              <div>L^c = ReLU( Σ_k [ Σ_ij (α_ijk^c · ReLU(∂Y^c / ∂A_ij^k)) ] · A^k )</div>
            </div>

            <p className="text-xs text-slate-500">
              The resulting tensor is rectified with <strong className="text-slate-900">ReLU</strong> to retain only positive evidence supporting the target class, and bilinearly interpolated back to native MRI dimensions (224×224).
            </p>
          </div>

          {/* Card 2: Neural Architecture Mapping */}
          <div className="bg-white rounded-2xl border border-slate-100 p-6 shadow-xs space-y-4">
            <div className="flex items-center gap-2 text-purple-600 font-bold text-xs">
              <Layers className="w-4 h-4" />
              <span>Feature Extraction Backbone</span>
            </div>
            <h3 className="font-serif text-lg font-bold text-slate-900">
              EfficientNet-B0 Layer Attributions
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Gradient hooks are attached to <code className="bg-slate-100 px-1 py-0.5 rounded text-slate-900 font-mono text-[11px]">model.features[-1]</code> (the final MBConv block with 1,280 channels and 7×7 spatial resolution). This layer captures the highest-level semantic abstractions:
            </p>

            <div className="space-y-2 pt-2 text-xs">
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-between">
                <div>
                  <strong className="text-slate-900 block">Conv Head Hook (features[-1])</strong>
                  <span className="text-[11px] text-slate-500">1,280 channels × 7 × 7 feature volume</span>
                </div>
                <span className="text-[11px] font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-100">
                  Active Hook
                </span>
              </div>

              <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-between">
                <div>
                  <strong className="text-slate-900 block">Quadrant Spatial Localization</strong>
                  <span className="text-[11px] text-slate-500">Right/Left frontal, temporal, parietal, and occipital lobes</span>
                </div>
                <span className="text-[11px] font-bold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-full border border-indigo-100">
                  4 Quadrants
                </span>
              </div>

              <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-between">
                <div>
                  <strong className="text-slate-900 block">Jet Colormap Normalization</strong>
                  <span className="text-[11px] text-slate-500">0.0 (blue background) to 1.0 (red peak tumor core)</span>
                </div>
                <span className="text-[11px] font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full border border-blue-100">
                  Normalized
                </span>
              </div>
            </div>
          </div>

        </div>

        {/* Comparison Table: Grad-CAM vs Grad-CAM++ */}
        <div className="bg-white rounded-2xl border border-slate-100 p-6 shadow-xs mb-8">
          <div className="mb-4">
            <h3 className="font-serif text-base font-bold text-slate-900">
              Comparative Analysis: Grad-CAM vs. Grad-CAM++
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Empirical advantages of higher-order derivative weighting in brain tumor neuroimaging.
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-100 text-[11px] font-semibold text-slate-400">
                  <th className="pb-3">Evaluation Axis</th>
                  <th className="pb-3 text-slate-500">Standard Grad-CAM (Selvaraju et al.)</th>
                  <th className="pb-3 text-indigo-600 font-bold">Grad-CAM++ (NeuroScan XAI)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50 font-medium">
                {comparisonFeatures.map((row) => (
                  <tr key={row.feature} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3.5 font-bold text-slate-900">{row.feature}</td>
                    <td className="py-3.5 text-slate-500">{row.standard}</td>
                    <td className="py-3.5 text-indigo-700 font-semibold">{row.plusPlus}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Action Link */}
        <div className="text-center pt-4">
          <Link
            href="/analyze"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-[#0F172A] hover:bg-slate-800 text-white font-medium text-xs shadow-sm hover:shadow-md transition-all cursor-pointer"
          >
            <Brain className="w-4 h-4" />
            <span>Test Live Grad-CAM++ on Real Scans</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

      </div>
    </div>
  );
}
