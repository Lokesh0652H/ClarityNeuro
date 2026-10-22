"use client";

import Link from "next/link";
import { Brain, ShieldCheck, Database, FileText, AlertTriangle, ExternalLink } from "lucide-react";

export function Footer() {
  return (
    <footer className="bg-[#FFFFFF] border-t border-[#E5EAF1] mt-auto">
      {/* Medical Responsibility Banner */}
      <div className="bg-[#F0F4F8] border-b border-[#E5EAF1] py-4 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto flex items-start sm:items-center gap-3 text-xs text-[#68758A]">
          <AlertTriangle className="w-5 h-5 text-[#F59E0B] shrink-0 mt-0.5 sm:mt-0" />
          <p>
            <strong className="text-[#15243A] font-semibold">Investigational & Research Use Only:</strong> NeuroScan XAI is designed exclusively for scientific evaluation, model interpretability, and educational research. It is not an FDA/CE cleared diagnostic device and should never replace qualified clinical radiological review.
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand Info */}
          <div className="md:col-span-1 space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#11B9D4] to-[#7867F5] flex items-center justify-center text-white">
                <Brain className="w-4 h-4" />
              </div>
              <span className="font-bold text-base text-[#15243A]">NeuroScan XAI</span>
            </div>
            <p className="text-xs text-[#68758A] leading-relaxed">
              Transparent, explainable brain tumor classification with genuine Grad-CAM++ attribution, Shannon entropy quantification, and rigorous shortcut auditing.
            </p>
            <div className="text-[11px] text-[#68758A] flex items-center gap-1.5 pt-1">
              <span className="w-2 h-2 rounded-full bg-[#10B981]"></span>
              <span>FastAPI Backend + PyTorch v2.13</span>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-[#15243A] mb-3">Capabilities</h4>
            <ul className="space-y-2 text-sm text-[#68758A]">
              <li>
                <Link href="/analyze" className="hover:text-[#11B9D4] transition-colors">
                  MRI Inference Workspace
                </Link>
              </li>
              <li>
                <Link href="/explainability" className="hover:text-[#11B9D4] transition-colors">
                  Grad-CAM++ Attribution
                </Link>
              </li>
              <li>
                <Link href="/dashboard" className="hover:text-[#11B9D4] transition-colors">
                  Benchmark Metrics & Confusion Matrix
                </Link>
              </li>
              <li>
                <Link href="/fairness" className="hover:text-[#11B9D4] transition-colors">
                  Demographic & Subgroup Parity
                </Link>
              </li>
            </ul>
          </div>

          {/* Trust & Transparency */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-[#15243A] mb-3">Trust & Audits</h4>
            <ul className="space-y-2 text-sm text-[#68758A]">
              <li>
                <Link href="/shortcut-audit" className="hover:text-[#11B9D4] transition-colors">
                  Shortcut Learning Audit
                </Link>
              </li>
              <li>
                <Link href="/datasets" className="hover:text-[#11B9D4] transition-colors">
                  Dataset Provenance (7,200 Scans)
                </Link>
              </li>
              <li>
                <Link href="/documentation" className="hover:text-[#11B9D4] transition-colors">
                  API Specification & Model Card
                </Link>
              </li>
              <li>
                <span className="text-[#68758A] text-xs">
                  Zero Synthetic/Mock Data Policy
                </span>
              </li>
            </ul>
          </div>

          {/* Provenance */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-[#15243A] mb-3">Provenance</h4>
            <p className="text-xs text-[#68758A] leading-relaxed mb-3">
              Dataset curated from Sartaj Bhuvaji et al. / Masoud Nickparvar Kaggle MRI benchmarks. 5,600 training & 1,600 testing verified scans across 4 balanced classes.
            </p>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#F0F4F8] text-[#15243A] text-xs font-medium border border-[#E5EAF1]">
              <Database className="w-3.5 h-3.5 text-[#11B9D4]" />
              <span>4 Classes | 7,200 Real Scans</span>
            </div>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-[#E5EAF1] flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-[#68758A]">
          <p>© 2026 NeuroScan XAI Platform. Built for scientific reproducibility.</p>
          <div className="flex items-center gap-4">
            <span className="text-[#10B981] font-medium flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-[#10B981]"></span>
              All Tests & Computations Genuine
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
}
