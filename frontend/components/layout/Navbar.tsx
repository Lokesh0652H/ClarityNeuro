"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { 
  Brain, 
  Sparkles, 
  BarChart3, 
  Scale, 
  ShieldAlert, 
  Database, 
  BookOpen, 
  Menu, 
  X,
  Sun,
  ChevronDown
} from "lucide-react";

export function Navbar() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [insightsDropdownOpen, setInsightsDropdownOpen] = useState(false);

  const isInsightsActive = 
    pathname === "/dashboard" || 
    pathname === "/fairness" || 
    pathname === "/shortcut-audit" || 
    pathname === "/explainability";

  return (
    <header className="sticky top-0 z-50 bg-[#FFFFFF]/90 backdrop-blur-md border-b border-[#E8EEF5]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Brand Logo matching the reference image */}
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-600 via-indigo-600 to-violet-600 flex items-center justify-center text-white shadow-sm shadow-indigo-500/20 group-hover:scale-105 transition-all">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <div className="flex items-baseline gap-1.5">
              <span className="font-serif font-bold text-xl tracking-tight text-[#0F172A]">
                ClarityNeuro
              </span>
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-indigo-50 text-indigo-600 border border-indigo-100">
                XAI
              </span>
            </div>
          </Link>

          {/* Center Navigation Links: Home, Analyze, Insights, Dataset, About */}
          <nav className="hidden md:flex items-center gap-1 text-sm font-medium">
            <Link
              href="/"
              className={`px-3 py-1.5 rounded-full transition-all ${
                pathname === "/"
                  ? "text-indigo-600 font-semibold bg-indigo-50/70"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
              }`}
            >
              Home
            </Link>

            <Link
              href="/analyze"
              className={`px-3 py-1.5 rounded-full transition-all ${
                pathname === "/analyze"
                  ? "text-indigo-600 font-semibold bg-indigo-50/70"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
              }`}
            >
              Analyze
            </Link>

            {/* Insights Dropdown */}
            <div className="relative">
              <button
                onClick={() => setInsightsDropdownOpen(!insightsDropdownOpen)}
                onBlur={() => setTimeout(() => setInsightsDropdownOpen(false), 200)}
                className={`flex items-center gap-1 px-3 py-1.5 rounded-full transition-all cursor-pointer ${
                  isInsightsActive
                    ? "text-indigo-600 font-semibold bg-indigo-50/70"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                }`}
              >
                <span>Insights</span>
                <ChevronDown className="w-3.5 h-3.5 opacity-70" />
              </button>

              {insightsDropdownOpen && (
                <div className="absolute top-full left-0 mt-1 w-56 bg-white rounded-2xl border border-slate-100 shadow-xl p-2 z-50 animate-in fade-in slide-in-from-top-2">
                  <Link
                    href="/dashboard"
                    className="flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-medium text-slate-700 hover:text-indigo-600 hover:bg-indigo-50/50 transition-colors"
                  >
                    <BarChart3 className="w-4 h-4 text-blue-500" />
                    <div>
                      <div className="font-semibold">Model Evaluation</div>
                      <div className="text-[10px] text-slate-400">Confusion matrix & ROC</div>
                    </div>
                  </Link>

                  <Link
                    href="/explainability"
                    className="flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-medium text-slate-700 hover:text-indigo-600 hover:bg-indigo-50/50 transition-colors"
                  >
                    <Sparkles className="w-4 h-4 text-violet-500" />
                    <div>
                      <div className="font-semibold">Grad-CAM++</div>
                      <div className="text-[10px] text-slate-400">Gradient saliency maps</div>
                    </div>
                  </Link>

                  <Link
                    href="/fairness"
                    className="flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-medium text-slate-700 hover:text-indigo-600 hover:bg-indigo-50/50 transition-colors"
                  >
                    <Scale className="w-4 h-4 text-amber-500" />
                    <div>
                      <div className="font-semibold">Fairness Audit</div>
                      <div className="text-[10px] text-slate-400">Subgroup disparity</div>
                    </div>
                  </Link>

                  <Link
                    href="/shortcut-audit"
                    className="flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-medium text-slate-700 hover:text-indigo-600 hover:bg-indigo-50/50 transition-colors"
                  >
                    <ShieldAlert className="w-4 h-4 text-rose-500" />
                    <div>
                      <div className="font-semibold">Shortcut Audit</div>
                      <div className="text-[10px] text-slate-400">Scanner artifact tests</div>
                    </div>
                  </Link>
                </div>
              )}
            </div>

            <Link
              href="/datasets"
              className={`px-3 py-1.5 rounded-full transition-all ${
                pathname === "/datasets"
                  ? "text-indigo-600 font-semibold bg-indigo-50/70"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
              }`}
            >
              Dataset
            </Link>

            <Link
              href="/documentation"
              className={`px-3 py-1.5 rounded-full transition-all ${
                pathname === "/documentation"
                  ? "text-indigo-600 font-semibold bg-indigo-50/70"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
              }`}
            >
              About
            </Link>
          </nav>

          {/* Right Action Icons: Light Theme Sun Icon + Status + CTA */}
          <div className="hidden md:flex items-center gap-3">
            {/* Light Theme Indicator Pill */}
            <div 
              title="Light theme active"
              className="w-8 h-8 rounded-full bg-slate-50 border border-slate-200/80 flex items-center justify-center text-slate-600 hover:text-indigo-600 transition-colors"
            >
              <Sun className="w-4 h-4 text-amber-500" />
            </div>

            {/* User / Clinician Avatar Badge */}
            <div 
              title="Researcher Profile"
              className="w-8 h-8 rounded-full bg-slate-900 text-white font-semibold text-xs flex items-center justify-center shadow-xs"
            >
              L
            </div>

            {/* Quick Action Button */}
            <Link
              href="/analyze"
              className="px-4 py-2 rounded-full bg-[#0F172A] hover:bg-slate-800 text-white text-xs font-semibold shadow-xs hover:shadow-md transition-all cursor-pointer"
            >
              Analyze MRI
            </Link>
          </div>

          {/* Mobile menu trigger */}
          <div className="md:hidden flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-slate-900 text-white font-semibold text-xs flex items-center justify-center">
              L
            </div>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100"
              aria-label="Toggle navigation"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>

        </div>
      </div>

      {/* Mobile Menu Panel */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-white border-b border-slate-200 px-4 pt-3 pb-6 space-y-2 animate-in fade-in">
          <Link
            href="/"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            Home
          </Link>
          <Link
            href="/analyze"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-lg text-sm font-semibold text-indigo-600 bg-indigo-50/50"
          >
            Analyze MRI
          </Link>
          <Link
            href="/dashboard"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            Insights & Evaluation
          </Link>
          <Link
            href="/explainability"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            Grad-CAM++ Explainability
          </Link>
          <Link
            href="/fairness"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            Fairness Audit
          </Link>
          <Link
            href="/shortcut-audit"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            Shortcut Audit
          </Link>
          <Link
            href="/datasets"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            Dataset & Transparency
          </Link>
          <Link
            href="/documentation"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            About & Documentation
          </Link>
        </div>
      )}
    </header>
  );
}
