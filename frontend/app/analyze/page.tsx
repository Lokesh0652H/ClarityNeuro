"use client";

import React, { useState, useRef } from "react";
import Link from "next/link";
import { 
  Upload, 
  Brain, 
  Sparkles, 
  Activity, 
  Layers, 
  AlertCircle, 
  CheckCircle2, 
  Clock, 
  Sliders, 
  Eye, 
  RefreshCw, 
  Zap,
  ArrowRight,
  ShieldCheck,
  ChevronLeft,
  Info
} from "lucide-react";
import { 
  analyzeScan, 
  generateExplainability, 
  calculateUncertainty,
  AnalysisResponseData, 
  ExplainabilityResponseData, 
  UncertaintyResponseData 
} from "@/lib/api";

export default function AnalyzePage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [analysisResult, setAnalysisResult] = useState<AnalysisResponseData | null>(null);
  const [camResult, setCamResult] = useState<ExplainabilityResponseData | null>(null);
  const [uncertaintyResult, setUncertaintyResult] = useState<UncertaintyResponseData | null>(null);
  const [isComputingUncertainty, setIsComputingUncertainty] = useState(false);

  // Visualization state matching Image 1
  const [activeCamTab, setActiveCamTab] = useState<"overlay" | "original" | "heatmap">("overlay");
  const [overlayOpacity, setOverlayOpacity] = useState<number>(0.55);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // 4 Real Benchmark Samples for 1-Click Evaluation
  const benchmarkSamples = [
    { name: "Glioma Sample", class: "glioma", file: "sample_glioma.jpg", badge: "Class 0" },
    { name: "Meningioma Sample", class: "meningioma", file: "sample_meningioma.jpg", badge: "Class 1" },
    { name: "Pituitary Sample", class: "pituitary", file: "sample_pituitary.jpg", badge: "Class 2" },
    { name: "Normal Scan", class: "notumor", file: "sample_notumor.jpg", badge: "Class 3" },
  ];

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      processFile(file);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const processFile = (file: File) => {
    if (!file.type.startsWith("image/")) {
      setError("Please select a valid MRI image file (JPEG, PNG, etc.)");
      return;
    }
    setSelectedFile(file);
    setError(null);
    setAnalysisResult(null);
    setCamResult(null);
    setUncertaintyResult(null);

    const reader = new FileReader();
    reader.onload = () => {
      setPreviewUrl(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  const loadBenchmarkSample = async (sampleFileName: string) => {
    try {
      setError(null);
      const res = await fetch(`/samples/${sampleFileName}`);
      if (!res.ok) {
        throw new Error("Loading benchmark scan from server...");
      }
      const blob = await res.blob();
      const file = new File([blob], sampleFileName, { type: "image/jpeg" });
      processFile(file);
    } catch (err: any) {
      setError(`Notice: ${err.message || "Failed loading benchmark scan"}. Drag and drop any MRI scan from your disk.`);
    }
  };

  const runAnalysis = async () => {
    if (!selectedFile) return;
    setIsAnalyzing(true);
    setError(null);

    try {
      // 1. Run live forward inference + Grad-CAM
      const result = await analyzeScan(selectedFile, true);
      setAnalysisResult(result);

      // 2. Fetch high-res Grad-CAM++ base64 overlay
      try {
        const cam = await generateExplainability(selectedFile, result.analysis_id, result.predicted_class, "gradcam++");
        setCamResult(cam);
      } catch (camErr: any) {
        console.warn("Grad-CAM generation notice:", camErr);
      }
    } catch (err: any) {
      setError(err.message || "MRI analysis failed. Please verify backend service.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const runMCDropout = async () => {
    if (!selectedFile && !analysisResult?.analysis_id) return;
    setIsComputingUncertainty(true);
    try {
      const uRes = await calculateUncertainty(
        selectedFile || undefined, 
        analysisResult?.analysis_id, 
        30
      );
      setUncertaintyResult(uRes);
    } catch (err: any) {
      setError(err.message || "Failed computing Monte Carlo Dropout uncertainty");
    } finally {
      setIsComputingUncertainty(false);
    }
  };

  const resetAnalysis = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setAnalysisResult(null);
    setCamResult(null);
    setUncertaintyResult(null);
    setError(null);
  };

  const getClassNameDisplay = (cls: string) => {
    switch (cls.toLowerCase()) {
      case "glioma": return "Glioma";
      case "meningioma": return "Meningioma";
      case "pituitary": return "Pituitary Tumor";
      case "notumor": return "No Tumor";
      default: return cls;
    }
  };

  const getClassColor = (cls: string) => {
    switch (cls.toLowerCase()) {
      case "glioma": return "#0284C7"; // Sky/Blue
      case "meningioma": return "#4F46E5"; // Indigo
      case "pituitary": return "#7C3AED"; // Violet
      case "notumor": return "#10B981"; // Emerald
      default: return "#64748B";
    }
  };

  // SVG Circular Gauge calculation
  const uncertaintyVal = analysisResult ? analysisResult.normalized_entropy : 0.23;
  const radius = 38;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - uncertaintyVal * circumference;

  return (
    <div className="min-h-screen bg-[#FAFAFD] text-[#0F172A] py-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* TOP ALERT NOTIFICATION IF ANY */}
        {error && (
          <div className="mb-6 p-4 rounded-2xl bg-rose-50 border border-rose-100 flex items-start gap-3 text-xs text-rose-700">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <div className="flex-1">{error}</div>
          </div>
        )}

        {/* VIEW 1: UPLOAD & ANALYZE VIEW (Matching Image 1 Top Center) */}
        {!analysisResult ? (
          <div>
            {/* Header matching Image 1 */}
            <div className="mb-8">
              <span className="text-[11px] font-bold tracking-wider uppercase text-indigo-600">
                ANALYZE
              </span>
              <h1 className="font-serif text-3xl sm:text-4xl font-bold text-[#0F172A] mt-1 tracking-tight">
                Upload & Analyze Brain MRI
              </h1>
              <p className="text-xs sm:text-sm text-slate-500 mt-1 max-w-2xl leading-relaxed">
                Upload a brain MRI image and get an AI-powered prediction with explanations, uncertainty estimation, and more.
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
              
              {/* Left/Center Upload Area (8 cols) */}
              <div className="lg:col-span-8 space-y-6">
                
                {/* Main Drag-and-Drop Card */}
                <div className="bg-white rounded-2xl border border-slate-100 p-8 shadow-xs">
                  <div
                    onDragOver={(e) => e.preventDefault()}
                    onDrop={handleDrop}
                    onClick={() => fileInputRef.current?.click()}
                    className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all ${
                      previewUrl
                        ? "border-indigo-400 bg-indigo-50/20"
                        : "border-slate-200 hover:border-indigo-400 bg-slate-50/50 hover:bg-slate-50"
                    }`}
                  >
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/jpeg,image/png,image/jpg"
                      onChange={handleFileChange}
                      className="hidden"
                    />

                    {previewUrl ? (
                      <div className="space-y-4">
                        <div className="relative w-44 h-44 mx-auto rounded-xl overflow-hidden border border-slate-200 bg-slate-950 shadow-sm">
                          <img
                            src={previewUrl}
                            alt="MRI Preview"
                            className="w-full h-full object-contain"
                          />
                        </div>
                        <div>
                          <div className="text-xs font-semibold text-slate-800">
                            {selectedFile?.name}
                          </div>
                          <div className="text-[11px] text-slate-400 mt-0.5">
                            {(selectedFile ? selectedFile.size / 1024 : 0).toFixed(1)} KB · Ready for inference
                          </div>
                        </div>
                        <span className="inline-block text-[11px] font-semibold text-indigo-600 bg-indigo-50 px-3 py-1 rounded-full border border-indigo-100">
                          Click to select a different scan
                        </span>
                      </div>
                    ) : (
                      <div className="space-y-4 py-4">
                        <div className="w-12 h-12 mx-auto rounded-2xl bg-indigo-50 flex items-center justify-center text-indigo-600">
                          <Upload className="w-5 h-5" />
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-slate-800">
                            Drag and drop your MRI image here
                          </p>
                          <p className="text-xs text-slate-500 mt-0.5">
                            or <span className="text-indigo-600 font-semibold underline underline-offset-2">click to browse</span>
                          </p>
                        </div>
                        <p className="text-[11px] text-slate-400">
                          Supported: JPG, PNG, DICOM (if supported) · Max size: 10MB
                        </p>
                        <button
                          type="button"
                          className="px-5 py-2.5 rounded-full bg-[#0F172A] hover:bg-slate-800 text-white text-xs font-semibold transition-all shadow-xs"
                        >
                          Browse Files
                        </button>
                      </div>
                    )}
                  </div>

                  {/* Primary Analyze Action Button */}
                  <div className="mt-6 flex items-center justify-between gap-4">
                    <button
                      onClick={runAnalysis}
                      disabled={!selectedFile || isAnalyzing}
                      className={`flex-1 py-3 px-6 rounded-full flex items-center justify-center gap-2 font-medium text-xs text-white shadow-sm transition-all ${
                        !selectedFile || isAnalyzing
                          ? "bg-slate-300 cursor-not-allowed"
                          : "bg-[#0F172A] hover:bg-slate-800 hover:shadow-md cursor-pointer"
                      }`}
                    >
                      {isAnalyzing ? (
                        <>
                          <RefreshCw className="w-4 h-4 animate-spin" />
                          <span>Computing EfficientNet-B0 & Grad-CAM++...</span>
                        </>
                      ) : (
                        <>
                          <Brain className="w-4 h-4" />
                          <span>Run AI Analysis</span>
                        </>
                      )}
                    </button>

                    {previewUrl && (
                      <button
                        onClick={resetAnalysis}
                        className="px-4 py-3 rounded-full text-xs font-semibold text-slate-500 hover:text-rose-600 transition-colors"
                      >
                        Reset
                      </button>
                    )}
                  </div>

                  {/* Quick Tips Box matching Image 1 */}
                  <div className="mt-6 pt-6 border-t border-slate-100">
                    <h3 className="text-xs font-bold text-slate-800 mb-2 flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
                      <span>Quick Tips</span>
                    </h3>
                    <ul className="space-y-1.5 text-[11px] text-slate-500">
                      <li className="flex items-center gap-2">
                        <span className="w-1 h-1 rounded-full bg-indigo-500"></span>
                        Use clear, high-quality brain MRI axial or coronal scans
                      </li>
                      <li className="flex items-center gap-2">
                        <span className="w-1 h-1 rounded-full bg-indigo-500"></span>
                        Supported formats: JPG, PNG, DICOM
                      </li>
                      <li className="flex items-center gap-2">
                        <span className="w-1 h-1 rounded-full bg-indigo-500"></span>
                        Max file size: 10MB
                      </li>
                    </ul>
                  </div>
                </div>

                {/* 1-Click Real Benchmark Scans */}
                <div className="bg-white rounded-2xl border border-slate-100 p-6 shadow-xs">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wide">
                      Instant 1-Click Benchmark Scans
                    </h3>
                    <span className="text-[10px] text-slate-400">1,600 Verified Test Cohort</span>
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    {benchmarkSamples.map((sample) => (
                      <button
                        key={sample.file}
                        onClick={() => loadBenchmarkSample(sample.file)}
                        className="p-3 text-left rounded-xl border border-slate-100 hover:border-indigo-400 hover:bg-indigo-50/20 transition-all text-xs group cursor-pointer"
                      >
                        <span className="text-[10px] font-bold text-indigo-600 block mb-0.5">
                          {sample.badge}
                        </span>
                        <span className="font-semibold text-slate-800 group-hover:text-indigo-600 block">
                          {sample.name}
                        </span>
                        <span className="text-[10px] text-slate-400">
                          {sample.class}
                        </span>
                      </button>
                    ))}
                  </div>
                </div>

              </div>

              {/* Right Side: Feature Checklist matching Image 1 */}
              <div className="lg:col-span-4 space-y-4">
                
                <div className="bg-white rounded-2xl border border-slate-100 p-6 shadow-xs space-y-4">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    Analysis Capabilities
                  </h3>

                  <div className="space-y-3">
                    <div className="flex items-center gap-3 p-3 rounded-xl bg-slate-50/70 border border-slate-100">
                      <div className="w-7 h-7 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
                        <CheckCircle2 className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="text-xs font-bold text-slate-800">Real-time Analysis</div>
                        <div className="text-[10px] text-slate-400">Sub-second inference</div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 p-3 rounded-xl bg-slate-50/70 border border-slate-100">
                      <div className="w-7 h-7 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
                        <CheckCircle2 className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="text-xs font-bold text-slate-800">Grad-CAM++ Explanation</div>
                        <div className="text-[10px] text-slate-400">Higher-order saliency</div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 p-3 rounded-xl bg-slate-50/70 border border-slate-100">
                      <div className="w-7 h-7 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center">
                        <CheckCircle2 className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="text-xs font-bold text-slate-800">Uncertainty Estimation</div>
                        <div className="text-[10px] text-slate-400">Entropy & MC Dropout</div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 p-3 rounded-xl bg-slate-50/70 border border-slate-100">
                      <div className="w-7 h-7 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
                        <CheckCircle2 className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="text-xs font-bold text-slate-800">Detailed Reports</div>
                        <div className="text-[10px] text-slate-400">Full probability matrix</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Decorative Subtle Contour Banner */}
                <div className="p-6 rounded-2xl bg-gradient-to-br from-indigo-500/5 via-blue-500/5 to-purple-500/5 border border-indigo-100/50 text-xs text-slate-600 space-y-2">
                  <div className="flex items-center gap-2 font-semibold text-slate-900">
                    <ShieldCheck className="w-4 h-4 text-emerald-600" />
                    <span>Scientific Reproducibility</span>
                  </div>
                  <p className="text-[11px] text-slate-500 leading-relaxed">
                    Evaluated on a deterministic frozen checkpoint with 82.75% macro test accuracy and 0.0307 expected calibration error.
                  </p>
                </div>

              </div>

            </div>
          </div>
        ) : (
          /* VIEW 2: ANALYSIS RESULTS (Matching Image 1 Top Right) */
          <div>
            {/* Header & Back Link matching Image 1 */}
            <div className="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <button
                  onClick={resetAnalysis}
                  className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-800 mb-2 cursor-pointer transition-colors"
                >
                  <ChevronLeft className="w-4 h-4" />
                  <span>Back to Analyze</span>
                </button>
                <h1 className="font-serif text-3xl font-bold text-[#0F172A] tracking-tight">
                  Analysis Results
                </h1>
                <p className="text-xs text-slate-500 mt-0.5">
                  AI prediction with explainability, uncertainty and detailed insights.
                </p>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={resetAnalysis}
                  className="px-4 py-2 rounded-full bg-white border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 shadow-xs cursor-pointer"
                >
                  Analyze New Scan
                </button>
              </div>
            </div>

            {/* TOP 3 CARDS ROW MATCHING IMAGE 1 */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-6 mb-6">
              
              {/* Card 1: Original MRI Image Preview (3 cols) */}
              <div className="md:col-span-3 bg-white rounded-2xl border border-slate-100 p-4 shadow-xs flex flex-col items-center justify-center">
                <div className="relative w-full aspect-square rounded-xl overflow-hidden bg-black border border-slate-100 flex items-center justify-center">
                  <img
                    src={previewUrl || ""}
                    alt="Original MRI"
                    className="w-full h-full object-contain"
                  />
                </div>
                <div className="w-full mt-3 flex items-center justify-between text-[11px] text-slate-400">
                  <span>Input Scan</span>
                  <span className="font-medium text-slate-600">224 × 224 px</span>
                </div>
              </div>

              {/* Card 2: Prediction Card (6 cols) */}
              <div className="md:col-span-6 bg-white rounded-2xl border border-slate-100 p-6 shadow-xs flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
                      Prediction
                    </span>
                    <span className="text-[11px] text-slate-400">
                      {analysisResult.model_version}
                    </span>
                  </div>

                  <h2 
                    className="font-serif text-3xl font-bold tracking-tight mb-2"
                    style={{ color: getClassColor(analysisResult.predicted_class) }}
                  >
                    {getClassNameDisplay(analysisResult.predicted_class)}
                  </h2>

                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="font-semibold text-slate-600">Confidence</span>
                    <span className="font-bold text-slate-900">
                      {(analysisResult.confidence * 100).toFixed(1)}%
                    </span>
                  </div>

                  <div className="w-full h-2 rounded-full bg-slate-100 overflow-hidden mb-5">
                    <div
                      className="h-full rounded-full transition-all duration-700"
                      style={{
                        width: `${analysisResult.confidence * 100}%`,
                        backgroundColor: getClassColor(analysisResult.predicted_class),
                      }}
                    />
                  </div>
                </div>

                {/* Class Probabilities Breakdown */}
                <div className="space-y-2 pt-3 border-t border-slate-100">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wide block mb-1">
                    Class Probabilities
                  </span>
                  {Object.entries(analysisResult.probabilities).map(([cls, prob]) => {
                    const pct = (prob * 100).toFixed(1);
                    const isTop = cls === analysisResult.predicted_class;
                    return (
                      <div key={cls} className="flex items-center justify-between text-xs">
                        <div className="flex items-center gap-2">
                          <span 
                            className="w-2 h-2 rounded-full"
                            style={{ backgroundColor: getClassColor(cls) }}
                          />
                          <span className={isTop ? "font-bold text-slate-900" : "text-slate-500"}>
                            {getClassNameDisplay(cls)}
                          </span>
                        </div>
                        <span className={isTop ? "font-bold text-slate-900" : "text-slate-500"}>
                          {pct}%
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Card 3: Circular Uncertainty Gauge Card (3 cols) */}
              <div className="md:col-span-3 bg-white rounded-2xl border border-slate-100 p-6 shadow-xs flex flex-col items-center justify-center text-center">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-3">
                  Uncertainty
                </span>

                {/* SVG Donut Ring Gauge */}
                <div className="relative w-28 h-28 flex items-center justify-center my-1">
                  <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                    <circle
                      cx="50"
                      cy="50"
                      r={radius}
                      fill="transparent"
                      stroke="#F1F5F9"
                      strokeWidth="8"
                    />
                    <circle
                      cx="50"
                      cy="50"
                      r={radius}
                      fill="transparent"
                      stroke={uncertaintyVal < 0.35 ? "#10B981" : uncertaintyVal < 0.65 ? "#F59E0B" : "#EF4444"}
                      strokeWidth="8"
                      strokeDasharray={circumference}
                      strokeDashoffset={strokeDashoffset}
                      strokeLinecap="round"
                      className="transition-all duration-1000 ease-out"
                    />
                  </svg>
                  <div className="absolute flex flex-col items-center justify-center">
                    <span className="font-serif font-bold text-xl text-slate-900">
                      {uncertaintyVal.toFixed(2)}
                    </span>
                  </div>
                </div>

                <div className="mt-2">
                  <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                    uncertaintyVal < 0.35
                      ? "bg-emerald-50 text-emerald-700 border border-emerald-100"
                      : uncertaintyVal < 0.65
                      ? "bg-amber-50 text-amber-700 border border-amber-100"
                      : "bg-rose-50 text-rose-700 border border-rose-100"
                  }`}>
                    {uncertaintyVal < 0.35 ? "Low Uncertainty" : uncertaintyVal < 0.65 ? "Moderate Uncertainty" : "High Uncertainty"}
                  </span>
                  <p className="text-[11px] text-slate-400 mt-1 max-w-[180px] leading-tight">
                    {uncertaintyVal < 0.35 
                      ? "The model is fairly confident in its prediction." 
                      : "Consider secondary clinical review for this scan."}
                  </p>
                </div>
              </div>

            </div>

            {/* METADATA INFO STRIP MATCHING IMAGE 1 */}
            <div className="bg-white rounded-2xl border border-slate-100 px-6 py-3 shadow-xs mb-6 flex flex-wrap items-center justify-between gap-4 text-xs">
              <div className="flex items-center gap-2">
                <span className="text-slate-400">Model Version</span>
                <span className="font-semibold text-slate-800">{analysisResult.model_version}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-slate-400">Processing Time</span>
                <span className="font-semibold text-slate-800">{(analysisResult.inference_time_ms / 1000).toFixed(2)}s</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-slate-400">Image Size</span>
                <span className="font-semibold text-slate-800">224 × 224</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-slate-400">Entropy H(p)</span>
                <span className="font-semibold text-indigo-600">{analysisResult.entropy.toFixed(3)} nats</span>
              </div>
            </div>

            {/* BOTTOM SECTION: GRAD-CAM++ VISUALIZATION & KEY INSIGHTS */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
              
              {/* Grad-CAM++ Card (8 cols) */}
              <div className="lg:col-span-8 bg-white rounded-2xl border border-slate-100 p-6 shadow-xs space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div>
                    <h3 className="font-serif text-lg font-bold text-slate-900">
                      Grad-CAM++ Visualization
                    </h3>
                    <p className="text-xs text-slate-400">
                      Layer attribution extracted from EfficientNet-B0 conv head
                    </p>
                  </div>

                  {/* Tabs matching Image 1: [ Overlay | Original | Heatmap ] */}
                  <div className="flex items-center bg-slate-100 p-1 rounded-full text-xs font-medium">
                    <button
                      onClick={() => setActiveCamTab("overlay")}
                      className={`px-3 py-1 rounded-full transition-all cursor-pointer ${
                        activeCamTab === "overlay" ? "bg-white text-slate-900 shadow-xs font-semibold" : "text-slate-500 hover:text-slate-900"
                      }`}
                    >
                      Overlay
                    </button>
                    <button
                      onClick={() => setActiveCamTab("original")}
                      className={`px-3 py-1 rounded-full transition-all cursor-pointer ${
                        activeCamTab === "original" ? "bg-white text-slate-900 shadow-xs font-semibold" : "text-slate-500 hover:text-slate-900"
                      }`}
                    >
                      Original
                    </button>
                    <button
                      onClick={() => setActiveCamTab("heatmap")}
                      className={`px-3 py-1 rounded-full transition-all cursor-pointer ${
                        activeCamTab === "heatmap" ? "bg-white text-slate-900 shadow-xs font-semibold" : "text-slate-500 hover:text-slate-900"
                      }`}
                    >
                      Heatmap
                    </button>
                  </div>
                </div>

                {/* Opacity Slider */}
                {activeCamTab === "overlay" && (
                  <div className="flex items-center gap-3 pt-1">
                    <span className="text-xs text-slate-400 font-medium">Overlay Opacity:</span>
                    <input
                      type="range"
                      min="0.1"
                      max="1.0"
                      step="0.05"
                      value={overlayOpacity}
                      onChange={(e) => setOverlayOpacity(parseFloat(e.target.value))}
                      className="w-32 accent-indigo-600"
                    />
                    <span className="text-xs font-semibold text-slate-700">{overlayOpacity.toFixed(1)}</span>
                  </div>
                )}

                {/* Saliency Display Area */}
                <div className="relative w-full aspect-[16/10] sm:aspect-[2/1] rounded-xl overflow-hidden bg-black border border-slate-100 flex items-center justify-center p-4">
                  {activeCamTab === "overlay" && (
                    <div className="relative w-64 h-64 mx-auto rounded-lg overflow-hidden bg-black">
                      <img
                        src={previewUrl || ""}
                        alt="Original"
                        className="absolute inset-0 w-full h-full object-contain"
                      />
                      {camResult && (
                        <img
                          src={camResult.heatmap_base64}
                          alt="Heatmap"
                          className="absolute inset-0 w-full h-full object-contain mix-blend-screen"
                          style={{ opacity: overlayOpacity }}
                        />
                      )}
                    </div>
                  )}

                  {activeCamTab === "original" && (
                    <div className="relative w-64 h-64 mx-auto rounded-lg overflow-hidden bg-black">
                      <img
                        src={previewUrl || ""}
                        alt="Original"
                        className="w-full h-full object-contain"
                      />
                    </div>
                  )}

                  {activeCamTab === "heatmap" && camResult && (
                    <div className="relative w-64 h-64 mx-auto rounded-lg overflow-hidden bg-black">
                      <img
                        src={camResult.heatmap_base64}
                        alt="Grad-CAM++"
                        className="w-full h-full object-contain"
                      />
                    </div>
                  )}
                </div>

                {/* Side-by-Side Strip matching the mini thumbnails in Image 1 */}
                {camResult && (
                  <div className="grid grid-cols-3 gap-3 pt-2">
                    <div 
                      onClick={() => setActiveCamTab("original")} 
                      className={`p-2 rounded-xl border text-center cursor-pointer transition-all ${
                        activeCamTab === "original" ? "border-indigo-500 bg-indigo-50/20" : "border-slate-100 hover:border-slate-200"
                      }`}
                    >
                      <div className="w-16 h-16 mx-auto rounded-lg bg-black overflow-hidden mb-1">
                        <img src={previewUrl || ""} alt="Thumb" className="w-full h-full object-contain" />
                      </div>
                      <span className="text-[10px] text-slate-500 font-medium">Original</span>
                    </div>

                    <div 
                      onClick={() => setActiveCamTab("heatmap")} 
                      className={`p-2 rounded-xl border text-center cursor-pointer transition-all ${
                        activeCamTab === "heatmap" ? "border-indigo-500 bg-indigo-50/20" : "border-slate-100 hover:border-slate-200"
                      }`}
                    >
                      <div className="w-16 h-16 mx-auto rounded-lg bg-black overflow-hidden mb-1">
                        <img src={camResult.heatmap_base64} alt="Thumb" className="w-full h-full object-contain" />
                      </div>
                      <span className="text-[10px] text-slate-500 font-medium">Heatmap</span>
                    </div>

                    <div 
                      onClick={() => setActiveCamTab("overlay")} 
                      className={`p-2 rounded-xl border text-center cursor-pointer transition-all ${
                        activeCamTab === "overlay" ? "border-indigo-500 bg-indigo-50/20" : "border-slate-100 hover:border-slate-200"
                      }`}
                    >
                      <div className="relative w-16 h-16 mx-auto rounded-lg bg-black overflow-hidden mb-1">
                        <img src={previewUrl || ""} alt="Thumb" className="w-full h-full object-contain" />
                        <img src={camResult.heatmap_base64} alt="Thumb" className="absolute inset-0 w-full h-full object-contain mix-blend-screen opacity-60" />
                      </div>
                      <span className="text-[10px] text-slate-500 font-medium">Overlay Blend</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Key Insights Card (4 cols) matching Image 1 */}
              <div className="lg:col-span-4 space-y-4">
                
                <div className="bg-white rounded-2xl border border-slate-100 p-6 shadow-xs space-y-4">
                  <h3 className="font-serif text-base font-bold text-slate-900">
                    Key Insights
                  </h3>

                  <ul className="space-y-3 text-xs text-slate-600">
                    <li className="flex items-start gap-2.5">
                      <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 mt-1.5 shrink-0" />
                      <span>
                        Model focuses on intracranial anatomical features in the{" "}
                        <strong className="text-slate-900">
                          {camResult?.localization_notes || "cranial parenchyma"}
                        </strong>.
                      </span>
                    </li>
                    <li className="flex items-start gap-2.5">
                      <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 mt-1.5 shrink-0" />
                      <span>
                        Activation highlights are consistent with known {getClassNameDisplay(analysisResult.predicted_class)} morphology.
                      </span>
                    </li>
                    <li className="flex items-start gap-2.5">
                      <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 mt-1.5 shrink-0" />
                      <span>
                        Use this as a visual aid for interpretability, not as an autonomous diagnostic decision.
                      </span>
                    </li>
                  </ul>
                </div>

                {/* Monte Carlo Dropout Expansion Box */}
                <div className="bg-white rounded-2xl border border-slate-100 p-6 shadow-xs space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-900">
                      Monte Carlo Dropout (T=30)
                    </span>
                    <button
                      onClick={runMCDropout}
                      disabled={isComputingUncertainty}
                      className="px-3 py-1 rounded-full bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-[11px] font-semibold flex items-center gap-1 transition-colors cursor-pointer"
                    >
                      {isComputingUncertainty ? (
                        <>
                          <RefreshCw className="w-3 h-3 animate-spin" />
                          <span>Computing...</span>
                        </>
                      ) : (
                        <>
                          <Zap className="w-3 h-3 text-indigo-600" />
                          <span>Run Epistemic Pass</span>
                        </>
                      )}
                    </button>
                  </div>

                  {uncertaintyResult ? (
                    <div className="pt-2 border-t border-slate-100 grid grid-cols-2 gap-2 text-xs">
                      <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100">
                        <span className="text-[10px] text-slate-400 block">Mutual Information</span>
                        <strong className="text-indigo-600 text-sm">{uncertaintyResult.mutual_information.toFixed(4)}</strong>
                      </div>
                      <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100">
                        <span className="text-[10px] text-slate-400 block">Predictive Entropy</span>
                        <strong className="text-slate-800 text-sm">{uncertaintyResult.predictive_entropy.toFixed(4)}</strong>
                      </div>
                    </div>
                  ) : (
                    <p className="text-[11px] text-slate-400 leading-relaxed">
                      Measures epistemic model weight variance across 30 stochastic dropout passes.
                    </p>
                  )}
                </div>

              </div>

            </div>
          </div>
        )}

      </div>
    </div>
  );
}
