/* eslint-disable @typescript-eslint/no-explicit-any */
export interface TimeSeriesDataPoint {
  timestamp: string;
  features: Record<string, number>;
}

export interface PredictionRequest {
  model_name: string;
  tipping_element: string;
  sequence: TimeSeriesDataPoint[];
  return_attention_weights?: boolean;
  return_uncertainty?: boolean;
}

export interface TippingAlert {
  alarm_triggered: boolean;
  alert_level: "NORMAL" | "WATCH" | "WARNING" | "CRITICAL";
  threshold: number;
  estimated_lead_time_steps: number | null;
}

export interface PredictionResponse {
  model_name: string;
  tipping_element: string;
  tipping_probability: number;
  alert: TippingAlert;
  uncertainty?: {
    std: number;
    lower_95: number;
    upper_95: number;
  } | null;
  interpretability?: {
    feature_importance?: Record<string, number>;
    ar1_critical_slowing_down?: number;
    [key: string]: any;
  } | null;
  metadata: {
    latency_ms: number;
    timestamp: string;
    sequence_length?: number;
    model_version?: string;
    [key: string]: any;
  };
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  gpu_available: boolean;
  device_count: number;
  registered_models: string[];
}

export interface ModelsResponse {
  models: string[];
}

/* UI & Domain Extension Types */

export type AlertLevel = "NORMAL" | "WATCH" | "WARNING" | "CRITICAL";

export interface TippingElementMetadata {
  id: string;
  name: string;
  shortName: string;
  region: string;
  coordinates: [number, number]; // [lat, lng]
  riskScore: number; // 0.0 to 1.0
  tempAnomaly: number; // in °C
  vegetationLoss?: number; // in %
  oceanCirculationAnomaly?: number; // in Sverdrups (Sv) or %
  iceLossRate?: number; // in Gt/year
  confidenceScore: number; // 0.0 to 1.0
  leadTimeMonths: number;
  status: AlertLevel;
  description: string;
  importantVariables: string[];
  recentAnomalies: string;
  supportingDatasets: string[];
  historicalTrend: { year: number; val: number; anomaly: number }[];
}

export interface ModelSpecification {
  id: string;
  name: string;
  category: "Transformer" | "GNN" | "Physics & Causal" | "Baseline";
  description: string;
  parameters: string;
  latencyMs: number;
  rocAuc: number;
  prAuc: number;
  f1Score: number;
  leadTimeAccuracy: string;
  architectureDetails: string[];
  strengths?: string[];
  hyperparameters: Record<string, any>;
}

export type ModelMetadata = ModelSpecification;

export interface DatasetMetadata {
  id: string;
  name: string;
  source: string;
  coverage: string;
  temporalResolution: string;
  spatialResolution: string;
  dateRange: string;
  variables: string[];
  status: "Active" | "Syncing" | "Archived";
  size: string;
  records: number;
}

export interface JobItem {
  id: string;
  elementId: string;
  modelId: string;
  status: "queued" | "running" | "completed" | "failed";
  progress: number;
  startTime: string;
  result?: PredictionResponse;
  logs: string[];
}
