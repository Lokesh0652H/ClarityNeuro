"use client";

import Link from "next/link";
import { 
  Brain, 
  ShieldAlert, 
  ExternalLink, 
  ArrowUp, 
  Activity, 
  Sparkles, 
  BarChart3, 
  Scale, 
  Code2, 
  FileText,
  Database
} from "lucide-react";

export function Footer() {
  const scrollToTop = () => {
    if (typeof window !== "undefined") {
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  return (
    <footer className="bg-slate-50/90 border-t border-slate-200/80 mt-auto transition-colors text-slate-700">
      {/* 1. Clinical Research & Regulatory Advisory Header Bar */}
      <div className="bg-amber-500/10 border-b border-amber-200/50 py-3 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
          <div className="flex items-center gap-2 text-amber-900">
            <ShieldAlert className="w-4 h-4 text-amber-600 shrink-0" />
            <span>
              <strong className="font-semibold">Investigational & Research Use Only:</strong> ClarityNeuro is an academic interpretability research system. Saliency maps and classification outputs are for computational study and must not supersede licensed radiologist evaluation.
            </span>
          </div>
          <div className="flex items-center gap-2 self-start sm:self-auto shrink-0">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-100/80 text-emerald-800 border border-emerald-300/60">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
              PyTorch 2.1.3 Active
            </span>
            <span className="hidden md:inline text-[11px] text-slate-500 font-mono">
              EfficientNet-B0 (5.3M weights)
            </span>
          </div>
        </div>
      </div>

      {/* 2. Main Multi-Column Research Platform Footer */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 lg:gap-10">
          
          {/* Column 1 & 2: Platform Identity, Mission & Engine Specs (Spans 2 cols on lg) */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-600 via-indigo-600 to-violet-600 flex items-center justify-center text-white shadow-sm shadow-indigo-500/20">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <div className="flex items-baseline gap-2">
                <span className="font-serif font-bold text-xl tracking-tight text-slate-900">
                  ClarityNeuro
                </span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-100/70 text-indigo-700 border border-indigo-200">
                  XAI Platform
                </span>
              </div>
            </div>

            <p className="text-xs text-slate-600 leading-relaxed pr-4">
              Production-grade Explainable AI (XAI) and uncertainty estimation platform for multi-class brain MRI tumor analysis. Built on PyTorch EfficientNet-B0 with Grad-CAM++ gradient attribution, Monte Carlo Dropout predictive entropy, and subgroup fairness auditing.
            </p>

            {/* Verifiable Technical Badges */}
            <div className="flex flex-wrap gap-2 pt-1 text-[11px]">
              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-white border border-slate-200 text-slate-600 font-medium shadow-2xs">
                <Database className="w-3 h-3 text-indigo-500" />
                7,200 Scans (Kaggle Verified)
              </span>
              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-white border border-slate-200 text-slate-600 font-medium shadow-2xs">
                <Activity className="w-3 h-3 text-emerald-500" />
                96.48% Test Accuracy
              </span>
              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-white border border-slate-200 text-slate-600 font-medium shadow-2xs">
                <Scale className="w-3 h-3 text-amber-500" />
                0.9448 Disparate Impact
              </span>
            </div>
          </div>

          {/* Column 3: Diagnostic Modules */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900 mb-3.5 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
              Diagnostic Modules
            </h4>
            <ul className="space-y-2.5 text-xs">
              <li>
                <Link href="/analyze" className="text-slate-600 hover:text-indigo-600 transition-colors inline-flex items-center gap-1">
                  MRI Inference & Saliency
                </Link>
              </li>
              <li>
                <Link href="/dashboard" className="text-slate-600 hover:text-indigo-600 transition-colors inline-flex items-center gap-1">
                  Model Evaluation & ROC
                </Link>
              </li>
              <li>
                <Link href="/explainability" className="text-slate-600 hover:text-indigo-600 transition-colors inline-flex items-center gap-1">
                  Grad-CAM++ Visualizer
                </Link>
              </li>
              <li>
                <Link href="/analyze" className="text-slate-600 hover:text-indigo-600 transition-colors inline-flex items-center gap-1">
                  Predictive Shannon Entropy
                </Link>
              </li>
              <li>
                <Link href="/analyze" className="text-slate-600 hover:text-indigo-600 transition-colors inline-flex items-center gap-1">
                  Monte Carlo Dropout Variance
                </Link>
              </li>
            </ul>
          </div>

          {/* Column 4: Trust, Audits & Provenance */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900 mb-3.5 flex items-center gap-1.5">
              <Scale className="w-3.5 h-3.5 text-amber-600" />
              Trust & Audits
            </h4>
            <ul className="space-y-2.5 text-xs">
              <li>
                <Link href="/fairness" className="text-slate-600 hover:text-indigo-600 transition-colors inline-flex items-center gap-1">
                  Subgroup Fairness Audit
                </Link>
              </li>
              <li>
                <Link href="/shortcut-audit" className="text-slate-600 hover:text-indigo-600 transition-colors inline-flex items-center gap-1">
                  Contrast & Motion Stress Tests
                </Link>
              </li>
              <li>
                <Link href="/datasets" className="text-slate-600 hover:text-indigo-600 transition-colors inline-flex items-center gap-1">
                  Dataset Provenance (7,200 Scans)
                </Link>
              </li>
              <li>
                <Link href="/documentation" className="text-slate-600 hover:text-indigo-600 transition-colors inline-flex items-center gap-1">
                  Multi-Tier System Architecture
                </Link>
              </li>
              <li>
                <Link href="/fairness" className="text-slate-600 hover:text-indigo-600 transition-colors inline-flex items-center gap-1">
                  Zero-Synthetic Disparity Policy
                </Link>
              </li>
            </ul>
          </div>

          {/* Column 5: Technical Resources & API */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900 mb-3.5 flex items-center gap-1.5">
              <Code2 className="w-3.5 h-3.5 text-emerald-600" />
              API & Resources
            </h4>
            <ul className="space-y-2.5 text-xs">
              <li>
                <a 
                  href="http://127.0.0.1:8000/docs" 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="text-slate-600 hover:text-indigo-600 transition-colors inline-flex items-center gap-1"
                >
                  <span>FastAPI Swagger UI</span>
                  <ExternalLink className="w-3 h-3 text-slate-400" />
                </a>
              </li>
              <li>
                <a 
                  href="http://127.0.0.1:8000/redoc" 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="text-slate-600 hover:text-indigo-600 transition-colors inline-flex items-center gap-1"
                >
                  <span>Interactive ReDoc API</span>
                  <ExternalLink className="w-3 h-3 text-slate-400" />
                </a>
              </li>
              <li>
                <a 
                  href="https://github.com/Lokesh0652H/ClarityNeuro" 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="text-slate-600 hover:text-indigo-600 transition-colors inline-flex items-center gap-1"
                >
                  <span>GitHub Repository</span>
                  <ExternalLink className="w-3 h-3 text-slate-400" />
                </a>
              </li>
              <li>
                <Link href="/documentation" className="text-slate-600 hover:text-indigo-600 transition-colors inline-flex items-center gap-1">
                  Tensor Flow Specs [1, 3, 224, 224]
                </Link>
              </li>
              <li>
                <span className="text-slate-400 font-mono text-[11px]">
                  License: CC BY 4.0 / Open Source
                </span>
              </li>
            </ul>
          </div>

        </div>

        {/* 3. Bottom Legal, Version & Scroll-to-Top Bar */}
        <div className="border-t border-slate-200/80 pt-6 mt-10 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
          <div>
            © 2026 <strong className="font-semibold text-slate-700">ClarityNeuro</strong>. All rights reserved. Deterministic empirical neuroimaging AI research.
          </div>

          <div className="flex items-center gap-4">
            <span className="font-mono text-[11px] text-slate-400 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
              v1.0.0-rc2
            </span>

            <button
              onClick={scrollToTop}
              className="inline-flex items-center gap-1 text-slate-600 hover:text-indigo-600 font-medium transition-colors cursor-pointer group"
              title="Return to top of page"
            >
              <span>Back to top</span>
              <ArrowUp className="w-3.5 h-3.5 group-hover:-translate-y-0.5 transition-transform" />
            </button>
          </div>
        </div>
      </div>
    </footer>
  );
}