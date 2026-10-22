// ClarityNeuro — Core TypeScript types

export interface HealthStatus {
  status: string;
  model_loaded: boolean;
  dataset_available: boolean;
  database_connected: boolean;
  timestamp: string;
}

export interface ModelStatus {
  available: boolean;
  architecture?: string;
  num_classes?: number;
  class_mapping?: Record<string, string>;
  checkpoint_path?: string;
  parameter_count?: number;
  error?: string;
}

export interface DatasetStatus {
  available: boolean;
  total_images?: number;
  class_distribution?: Record<string, number>;
  splits?: Record<string, number>;
  validation_status?: string;
  source?: string;
  error?: string;
}

export interface AnalysisResult {
  analysis_id: string;
  predicted_class: string;
  confidence: number;
  probabilities: Record<string, number>;
  entropy: number;
  normalized_entropy: number;
  prediction_margin: number;
  inference_time_ms: number;
  model_version: string;
  created_at?: string;
  filename?: string;
}

export interface ExplainabilityResult {
  predicted_class: string;
  target_class: string;
  confidence: number;
  heatmap_overlay: string; // base64
  heatmap_only: string; // base64
  original_image: string; // base64
}

export interface UncertaintyResult {
  predicted_class: string;
  probabilities: Record<string, number>;
  entropy: number;
  normalized_entropy: number;
  prediction_margin: number;
  mc_dropout?: {
    mean_probabilities: Record<string, number>;
    std_per_class: Record<string, number>;
    predictive_entropy: number;
    mutual_information: number;
    n_passes: number;
  };
}

export interface FairnessResult {
  status: string;
  subgroup_column?: string;
  results?: SubgroupMetrics[];
  max_performance_gap?: number;
  message?: string;
}

export interface SubgroupMetrics {
  group: string;
  sample_count: number;
  accuracy: number;
  macro_f1: number;
  sensitivity?: Record<string, number>;
  specificity?: Record<string, number>;
  warning?: string;
}

export interface ShortcutAuditResult {
  visual_artifacts: {
    has_bright_borders: boolean;
    has_corner_text: boolean;
    border_intensity_mean: number;
    background_uniformity: number;
  };
  perturbation_results: {
    original_prediction: string;
    original_confidence: number;
    border_masked_confidence: number;
    corner_masked_confidence: number;
    prediction_changed: boolean;
    max_confidence_drop: number;
  };
}

export interface AnalysisHistoryItem {
  analysis_id: string;
  filename: string;
  predicted_class: string;
  confidence: number;
  entropy: number;
  normalized_entropy: number;
  model_version: string;
  created_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface EvaluationMetrics {
  accuracy: number;
  balanced_accuracy: number;
  per_class_metrics: Record<string, {
    precision: number;
    recall: number;
    f1: number;
    support: number;
  }>;
  macro_f1: number;
  weighted_f1: number;
  confusion_matrix: number[][];
  log_loss: number;
  parameter_count: number;
  checkpoint_id: string;
  evaluation_split: string;
}

export interface ExperimentRecord {
  id: string;
  name: string;
  experiment_type: string;
  config: Record<string, unknown>;
  results: Record<string, unknown>;
  model_id?: string;
  dataset_id?: string;
  status: string;
  created_at: string;
  completed_at?: string;
}

export interface ModelRegistryEntry {
  id: string;
  name: string;
  architecture: string;
  num_classes: number;
  class_mapping: Record<string, string>;
  checkpoint_path: string;
  is_active: boolean;
  created_at: string;
  metrics?: Record<string, unknown>;
}

export type TumorClass = 'glioma' | 'meningioma' | 'pituitary' | 'notumor';

export const CLASS_LABELS: Record<TumorClass, string> = {
  glioma: 'Glioma',
  meningioma: 'Meningioma',
  pituitary: 'Pituitary',
  notumor: 'No Tumor',
};

export const CLASS_COLORS: Record<TumorClass, string> = {
  glioma: '#6366f1',
  meningioma: '#8b5cf6',
  pituitary: '#06b6d4',
  notumor: '#10b981',
};
