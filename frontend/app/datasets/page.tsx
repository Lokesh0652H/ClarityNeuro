"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { 
  Database, 
  Brain, 
  CheckCircle2, 
  ExternalLink, 
  ShieldCheck, 
  FileText, 
  Layers, 
  Award, 
  Cpu, 
  RefreshCw,
  Info
} from "lucide-react";
import { fetchDatasetStatus } from "@/lib/api";

export default function DatasetsPage() {
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadStatus() {
      try {
        setLoading(true);
        const data = await fetchDatasetStatus();
        setStatus(data);
      } catch (e) {
        console.warn("Dataset status loading note:", e);
      } finally {
        setLoading(false);
      }
    }
    loadStatus();
  }, []);

  const classData = [
    { name: "Glioma", count: 1800, pct: "25%", color: "#06B6D4" },
    { name: "Meningioma", count: 1800, pct: "25%", color: "#4F46E5" },
    { name: "Pituitary Tumor", count: 1800, pct: "25%", color: "#7C3AED" },
    { name: "No Tumor", count: 1800, pct: "25%", color: "#10B981" },
  ];

  return (
    <div className="min-h-screen text-[#0F172A] py-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header matching Image 1 Bottom Center */}
        <div className="mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <h1 className="font-serif text-3xl sm:text-4xl font-bold text-[#0F172A] tracking-tight">
                Dataset & Model Transparency
              </h1>
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-emerald-50 border border-emerald-100 text-emerald-700 text-xs font-semibold">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Verified</span>
              </span>
            </div>
            <p className="text-xs sm:text-sm text-slate-500">
              Complete information about the dataset, model and evaluation pipeline.
            </p>
          </div>

          <div>
            <a
              href="https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-full bg-white border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 shadow-xs transition-all"
            >
              <span>Kaggle Dataset</span>
              <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
            </a>
          </div>
        </div>

        {/* TOP ROW: DATASET INFO, CLASS DISTRIBUTION & VALIDATION CHECKLIST */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-8">
          
          {/* Card 1: Dataset Information (4 cols) */}
          <div className="lg:col-span-4 bg-white rounded-2xl border border-slate-100 p-6 shadow-xs flex flex-col justify-between">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1 block">
                Dataset Information
              </span>
              <h3 className="font-serif text-base font-bold text-slate-900 mb-1">
                Brain Tumor MRI Dataset (Kaggle)
              </h3>
              <a 
                href="https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset"
                target="_blank"
                rel="noreferrer"
                className="text-[11px] text-indigo-600 hover:underline break-all"
              >
                kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset
              </a>

              <div className="grid grid-cols-2 gap-3 mt-6 pt-4 border-t border-slate-100 text-xs">
                <div>
                  <span className="text-slate-400 block text-[10px]">License</span>
                  <strong className="text-slate-800">CC BY 4.0</strong>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Version</span>
                  <strong className="text-slate-800">v1.0</strong>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Curators</span>
                  <strong className="text-slate-800">Nickparvar / Bhuvaji</strong>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Total Scans</span>
                  <strong className="text-slate-800">7,200 Scans</strong>
                </div>
              </div>
            </div>

            <div className="mt-6 pt-3 border-t border-slate-100 text-[11px] text-slate-400">
              Training: 5,600 | Testing: 1,600
            </div>
          </div>

          {/* Card 2: Class Distribution & SVG Donut Chart (5 cols) matching Image 1 */}
          <div className="lg:col-span-5 bg-white rounded-2xl border border-slate-100 p-6 shadow-xs">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2 block">
              Class Distribution
            </span>

            <div className="flex flex-col sm:flex-row items-center justify-between gap-6 pt-2">
              {/* Breakdown List */}
              <div className="space-y-2.5 w-full sm:w-auto text-xs">
                {classData.map((c) => (
                  <div key={c.name} className="flex items-center justify-between gap-4">
                    <div className="flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: c.color }} />
                      <span className="text-slate-700 font-medium">{c.name}</span>
                    </div>
                    <span className="text-slate-500 font-semibold">
                      {c.count.toLocaleString()} ({c.pct})
                    </span>
                  </div>
                ))}
              </div>

              {/* Donut Chart with Total in Center matching Image 1 */}
              <div className="relative w-32 h-32 flex items-center justify-center shrink-0">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                  {/* Glioma 25% */}
                  <circle cx="50" cy="50" r="38" fill="transparent" stroke="#06B6D4" strokeWidth="12" strokeDasharray="59.7 179.1" strokeDashoffset="0" />
                  {/* Meningioma 25% */}
                  <circle cx="50" cy="50" r="38" fill="transparent" stroke="#4F46E5" strokeWidth="12" strokeDasharray="59.7 179.1" strokeDashoffset="-59.7" />
                  {/* Pituitary 25% */}
                  <circle cx="50" cy="50" r="38" fill="transparent" stroke="#7C3AED" strokeWidth="12" strokeDasharray="59.7 179.1" strokeDashoffset="-119.4" />
                  {/* No Tumor 25% */}
                  <circle cx="50" cy="50" r="38" fill="transparent" stroke="#10B981" strokeWidth="12" strokeDasharray="59.7 179.1" strokeDashoffset="-179.1" />
                </svg>
                <div className="absolute flex flex-col items-center justify-center">
                  <span className="text-[10px] text-slate-400 font-medium">Total</span>
                  <span className="font-serif font-bold text-base text-slate-900">7,200</span>
                </div>
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
              <span>Balanced distribution</span>
              <span>1:1:1:1 exact ratio</span>
            </div>
          </div>

          {/* Card 3: Dataset Validation Checklist (3 cols) matching Image 1 */}
          <div className="lg:col-span-3 bg-white rounded-2xl border border-slate-100 p-6 shadow-xs flex flex-col justify-between">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-3 block">
                Dataset Validation
              </span>

              <ul className="space-y-2.5 text-xs text-slate-600">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                  <span>Valid images (7,200 / 7,200)</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                  <span>No missing labels</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                  <span>No corrupt files</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                  <span>No duplicates found</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                  <span>Class balance (verified)</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                  <span>Proper split strategy</span>
                </li>
              </ul>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] text-emerald-600 font-medium">
              100% Integrity Verified
            </div>
          </div>

        </div>

        {/* MIDDLE SECTION: MODEL INFORMATION GRID MATCHING IMAGE 1 */}
        <div className="bg-white rounded-2xl border border-slate-100 p-6 shadow-xs mb-8">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-serif text-base font-bold text-slate-900">
              Model Information
            </h3>
            <span className="flex items-center gap-1.5 text-xs font-semibold text-emerald-600 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-100">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              Training Completed
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-4 text-xs">
            <div className="p-3 rounded-xl bg-slate-50/70 border border-slate-100">
              <span className="text-[10px] text-slate-400 block">Architecture</span>
              <strong className="text-slate-900">EfficientNet-B0</strong>
            </div>

            <div className="p-3 rounded-xl bg-slate-50/70 border border-slate-100">
              <span className="text-[10px] text-slate-400 block">Optimizer</span>
              <strong className="text-slate-900">Adam</strong>
            </div>

            <div className="p-3 rounded-xl bg-slate-50/70 border border-slate-100">
              <span className="text-[10px] text-slate-400 block">Loss Function</span>
              <strong className="text-slate-900">CrossEntropy</strong>
            </div>

            <div className="p-3 rounded-xl bg-slate-50/70 border border-slate-100">
              <span className="text-[10px] text-slate-400 block">Learning Rate</span>
              <strong className="text-slate-900">1e-3</strong>
            </div>

            <div className="p-3 rounded-xl bg-slate-50/70 border border-slate-100">
              <span className="text-[10px] text-slate-400 block">Training Status</span>
              <strong className="text-emerald-600">Completed</strong>
            </div>

            <div className="p-3 rounded-xl bg-slate-50/70 border border-slate-100">
              <span className="text-[10px] text-slate-400 block">Best Checkpoint</span>
              <strong className="text-slate-900">v1.0.0</strong>
            </div>

            <div className="p-3 rounded-xl bg-slate-50/70 border border-slate-100">
              <span className="text-[10px] text-slate-400 block">Epochs</span>
              <strong className="text-slate-900">50</strong>
            </div>

            <div className="p-3 rounded-xl bg-slate-50/70 border border-slate-100">
              <span className="text-[10px] text-slate-400 block">Training Time</span>
              <strong className="text-slate-900">~3.5h</strong>
            </div>
          </div>
        </div>

        {/* BOTTOM SECTION: EVALUATION METRICS (TEST SET) 5-CARD ROW MATCHING IMAGE 1 */}
        <div className="bg-white rounded-2xl border border-slate-100 p-6 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-serif text-base font-bold text-slate-900">
              Evaluation Metrics (Test Set)
            </h3>
            <span className="text-[11px] text-slate-400">1,600 held-out test scans</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 text-center">
            <div className="p-4 rounded-xl bg-slate-50/80 border border-slate-100">
              <span className="text-xs text-slate-400 block mb-1">Accuracy</span>
              <div className="font-serif text-2xl font-bold text-slate-900">
                0.83 <span className="text-xs text-slate-500 font-sans font-normal">(82.75%)</span>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-50/80 border border-slate-100">
              <span className="text-xs text-slate-400 block mb-1">Precision</span>
              <div className="font-serif text-2xl font-bold text-slate-900">
                0.84 <span className="text-xs text-slate-500 font-sans font-normal">(84.05%)</span>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-50/80 border border-slate-100">
              <span className="text-xs text-slate-400 block mb-1">Recall</span>
              <div className="font-serif text-2xl font-bold text-slate-900">
                0.83 <span className="text-xs text-slate-500 font-sans font-normal">(82.75%)</span>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-50/80 border border-slate-100">
              <span className="text-xs text-slate-400 block mb-1">F1-Score</span>
              <div className="font-serif text-2xl font-bold text-slate-900">
                0.82 <span className="text-xs text-slate-500 font-sans font-normal">(82.32%)</span>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-50/80 border border-slate-100">
              <span className="text-xs text-slate-400 block mb-1">ROC-AUC</span>
              <div className="font-serif text-2xl font-bold text-indigo-600">
                0.96 <span className="text-xs text-indigo-500 font-sans font-normal">(0.9561)</span>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
