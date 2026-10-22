/**
 * NeuroScan XAI API Client
 * Interfaces directly with the FastAPI backend on http://localhost:8000
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface AnalysisResponseData {
  analysis_id: string;
  filename: string;
  predicted_class: "glioma" | "meningioma" | "pituitary" | "notumor";
  confidence: number;
  probabilities: {
    glioma: number;
    meningioma: number;
    pituitary: number;
    notumor: number;
  };
  entropy: number;
  normalized_entropy: number;
  prediction_margin: number;
  inference_time_ms: number;
  model_version: string;
  gradcam_path?: string;
}

export interface ExplainabilityResponseData {
  analysis_id?: string;
  target_class: string;
  target_class_idx: number;
  confidence: number;
  method: string;
  heatmap_path: string;
  heatmap_url: string;
  heatmap_base64: string;
  salient_regions_summary: {
    top_right: number;
    top_left: number;
    bottom_left: number;
    bottom_right: number;
  };
  localization_notes?: string;
}

export interface UncertaintyResponseData {
  analysis_id?: string;
  passes: number;
  mean_probabilities: Record<string, number>;
  variance: Record<string, number>;
  standard_deviation: Record<string, number>;
  confidence_interval: Record<string, [number, number]>;
  predictive_entropy: number;
  expected_entropy: number;
  mutual_information: number;
}

export interface EvaluationData {
  model_id: string;
  model_name: string;
  dataset_name: string;
  test_samples: number;
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  roc_auc: number;
  ece: number;
  confusion_matrix: number[][];
  class_labels: string[];
  class_metrics: Record<
    string,
    {
      precision: number;
      recall: number;
      f1_score: number;
      support: number;
    }
  >;
  evaluation_date?: string;
}

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/api/health`, { cache: "no-store" });
  if (!res.ok) throw new Error("Backend offline");
  return res.json();
}

export async function fetchModelStatus() {
  const res = await fetch(`${API_BASE}/api/model/status`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch model status");
  return res.json();
}

export async function fetchDatasetStatus() {
  const res = await fetch(`${API_BASE}/api/dataset/status`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch dataset status");
  return res.json();
}

export async function analyzeScan(file: File, generateCam = true): Promise<AnalysisResponseData> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/api/analyze?generate_cam=${generateCam}`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Inference error: ${res.statusText}`);
  }
  return res.json();
}

export async function generateExplainability(
  file?: File,
  analysisId?: string,
  targetClass?: string,
  method = "gradcam++"
): Promise<ExplainabilityResponseData> {
  const formData = new FormData();
  if (file) formData.append("file", file);
  if (analysisId) formData.append("analysis_id", analysisId);
  if (targetClass) formData.append("target_class", targetClass);
  formData.append("method", method);

  const res = await fetch(`${API_BASE}/api/explain`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Explainability error: ${res.statusText}`);
  }
  return res.json();
}

export async function calculateUncertainty(
  file?: File,
  analysisId?: string,
  passes = 30
): Promise<UncertaintyResponseData> {
  const formData = new FormData();
  if (file) formData.append("file", file);
  if (analysisId) formData.append("analysis_id", analysisId);
  formData.append("passes", passes.toString());

  const res = await fetch(`${API_BASE}/api/uncertainty`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Uncertainty error: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchEvaluationMetrics(): Promise<EvaluationData> {
  const res = await fetch(`${API_BASE}/api/evaluation`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error("Failed to fetch evaluation metrics");
  }
  return res.json();
}

export async function fetchFairnessAudit() {
  const res = await fetch(`${API_BASE}/api/audits/fairness`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model_id: "efficientnet-b0-v1",
      disparate_impact_threshold: 0.8,
    }),
  });
  if (!res.ok) throw new Error("Failed to run fairness audit");
  return res.json();
}

export async function fetchShortcutAudit() {
  const res = await fetch(`${API_BASE}/api/audits/shortcut`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model_id: "efficientnet-b0-v1",
    }),
  });
  if (!res.ok) throw new Error("Failed to run shortcut audit");
  return res.json();
}
