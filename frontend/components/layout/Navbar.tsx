"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect, useRef } from "react";
import { 
  Brain, 
  Sparkles, 
  BarChart3, 
  Scale, 
  ShieldAlert, 
  Menu, 
  X,
  ChevronDown
} from "lucide-react";

export function Navbar() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [insightsDropdownOpen, setInsightsDropdownOpen] = useState(false);

  const dropdownRef = useRef<HTMLDivElement>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Ensure clean light mode
  useEffect(() => {
    try {
      localStorage.removeItem("clarityneuro_theme");
      document.documentElement.classList.remove("dark");
    } catch {
      // ignore
    }
  }, []);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setInsightsDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, []);

  const handleMouseEnter = () => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    setInsightsDropdownOpen(true);
  };

  const handleMouseLeave = () => {
    timeoutRef.current = setTimeout(() => {
      setInsightsDropdownOpen(false);
    }, 150);
  };

  const isInsightsActive = 
    pathname === "/dashboard" || 
    pathname === "/fairness" || 
    pathname === "/shortcut-audit" || 
    pathname === "/explainability";

  return (
    <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-200/60 shadow-xs transition-colors">
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

            {/* Insights Dropdown with Reliable Hover & Click Navigation */}
            <div 
              ref={dropdownRef}
              className="relative"
              onMouseEnter={handleMouseEnter}
              onMouseLeave={handleMouseLeave}
            >
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  setInsightsDropdownOpen((prev) => !prev);
                }}
                className={`flex items-center gap-1 px-3 py-1.5 rounded-full transition-all cursor-pointer ${
                  isInsightsActive
                    ? "text-indigo-600 font-semibold bg-indigo-50/70"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                }`}
                aria-expanded={insightsDropdownOpen}
                aria-haspopup="true"
              >
                <span>Insights</span>
                <ChevronDown className={`w-3.5 h-3.5 opacity-70 transition-transform duration-200 ${insightsDropdownOpen ? "rotate-180 text-indigo-600" : ""}`} />
              </button>

              {insightsDropdownOpen && (
                <div 
                  className="absolute top-full left-0 mt-1 w-60 bg-white rounded-2xl border border-slate-100 shadow-xl p-2 z-50 animate-in fade-in slide-in-from-top-2"
                  onMouseDown={(e) => e.stopPropagation()}
                >
                  {/* 1. Model Evaluation */}
                  <Link
                    href="/dashboard"
                    onClick={() => setInsightsDropdownOpen(false)}
                    className="flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-medium text-slate-700 hover:text-indigo-600 hover:bg-indigo-50/60 transition-colors group cursor-pointer"
                  >
                    <div className="w-7 h-7 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
                      <BarChart3 className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="font-semibold text-slate-900 group-hover:text-indigo-600">Model Evaluation</div>
                      <div className="text-[10px] text-slate-400">Confusion matrix & ROC</div>
                    </div>
                  </Link>

                  {/* 2. Grad-CAM++ */}
                  <Link
                    href="/explainability"
                    onClick={() => setInsightsDropdownOpen(false)}
                    className="flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-medium text-slate-700 hover:text-indigo-600 hover:bg-indigo-50/60 transition-colors group cursor-pointer"
                  >
                    <div className="w-7 h-7 rounded-lg bg-violet-50 text-violet-600 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
                      <Sparkles className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="font-semibold text-slate-900 group-hover:text-indigo-600">Grad-CAM++</div>
                      <div className="text-[10px] text-slate-400">Gradient saliency maps</div>
                    </div>
                  </Link>

                  {/* 3. Fairness Audit */}
                  <Link
                    href="/fairness"
                    onClick={() => setInsightsDropdownOpen(false)}
                    className="flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-medium text-slate-700 hover:text-indigo-600 hover:bg-indigo-50/60 transition-colors group cursor-pointer"
                  >
                    <div className="w-7 h-7 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
                      <Scale className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="font-semibold text-slate-900 group-hover:text-indigo-600">Fairness Audit</div>
                      <div className="text-[10px] text-slate-400">Subgroup disparity</div>
                    </div>
                  </Link>

                  {/* 4. Shortcut Audit */}
                  <Link
                    href="/shortcut-audit"
                    onClick={() => setInsightsDropdownOpen(false)}
                    className="flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-medium text-slate-700 hover:text-indigo-600 hover:bg-indigo-50/60 transition-colors group cursor-pointer"
                  >
                    <div className="w-7 h-7 rounded-lg bg-rose-50 text-rose-600 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
                      <ShieldAlert className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="font-semibold text-slate-900 group-hover:text-indigo-600">Shortcut Audit</div>
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

          {/* Right Action Icons: Avatar + Primary CTA */}
          <div className="hidden md:flex items-center gap-3">
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
              className="p-2 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 cursor-pointer"
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

          {/* Insights Mobile Group */}
          <div className="pt-2 pb-1 px-3">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
              Insights & Audits
            </span>
            <div className="space-y-1 pl-1">
              <Link
                href="/dashboard"
                onClick={() => setMobileMenuOpen(false)}
                className="flex items-center gap-2 px-2 py-1.5 rounded-lg text-xs font-medium text-slate-700 hover:bg-slate-50"
              >
                <BarChart3 className="w-3.5 h-3.5 text-blue-500" />
                <span>Model Evaluation (Confusion matrix & ROC)</span>
              </Link>
              <Link
                href="/explainability"
                onClick={() => setMobileMenuOpen(false)}
                className="flex items-center gap-2 px-2 py-1.5 rounded-lg text-xs font-medium text-slate-700 hover:bg-slate-50"
              >
                <Sparkles className="w-3.5 h-3.5 text-violet-500" />
                <span>Grad-CAM++ (Gradient saliency maps)</span>
              </Link>
              <Link
                href="/fairness"
                onClick={() => setMobileMenuOpen(false)}
                className="flex items-center gap-2 px-2 py-1.5 rounded-lg text-xs font-medium text-slate-700 hover:bg-slate-50"
              >
                <Scale className="w-3.5 h-3.5 text-amber-500" />
                <span>Fairness Audit (Subgroup disparity)</span>
              </Link>
              <Link
                href="/shortcut-audit"
                onClick={() => setMobileMenuOpen(false)}
                className="flex items-center gap-2 px-2 py-1.5 rounded-lg text-xs font-medium text-slate-700 hover:bg-slate-50"
              >
                <ShieldAlert className="w-3.5 h-3.5 text-rose-500" />
                <span>Shortcut Audit (Scanner artifact tests)</span>
              </Link>
            </div>
          </div>

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
