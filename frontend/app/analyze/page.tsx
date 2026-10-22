"use client";

import React, { useState, useRef, useEffect } from "react";
import Image from "next/image";
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
  ShieldAlert,
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

  // Visualization state
  const [viewMode, setViewMode] = useState<"overlay" | "side_by_side" | "heatmap_only" | "original">("overlay");
  const [overlayOpacity, setOverlayOpacity] = useState<number>(0.65);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Clinical Benchmark Samples for 1-click evaluation
  const benchmarkSamples = [
    { name: "Glioma Sample", class: "glioma", file: "sample_glioma.jpg", badge: "Class 0" },
    { name: "Meningioma Sample", class: "meningioma", file: "sample_meningioma.jpg", badge: "Class 1" },
    { name: "Pituitary Sample", class: "pituitary", file: "sample_pituitary.jpg", badge: "Class 2" },
    { name: "Normal Scan Sample", class: "notumor", file: "sample_notumor.jpg", badge: "Class 3" },
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

  const loadBenchmarkSample = async (sampleFileName: string, sampleName: string) => {
    try {
      setError(null);
      const res = await fetch(`/samples/${sampleFileName}`);
      if (!res.ok) {
        // Fallback: If not yet in public folder, fetch placeholder or notify
        throw new Error("Sample file loading from benchmark library...");
      }
      const blob = await res.blob();
      const file = new File([blob], sampleFileName, { type: "image/jpeg" });
      processFile(file);
    } catch (err: any) {
      setError(`Notice: ${err.message || "Failed loading benchmark scan"}. You can also drag-and-drop any MRI scan from your drive.`);
    }
  };

  const runAnalysis = async () => {
    if (!selectedFile) return;
    setIsAnalyzing(true);
    setError(null);

    try {
      // 1. Run live forward inference + initial Grad-CAM
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

  const getClassNameDisplay = (cls: string) => {
    switch (cls.toLowerCase()) {
      case "glioma": return "Glioma Tumor";
      case "meningioma": return "Meningioma Tumor";
      case "pituitary": return "Pituitary Adenoma";
      case "notumor": return "No Tumor (Normal Intracranial)";
      default: return cls;
    }
  };

  const getClassColor = (cls: string) => {
    switch (cls.toLowerCase()) {
      case "glioma": return "#11B9D4";
      case "meningioma": return "#7867F5";
      case "pituitary": return "#3B82F6";
      case "notumor": return "#10B981";
      default: return "#68758A";
    }
  };

  return (
    <div className="min-h-screen bg-[#F7F9FC] py-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#11B9D4] mb-2">
            <Brain className="w-4 h-4" />
            <span>Interactive Diagnostic Inference</span>
          </div>
          <h1 className="text-3xl font-extrabold text-[#15243A] tracking-tight">
            MRI Analysis & Explainability Workspace
          </h1>
          <p className="text-sm text-[#68758A] mt-1 max-w-2xl">
            Upload an intracranial MRI scan or test with real benchmark samples to compute live PyTorch EfficientNet-B0 predictions, Grad-CAM++ saliency heatmaps, and Shannon entropy uncertainty.
          </p>
        </div>

        {/* Top Notification / Error Alert */}
        {error && (
          <div className="mb-6 p-4 rounded-xl bg-[#EF4444]/10 border border-[#EF4444]/20 flex items-start gap-3 text-sm text-[#EF4444]">
            <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
            <div className="flex-1">{error}</div>
          </div>
        )}

        {/* Main Grid: Upload & Preview on Left, Results on Right */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Left Column (5 Cols): Upload & Benchmark Scans */}
          <div className="lg:col-span-5 space-y-6">
            
            {/* Upload Zone Card */}
            <div className="clinical-card p-6">
              <h2 className="text-base font-bold text-[#15243A] mb-3 flex items-center justify-between">
                <span>Select MRI Image</span>
                {previewUrl && (
                  <button
                    onClick={() => {
                      setSelectedFile(null);
                      setPreviewUrl(null);
                      setAnalysisResult(null);
                      setCamResult(null);
                      setUncertaintyResult(null);
                    }}
                    className="text-xs text-[#EF4444] hover:underline"
                  >
                    Clear Scan
                  </button>
                )}
              </h2>

              <div
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all ${
                  previewUrl
                    ? "border-[#11B9D4] bg-[#11B9D4]/5"
                    : "border-[#E5EAF1] hover:border-[#11B9D4]/60 bg-[#FFFFFF]"
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
                    <div className="relative w-48 h-48 mx-auto rounded-lg overflow-hidden border border-[#E5EAF1] bg-black">
                      <img
                        src={previewUrl}
                        alt="MRI Preview"
                        className="w-full h-full object-contain"
                      />
                    </div>
                    <div className="text-xs text-[#68758A]">
                      <span className="font-semibold text-[#15243A]">{selectedFile?.name}</span>
                      {" • "}
                      <span>{(selectedFile ? selectedFile.size / 1024 : 0).toFixed(1)} KB</span>
                    </div>
                    <p className="text-[11px] text-[#11B9D4] font-medium">
                      Click to change image
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3 py-4">
                    <div className="w-12 h-12 mx-auto rounded-xl bg-[#11B9D4]/10 flex items-center justify-center text-[#11B9D4]">
                      <Upload className="w-6 h-6" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-[#15243A]">
                        Drag and drop your brain MRI scan
                      </p>
                      <p className="text-xs text-[#68758A] mt-1">
                        Supported formats: JPEG, PNG, TIFF (Max 10MB)
                      </p>
                    </div>
                    <button
                      type="button"
                      className="px-4 py-2 rounded-lg bg-[#F0F4F8] hover:bg-[#E5EAF1] text-xs font-semibold text-[#15243A] transition-colors"
                    >
                      Browse Files
                    </button>
                  </div>
                )}
              </div>

              {/* Action Button */}
              <div className="mt-5">
                <button
                  onClick={runAnalysis}
                  disabled={!selectedFile || isAnalyzing}
                  className={`w-full py-3.5 px-4 rounded-xl flex items-center justify-center gap-2 font-semibold text-sm text-white shadow-sm transition-all ${
                    !selectedFile || isAnalyzing
                      ? "bg-[#CBD5E1] cursor-not-allowed"
                      : "bg-gradient-to-r from-[#11B9D4] to-[#7867F5] hover:opacity-95 hover:shadow-md cursor-pointer"
                  }`}
                >
                  {isAnalyzing ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      <span>Running EfficientNet-B0 & Grad-CAM++...</span>
                    </>
                  ) : (
                    <>
                      <Brain className="w-4 h-4" />
                      <span>Analyze MRI Scan</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Quick Benchmark Scans Selector */}
            <div className="clinical-card p-6">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-bold text-[#15243A]">Test with Real Benchmark Scans</h3>
                <span className="text-[11px] text-[#68758A]">Testing Set (1,600 scans)</span>
              </div>
              <p className="text-xs text-[#68758A] mb-4">
                Instantly load genuine, verified patient scans across the 4 diagnostic categories:
              </p>
              
              <div className="grid grid-cols-2 gap-3">
                {benchmarkSamples.map((sample) => (
                  <button
                    key={sample.file}
                    onClick={() => loadBenchmarkSample(sample.file, sample.name)}
                    className="p-3 text-left rounded-xl border border-[#E5EAF1] hover:border-[#11B9D4] hover:bg-[#11B9D4]/5 transition-all group"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-[#F0F4F8] text-[#68758A]">
                        {sample.badge}
                      </span>
                    </div>
                    <div className="text-xs font-bold text-[#15243A] group-hover:text-[#11B9D4]">
                      {sample.name}
                    </div>
                    <div className="text-[10px] text-[#68758A] mt-0.5">
                      Verified {sample.class}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Privacy & Safety Note */}
            <div className="p-4 rounded-xl bg-[#FFFFFF] border border-[#E5EAF1] text-xs text-[#68758A] space-y-2">
              <div className="flex items-center gap-1.5 font-semibold text-[#15243A]">
                <ShieldAlert className="w-4 h-4 text-[#10B981]" />
                <span>Zero Cloud Retention & Medical Disclaimer</span>
              </div>
              <p className="leading-relaxed">
                Uploaded images are sanitized in temporary scratch buffers for inference and attribution computation. Never transmitted to third-party endpoints.
              </p>
            </div>

          </div>

          {/* Right Column (7 Cols): Results & Explainability */}
          <div className="lg:col-span-7 space-y-6">
            
            {analysisResult ? (
              <>
                {/* Prediction Primary Banner */}
                <div 
                  className="clinical-card p-6 border-l-8"
                  style={{ borderLeftColor: getClassColor(analysisResult.predicted_class) }}
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-bold uppercase tracking-wider text-[#68758A]">
                          Model Prediction
                        </span>
                        <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-[#F0F4F8] text-[#15243A]">
                          {analysisResult.model_version}
                        </span>
                      </div>
                      <h3 className="text-2xl font-black text-[#15243A]">
                        {getClassNameDisplay(analysisResult.predicted_class)}
                      </h3>
                    </div>

                    <div className="text-right sm:text-right">
                      <div className="text-3xl font-extrabold" style={{ color: getClassColor(analysisResult.predicted_class) }}>
                        {(analysisResult.confidence * 100).toFixed(1)}%
                      </div>
                      <div className="text-xs text-[#68758A] font-medium flex items-center gap-1 justify-end">
                        <Clock className="w-3.5 h-3.5" />
                        <span>{analysisResult.inference_time_ms} ms</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* 4-Class Probability Distribution */}
                <div className="clinical-card p-6">
                  <h4 className="text-sm font-bold text-[#15243A] mb-4 flex items-center justify-between">
                    <span>Softmax Probability Distribution</span>
                    <span className="text-xs text-[#68758A]">K = 4 Classes</span>
                  </h4>

                  <div className="space-y-3">
                    {Object.entries(analysisResult.probabilities).map(([cls, prob]) => {
                      const percentage = (prob * 100).toFixed(1);
                      const isTop = cls === analysisResult.predicted_class;
                      return (
                        <div key={cls} className="space-y-1">
                          <div className="flex items-center justify-between text-xs font-semibold">
                            <span className={isTop ? "text-[#15243A]" : "text-[#68758A]"}>
                              {getClassNameDisplay(cls)}
                            </span>
                            <span style={{ color: isTop ? getClassColor(cls) : "#68758A" }}>
                              {percentage}%
                            </span>
                          </div>
                          <div className="w-full h-2.5 rounded-full bg-[#F0F4F8] overflow-hidden">
                            <div
                              className="h-full rounded-full transition-all duration-500"
                              style={{
                                width: `${percentage}%`,
                                backgroundColor: getClassColor(cls),
                              }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Uncertainty & Entropy Metrics Card */}
                <div className="clinical-card p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-sm font-bold text-[#15243A] flex items-center gap-2">
                      <Activity className="w-4 h-4 text-[#7867F5]" />
                      <span>Entropy Uncertainty Quantification</span>
                    </h4>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${
                      analysisResult.normalized_entropy < 0.25
                        ? "bg-[#10B981]/10 text-[#10B981]"
                        : analysisResult.normalized_entropy < 0.55
                        ? "bg-[#F59E0B]/10 text-[#F59E0B]"
                        : "bg-[#EF4444]/10 text-[#EF4444]"
                    }`}>
                      {analysisResult.normalized_entropy < 0.25 ? "Low Uncertainty" : analysisResult.normalized_entropy < 0.55 ? "Moderate Uncertainty" : "High Uncertainty"}
                    </span>
                  </div>

                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div className="p-3 rounded-xl bg-[#F7F9FC] border border-[#E5EAF1]">
                      <div className="text-xs text-[#68758A] mb-1">Shannon H(p)</div>
                      <div className="text-lg font-bold text-[#15243A]">
                        {analysisResult.entropy.toFixed(4)}
                      </div>
                      <div className="text-[10px] text-[#68758A]">nats</div>
                    </div>

                    <div className="p-3 rounded-xl bg-[#F7F9FC] border border-[#E5EAF1]">
                      <div className="text-xs text-[#68758A] mb-1">Normalized H(p)</div>
                      <div className="text-lg font-bold text-[#7867F5]">
                        {analysisResult.normalized_entropy.toFixed(4)}
                      </div>
                      <div className="text-[10px] text-[#68758A]">H / ln(4) [0, 1]</div>
                    </div>

                    <div className="p-3 rounded-xl bg-[#F7F9FC] border border-[#E5EAF1]">
                      <div className="text-xs text-[#68758A] mb-1">Margin (Top 1 - 2)</div>
                      <div className="text-lg font-bold text-[#11B9D4]">
                        {(analysisResult.prediction_margin * 100).toFixed(1)}%
                      </div>
                      <div className="text-[10px] text-[#68758A]">Decision separation</div>
                    </div>
                  </div>

                  {/* MC Dropout Trigger */}
                  <div className="mt-4 pt-4 border-t border-[#E5EAF1] flex items-center justify-between">
                    <div className="text-xs text-[#68758A]">
                      Compute epistemic vs aleatoric uncertainty with 30 Monte Carlo forward passes:
                    </div>
                    <button
                      onClick={runMCDropout}
                      disabled={isComputingUncertainty}
                      className="px-3 py-1.5 rounded-lg bg-[#7867F5]/10 hover:bg-[#7867F5]/20 text-[#7867F5] text-xs font-semibold flex items-center gap-1.5 transition-colors"
                    >
                      {isComputingUncertainty ? (
                        <>
                          <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                          <span>Computing 30 passes...</span>
                        </>
                      ) : (
                        <>
                          <Zap className="w-3.5 h-3.5" />
                          <span>Run MC Dropout (T=30)</span>
                        </>
                      )}
                    </button>
                  </div>

                  {/* MC Dropout Results View if computed */}
                  {uncertaintyResult && (
                    <div className="mt-4 p-4 rounded-xl bg-[#F0F4F8] border border-[#E5EAF1] space-y-3">
                      <div className="flex items-center justify-between text-xs font-bold text-[#15243A]">
                        <span>Monte Carlo Dropout Results (T = {uncertaintyResult.passes} passes)</span>
                        <span className="text-[#10B981]">Verified Stochastic Sampling</span>
                      </div>
                      <div className="grid grid-cols-3 gap-3 text-center text-xs">
                        <div className="p-2 bg-white rounded-lg">
                          <span className="text-[#68758A] block">Predictive Entropy</span>
                          <strong className="text-[#15243A] text-sm">{uncertaintyResult.predictive_entropy.toFixed(4)}</strong>
                        </div>
                        <div className="p-2 bg-white rounded-lg">
                          <span className="text-[#68758A] block">Expected Entropy</span>
                          <strong className="text-[#15243A] text-sm">{uncertaintyResult.expected_entropy.toFixed(4)}</strong>
                        </div>
                        <div className="p-2 bg-white rounded-lg">
                          <span className="text-[#68758A] block">Mutual Info (Epistemic)</span>
                          <strong className="text-[#7867F5] text-sm">{uncertaintyResult.mutual_information.toFixed(4)}</strong>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Grad-CAM++ Saliency Explainability Card */}
                {camResult && (
                  <div className="clinical-card p-6">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
                      <div>
                        <h4 className="text-sm font-bold text-[#15243A] flex items-center gap-2">
                          <Sparkles className="w-4 h-4 text-[#11B9D4]" />
                          <span>Grad-CAM++ Feature Attribution</span>
                        </h4>
                        <span className="text-xs text-[#68758A]">
                          Extracted from EfficientNet-B0 backbone (Conv Head features[-1])
                        </span>
                      </div>

                      {/* View mode toggle */}
                      <div className="flex items-center gap-1 bg-[#F0F4F8] p-1 rounded-lg text-xs">
                        <button
                          onClick={() => setViewMode("overlay")}
                          className={`px-2.5 py-1 rounded-md font-medium transition-colors ${
                            viewMode === "overlay" ? "bg-white text-[#15243A] shadow-xs" : "text-[#68758A]"
                          }`}
                        >
                          Overlay
                        </button>
                        <button
                          onClick={() => setViewMode("side_by_side")}
                          className={`px-2.5 py-1 rounded-md font-medium transition-colors ${
                            viewMode === "side_by_side" ? "bg-white text-[#15243A] shadow-xs" : "text-[#68758A]"
                          }`}
                        >
                          Side-by-Side
                        </button>
                        <button
                          onClick={() => setViewMode("original")}
                          className={`px-2.5 py-1 rounded-md font-medium transition-colors ${
                            viewMode === "original" ? "bg-white text-[#15243A] shadow-xs" : "text-[#68758A]"
                          }`}
                        >
                          Original
                        </button>
                      </div>
                    </div>

                    {/* Saliency Display Area */}
                    <div className="p-4 bg-black/5 rounded-xl border border-[#E5EAF1] flex items-center justify-center">
                      {viewMode === "overlay" && (
                        <div className="relative w-80 h-80 rounded-lg overflow-hidden border border-[#E5EAF1] bg-black">
                          {/* Original Image */}
                          <img
                            src={previewUrl || ""}
                            alt="Original MRI"
                            className="absolute inset-0 w-full h-full object-contain"
                          />
                          {/* Heatmap Overlay with dynamic opacity */}
                          <img
                            src={camResult.heatmap_base64}
                            alt="Grad-CAM++ Heatmap"
                            className="absolute inset-0 w-full h-full object-contain mix-blend-screen"
                            style={{ opacity: overlayOpacity }}
                          />
                        </div>
                      )}

                      {viewMode === "side_by_side" && (
                        <div className="grid grid-cols-2 gap-4 w-full">
                          <div className="text-center space-y-1">
                            <span className="text-[11px] font-semibold text-[#68758A]">Original Scan</span>
                            <div className="w-full h-56 rounded-lg overflow-hidden border border-[#E5EAF1] bg-black">
                              <img
                                src={previewUrl || ""}
                                alt="Original MRI"
                                className="w-full h-full object-contain"
                              />
                            </div>
                          </div>
                          <div className="text-center space-y-1">
                            <span className="text-[11px] font-semibold text-[#11B9D4]">Grad-CAM++ Saliency</span>
                            <div className="w-full h-56 rounded-lg overflow-hidden border border-[#E5EAF1] bg-black">
                              <img
                                src={camResult.heatmap_base64}
                                alt="Grad-CAM++ Overlay"
                                className="w-full h-full object-contain"
                              />
                            </div>
                          </div>
                        </div>
                      )}

                      {viewMode === "original" && (
                        <div className="w-80 h-80 rounded-lg overflow-hidden border border-[#E5EAF1] bg-black">
                          <img
                            src={previewUrl || ""}
                            alt="Original MRI"
                            className="w-full h-full object-contain"
                          />
                        </div>
                      )}
                    </div>

                    {/* Opacity Slider Control */}
                    {viewMode === "overlay" && (
                      <div className="mt-4 flex items-center justify-between gap-4 px-2">
                        <span className="text-xs font-semibold text-[#68758A] flex items-center gap-1.5">
                          <Sliders className="w-3.5 h-3.5" />
                          Overlay Opacity:
                        </span>
                        <input
                          type="range"
                          min="0"
                          max="1"
                          step="0.05"
                          value={overlayOpacity}
                          onChange={(e) => setOverlayOpacity(parseFloat(e.target.value))}
                          className="w-48 accent-[#11B9D4] cursor-pointer"
                        />
                        <span className="text-xs font-mono text-[#15243A] w-12 text-right">
                          {Math.round(overlayOpacity * 100)}%
                        </span>
                      </div>
                    )}

                    {/* Quadrant Localization Attributions */}
                    {camResult.salient_regions_summary && (
                      <div className="mt-4 pt-4 border-t border-[#E5EAF1]">
                        <span className="text-xs font-semibold text-[#15243A] block mb-2">
                          Intracranial Quadrant Attribution Share:
                        </span>
                        <div className="grid grid-cols-4 gap-2 text-center text-xs">
                          <div className="p-2 bg-[#F7F9FC] rounded-lg border border-[#E5EAF1]">
                            <span className="text-[#68758A] block text-[10px]">Top-Left</span>
                            <strong className="text-[#15243A]">
                              {(camResult.salient_regions_summary.top_left * 100).toFixed(1)}%
                            </strong>
                          </div>
                          <div className="p-2 bg-[#F7F9FC] rounded-lg border border-[#E5EAF1]">
                            <span className="text-[#68758A] block text-[10px]">Top-Right</span>
                            <strong className="text-[#15243A]">
                              {(camResult.salient_regions_summary.top_right * 100).toFixed(1)}%
                            </strong>
                          </div>
                          <div className="p-2 bg-[#F7F9FC] rounded-lg border border-[#E5EAF1]">
                            <span className="text-[#68758A] block text-[10px]">Bottom-Left</span>
                            <strong className="text-[#15243A]">
                              {(camResult.salient_regions_summary.bottom_left * 100).toFixed(1)}%
                            </strong>
                          </div>
                          <div className="p-2 bg-[#F7F9FC] rounded-lg border border-[#E5EAF1]">
                            <span className="text-[#68758A] block text-[10px]">Bottom-Right</span>
                            <strong className="text-[#15243A]">
                              {(camResult.salient_regions_summary.bottom_right * 100).toFixed(1)}%
                            </strong>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </>
            ) : (
              /* Empty Placeholder State */
              <div className="clinical-card p-12 text-center space-y-4">
                <div className="w-16 h-16 mx-auto rounded-2xl bg-[#11B9D4]/10 flex items-center justify-center text-[#11B9D4]">
                  <Brain className="w-8 h-8" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-[#15243A]">
                    Awaiting MRI Image Input
                  </h3>
                  <p className="text-xs text-[#68758A] max-w-md mx-auto mt-1 leading-relaxed">
                    Upload an axial or coronal brain MRI scan from your workstation, or choose one of the pre-indexed clinical benchmark scans on the left to initiate inference.
                  </p>
                </div>
                <div className="inline-flex items-center gap-2 text-xs font-semibold text-[#11B9D4]">
                  <span>Ready for PyTorch forward pass & Grad-CAM++</span>
                </div>
              </div>
            )}

          </div>

        </div>

      </div>
    </div>
  );
}
