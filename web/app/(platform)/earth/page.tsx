"use client";

import * as React from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Globe,
  Layers,
  Thermometer,
  Wind,
  Droplets,
  TrendingDown,
  TrendingUp,
  Activity,
  ShieldAlert,
  ArrowUpRight,
  Info,
  Calendar,
  Database,
  Cpu,
  Zap,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Globe3D } from "@/components/earth/Globe3D";
import { TIPPING_ELEMENTS, MODEL_ZOO } from "@/constants";
import { useGlobalStore } from "@/store";
import { cn } from "@/lib/utils";

function InteractiveEarthContent() {
  const searchParams = useSearchParams();
  const elementParam = searchParams.get("element");
  
  const { selectedElementId, setSelectedElementId } = useGlobalStore();
  
  React.useEffect(() => {
    if (elementParam && TIPPING_ELEMENTS.some((e) => e.id === elementParam)) {
      setSelectedElementId(elementParam);
    }
  }, [elementParam, setSelectedElementId]);

  const currentElement = TIPPING_ELEMENTS.find((e) => e.id === selectedElementId) || TIPPING_ELEMENTS[0];

  return (
    <div className="space-y-6 animate-in fade-in-50 duration-300 h-full flex flex-col">
      {/* Header Selector Strip */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 rounded-2xl border border-white/10 bg-slate-950/80 p-4 backdrop-blur-xl shrink-0">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-500/15 text-cyan-400 border border-cyan-500/30">
            <Globe className="h-5 w-5 animate-spin" style={{ animationDuration: "20s" }} />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              Interactive 3D Earth Viewport
              <Badge variant="outline" className="text-[10px] font-mono border-cyan-500/30 text-cyan-300">
                Lat/Lon Spatial Overlays
              </Badge>
            </h2>
            <p className="text-xs text-slate-400">Select a region below or click directly on the rotating 3D globe to inspect telemetry.</p>
          </div>
        </div>

        {/* Region Toggle Pill Buttons */}
        <div className="flex flex-wrap items-center gap-2">
          {TIPPING_ELEMENTS.map((el) => {
            const isSelected = el.id === selectedElementId;
            return (
              <button
                key={el.id}
                onClick={() => setSelectedElementId(el.id)}
                className={cn(
                  "flex items-center gap-2 rounded-xl px-3 py-2 text-xs font-semibold transition-all cursor-pointer border",
                  isSelected
                    ? "bg-gradient-to-r from-cyan-500/20 to-teal-500/20 text-white border-cyan-500/50 shadow-md shadow-cyan-500/15"
                    : "bg-slate-900/60 text-slate-400 border-white/10 hover:bg-white/5 hover:text-slate-200"
                )}
              >
                <span
                  className="h-2 w-2 rounded-full"
                  style={{
                    backgroundColor: el.status === "CRITICAL" ? "#F77F00" : el.status === "WARNING" ? "#FCBF49" : "#00B4D8",
                  }}
                />
                <span>{el.shortName}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Viewport Grid: 3D Globe (Left) + Scientific Inspection Panel (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-[600px]">
        {/* Left Column / 3D Globe Canvas (2 Cols) */}
        <Card className="lg:col-span-2 p-6 bg-gradient-to-b from-slate-950/90 to-slate-900/80 border-white/10 flex flex-col relative overflow-hidden">
          <div className="flex items-center justify-between border-b border-white/10 pb-3 z-10">
            <div className="flex items-center gap-2 text-xs font-mono text-slate-300">
              <span className="h-2 w-2 rounded-full bg-cyan-400 animate-ping" />
              <span>Target Coordinates: {currentElement.coordinates[0]}°N, {currentElement.coordinates[1]}°E</span>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="font-mono text-[10px]">WebGL Raycaster</Badge>
            </div>
          </div>

          {/* 3D Globe Viewport */}
          <div className="flex-1 w-full h-full min-h-[450px] relative flex items-center justify-center my-4">
            <Globe3D onSelectElement={(id) => setSelectedElementId(id)} />
          </div>

          {/* Bottom Legend */}
          <div className="border-t border-white/10 pt-3 flex flex-wrap items-center justify-between gap-4 text-xs font-mono text-slate-400 z-10 bg-slate-950/60 p-3 rounded-xl">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-full bg-emerald-500" /> Normal Stable</span>
              <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-full bg-cyan-400" /> Watch (P ≥ 0.50)</span>
              <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-full bg-amber-400" /> Warning (P ≥ 0.65)</span>
              <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-full bg-orange-500" /> Critical (P ≥ 0.80)</span>
            </div>
            <span className="text-cyan-400">Drag to rotate • Click marker to inspect</span>
          </div>
        </Card>

        {/* Right Column / Scientific Telemetry Panel (1 Col) */}
        <Card className="p-6 bg-slate-900/90 border-white/10 flex flex-col justify-between space-y-6 overflow-y-auto">
          <div className="space-y-4">
            <div className="flex items-start justify-between">
              <div>
                <span className="text-xs font-mono text-cyan-400 uppercase tracking-wider">{currentElement.region}</span>
                <h3 className="text-2xl font-bold text-white mt-1">{currentElement.name}</h3>
              </div>
              <Badge
                variant={currentElement.status === "CRITICAL" ? "destructive" : currentElement.status === "WARNING" ? "warning" : "default"}
                className="font-bold text-xs py-1 px-3"
              >
                {currentElement.status}
              </Badge>
            </div>

            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed bg-slate-950/50 p-3.5 rounded-xl border border-white/5">
              {currentElement.description}
            </p>

            {/* Key Risk Indicators Grid */}
            <div className="grid grid-cols-2 gap-3 font-mono">
              <div className="p-3 rounded-xl bg-slate-950/70 border border-white/10 space-y-1">
                <span className="text-[10px] text-slate-400 uppercase">Tipping Probability</span>
                <div className="text-xl font-bold text-orange-400">{(currentElement.riskScore * 100).toFixed(0)}%</div>
                <div className="text-[10px] text-slate-400">AR(1) Slowing Down</div>
              </div>

              <div className="p-3 rounded-xl bg-slate-950/70 border border-white/10 space-y-1">
                <span className="text-[10px] text-slate-400 uppercase">Est. Lead Time</span>
                <div className="text-xl font-bold text-cyan-400">~{currentElement.leadTimeMonths} mo</div>
                <div className="text-[10px] text-slate-400">Before bifurcation</div>
              </div>

              <div className="p-3 rounded-xl bg-slate-950/70 border border-white/10 space-y-1">
                <span className="text-[10px] text-slate-400 uppercase">Temp Anomaly</span>
                <div className="text-base font-bold text-white">{currentElement.tempAnomaly} °C</div>
                <div className="text-[10px] text-slate-400">vs 1980 baseline</div>
              </div>

              <div className="p-3 rounded-xl bg-slate-950/70 border border-white/10 space-y-1">
                <span className="text-[10px] text-slate-400 uppercase">AI Confidence</span>
                <div className="text-base font-bold text-emerald-400">{(currentElement.confidenceScore * 100).toFixed(0)}%</div>
                <div className="text-[10px] text-slate-400">Bootstrap paired test</div>
              </div>
            </div>

            {/* Recent Anomaly Callout */}
            <div className="rounded-xl border border-orange-500/30 bg-orange-500/10 p-3.5 space-y-1.5">
              <div className="text-xs font-bold text-orange-300 flex items-center gap-1.5">
                <Activity className="h-3.5 w-3.5 animate-pulse" /> Latest Observational Anomaly
              </div>
              <p className="text-xs text-slate-200 leading-relaxed">
                {currentElement.recentAnomalies}
              </p>
            </div>

            {/* Important Variables List */}
            <div className="space-y-2">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
                Primary Monitored Features
              </span>
              <div className="flex flex-wrap gap-1.5">
                {currentElement.importantVariables.map((v) => (
                  <span key={v} className="px-2 py-1 rounded bg-white/5 border border-white/10 text-[11px] font-mono text-cyan-300">
                    {v}
                  </span>
                ))}
              </div>
            </div>

            {/* Supporting Datasets List */}
            <div className="space-y-2">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
                Ingested Data Sources
              </span>
              <div className="space-y-1 text-xs font-mono text-slate-300">
                {currentElement.supportingDatasets.map((ds) => (
                  <div key={ds} className="flex items-center gap-2">
                    <Database className="h-3 w-3 text-emerald-400 shrink-0" />
                    <span className="truncate">{ds}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Action CTAs */}
          <div className="pt-4 border-t border-white/10 space-y-2.5">
            <Link href={`/predict?element=${currentElement.id}`} className="w-full block">
              <Button variant="gradient" className="w-full gap-2 shadow-lg shadow-cyan-500/20 font-bold">
                <Zap className="h-4 w-4" />
                <span>Run AI Prediction on {currentElement.shortName}</span>
              </Button>
            </Link>
            <Link href="/explorer" className="w-full block">
              <Button variant="outline" className="w-full text-xs border-white/10 hover:bg-white/5">
                Compare Across All Tipping Elements →
              </Button>
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
}

export default function InteractiveEarthPage() {
  return (
    <React.Suspense fallback={<div className="h-[85vh] w-full flex items-center justify-center text-slate-400 font-mono text-sm">Loading 3D Earth projection...</div>}>
      <InteractiveEarthContent />
    </React.Suspense>
  );
}
