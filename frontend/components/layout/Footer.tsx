"use client";

import Link from "next/link";
import { Brain, ShieldAlert } from "lucide-react";

export function Footer() {
  return (
    <footer className="bg-white border-t border-slate-100 mt-auto">
      {/* Research & Clinical Disclaimer */}
      <div className="bg-slate-50/60 border-b border-slate-100 py-3 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto flex items-center justify-between text-xs text-slate-500">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-3.5 h-3.5 text-amber-500 shrink-0" />
            <span>
              <strong>Research & Educational Tool:</strong> NeuroScan XAI is designed for interpretability research and educational evaluation, not as a standalone medical diagnostic device.
            </span>
          </div>
          <span className="hidden sm:inline text-[11px] text-emerald-600 font-medium bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-100">
            Real PyTorch Computations Only
          </span>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-6">
          {/* Logo & Tagline */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-600 via-indigo-600 to-violet-600 flex items-center justify-center text-white shadow-xs">
              <Brain className="w-4 h-4 text-white" />
            </div>
            <div>
              <span className="font-serif font-bold text-base text-slate-900 tracking-tight">
                ClarityNeuro
              </span>
              <p className="text-[11px] text-slate-400">
                Explainable Brain MRI Intelligence
              </p>
            </div>
          </div>

          {/* Clean Navigation Links matching image */}
          <nav className="flex items-center gap-6 text-xs font-medium text-slate-500">
            <Link href="/" className="hover:text-indigo-600 transition-colors">
              Home
            </Link>
            <Link href="/analyze" className="hover:text-indigo-600 transition-colors">
              Analyze
            </Link>
            <Link href="/dashboard" className="hover:text-indigo-600 transition-colors">
              Insights
            </Link>
            <Link href="/datasets" className="hover:text-indigo-600 transition-colors">
              Dataset
            </Link>
            <Link href="/documentation" className="hover:text-indigo-600 transition-colors">
              About
            </Link>
          </nav>

          {/* Copyright */}
          <div className="text-xs text-slate-400">
            © 2026 ClarityNeuro. All rights reserved.
          </div>
        </div>
      </div>
    </footer>
  );
}
