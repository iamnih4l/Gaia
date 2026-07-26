import {
  HealthResponse,
  ModelsResponse,
  PredictionRequest,
  PredictionResponse,
  TippingAlert,
} from "@/types/api";
import { API_BASE_URL, TIPPING_ELEMENTS, MODEL_ZOO } from "@/constants";

class ApiService {
  private baseUrl: string;
  private forceSimulation: boolean;

  constructor() {
    this.baseUrl = API_BASE_URL;
    this.forceSimulation = false;
  }

  public setSimulationMode(enabled: boolean) {
    this.forceSimulation = enabled;
  }

  public getSimulationMode(): boolean {
    return this.forceSimulation;
  }

  private async fetchWithTimeout(url: string, options: RequestInit = {}, timeoutMs = 4000): Promise<Response> {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
      });
      clearTimeout(id);
      return response;
    } catch (error) {
      clearTimeout(id);
      throw error;
    }
  }

  public async getHealth(): Promise<HealthResponse> {
    if (this.forceSimulation) {
      return this.simulateHealth();
    }
    try {
      const res = await this.fetchWithTimeout(`${this.baseUrl}/health`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      console.warn("Backend API unreachable, using research simulation mode:", err);
      return this.simulateHealth();
    }
  }

  public async getModels(): Promise<ModelsResponse> {
    if (this.forceSimulation) {
      return { models: MODEL_ZOO.map((m) => m.id) };
    }
    try {
      const res = await this.fetchWithTimeout(`${this.baseUrl}/models`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      return { models: MODEL_ZOO.map((m) => m.id) };
    }
  }

  public async predict(request: PredictionRequest): Promise<PredictionResponse> {
    if (this.forceSimulation) {
      return this.simulatePrediction(request);
    }
    try {
      const res = await this.fetchWithTimeout(`${this.baseUrl}/predict`, {
        method: "POST",
        body: JSON.stringify(request),
      }, 10000); // 10s timeout for inference
      if (!res.ok) {
        const errText = await res.text();
        throw new Error(`API Inference Error (${res.status}): ${errText}`);
      }
      return await res.json();
    } catch (err) {
      console.warn("Inference API fallback triggered, generating simulated research prediction:", err);
      return this.simulatePrediction(request);
    }
  }

  /* Simulated Research-Grade Telemetry Fallbacks */

  private async simulateHealth(): Promise<HealthResponse> {
    await new Promise((r) => setTimeout(r, 200));
    return {
      status: "healthy (simulated)",
      timestamp: new Date().toISOString(),
      gpu_available: true,
      device_count: 2,
      registered_models: MODEL_ZOO.map((m) => m.id),
    };
  }

  private async simulatePrediction(req: PredictionRequest): Promise<PredictionResponse> {
    await new Promise((r) => setTimeout(r, 600 + Math.random() * 400));

    const elementMeta = TIPPING_ELEMENTS.find((e) => e.id === req.tipping_element) || TIPPING_ELEMENTS[0];
    const baseProb = elementMeta.riskScore + (Math.random() * 0.08 - 0.04);
    const prob = Math.max(0.05, Math.min(0.98, baseProb));

    let alertLevel: "NORMAL" | "WATCH" | "WARNING" | "CRITICAL" = "NORMAL";
    let leadTime: number | null = null;

    if (prob >= 0.8) {
      alertLevel = "CRITICAL";
      leadTime = Math.max(2, elementMeta.leadTimeMonths - 4);
    } else if (prob >= 0.65) {
      alertLevel = "WARNING";
      leadTime = elementMeta.leadTimeMonths;
    } else if (prob >= 0.5) {
      alertLevel = "WATCH";
      leadTime = elementMeta.leadTimeMonths + 8;
    }

    const alert: TippingAlert = {
      alarm_triggered: prob >= 0.5,
      alert_level: alertLevel,
      threshold: 0.5,
      estimated_lead_time_steps: leadTime,
    };

    let uncertainty = null;
    if (req.return_uncertainty) {
      const std = 0.04 + 0.08 * (1 - Math.abs(prob - 0.5) * 2);
      uncertainty = {
        std: Number(std.toFixed(4)),
        lower_95: Number(Math.max(0, prob - 1.96 * std).toFixed(4)),
        upper_95: Number(Math.min(1, prob + 1.96 * std).toFixed(4)),
      };
    }

    let interpretability = null;
    if (req.return_attention_weights && req.sequence.length > 0) {
      const featNames = Object.keys(req.sequence[0].features || { val_0: 1, val_1: 1 });
      const rawWeights = featNames.map(() => Math.random() + 0.2);
      const sum = rawWeights.reduce((a, b) => a + b, 0);
      const featImp: Record<string, number> = {};
      featNames.forEach((name, idx) => {
        featImp[name] = Number((rawWeights[idx] / sum).toFixed(4));
      });
      interpretability = {
        feature_importance: featImp,
        ar1_critical_slowing_down: Number((0.45 + Math.random() * 0.4).toFixed(4)),
        dfa_scaling_exponent: Number((1.15 + Math.random() * 0.3).toFixed(4)),
        rolling_variance_trend: "+34.2% over 24 mo",
      };
    }

    return {
      model_name: req.model_name,
      tipping_element: req.tipping_element,
      tipping_probability: Number(prob.toFixed(4)),
      alert,
      uncertainty,
      interpretability,
      metadata: {
        latency_ms: Number((35 + Math.random() * 25).toFixed(2)),
        timestamp: new Date().toISOString(),
        sequence_length: req.sequence.length,
        model_version: "1.0.0-prod (simulated)",
        execution_device: "NVIDIA A100-SXM4-80GB (simulated)",
      },
    };
  }
}

export const apiService = new ApiService();
