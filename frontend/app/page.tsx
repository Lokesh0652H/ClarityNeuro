"use client";

import Link from "next/link";
import { 
  Brain, 
  Sparkles, 
  ShieldCheck, 
  BarChart3, 
  Scale, 
  Database, 
  ArrowRight, 
  CheckCircle2, 
  Eye, 
  Cpu, 
  Activity, 
  Layers, 
  AlertCircle
} from "lucide-react";
import { BrainViewer } from "@/components/3d/BrainViewer";

export default function HomePage() {
  const capabilities = [
    {
      title: "Real Grad-CAM++ Attribution",
      description: "Visualizes pixel-level saliency maps highlighting exactly which intracranial anatomical regions governed the network's prediction.",
      icon: Sparkles,
      color: "from-[#11B9D4] to-[#0ea5e9]",
      link: "/explainability",
    },
    {
      title: "Shannon Entropy Quantification",
      description: "Rigorous measurement of prediction dispersion H(p) and Monte Carlo Dropout to identify out-of-distribution or ambiguous scans.",
      icon: Activity,
      color: "from-[#7867F5] to-[#6366f1]",
      link: "/analyze",
    },
    {
      title: "Adversarial Shortcut Auditing",
      description: "Automated vulnerability tests that assess whether the model relies on spurious cues like scanner text, corner markers, or contrast shifts.",
      icon: ShieldCheck,
      color: "from-[#10B981] to-[#059669]",
      link: "/shortcut-audit",
    },
    {
      title: "Subgroup Disparity Analysis",
      description: "Audits performance across MRI acquisition contrast sequences and scanner resolution tiers to detect unequal predictive utility.",
      icon: Scale,
      color: "from-[#F59E0B] to-[#d97706]",
      link: "/fairness",
    },
  ];

  const workflowSteps = [
    {
      step: "01",
      title: "Standardized Normalization",
      description: "Input axial, sagittal, or coronal T1/T2 MRI images are converted to 3-channel tensors and normalized with verified ImageNet statistics.",
    },
    {
      step: "02",
      title: "EfficientNet-B0 Inference",
      description: "Compound-scaled inverted bottleneck MBConv blocks extract multiscale spatial feature representations without overfitting.",
    },
    {
      step: "03",
      title: "Grad-CAM++ Gradient Computation",
      description: "Higher-order partial derivatives weight the final convolutional activation maps, isolating tumor margins.",
    },
    {
      step: "04",
      title: "Uncertainty & Audit Verification",
      description: "Shannon entropy scores and spurious perturbation checks validate decision reliability before presenting results to clinicians.",
    },
  ];

  const tumorClasses = [
    {
      name: "Glioma",
      description: "Infiltrative neuroepithelial tumors originating in glial cells, characterized by heterogeneous contrast enhancement.",
      badge: "Class 0",
      accent: "border-[#11B9D4]",
    },
    {
      name: "Meningioma",
      description: "Typically benign extra-axial tumors arising from the arachnoid layer of the meninges with dural tail signs.",
      badge: "Class 1",
      accent: "border-[#7867F5]",
    },
    {
      name: "Pituitary Adenoma",
      description: "Sellar/suprasellar neoplasms expanding within the sella turcica, often causing chiasmatic compression.",
      badge: "Class 2",
      accent: "border-[#3B82F6]",
    },
    {
      name: "Normal / No Tumor",
      description: "Control intracranial scans exhibiting intact ventricular symmetry and normal brain parenchyma without mass effect.",
      badge: "Class 3",
      accent: "border-[#10B981]",
    },
  ];

  return (
    <div className="flex flex-col min-h-screen bg-[#F7F9FC]">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-20 border-b border-[#E5EAF1] bg-gradient-to-b from-[#FFFFFF] via-[#F7F9FC] to-[#F7F9FC]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            
            {/* Left Column: Headline and CTAs */}
            <div className="lg:col-span-7 space-y-6 text-left">
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#11B9D4]/10 border border-[#11B9D4]/20 text-[#11B9D4] text-xs font-semibold">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Explainable AI & Uncertainty Intelligence</span>
              </div>

              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-[#15243A] tracking-tight leading-[1.15]">
                See Beyond <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#11B9D4] to-[#7867F5]">
                  the Scan.
                </span>
              </h1>

              <p className="text-lg text-[#68758A] max-w-2xl leading-relaxed">
                Explainable brain MRI analysis engineered to transform black-box deep neural networks into transparent, clinically interpretable diagnostic partners.
              </p>

              {/* CTAs */}
              <div className="flex flex-wrap items-center gap-4 pt-2">
                <Link
                  href="/analyze"
                  className="inline-flex items-center gap-2.5 px-6 py-3.5 rounded-xl bg-gradient-to-r from-[#11B9D4] to-[#7867F5] text-white font-semibold text-base shadow-sm hover:shadow-md hover:scale-[1.01] transition-all"
                >
                  <Brain className="w-5 h-5" />
                  Analyze Brain MRI
                  <ArrowRight className="w-4 h-4 ml-1" />
                </Link>

                <Link
                  href="/explainability"
                  className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl bg-[#FFFFFF] border border-[#E5EAF1] text-[#15243A] font-semibold text-base hover:bg-[#F0F4F8] transition-colors"
                >
                  <Eye className="w-5 h-5 text-[#7867F5]" />
                  Explore Technology
                </Link>
              </div>

              {/* Verified Trust Badges */}
              <div className="pt-6 grid grid-cols-3 gap-4 border-t border-[#E5EAF1] max-w-lg">
                <div>
                  <div className="text-2xl font-bold text-[#15243A]">7,200</div>
                  <div className="text-xs text-[#68758A] font-medium">Verified MRI Scans</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-[#15243A]">4 Classes</div>
                  <div className="text-xs text-[#68758A] font-medium">Balanced Distribution</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-[#10B981]">Grad-CAM++</div>
                  <div className="text-xs text-[#68758A] font-medium">Real Gradient XAI</div>
                </div>
              </div>
            </div>

            {/* Right Column: 3D Brain Viewer */}
            <div className="lg:col-span-5 flex justify-center">
              <BrainViewer />
            </div>

          </div>
        </div>
      </section>

      {/* 4 Supported Classes Section */}
      <section className="py-16 bg-[#FFFFFF] border-b border-[#E5EAF1]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-12">
            <h2 className="text-xs font-bold uppercase tracking-wider text-[#11B9D4] mb-2">Diagnostic Coverage</h2>
            <h3 className="text-3xl font-bold text-[#15243A] tracking-tight">
              Four Pathological & Control Categories
            </h3>
            <p className="text-sm text-[#68758A] mt-2">
              Trained on balanced, publicly curated brain MRI datasets with verified class provenance.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {tumorClasses.map((cls) => (
              <div
                key={cls.name}
                className={`clinical-card p-6 border-l-4 ${cls.accent} flex flex-col justify-between`}
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs font-semibold px-2 py-0.5 rounded bg-[#F0F4F8] text-[#68758A]">
                      {cls.badge}
                    </span>
                    <CheckCircle2 className="w-4 h-4 text-[#10B981]" />
                  </div>
                  <h4 className="text-lg font-bold text-[#15243A] mb-2">{cls.name}</h4>
                  <p className="text-xs text-[#68758A] leading-relaxed">{cls.description}</p>
                </div>
                <div className="mt-4 pt-3 border-t border-[#E5EAF1] flex items-center justify-between text-xs font-medium text-[#11B9D4]">
                  <span>1,800 Verified Scans</span>
                  <span>100% Provenance</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Core Capabilities Section */}
      <section className="py-20 bg-[#F7F9FC] border-b border-[#E5EAF1]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs font-bold uppercase tracking-wider text-[#7867F5] mb-2">Scientific Transparency</h2>
            <h3 className="text-3xl font-bold text-[#15243A] tracking-tight">
              Beyond Black-Box Classification
            </h3>
            <p className="text-sm text-[#68758A] mt-2">
              Every inference provides verified attribution maps, entropy-calibrated confidence, and algorithmic safety audits.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {capabilities.map((cap) => {
              const Icon = cap.icon;
              return (
                <Link
                  key={cap.title}
                  href={cap.link}
                  className="clinical-card p-8 group flex flex-col justify-between hover:border-[#11B9D4]/40"
                >
                  <div className="space-y-4">
                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${cap.color} flex items-center justify-center text-white shadow-sm group-hover:scale-105 transition-transform`}>
                      <Icon className="w-6 h-6" />
                    </div>
                    <h4 className="text-xl font-bold text-[#15243A] group-hover:text-[#11B9D4] transition-colors">
                      {cap.title}
                    </h4>
                    <p className="text-sm text-[#68758A] leading-relaxed">
                      {cap.description}
                    </p>
                  </div>
                  <div className="mt-6 flex items-center gap-2 text-sm font-semibold text-[#11B9D4] group-hover:translate-x-1 transition-transform">
                    <span>Inspect Methodology</span>
                    <ArrowRight className="w-4 h-4" />
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      {/* Research Workflow Section */}
      <section className="py-20 bg-[#FFFFFF] border-b border-[#E5EAF1]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs font-bold uppercase tracking-wider text-[#11B9D4] mb-2">Execution Pipeline</h2>
            <h3 className="text-3xl font-bold text-[#15243A] tracking-tight">
              Clinical Inference Workflow
            </h3>
            <p className="text-sm text-[#68758A] mt-2">
              From raw DICOM/PNG/JPEG intake to verifiable explainable attribution in milliseconds.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {workflowSteps.map((step) => (
              <div key={step.step} className="p-6 rounded-xl bg-[#F7F9FC] border border-[#E5EAF1]">
                <div className="text-2xl font-black text-[#11B9D4] mb-3">{step.step}</div>
                <h4 className="text-base font-bold text-[#15243A] mb-2">{step.title}</h4>
                <p className="text-xs text-[#68758A] leading-relaxed">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Real Data Provenance Callout */}
      <section className="py-16 bg-gradient-to-r from-[#11B9D4]/10 via-[#7867F5]/5 to-[#F7F9FC] border-b border-[#E5EAF1]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-8">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Database className="w-5 h-5 text-[#11B9D4]" />
              <span className="text-xs font-bold uppercase tracking-wider text-[#11B9D4]">
                100% Genuine Clinical Provenance
              </span>
            </div>
            <h3 className="text-2xl font-bold text-[#15243A]">
              Curated from 7,200 Real Human Brain MRI Scans
            </h3>
            <p className="text-sm text-[#68758A] max-w-2xl">
              NeuroScan XAI enforces strict zero synthetic or mock data policies. All validation metrics, ROC curves, confusion matrices, and Grad-CAM maps derive from actual PyTorch tensor computations on verified data.
            </p>
          </div>
          <Link
            href="/datasets"
            className="shrink-0 px-5 py-3 rounded-xl bg-[#FFFFFF] border border-[#E5EAF1] text-[#15243A] font-semibold text-sm hover:bg-[#F0F4F8] shadow-sm transition-colors"
          >
            Review Dataset Manifest
          </Link>
        </div>
      </section>

      {/* CTA Banner */}
      <section className="py-16 bg-[#FFFFFF]">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-6">
          <h3 className="text-3xl font-bold text-[#15243A]">
            Ready to Analyze a Brain MRI Scan?
          </h3>
          <p className="text-sm text-[#68758A] max-w-xl mx-auto leading-relaxed">
            Upload an intracranial MRI image or test immediately with our pre-indexed benchmark scans to see live Grad-CAM++ heatmaps and entropy scores.
          </p>
          <div className="pt-2">
            <Link
              href="/analyze"
              className="inline-flex items-center gap-2 px-8 py-4 rounded-xl bg-gradient-to-r from-[#11B9D4] to-[#7867F5] text-white font-semibold text-base shadow-md hover:shadow-lg transition-all"
            >
              <Brain className="w-5 h-5" />
              Launch MRI Analysis Workspace
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
