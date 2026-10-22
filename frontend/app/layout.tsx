import type { Metadata } from "next";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import "./globals.css";

export const metadata: Metadata = {
  title: "ClarityNeuro — Explainable Brain MRI Tumor Analysis",
  description:
    "Production-grade Explainable AI (XAI) & Uncertainty-Aware Brain MRI Classification platform using EfficientNet-B0, Grad-CAM++, and Shannon entropy estimation.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className="min-h-full flex flex-col bg-[#FAFAFD] text-[#0F172A] antialiased bg-grid-clean selection:bg-indigo-100 selection:text-indigo-900">
        {/* Subtle Ambient Radial Lighting for Editorial Aesthetic */}
        <div className="fixed inset-0 pointer-events-none z-0 ambient-glow"></div>
        
        <Navbar />
        <main className="flex-1 relative z-10">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
