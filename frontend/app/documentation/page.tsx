"use client";

import Link from "next/link";
import { 
  BookOpen, 
  Brain, 
  Code2, 
  Database, 
  Server, 
  ShieldCheck, 
  Sparkles, 
  AlertTriangle, 
  CheckCircle2, 
  Layers, 
  Terminal,
  ExternalLink
} from "lucide-react";

export default function DocumentationPage() {
  const apiEndpoints = [
    {
      method: "GET",
      path: "/api/health",
      desc: "Returns operational health of FastAPI server, model readiness, and SQLite database connectivity.",
    },
    {
      method: "GET",
      path: "/api/model/status",
      desc: "Returns active checkpoint path, parameter count, class mappings, and device placement.",
    },
    {
      method: "GET",
      path: "/api/dataset/status",
      desc: "Scans local filesystem to verify image counts across training and testing splits.",
    },
    {
      method: "POST",
      path: "/api/analyze?generate_cam=true",
      desc: "Accepts uploaded MRI scan image, executes forward pass, computes entropy, and returns probabilities.",
    },
    {
      method: "POST",
      path: "/api/explain",
      desc: "Calculates Grad-CAM or Grad-CAM++ higher-order activation map and quadrant localization.",
    },
    {
      method: "POST",
      path: "/api/uncertainty",
      desc: "Executes Monte Carlo Dropout (T=30 stochastic forward passes) for epistemic & aleatoric quantification.",
    },
    {
      method: "GET",
      path: "/api/evaluation",
      desc: "Returns empirical confusion matrix, macro F1, ROC-AUC, and per-class precision/recall on test cohort.",
    },
    {
      method: "POST",
      path: "/api/audits/fairness",
      desc: "Computes disparate impact ratio and equalized odds disparities across MRI parameter slices.",
    },
    {
      method: "POST",
      path: "/api/audits/shortcut",
      desc: "Runs adversarial stress tests evaluating watermark and scanner artifact shortcut reliance.",
    },
  ];

  return (
    <div className="min-h-screen bg-[#F7F9FC] py-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header */}
        <div className="mb-10">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#11B9D4] mb-2">
            <BookOpen className="w-4 h-4" />
            <span>Developer & Clinical Documentation</span>
          </div>
          <h1 className="text-3xl font-extrabold text-[#15243A] tracking-tight">
            NeuroScan XAI Technical Documentation
          </h1>
          <p className="text-sm text-[#68758A] mt-1 max-w-3xl leading-relaxed">
            Architectural specifications, machine learning inference pipeline, Grad-CAM++ mathematics, API reference, and clinical safety constraints.
          </p>
        </div>

        {/* Section 1: System Architecture */}
        <div className="clinical-card p-8 mb-10 space-y-6">
          <div className="flex items-center gap-2 text-[#11B9D4] font-bold text-sm">
            <Server className="w-4 h-4" />
            <span>System Architecture Overview</span>
          </div>
          <h3 className="text-xl font-bold text-[#15243A]">
            Modular FastAPI + React Micro-Architecture
          </h3>
          <p className="text-xs text-[#68758A] leading-relaxed">
            The platform is organized into strictly decoupled presentation and scientific computation layers:
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-xs">
            <div className="p-4 rounded-xl bg-[#F7F9FC] border border-[#E5EAF1] space-y-2">
              <span className="font-bold text-[#15243A] block text-sm">Frontend Presentation</span>
              <p className="text-[#68758A] leading-relaxed">
                React 19 & Next.js App Router with Tailwind CSS, Lucide icons, Framer Motion, and Three.js 3D spatial geometry. Enforces strict light theme tokens with high-contrast accessibility.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-[#F7F9FC] border border-[#E5EAF1] space-y-2">
              <span className="font-bold text-[#11B9D4] block text-sm">FastAPI REST Services</span>
              <p className="text-[#68758A] leading-relaxed">
                Asynchronous Python backend validating uploads, managing database persistence with SQLAlchemy/SQLite, orchestrating PyTorch inference, and serving Grad-CAM++ heatmaps.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-[#F7F9FC] border border-[#E5EAF1] space-y-2">
              <span className="font-bold text-[#7867F5] block text-sm">PyTorch ML & XAI Engine</span>
              <p className="text-[#68758A] leading-relaxed">
                EfficientNet-B0 backbone with backward hook registration on final convolutional feature maps, Monte Carlo Dropout sampling, and Shannon entropy estimation routines.
              </p>
            </div>
          </div>
        </div>

        {/* Section 2: Mathematical Theory */}
        <div className="clinical-card p-8 mb-10 space-y-6">
          <div className="flex items-center gap-2 text-[#7867F5] font-bold text-sm">
            <Code2 className="w-4 h-4" />
            <span>Mathematical Foundations</span>
          </div>
          <h3 className="text-xl font-bold text-[#15243A]">
            Shannon Entropy & Monte Carlo Uncertainty
          </h3>
          <p className="text-xs text-[#68758A] leading-relaxed">
            Predictive uncertainty is quantified via normalized Shannon entropy across softmax class probabilities:
          </p>

          <div className="p-4 rounded-xl bg-[#F0F4F8] border border-[#E5EAF1] font-mono text-xs text-[#15243A] space-y-2">
            <div><strong>Shannon Entropy:</strong> H(p) = - Σ_i p_i · ln(p_i)   [nats]</div>
            <div><strong>Normalized Entropy:</strong> H_norm(p) = H(p) / ln(K)   where K = 4 classes, bounded in [0, 1]</div>
            <div><strong>Prediction Margin:</strong> Margin = p_top1 - p_top2</div>
            <div><strong>Epistemic Uncertainty:</strong> I(y; W | x) = H( E_W[p(y|x,W)] ) - E_W[ H(p(y|x,W)) ]</div>
          </div>

          <p className="text-xs text-[#68758A]">
            Low normalized entropy (<code className="bg-[#F0F4F8] px-1 py-0.5 rounded text-[#10B981] font-bold">&lt; 0.25</code>) indicates high predictive consensus, whereas elevated entropy (<code className="bg-[#F0F4F8] px-1 py-0.5 rounded text-[#EF4444] font-bold">&gt; 0.55</code>) flags ambiguous morphology or scanner variance requiring clinical radiologist review.
          </p>
        </div>

        {/* Section 3: API Specification */}
        <div className="clinical-card p-8 mb-10 space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-[#10B981] font-bold text-sm">
              <Terminal className="w-4 h-4" />
              <span>FastAPI Endpoint Reference</span>
            </div>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-[#11B9D4] hover:underline flex items-center gap-1 font-semibold"
            >
              <span>Interactive Swagger UI</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-[#E5EAF1] text-[#68758A]">
                  <th className="pb-3 font-semibold uppercase tracking-wider w-24">Method</th>
                  <th className="pb-3 font-semibold uppercase tracking-wider w-64">Route</th>
                  <th className="pb-3 font-semibold uppercase tracking-wider">Functional Description</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E5EAF1]">
                {apiEndpoints.map((ep) => (
                  <tr key={ep.path} className="hover:bg-[#F7F9FC]">
                    <td className="py-3">
                      <span className={`px-2 py-0.5 rounded font-mono font-bold text-[10px] ${
                        ep.method === "GET" 
                          ? "bg-[#10B981]/10 text-[#10B981]" 
                          : "bg-[#11B9D4]/10 text-[#11B9D4]"
                      }`}>
                        {ep.method}
                      </span>
                    </td>
                    <td className="py-3 font-mono font-bold text-[#15243A]">{ep.path}</td>
                    <td className="py-3 text-[#68758A] leading-relaxed">{ep.desc}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Section 4: Clinical Safety & Disclaimer */}
        <div className="clinical-card p-8 border-l-8 border-[#F59E0B] space-y-4">
          <div className="flex items-center gap-2 text-[#F59E0B] font-bold text-sm">
            <AlertTriangle className="w-4 h-4" />
            <span>Investigational & Regulatory Notice</span>
          </div>
          <h3 className="text-xl font-bold text-[#15243A]">
            Clinical Decision Support Disclaimer
          </h3>
          <div className="text-xs text-[#68758A] space-y-2 leading-relaxed">
            <p>
              NeuroScan XAI is an experimental research platform engineered to advance machine learning interpretability and explainability. It is not an FDA 510(k) cleared software as a medical device (SaMD) or CE marked in vitro diagnostic tool.
            </p>
            <p>
              Its predictions, Grad-CAM++ heatmaps, and entropy estimations must never be used as sole evidence for patient diagnosis, surgical planning, or biopsy withholding. All medical decisions must be made by licensed medical doctors and board-certified radiologists in clinical context.
            </p>
          </div>
        </div>

      </div>
    </div>
  );
}
