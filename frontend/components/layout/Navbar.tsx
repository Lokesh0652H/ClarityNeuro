"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect } from "react";
import { 
  Activity, 
  Brain, 
  ShieldAlert, 
  BarChart3, 
  Scale, 
  Database, 
  BookOpen, 
  CheckCircle2, 
  Sparkles,
  Menu,
  X
} from "lucide-react";

export function Navbar() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [systemReady, setSystemReady] = useState(true);

  const navLinks = [
    { href: "/analyze", label: "Analyze MRI", icon: Brain },
    { href: "/explainability", label: "Grad-CAM++", icon: Sparkles },
    { href: "/dashboard", label: "Model Evaluation", icon: BarChart3 },
    { href: "/fairness", label: "Fairness Audit", icon: Scale },
    { href: "/shortcut-audit", label: "Shortcut Audit", icon: ShieldAlert },
    { href: "/datasets", label: "Data Transparency", icon: Database },
    { href: "/documentation", label: "Documentation", icon: BookOpen },
  ];

  return (
    <header className="sticky top-0 z-50 bg-[#FFFFFF]/90 backdrop-blur-md border-b border-[#E5EAF1]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo */}
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#11B9D4] to-[#7867F5] flex items-center justify-center text-white shadow-sm group-hover:scale-105 transition-transform">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-1.5">
                <span className="font-bold text-lg tracking-tight text-[#15243A]">NeuroScan</span>
                <span className="text-xs font-semibold px-1.5 py-0.5 rounded bg-[#11B9D4]/10 text-[#11B9D4] border border-[#11B9D4]/20">
                  XAI
                </span>
              </div>
              <span className="text-[10px] text-[#68758A] font-medium tracking-wide">
                Explainable MRI Intelligence
              </span>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <nav className="hidden lg:flex items-center gap-1">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? "bg-[#11B9D4]/10 text-[#11B9D4] font-semibold"
                      : "text-[#68758A] hover:text-[#15243A] hover:bg-[#F0F4F8]"
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? "text-[#11B9D4]" : "text-[#68758A]"}`} />
                  {link.label}
                </Link>
              );
            })}
          </nav>

          {/* System Status Indicator & Primary CTA */}
          <div className="hidden md:flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#10B981]/10 border border-[#10B981]/20 text-[#10B981] text-xs font-medium">
              <span className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse"></span>
              <span>EfficientNet-B0 Ready</span>
            </div>

            <Link
              href="/analyze"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-[#11B9D4] to-[#7867F5] text-white text-sm font-semibold shadow-sm hover:opacity-95 transition-opacity"
            >
              <Brain className="w-4 h-4" />
              Analyze Scan
            </Link>
          </div>

          {/* Mobile menu button */}
          <div className="lg:hidden flex items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-md text-[#68758A] hover:text-[#15243A] hover:bg-[#F0F4F8]"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile dropdown */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-b border-[#E5EAF1] bg-[#FFFFFF] px-4 pt-2 pb-4 space-y-1">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center gap-2 px-3 py-2.5 rounded-md text-base font-medium ${
                  isActive
                    ? "bg-[#11B9D4]/10 text-[#11B9D4] font-semibold"
                    : "text-[#68758A] hover:bg-[#F0F4F8] hover:text-[#15243A]"
                }`}
              >
                <Icon className="w-5 h-5" />
                {link.label}
              </Link>
            );
          })}
          <div className="pt-3 border-t border-[#E5EAF1]">
            <Link
              href="/analyze"
              onClick={() => setMobileMenuOpen(false)}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-gradient-to-r from-[#11B9D4] to-[#7867F5] text-white font-medium"
            >
              <Brain className="w-4 h-4" />
              Start MRI Analysis
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}
