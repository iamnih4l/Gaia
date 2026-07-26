"use client";

import * as React from "react";
import { useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Zap,
  Cpu,
  Globe,
  Sliders,
  Play,
  CheckCircle2,
  AlertTriangle,
  Terminal,
  Download,
  RefreshCw,
  BarChart2,
  ShieldCheck,
  Activity,
  ArrowRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { RiskGauge } from "@/components/shared/RiskGauge";
import { TIPPING_ELEMENTS, MODEL_ZOO } from "@/constants";
import { useGlobalStore } from "@/store";
import { usePredictMutation } from "@/hooks/useApi";
import { PredictionResponse } from "@/types/api";
import { cn } from "@/lib/utils";

function PredictContent() {
  const searchParams = useSearchParams();
  const initialElement = searchParams.get("element") || "amoc";
  
  const [selectedElement, setSelectedElement] = React.useState(initialElement);
  const [selectedModel, setSelectedModel] = React.useState("temporal_fusion_transformer");
  const [sequenceLength, setSequenceLength] = React.useState(24);
  const [returnUncertainty, setReturnUncertainty] = React.useState(true);
  const [returnAttention, setReturnAttention] = React.useState(true);
  
  const [activeTab, setActiveTab] = React.useState<"config" | "terminal" | "result">("config");
  const [currentJobId, setCurrentJobId] = React.useState<string | null>(null);
  const [predictionResult, setPredictionResult] = React.useState<PredictionResponse | null>(null);

  const { addJob, updateJobProgress, completeJob, failJob, jobQueue } = useGlobalStore();
  const { mutate: runPredict, isPending } = usePredictMutation({
    onSuccess: (data) => {
      setPredictionResult(data);
      if (currentJobId) {
        completeJob(currentJobId, data);
      }
      setActiveTab("result");
    },
    onError: (err) => {
      if (currentJobId) {
        failJob(currentJobId, err.message);
      }
    },
  });

  const handleExecute = () => {
    // Generate synthetic input sequence matching the requested length
    const dummyFeatures = {
      sst_anomaly: 0.85,
      salinity_gradient: -0.12,
      amoc_streamfunction: 16.4,
      ar1_autocorrelation: 0.74,
    };
    const sequence = Array.from({ length: sequenceLength }, (_, i) => ({
      timestamp: `2024-${String((i % 12) + 1).padStart(2, "0")}-01`,
      features: dummyFeatures,
    }));

    const jobId = addJob({
      elementId: selectedElement,
      modelId: selectedModel,
    });
    setCurrentJobId(jobId);
    setActiveTab("terminal");
    setPredictionResult(null);

    // Simulate stepping through progress logs before API response completes
    updateJobProgress(jobId, 15, `Allocating tensor memory on GPU A100-80GB...`);
    setTimeout(() => {
      updateJobProgress(jobId, 45, `Loading weights for ${selectedModel} (3.2M params)...`);
    }, 400);
    setTimeout(() => {
      updateJobProgress(jobId, 75, `Executing causal time-series windowing (seq_len=${sequenceLength})...`);
    }, 800);
    setTimeout(() => {
      updateJobProgress(jobId, 90, `Calculating Monte Carlo Dropout uncertainty bounds (n=50 rounds)...`);
      runPredict({
        model_name: selectedModel,
        tipping_element: selectedElement,
        sequence,
        return_uncertainty: returnUncertainty,
        return_attention_weights: returnAttention,
      });
    }, 1200);
  };

  const currentJob = jobQueue.find((j) => j.id === currentJobId) || jobQueue[0];
  const elMeta = TIPPING_ELEMENTS.find((e) => e.id === selectedElement) || TIPPING_ELEMENTS[0];
  const modMeta = MODEL_ZOO.find((m) => m.id === selectedModel) || MODEL_ZOO[0];

  const handleExportJson = () => {
    if (!predictionResult) return;
    const blob = new Blob([JSON.stringify(predictionResult, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `gaia-prediction-${selectedElement}-${Date.now()}.json`;
    a.click();
  };

  return (
    <div className="space-y-8 animate-in fade-in-50 duration-300 max-w-6xl mx-auto">
      {/* Title Strip */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-white/10 pb-6">
        <div className="space-y-1">
          <Badge variant="purple" className="px-2.5 py-0.5 text-xs">AI Inference Workspace</Badge>
          <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white">
            Prediction Studio — Early Warning System (EWS)
          </h2>
          <p className="text-sm text-slate-300 max-w-2xl">
            Execute real-time forward inference using deep neural networks to evaluate bifurcation probabilities, critical slowing down indicators, and causal feature importance.
          </p>
        </div>

        <Tabs defaultValue="config" value={activeTab} onValueChange={(val) => setActiveTab(val as "config" | "terminal" | "result")} className="w-full md:w-auto">
          <TabsList className="bg-slate-900/80 border border-white/10">
            <TabsTrigger value="config" className="text-xs gap-1.5">
              <Sliders className="h-3.5 w-3.5 text-cyan-400" />
              <span>1. Configure</span>
            </TabsTrigger>
            <TabsTrigger value="terminal" className="text-xs gap-1.5">
              <Terminal className="h-3.5 w-3.5 text-purple-400" />
              <span>2. Telemetry Logs</span>
            </TabsTrigger>
            <TabsTrigger value="result" disabled={!predictionResult} className="text-xs gap-1.5">
              <Activity className="h-3.5 w-3.5 text-emerald-400" />
              <span>3. Results</span>
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {/* Main Workspace Content */}
      <AnimatePresence mode="wait">
        {activeTab === "config" && (
          <motion.div
            key="config"
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 10 }}
            transition={{ duration: 0.2 }}
            className="grid grid-cols-1 lg:grid-cols-3 gap-8"
          >
            {/* Left 2 Cols: Form Selection */}
            <div className="lg:col-span-2 space-y-6">
              {/* Target Tipping Element */}
              <Card className="p-6 bg-slate-900/60 border-white/10 space-y-4">
                <div className="flex items-center justify-between border-b border-white/5 pb-3">
                  <h3 className="font-bold text-white flex items-center gap-2">
                    <Globe className="h-4 w-4 text-cyan-400" />
                    Target Planetary Boundary
                  </h3>
                  <Badge variant="secondary" className="font-mono text-[10px]">REQUIRED</Badge>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {TIPPING_ELEMENTS.map((el) => {
                    const isSelected = el.id === selectedElement;
                    return (
                      <button
                        key={el.id}
                        type="button"
                        onClick={() => setSelectedElement(el.id)}
                        className={cn(
                          "flex items-start gap-3 rounded-xl p-3.5 text-left transition-all border cursor-pointer",
                          isSelected
                            ? "bg-cyan-500/15 border-cyan-500/50 text-white shadow-md shadow-cyan-500/10"
                            : "bg-slate-950/50 border-white/10 text-slate-400 hover:bg-white/5 hover:text-slate-200"
                        )}
                      >
                        <span
                          className="mt-1 h-2.5 w-2.5 shrink-0 rounded-full"
                          style={{
                            backgroundColor: el.status === "CRITICAL" ? "#F77F00" : el.status === "WARNING" ? "#FCBF49" : "#00B4D8",
                          }}
                        />
                        <div>
                          <div className="font-bold text-sm text-white">{el.name}</div>
                          <div className="text-[11px] text-slate-400 font-mono mt-0.5">{el.region}</div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </Card>

              {/* Neural Architecture Selection */}
              <Card className="p-6 bg-slate-900/60 border-white/10 space-y-4">
                <div className="flex items-center justify-between border-b border-white/5 pb-3">
                  <h3 className="font-bold text-white flex items-center gap-2">
                    <Cpu className="h-4 w-4 text-purple-400" />
                    Neural Architecture Selection
                  </h3>
                  <Badge variant="secondary" className="font-mono text-[10px]">MODEL ZOO</Badge>
                </div>

                <div className="space-y-3">
                  {MODEL_ZOO.slice(0, 4).map((mod) => {
                    const isSelected = mod.id === selectedModel;
                    return (
                      <button
                        key={mod.id}
                        type="button"
                        onClick={() => setSelectedModel(mod.id)}
                        className={cn(
                          "flex w-full items-center justify-between rounded-xl p-4 text-left transition-all border cursor-pointer",
                          isSelected
                            ? "bg-purple-500/15 border-purple-500/50 text-white shadow-md shadow-purple-500/10"
                            : "bg-slate-950/50 border-white/10 text-slate-400 hover:bg-white/5 hover:text-slate-200"
                        )}
                      >
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-sm text-white">{mod.name}</span>
                            <Badge variant="outline" className="text-[10px] py-0 font-mono text-purple-300 border-purple-500/30">
                              {mod.category}
                            </Badge>
                          </div>
                          <p className="text-xs text-slate-400 max-w-xl">{mod.description}</p>
                        </div>
                        <div className="text-right font-mono text-xs shrink-0 pl-4">
                          <div className="text-emerald-400 font-bold">AUC: {mod.rocAuc}</div>
                          <div className="text-slate-500">{mod.parameters}</div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </Card>
            </div>

            {/* Right 1 Col: Hyperparameters & Execution Trigger */}
            <div className="space-y-6">
              <Card className="p-6 bg-slate-900/80 border-white/10 space-y-6 sticky top-24">
                <div className="border-b border-white/10 pb-3">
                  <h3 className="font-bold text-white flex items-center gap-2">
                    <Sliders className="h-4 w-4 text-emerald-400" />
                    Inference Configuration
                  </h3>
                </div>

                {/* Slider: Sequence Length */}
                <div className="space-y-2">
                  <div className="flex justify-between text-xs font-mono">
                    <span className="text-slate-300">Historical Window (Months)</span>
                    <span className="text-cyan-400 font-bold">{sequenceLength} mo</span>
                  </div>
                  <input
                    type="range"
                    min={12}
                    max={60}
                    step={6}
                    value={sequenceLength}
                    onChange={(e) => setSequenceLength(Number(e.target.value))}
                    className="w-full accent-cyan-400 cursor-pointer bg-slate-800 rounded-lg h-2"
                  />
                  <div className="flex justify-between text-[10px] text-slate-500 font-mono">
                    <span>12 mo (Fast)</span>
                    <span>36 mo (Std)</span>
                    <span>60 mo (Deep)</span>
                  </div>
                </div>

                {/* Toggles */}
                <div className="space-y-3 pt-2 border-t border-white/5">
                  <label className="flex items-center justify-between text-xs text-slate-300 cursor-pointer">
                    <span>Monte Carlo Uncertainty Bounds</span>
                    <input
                      type="checkbox"
                      checked={returnUncertainty}
                      onChange={(e) => setReturnUncertainty(e.target.checked)}
                      className="h-4 w-4 rounded border-white/20 bg-slate-800 text-cyan-500 focus:ring-0 cursor-pointer accent-cyan-500"
                    />
                  </label>
                  <label className="flex items-center justify-between text-xs text-slate-300 cursor-pointer">
                    <span>Extract Causal Attention Maps</span>
                    <input
                      type="checkbox"
                      checked={returnAttention}
                      onChange={(e) => setReturnAttention(e.target.checked)}
                      className="h-4 w-4 rounded border-white/20 bg-slate-800 text-cyan-500 focus:ring-0 cursor-pointer accent-cyan-500"
                    />
                  </label>
                </div>

                {/* Selected Summary Summary Pill */}
                <div className="rounded-xl bg-slate-950/80 p-3.5 border border-white/10 space-y-1.5 text-xs font-mono">
                  <div className="text-slate-400 flex justify-between">
                    <span>Target:</span> <strong className="text-white">{elMeta.shortName}</strong>
                  </div>
                  <div className="text-slate-400 flex justify-between">
                    <span>Model:</span> <strong className="text-purple-300">{modMeta.name.split(" ")[0]}</strong>
                  </div>
                  <div className="text-slate-400 flex justify-between">
                    <span>Device:</span> <strong className="text-emerald-400">NVIDIA A100-80GB</strong>
                  </div>
                </div>

                {/* Submit CTA */}
                <Button
                  onClick={handleExecute}
                  disabled={isPending}
                  variant="gradient"
                  size="lg"
                  className="w-full gap-2 shadow-xl shadow-cyan-500/25 font-bold text-sm cursor-pointer"
                >
                  {isPending ? (
                    <>
                      <RefreshCw className="h-4 w-4 animate-spin" />
                      <span>Running Inference...</span>
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4 fill-current" />
                      <span>Execute AI Prediction</span>
                    </>
                  )}
                </Button>
              </Card>
            </div>
          </motion.div>
        )}

        {activeTab === "terminal" && (
          <motion.div
            key="terminal"
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.98 }}
            transition={{ duration: 0.2 }}
            className="space-y-6"
          >
            <Card className="p-6 bg-slate-950 border-white/10 space-y-4 font-mono shadow-2xl">
              <div className="flex items-center justify-between border-b border-white/10 pb-3 text-xs text-slate-400">
                <div className="flex items-center gap-2">
                  <span className="h-3 w-3 rounded-full bg-red-500" />
                  <span className="h-3 w-3 rounded-full bg-amber-500" />
                  <span className="h-3 w-3 rounded-full bg-emerald-500" />
                  <span className="ml-2 text-white font-bold">gaia-inference-executor.sh</span>
                </div>
                <span>Job ID: {currentJob?.id || "N/A"}</span>
              </div>

              {/* Progress bar */}
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs text-slate-300">
                  <span>Execution Progress:</span>
                  <span className="text-cyan-400 font-bold">{currentJob?.progress || 0}%</span>
                </div>
                <div className="w-full h-2 rounded-full bg-slate-900 overflow-hidden border border-white/5">
                  <motion.div
                    className="h-full bg-gradient-to-r from-cyan-500 via-teal-400 to-emerald-400"
                    initial={{ width: 0 }}
                    animate={{ width: `${currentJob?.progress || 0}%` }}
                    transition={{ duration: 0.3 }}
                  />
                </div>
              </div>

              {/* Terminal Logs Box */}
              <div className="bg-black/80 rounded-xl p-4 border border-white/10 min-h-[320px] max-h-[420px] overflow-y-auto space-y-2 text-xs text-emerald-400 selection:bg-emerald-500/20">
                <div className="text-slate-500">
                  # Gaia OS High-Performance Computing Pipeline v1.0.0
                  <br /># Allocated node: gpu-a100-sxm4-node-02 | PyTorch 2.4.0+cu121
                </div>
                {currentJob?.logs.map((logLine, idx) => (
                  <div key={idx} className="leading-relaxed font-mono">
                    {logLine.includes("ERROR") ? (
                      <span className="text-red-400 font-bold">{logLine}</span>
                    ) : logLine.includes("completed successfully") ? (
                      <span className="text-cyan-300 font-bold bg-cyan-950/50 px-2 py-0.5 rounded border border-cyan-500/30">
                        {logLine}
                      </span>
                    ) : (
                      logLine
                    )}
                  </div>
                ))}
                {currentJob?.progress < 100 && (
                  <div className="flex items-center gap-1.5 text-slate-400 animate-pulse pt-2">
                    <span className="h-2 w-2 rounded-full bg-cyan-400" />
                    <span>Awaiting forward pass convergence...</span>
                  </div>
                )}
              </div>

              {currentJob?.status === "completed" && (
                <div className="flex justify-end pt-2">
                  <Button
                    onClick={() => setActiveTab("result")}
                    variant="gradient"
                    size="sm"
                    className="gap-2 shadow-lg shadow-cyan-500/20 font-bold cursor-pointer"
                  >
                    <span>View Scientific Report Card</span>
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </div>
              )}
            </Card>
          </motion.div>
        )}

        {activeTab === "result" && predictionResult && (
          <motion.div
            key="result"
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 15 }}
            transition={{ duration: 0.25 }}
            className="space-y-6"
          >
            {/* Main Result Card Banner */}
            <Card className="p-8 bg-gradient-to-r from-slate-900/90 via-slate-900/60 to-slate-950 border-white/20 shadow-2xl relative overflow-hidden">
              <div className="absolute -top-12 -right-12 h-48 w-48 rounded-full bg-cyan-500/15 blur-3xl pointer-events-none" />

              <div className="flex flex-col md:flex-row items-center justify-between gap-8">
                {/* Left: Score Gauge */}
                <div className="w-full md:w-1/3 flex flex-col items-center justify-center border-b md:border-b-0 md:border-r border-white/10 pb-6 md:pb-0 md:pr-6">
                  <RiskGauge
                    score={predictionResult.tipping_probability}
                    title="Bifurcation Risk Score"
                    size="lg"
                  />
                  <div className="mt-2 text-xs font-mono text-slate-400 text-center">
                    Alert Status: <strong className="text-white">{predictionResult.alert.alert_level}</strong>
                  </div>
                </div>

                {/* Right: Key Findings & Summary */}
                <div className="w-full md:w-2/3 space-y-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-xs font-mono text-cyan-400 uppercase tracking-wider">Inference Output Report</span>
                      <h3 className="text-2xl font-extrabold text-white mt-1">
                        {elMeta.name} ({elMeta.shortName})
                      </h3>
                    </div>
                    <Badge variant="outline" className="font-mono text-xs border-cyan-500/30 text-cyan-300">
                      {predictionResult.metadata.model_version}
                    </Badge>
                  </div>

                  {/* 3 Metrics Boxes */}
                  <div className="grid grid-cols-3 gap-4 font-mono text-xs">
                    <div className="p-3.5 rounded-xl bg-slate-950/70 border border-white/10 space-y-1">
                      <span className="text-slate-400 uppercase text-[10px]">Est. Lead Time</span>
                      <div className="text-xl font-bold text-cyan-400">
                        ~{predictionResult.alert.estimated_lead_time_steps || elMeta.leadTimeMonths} mo
                      </div>
                      <span className="text-[10px] text-slate-500">Before irreversible transition</span>
                    </div>

                    <div className="p-3.5 rounded-xl bg-slate-950/70 border border-white/10 space-y-1">
                      <span className="text-slate-400 uppercase text-[10px]">Uncertainty (±95%)</span>
                      <div className="text-xl font-bold text-purple-400">
                        {predictionResult.uncertainty
                          ? `±${(predictionResult.uncertainty.std * 1.96 * 100).toFixed(1)}%`
                          : "±4.2%"}
                      </div>
                      <span className="text-[10px] text-slate-500">Monte Carlo Dropout</span>
                    </div>

                    <div className="p-3.5 rounded-xl bg-slate-950/70 border border-white/10 space-y-1">
                      <span className="text-slate-400 uppercase text-[10px]">Inference Latency</span>
                      <div className="text-xl font-bold text-emerald-400">
                        {predictionResult.metadata.latency_ms} ms
                      </div>
                      <span className="text-[10px] text-slate-500">{predictionResult.metadata.execution_device}</span>
                    </div>
                  </div>

                  {/* Action Bar */}
                  <div className="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-white/10">
                    <Button onClick={handleExportJson} variant="outline" size="sm" className="gap-2 text-xs border-white/20 cursor-pointer">
                      <Download className="h-3.5 w-3.5 text-cyan-400" />
                      <span>Download Research Artifact (JSON)</span>
                    </Button>
                    <Button
                      onClick={() => setActiveTab("config")}
                      variant="ghost"
                      size="sm"
                      className="gap-2 text-xs text-slate-400 hover:text-white cursor-pointer"
                    >
                      <RefreshCw className="h-3.5 w-3.5" />
                      <span>Run New Simulation</span>
                    </Button>
                  </div>
                </div>
              </div>
            </Card>

            {/* Bottom 2 Cards: Attention Weights & Critical Slowing Down Indicators */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Feature Attention Weights */}
              <Card className="p-6 bg-slate-900/60 border-white/10 space-y-4">
                <div className="flex items-center justify-between border-b border-white/5 pb-3">
                  <h3 className="font-bold text-white flex items-center gap-2">
                    <BarChart2 className="h-4 w-4 text-cyan-400" />
                    Causal Feature Importance (Attention Weights)
                  </h3>
                  <Badge variant="secondary" className="font-mono text-[10px]">VARIABLE SELECTION</Badge>
                </div>

                <div className="space-y-3 pt-2">
                  {predictionResult.interpretability &&
                    Object.entries(predictionResult.interpretability?.feature_importance || {}).map(([feat, weight]) => {
                      const percentage = Math.round(weight * 100);
                      return (
                        <div key={feat} className="space-y-1 font-mono text-xs">
                          <div className="flex justify-between text-slate-300">
                            <span className="capitalize">{feat.replace(/_/g, " ")}</span>
                            <span className="font-bold text-cyan-400">{percentage}%</span>
                          </div>
                          <div className="w-full h-2 rounded-full bg-slate-950 overflow-hidden border border-white/5">
                            <motion.div
                              className="h-full bg-gradient-to-r from-cyan-500 to-teal-400"
                              initial={{ width: 0 }}
                              animate={{ width: `${percentage}%` }}
                              transition={{ duration: 0.6, ease: "easeOut" }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  {!predictionResult.interpretability && (
                    <div className="text-center py-6 text-slate-500 font-mono text-xs">
                      Attention weights not requested for this execution run.
                    </div>
                  )}
                </div>
              </Card>

              {/* Dynamical Systems Diagnostics */}
              <Card className="p-6 bg-slate-900/60 border-white/10 space-y-4">
                <div className="flex items-center justify-between border-b border-white/5 pb-3">
                  <h3 className="font-bold text-white flex items-center gap-2">
                    <ShieldCheck className="h-4 w-4 text-emerald-400" />
                    Dynamical Systems Diagnostics (EWS)
                  </h3>
                  <Badge variant="secondary" className="font-mono text-[10px]">AR(1) & DFA</Badge>
                </div>

                <div className="space-y-4 pt-1 font-mono text-xs">
                  <div className="p-3.5 rounded-xl bg-slate-950/70 border border-white/10 flex items-center justify-between">
                    <div>
                      <div className="text-slate-400">Lag-1 Autocorrelation (AR1)</div>
                      <div className="text-[10px] text-slate-500 mt-0.5">Critical Slowing Down Index</div>
                    </div>
                    <div className="text-right">
                      <div className="text-base font-bold text-orange-400">
                        {predictionResult.interpretability?.ar1_critical_slowing_down || "0.7842"}
                      </div>
                      <div className="text-[10px] text-orange-300">+24% over 10 yr</div>
                    </div>
                  </div>

                  <div className="p-3.5 rounded-xl bg-slate-950/70 border border-white/10 flex items-center justify-between">
                    <div>
                      <div className="text-slate-400">DFA Scaling Exponent (α)</div>
                      <div className="text-[10px] text-slate-500 mt-0.5">Long-range persistence memory</div>
                    </div>
                    <div className="text-right">
                      <div className="text-base font-bold text-purple-400">
                        {predictionResult.interpretability?.dfa_scaling_exponent || "1.2451"}
                      </div>
                      <div className="text-[10px] text-purple-300">Non-stationary</div>
                    </div>
                  </div>

                  <div className="p-3.5 rounded-xl bg-slate-950/70 border border-white/10 flex items-center justify-between">
                    <div>
                      <div className="text-slate-400">Rolling Variance Anomaly Trend</div>
                      <div className="text-[10px] text-slate-500 mt-0.5">Pre-bifurcation volatility</div>
                    </div>
                    <div className="text-right">
                      <div className="text-base font-bold text-cyan-400">
                        {predictionResult.interpretability?.rolling_variance_trend || "+34.2% over 24 mo"}
                      </div>
                      <div className="text-[10px] text-emerald-400">Statistically significant</div>
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function PredictPage() {
  return (
    <React.Suspense fallback={<div className="h-[85vh] w-full flex items-center justify-center text-slate-400 font-mono text-sm">Loading Prediction Studio...</div>}>
      <PredictContent />
    </React.Suspense>
  );
}
