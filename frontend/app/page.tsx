"use client";

import Link from "next/link";
import { useState } from "react";
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
  Activity, 
  Layers, 
  ShieldAlert,
  Beaker,
  Lock,
  Cpu
} from "lucide-react";
import { BrainViewer } from "@/components/3d/BrainViewer";

export default function HomePage() {
  const [activeVisualMode, setActiveVisualMode] = useState<"neural" | "3d">("neural");

  // 4 Core Highlight Cards matching Image 1
  const highlightCards = [
    {
      title: "Explainable AI",
      subtitle: "Understand the model's reasoning",
      desc: "Pixel-level Grad-CAM++ attribution isolating cranial tumor margins.",
      icon: Sparkles,
      iconBg: "bg-purple-50/80 text-purple-600 border-purple-100",
      href: "/explainability"
    },
    {
      title: "4-Class Detection",
      subtitle: "Glioma, Meningioma, Pituitary, No Tumor",
      desc: "Trained on 7,200 real MRI scans across 4 balanced categories.",
      icon: Brain,
      iconBg: "bg-blue-50/80 text-blue-600 border-blue-100",
      href: "/analyze"
    },
    {
      title: "Reliable & Fair",
      subtitle: "Built for real-world transparency",
      desc: "Disparate Impact Ratio 0.9524 and imaging-condition robustness audits.",
      icon: Scale,
      iconBg: "bg-cyan-50/80 text-cyan-600 border-cyan-100",
      href: "/fairness"
    },
    {
      title: "Research Focused",
      subtitle: "Not a clinical diagnostic tool",
      desc: "Engineered strictly for algorithmic interpretability and open science.",
      icon: Beaker,
      iconBg: "bg-indigo-50/80 text-indigo-600 border-indigo-100",
      href: "/documentation"
    },
  ];

  // 6-Step Research Workflow matching Image 1
  const researchWorkflow = [
    { step: 1, title: "Dataset Acquisition", desc: "7,200 curated Kaggle scans" },
    { step: 2, title: "Preprocessing & Cleaning", desc: "Standardized 224×224 tensors" },
    { step: 3, title: "Model Training", desc: "EfficientNet-B0 transfer learning" },
    { step: 4, title: "MRI Inference", desc: "Forward pass & softmax output" },
    { step: 5, title: "Explainability & Audit", desc: "Grad-CAM++ & subgroup tests" },
    { step: 6, title: "Evaluation & Reporting", desc: "82.75% test accuracy verification" },
  ];

  const tumorClasses = [
    {
      name: "Glioma",
      description: "Infiltrative neuroepithelial tumors originating in glial cells with irregular contrast margins.",
      count: "1,800 Scans",
      badge: "Class 0",
      accent: "border-cyan-500",
      color: "text-cyan-600",
    },
    {
      name: "Meningioma",
      description: "Typically benign extra-axial tumors arising from the arachnoid layer of the meninges.",
      count: "1,800 Scans",
      badge: "Class 1",
      accent: "border-indigo-500",
      color: "text-indigo-600",
    },
    {
      name: "Pituitary Adenoma",
      description: "Sellar neoplasms expanding within the sella turcica with chiasmatic mass effect.",
      count: "1,800 Scans",
      badge: "Class 2",
      accent: "border-blue-500",
      color: "text-blue-600",
    },
    {
      name: "Normal / No Tumor",
      description: "Control intracranial scans exhibiting intact ventricular symmetry and healthy parenchyma.",
      count: "1,800 Scans",
      badge: "Class 3",
      accent: "border-emerald-500",
      color: "text-emerald-600",
    },
  ];

  return (
    <div className="flex flex-col min-h-screen text-[#0F172A]">
      
      {/* Hero Section matching Image 1 & Image 2 */}
      <section className="relative overflow-hidden pt-12 pb-16 lg:pt-16 lg:pb-24 border-b border-slate-200/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            
            {/* Left Column: Editorial Headline & Actions */}
            <div className="lg:col-span-7 space-y-6 text-left">
              
              {/* Pill badge matching Image 2 */}
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/95 border border-slate-200/80 shadow-xs text-xs font-medium text-slate-700 backdrop-blur-xs">
                <span className="text-indigo-600">✦</span>
                <span>Research build · EfficientNet-B0 · Grad-CAM++ · Model ethics</span>
              </div>

              {/* Large Editorial Serif Headline */}
              <h1 className="font-serif text-5xl sm:text-6xl lg:text-[68px] font-bold tracking-tight text-[#0F172A] leading-[1.12]">
                Seeing how a model <br />
                <span className="italic font-normal bg-gradient-to-r from-blue-600 via-indigo-600 to-violet-600 bg-clip-text text-transparent">
                  sees
                </span>{" "}
                a brain.
              </h1>

              {/* Precise Subtitle */}
              <p className="text-base sm:text-lg text-slate-600 max-w-2xl leading-relaxed">
                ClarityNeuro is a research platform for brain MRI tumor analysis — real EfficientNet-B0 inference, Grad-CAM++ explainability, uncertainty quantification, and honest fairness & shortcut-learning audits.
              </p>

              {/* Action Buttons matching Image 1 & Image 2 */}
              <div className="flex flex-wrap items-center gap-3.5 pt-2">
                <Link
                  href="/analyze"
                  className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-[#0F172A] hover:bg-slate-800 text-white font-medium text-sm shadow-md hover:shadow-lg hover:-translate-y-0.5 transition-all cursor-pointer"
                >
                  <Brain className="w-4 h-4" />
                  <span>Analyze MRI</span>
                  <ArrowRight className="w-4 h-4 ml-0.5" />
                </Link>

                <Link
                  href="/fairness"
                  className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-white/90 backdrop-blur-xs border border-slate-200/90 hover:bg-white text-slate-800 font-medium text-sm shadow-xs hover:shadow-sm transition-all"
                >
                  <ShieldCheck className="w-4 h-4 text-indigo-600" />
                  <span>Explore Model Ethics</span>
                </Link>

                <Link
                  href="/documentation"
                  className="inline-flex items-center gap-1.5 px-4 py-3 text-xs font-semibold text-slate-500 hover:text-indigo-600 transition-colors"
                >
                  <span>Read Paper & Docs</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>

              {/* Quick Provenance Counters */}
              <div className="pt-6 grid grid-cols-3 gap-6 border-t border-slate-200/70 max-w-md">
                <div>
                  <div className="text-2xl font-bold font-serif text-slate-900">7,200</div>
                  <div className="text-[11px] text-slate-500 font-medium">Curated MRI Scans</div>
                </div>
                <div>
                  <div className="text-2xl font-bold font-serif text-slate-900">82.75%</div>
                  <div className="text-[11px] text-slate-500 font-medium">Test Set Accuracy</div>
                </div>
                <div>
                  <div className="text-2xl font-bold font-serif text-indigo-600">Grad-CAM++</div>
                  <div className="text-[11px] text-slate-500 font-medium">Pixel Attribution</div>
                </div>
              </div>

            </div>

            {/* Right Column: Radiant Glowing Brain Visual matching Image 1 */}
            <div className="lg:col-span-5 flex flex-col items-center justify-center relative">
              
              {/* Visual Mode Selector (Neural Orb vs 3D Interactive) */}
              <div className="absolute top-0 right-4 z-20 flex items-center bg-white/95 backdrop-blur-xs border border-slate-200/80 rounded-full p-1 shadow-xs text-[11px] font-medium text-slate-600">
                <button
                  onClick={() => setActiveVisualMode("neural")}
                  className={`px-3 py-1 rounded-full transition-all cursor-pointer ${
                    activeVisualMode === "neural" ? "bg-indigo-50 text-indigo-600 font-semibold" : "hover:text-slate-900"
                  }`}
                >
                  Neural Glow
                </button>
                <button
                  onClick={() => setActiveVisualMode("3d")}
                  className={`px-3 py-1 rounded-full transition-all cursor-pointer ${
                    activeVisualMode === "3d" ? "bg-indigo-50 text-indigo-600 font-semibold" : "hover:text-slate-900"
                  }`}
                >
                  3D Canvas
                </button>
              </div>

              {activeVisualMode === "neural" ? (
                <div className="relative w-full max-w-[420px] aspect-square flex items-center justify-center pt-8">
                  {/* Glowing Concentric Halo Rings */}
                  <div className="absolute w-[360px] h-[360px] rounded-full bg-gradient-to-tr from-blue-400/15 via-indigo-500/20 to-purple-400/15 blur-2xl animate-soft-pulse pointer-events-none"></div>
                  
                  <div className="relative w-[340px] h-[340px] rounded-full border border-indigo-100 bg-white/80 backdrop-blur-md shadow-[0_8px_32px_rgba(79,70,229,0.08)] flex items-center justify-center p-6 group">
                    
                    {/* Concentric subtle circular rings */}
                    <div className="absolute inset-4 rounded-full border border-dashed border-indigo-200/50 animate-[spin_60s_linear_infinite]"></div>
                    <div className="absolute inset-10 rounded-full border border-indigo-100/70"></div>
                    <div className="absolute inset-16 rounded-full border border-dashed border-purple-200/40 animate-[spin_40s_linear_infinite_reverse]"></div>

                    {/* SVG Brain Neural Graphic */}
                    <svg viewBox="0 0 200 200" className="w-56 h-56 text-indigo-600 drop-shadow-[0_4px_16px_rgba(79,70,229,0.25)]">
                      <defs>
                        <linearGradient id="brainGlow" x1="0%" y1="0%" x2="100%" y2="100%">
                          <stop offset="0%" stopColor="#2563EB" />
                          <stop offset="50%" stopColor="#4F46E5" />
                          <stop offset="100%" stopColor="#7C3AED" />
                        </linearGradient>
                      </defs>
                      {/* Stylized Cranial Contours */}
                      <path
                        d="M 100 25 C 135 25 165 50 165 90 C 165 125 145 155 120 168 C 115 170 108 175 105 180 L 95 180 C 92 175 85 170 80 168 C 55 155 35 125 35 90 C 35 50 65 25 100 25 Z"
                        fill="none"
                        stroke="url(#brainGlow)"
                        strokeWidth="2.5"
                        strokeDasharray="4 2"
                      />
                      {/* Cortical Gyri Foldings */}
                      <path
                        d="M 65 75 Q 85 55 100 75 T 135 75 Q 145 100 130 115 T 100 110 T 70 115 Q 55 95 65 75"
                        fill="none"
                        stroke="url(#brainGlow)"
                        strokeWidth="2"
                        opacity="0.85"
                      />
                      <path
                        d="M 80 90 Q 100 95 110 85 T 120 105 T 100 130 T 80 120 Z"
                        fill="none"
                        stroke="url(#brainGlow)"
                        strokeWidth="1.8"
                        opacity="0.7"
                      />
                      {/* Neural Nodes / Synapses */}
                      <circle cx="100" cy="50" r="3.5" fill="#4F46E5" className="animate-pulse" />
                      <circle cx="130" cy="80" r="3" fill="#2563EB" />
                      <circle cx="70" cy="80" r="3" fill="#7C3AED" />
                      <circle cx="120" cy="115" r="3.5" fill="#06B6D4" />
                      <circle cx="80" cy="115" r="3" fill="#4F46E5" />
                      <circle cx="100" cy="140" r="3.5" fill="#2563EB" />
                    </svg>

                    {/* Handwritten/Italic Floating Annotation matching Image 1 */}
                    <div className="absolute bottom-6 right-2 text-right">
                      <span className="font-serif italic text-xs text-indigo-700 font-medium tracking-tight block">
                        Better insights.
                      </span>
                      <span className="font-serif italic text-xs text-violet-700 font-medium tracking-tight block">
                        Greater clarity.
                      </span>
                    </div>

                  </div>
                </div>
              ) : (
                <div className="w-full max-w-[420px] aspect-square flex items-center justify-center pt-8">
                  <BrainViewer />
                </div>
              )}

            </div>

          </div>

        </div>
      </section>

      {/* 4 Feature Highlight Cards matching Image 1 */}
      <section className="py-12 border-b border-slate-200/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {highlightCards.map((card) => {
              const Icon = card.icon;
              return (
                <Link
                  key={card.title}
                  href={card.href}
                  className="clean-card p-6 flex flex-col justify-between group cursor-pointer"
                >
                  <div className="space-y-3">
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center border ${card.iconBg}`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="font-bold text-sm text-[#0F172A] group-hover:text-indigo-600 transition-colors">
                        {card.title}
                      </h3>
                      <p className="text-xs text-slate-500 font-medium mt-0.5">
                        {card.subtitle}
                      </p>
                    </div>
                    <p className="text-[11px] text-slate-400 leading-relaxed">
                      {card.desc}
                    </p>
                  </div>
                  <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs font-semibold text-indigo-600 group-hover:translate-x-0.5 transition-transform">
                    <span>Explore</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      {/* The Research Workflow (6-step timeline) matching Image 1 */}
      <section className="py-16 border-b border-slate-200/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="font-serif text-2xl sm:text-3xl font-bold text-[#0F172A] tracking-tight">
              The Research Workflow
            </h2>
            <p className="text-xs sm:text-sm text-slate-500 mt-1.5">
              From data to transparency. Every step matters.
            </p>
          </div>

          <div className="relative">
            {/* Horizontal Timeline Connector Bar on desktop */}
            <div className="hidden lg:block absolute top-7 left-12 right-12 h-0.5 bg-slate-200/80 -z-0"></div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 relative z-10">
              {researchWorkflow.map((item) => (
                <div 
                  key={item.step} 
                  className="clean-card-flat p-4 text-center hover:shadow-sm transition-all"
                >
                  <div className="w-9 h-9 mx-auto rounded-full bg-indigo-50 border-2 border-white shadow-xs text-indigo-600 font-bold text-xs flex items-center justify-center mb-3">
                    {item.step}
                  </div>
                  <h4 className="text-xs font-bold text-slate-800 leading-tight">
                    {item.title}
                  </h4>
                  <p className="text-[11px] text-slate-400 mt-1">
                    {item.desc}
                  </p>
                </div>
              ))}
            </div>
          </div>

        </div>
      </section>

      {/* 4 Diagnostic Classes Grid */}
      <section className="py-16 border-b border-slate-200/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-10 gap-4">
            <div>
              <span className="text-[11px] font-bold tracking-wider uppercase text-indigo-600">
                Diagnostic Coverage
              </span>
              <h2 className="font-serif text-2xl sm:text-3xl font-bold text-[#0F172A] mt-1">
                Pathological & Control Classes
              </h2>
            </div>
            <span className="text-xs text-slate-500 font-medium">
              1,800 Scans per Category · 7,200 Scans Total
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {tumorClasses.map((cls) => (
              <div
                key={cls.name}
                className={`clean-card p-6 border-t-4 ${cls.accent} flex flex-col justify-between`}
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
                      {cls.badge}
                    </span>
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                  </div>
                  <h3 className="font-bold text-base text-slate-900 mb-1.5">
                    {cls.name}
                  </h3>
                  <p className="text-xs text-slate-500 leading-relaxed">
                    {cls.description}
                  </p>
                </div>
                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] font-semibold text-slate-600">
                  <span className={cls.color}>{cls.count}</span>
                  <span className="text-slate-400">100% Provenance</span>
                </div>
              </div>
            ))}
          </div>

        </div>
      </section>

      {/* Scientific Transparency Callout */}
      <section className="py-16">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-6">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-50/90 border border-indigo-100 text-indigo-700 text-xs font-semibold backdrop-blur-xs">
            <Database className="w-3.5 h-3.5" />
            <span>Zero Synthetic Data Policy</span>
          </div>

          <h2 className="font-serif text-3xl sm:text-4xl font-bold text-[#0F172A]">
            Trained and Evaluated on Real Scans
          </h2>
          
          <p className="text-sm text-slate-600 max-w-2xl mx-auto leading-relaxed">
            All accuracy figures, ROC-AUC measurements (0.9561), and Grad-CAM++ feature heatmaps are generated through live PyTorch computations on verified human brain MRI cohorts.
          </p>

          <div className="pt-2 flex flex-wrap justify-center gap-4">
            <Link
              href="/analyze"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-[#0F172A] hover:bg-slate-800 text-white font-medium text-sm shadow-sm hover:shadow-md transition-all cursor-pointer"
            >
              <Brain className="w-4 h-4" />
              <span>Launch Analysis Workspace</span>
            </Link>

            <Link
              href="/datasets"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-white/90 backdrop-blur-xs border border-slate-200 text-slate-700 hover:bg-white font-medium text-sm transition-all shadow-xs"
            >
              <Database className="w-4 h-4 text-indigo-600" />
              <span>Inspect Dataset Transparency</span>
            </Link>
          </div>
        </div>
      </section>

    </div>
  );
}
