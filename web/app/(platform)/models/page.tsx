"use client";

import * as React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Cpu,
  Search,
  Zap,
  CheckCircle2,
  FileCode,
  Layers,
  ArrowRight,
  ShieldCheck,
  Activity,
  GitBranch,
  Terminal,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { MODEL_ZOO } from "@/constants";
import { ModelMetadata } from "@/types/api";
import { cn } from "@/lib/utils";

export default function ModelsPage() {
  const [search, setSearch] = React.useState("");
  const [selectedCategory, setSelectedCategory] = React.useState<string>("all");
  const [selectedModel, setSelectedModel] = React.useState<ModelMetadata | null>(null);

  const categories = ["all", "Transformers", "Graph NNs", "PINNs", "Baselines"];

  const filteredModels = React.useMemo(() => {
    return MODEL_ZOO.filter((m) => {
      const matchesSearch =
        m.name.toLowerCase().includes(search.toLowerCase()) ||
        m.description.toLowerCase().includes(search.toLowerCase()) ||
        m.category.toLowerCase().includes(search.toLowerCase());
      const matchesCat = selectedCategory === "all" || m.category.toLowerCase().includes(selectedCategory.toLowerCase().slice(0, 4));
      return matchesSearch && matchesCat;
    });
  }, [search, selectedCategory]);

  return (
    <div className="space-y-8 animate-in fade-in-50 duration-300">
      {/* Title Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-white/10 pb-6">
        <div className="space-y-1">
          <Badge variant="purple" className="px-2.5 py-0.5 text-xs">AI Architectures & Zoo</Badge>
          <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white">
            Neural Model Zoo & Physics-Informed Architectures
          </h2>
          <p className="text-sm text-slate-300 max-w-3xl">
            State-of-the-art deep learning architectures specifically engineered for non-linear dynamical systems, causal feature selection, and thermodynamic energy balance preservation.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link href="/predict">
            <Button variant="gradient" className="gap-2 shadow-lg shadow-purple-500/20 font-bold">
              <Zap className="h-4 w-4" />
              <span>Launch Prediction Studio</span>
            </Button>
          </Link>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <Card className="p-4 bg-slate-900/60 border-white/10 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="relative w-full sm:w-80">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search model name, architecture, or specs..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-xl border border-white/10 bg-slate-950/60 py-2 pl-9 pr-4 text-xs text-white placeholder:text-slate-500 focus:border-purple-500 focus:outline-none"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto justify-end overflow-x-auto">
          <div className="flex rounded-xl bg-slate-950/80 p-1 border border-white/10 text-xs font-semibold shrink-0">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={cn(
                  "rounded-lg px-3 py-1 capitalize transition-all cursor-pointer whitespace-nowrap",
                  selectedCategory === cat ? "bg-purple-500/20 text-purple-300 border border-purple-500/30" : "text-slate-400 hover:text-white"
                )}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {/* Grid of Model Zoo Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredModels.map((mod, idx) => (
          <motion.div
            key={mod.id}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.08, duration: 0.3 }}
            className="h-full"
          >
            <Card className="h-full p-6 flex flex-col justify-between bg-slate-900/60 border-white/10 hover:border-purple-500/40 transition-all hover:shadow-xl relative overflow-hidden group">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <Badge variant="outline" className="font-mono text-[10px] text-purple-300 border-purple-500/30 bg-purple-500/10">
                    {mod.category}
                  </Badge>
                  <span className="text-xs font-mono font-bold text-cyan-400">{mod.parameters} params</span>
                </div>

                <div>
                  <h3 className="text-xl font-bold text-white group-hover:text-purple-300 transition-colors">
                    {mod.name}
                  </h3>
                  <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                    {mod.description}
                  </p>
                </div>

                {/* Performance Specs Box */}
                <div className="grid grid-cols-2 gap-2 p-3 rounded-xl bg-slate-950/70 border border-white/5 font-mono text-xs">
                  <div>
                    <span className="text-[10px] text-slate-500 block">ROC-AUC Score</span>
                    <span className="text-emerald-400 font-bold text-sm">{mod.rocAuc}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 block">Lead Accuracy</span>
                    <span className="text-white font-bold text-sm">{mod.leadTimeAccuracy}</span>
                  </div>
                </div>

                <div className="space-y-1.5 pt-1">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                    Key Architectural Strengths
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {mod.architectureDetails.map((st) => (
                      <span key={st} className="px-2 py-0.5 rounded bg-white/5 border border-white/5 text-[11px] font-mono text-slate-300">
                        ✓ {st}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Bottom Action Strip */}
              <div className="flex items-center gap-2 pt-5 mt-4 border-t border-white/5">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => setSelectedModel(mod)}
                  className="flex-1 text-xs gap-1 cursor-pointer"
                >
                  <FileCode className="h-3.5 w-3.5 text-purple-400" />
                  <span>Architecture Docs</span>
                </Button>
                <Link href={`/predict?model=${mod.id}`} className="flex-1">
                  <Button variant="gradient" size="sm" className="w-full text-xs gap-1 shadow-md shadow-purple-500/15 font-bold">
                    <Zap className="h-3.5 w-3.5" />
                    <span>Run Inference</span>
                  </Button>
                </Link>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Model Architecture Inspection Modal */}
      <Dialog open={!!selectedModel} onOpenChange={(open) => !open && setSelectedModel(null)}>
        {selectedModel && (
          <DialogContent className="max-w-3xl p-6 bg-slate-900/95 border-white/10 space-y-6 text-white">
            <DialogHeader>
              <div className="flex items-center justify-between pr-8">
                <Badge variant="outline" className="font-mono text-xs text-purple-300 border-purple-500/30 bg-purple-500/10">
                  {selectedModel.category}
                </Badge>
                <span className="text-xs font-mono text-cyan-400 font-bold">{selectedModel.parameters} total parameters</span>
              </div>
              <DialogTitle className="text-2xl font-extrabold text-white mt-1">
                {selectedModel.name}
              </DialogTitle>
              <DialogDescription className="text-sm text-slate-300 leading-relaxed mt-2">
                {selectedModel.description}
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-6 pt-2">
              {/* Architecture Blueprint Callout */}
              <div className="rounded-xl border border-purple-500/30 bg-purple-500/10 p-4 space-y-2">
                <div className="text-xs font-bold text-purple-300 flex items-center gap-2 uppercase tracking-wider">
                  <GitBranch className="h-4 w-4" /> Architectural Blueprint & Loss Formulation
                </div>
                <p className="text-xs text-slate-200 leading-relaxed font-mono">
                  {selectedModel.id === "temporal_fusion_transformer" &&
                    "L_total = L_quantile + λ * L_variable_selection. Employs multi-head attention over continuous historical time-series windows to isolate causal precursor signatures before fold bifurcation."}
                  {selectedModel.id === "physics_informed_nn" &&
                    "L_total = L_data + β * ||∂u/∂t + u·∇u - ν∇²u||² + γ * ||ΔQ_thermodynamic||². Enforces fluid dynamic conservation equations as soft penalties during backward propagation."}
                  {selectedModel.id !== "temporal_fusion_transformer" &&
                    selectedModel.id !== "physics_informed_nn" &&
                    "Optimized using AdamW with cosine annealing learning rate schedules on NVIDIA A100 clusters. Pre-trained on 40 years of ERA5 global reanalysis data."}
                </p>
              </div>

              {/* Specs Table */}
              <div className="grid grid-cols-3 gap-4 font-mono text-xs">
                <div className="p-3.5 rounded-xl bg-slate-950/80 border border-white/10">
                  <span className="text-slate-500 block text-[10px] uppercase">ROC-AUC Benchmark</span>
                  <span className="text-emerald-400 font-bold text-lg">{selectedModel.rocAuc}</span>
                </div>
                <div className="p-3.5 rounded-xl bg-slate-950/80 border border-white/10">
                  <span className="text-slate-500 block text-[10px] uppercase">Lead Time Precision</span>
                  <span className="text-cyan-400 font-bold text-lg">{selectedModel.leadTimeAccuracy}</span>
                </div>
                <div className="p-3.5 rounded-xl bg-slate-950/80 border border-white/10">
                  <span className="text-slate-500 block text-[10px] uppercase">Hardware Target</span>
                  <span className="text-white font-bold text-base">2x A100 GPU</span>
                </div>
              </div>

              {/* Strengths List */}
              <div className="space-y-2">
                <span className="text-xs font-bold text-slate-300 uppercase tracking-wider block">
                  Why Use This Model?
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs font-mono text-slate-300">
                  {selectedModel.architectureDetails.map((st, i) => (
                    <div key={i} className="flex items-center gap-2 rounded-lg bg-slate-950/50 p-2.5 border border-white/5">
                      <CheckCircle2 className="h-3.5 w-3.5 text-purple-400 shrink-0" />
                      <span>{st}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-4 border-t border-white/10">
              <Button variant="outline" size="sm" onClick={() => setSelectedModel(null)} className="text-xs">
                Close
              </Button>
              <Link href={`/predict?model=${selectedModel.id}`}>
                <Button variant="gradient" size="sm" className="gap-2 text-xs shadow-md shadow-purple-500/20 font-bold">
                  <Zap className="h-3.5 w-3.5" />
                  <span>Execute AI Prediction with {selectedModel.name}</span>
                </Button>
              </Link>
            </div>
          </DialogContent>
        )}
      </Dialog>
    </div>
  );
}
