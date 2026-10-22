import type { Metadata } from "next";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import "./globals.css";

export const metadata: Metadata = {
  title: "NeuroScan XAI — Explainable Brain MRI Tumor Analysis",
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
      <body className="min-h-full flex flex-col bg-[#F7F9FC] text-[#15243A] antialiased">
        <Navbar />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
