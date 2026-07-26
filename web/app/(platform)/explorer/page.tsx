"use client";

import * as React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Compass,
  Globe,
  Zap,
  TrendingDown,
  TrendingUp,
  AlertTriangle,
  Database,
  ArrowRight,
  Info,
  Calendar,
  Layers,
  Thermometer,
  Activity,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { TrendChart } from "@/components/charts/TrendChart";
import { TIPPING_ELEMENTS } from "@/constants";
import { TippingElementMetadata } from "@/types/api";
import { cn } from "@/lib/utils";

export default function ExplorerPage() {
  const [selectedElement, setSelectedElement] = React.useState<TippingElementMetadata | null>(null);

  return (
    <div className="space-y-8 animate-in fade-in-50 duration-300">
      {/* Title Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-white/10 pb-6">
        <div className="space-y-1">
          <Badge variant="default" className="px-2.5 py-0.5 text-xs">Planetary Boundaries</Badge>
          <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white">
            Climate Risk Explorer & Tipping Element Catalog
          </h2>
          <p className="text-sm text-slate-300 max-w-3xl">
            Interactive analytical dossiers for the 5 critical climate tipping elements. Each card features real-time risk gauges, historical observational trends, and estimated lead times before structural fold bifurcation.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link href="/earth">
            <Button variant="outline" className="gap-2 border-white/20">
              <Globe className="h-4 w-4 text-cyan-400" />
              <span>Explore on 3D Globe</span>
            </Button>
          </Link>
        </div>
      </div>

      {/* Grid of Tipping Element Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {TIPPING_ELEMENTS.map((el, idx) => {
          const isCritical = el.status === "CRITICAL";
          const isWarning = el.status === "WARNING";
          const colorHex = isCritical ? "#F77F00" : isWarning ? "#FCBF49" : "#00B4D8";

          return (
            <motion.div
              key={el.id}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.08, duration: 0.3 }}
              className="h-full"
            >
              <Card className="h-full p-6 flex flex-col justify-between bg-slate-900/60 border-white/10 hover:border-white/20 transition-all hover:shadow-xl relative overflow-hidden group">
                {/* Top Status & Region */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">{el.region}</span>
                    <Badge
                      variant={isCritical ? "destructive" : isWarning ? "warning" : "default"}
                      className="font-bold text-[10px]"
                    >
                      {el.status}
                    </Badge>
                  </div>

                  <div>
                    <h3 className="text-xl font-bold text-white group-hover:text-cyan-300 transition-colors">
                      {el.name}
                    </h3>
                    <p className="text-xs text-slate-300 mt-1.5 line-clamp-2 leading-relaxed">
                      {el.description}
                    </p>
                  </div>
                </div>

                {/* Middle: Historical Trend Chart */}
                <div className="my-5 pt-3 border-t border-white/5 space-y-2">
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="text-slate-400">20-Year Observational Trend</span>
                    <span className="font-semibold" style={{ color: colorHex }}>
                      {el.historicalTrend[el.historicalTrend.length - 1].val} units
                    </span>
                  </div>
                  <div className="rounded-xl bg-slate-950/70 p-2 border border-white/5">
                    <TrendChart data={el.historicalTrend} color={colorHex} height={110} />
                  </div>
                </div>

                {/* Bottom Stats & CTAs */}
                <div className="space-y-4 pt-3 border-t border-white/5">
                  <div className="grid grid-cols-3 gap-2 text-center font-mono text-xs">
                    <div className="p-2 rounded-lg bg-slate-950/60 border border-white/5">
                      <span className="text-[10px] text-slate-500 block">Risk Score</span>
                      <span className="font-bold text-base" style={{ color: colorHex }}>
                        {(el.riskScore * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="p-2 rounded-lg bg-slate-950/60 border border-white/5">
                      <span className="text-[10px] text-slate-500 block">Lead Time</span>
                      <span className="font-bold text-base text-cyan-400">~{el.leadTimeMonths} mo</span>
                    </div>
                    <div className="p-2 rounded-lg bg-slate-950/60 border border-white/5">
                      <span className="text-[10px] text-slate-500 block">Confidence</span>
                      <span className="font-bold text-base text-emerald-400">
                        {(el.confidenceScore * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => setSelectedElement(el)}
                      className="flex-1 text-xs gap-1.5 cursor-pointer"
                    >
                      <Info className="h-3.5 w-3.5 text-cyan-400" />
                      <span>Deep Analysis</span>
                    </Button>
                    <Link href={`/predict?element=${el.id}`} className="flex-1">
                      <Button variant="gradient" size="sm" className="w-full text-xs gap-1 shadow-md shadow-cyan-500/15 font-semibold">
                        <Zap className="h-3.5 w-3.5" />
                        <span>Predict</span>
                      </Button>
                    </Link>
                  </div>
                </div>
              </Card>
            </motion.div>
          );
        })}
      </div>

      {/* Slide-over / Modal for Detailed Analysis */}
      <Dialog open={!!selectedElement} onOpenChange={(open) => !open && setSelectedElement(null)}>
        {selectedElement && (
          <DialogContent className="max-w-3xl p-6 bg-slate-900/95 border-white/10 space-y-6">
            <DialogHeader>
              <div className="flex items-center justify-between pr-8">
                <span className="text-xs font-mono text-cyan-400 uppercase tracking-wider">{selectedElement.region}</span>
                <Badge
                  variant={selectedElement.status === "CRITICAL" ? "destructive" : selectedElement.status === "WARNING" ? "warning" : "default"}
                  className="font-bold text-xs"
                >
                  {selectedElement.status}
                </Badge>
              </div>
              <DialogTitle className="text-2xl font-extrabold text-white mt-1">
                {selectedElement.name}
              </DialogTitle>
              <DialogDescription className="text-sm text-slate-300 leading-relaxed mt-2">
                {selectedElement.description}
              </DialogDescription>
            </DialogHeader>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
              {/* Left / Trend Chart & Telemetry */}
              <div className="space-y-4">
                <div className="rounded-xl bg-slate-950/80 p-4 border border-white/10 space-y-2">
                  <div className="text-xs font-mono font-semibold text-slate-300 flex items-center justify-between">
                    <span>20-Year Observational Anomaly Profile</span>
                    <span className="text-cyan-400 font-bold">2004 — 2024</span>
                  </div>
                  <TrendChart
                    data={selectedElement.historicalTrend}
                    color={selectedElement.status === "CRITICAL" ? "#F77F00" : "#00B4D8"}
                    height={160}
                  />
                </div>

                <div className="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4 space-y-1.5">
                  <div className="text-xs font-bold text-orange-300 flex items-center gap-1.5">
                    <AlertTriangle className="h-4 w-4 animate-bounce" /> Current Observational Status
                  </div>
                  <p className="text-xs text-slate-200 leading-relaxed font-mono">
                    {selectedElement.recentAnomalies}
                  </p>
                </div>
              </div>

              {/* Right / Features & Datasets */}
              <div className="space-y-4">
                <div className="space-y-2">
                  <span className="text-xs font-bold text-slate-300 uppercase tracking-wider block">
                    Primary Monitored Features (AR1 / Variance / Alpha)
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {selectedElement.importantVariables.map((v) => (
                      <span key={v} className="px-2.5 py-1 rounded-lg bg-white/5 border border-white/10 text-xs font-mono text-cyan-300">
                        {v}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="space-y-2">
                  <span className="text-xs font-bold text-slate-300 uppercase tracking-wider block">
                    Supporting Ingested Datasets
                  </span>
                  <div className="space-y-1.5 rounded-xl bg-slate-950/60 p-3 border border-white/5 text-xs font-mono text-slate-300">
                    {selectedElement.supportingDatasets.map((ds) => (
                      <div key={ds} className="flex items-center gap-2">
                        <Database className="h-3.5 w-3.5 text-emerald-400 shrink-0" />
                        <span>{ds}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-purple-500/10 border border-purple-500/20 text-xs font-mono text-purple-300">
                  ⚡ AI Confidence Score: <strong>{(selectedElement.confidenceScore * 100).toFixed(1)}%</strong> via bootstrap paired t-test evaluation against statistical ARIMABaseline.
                </div>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row items-center justify-end gap-3 pt-4 border-t border-white/10">
              <Link href={`/earth?element=${selectedElement.id}`} className="w-full sm:w-auto">
                <Button variant="outline" className="w-full sm:w-auto gap-2 border-white/20">
                  <Globe className="h-4 w-4 text-cyan-400" />
                  <span>Inspect in 3D Globe</span>
                </Button>
              </Link>
              <Link href={`/predict?element=${selectedElement.id}`} className="w-full sm:w-auto">
                <Button variant="gradient" className="w-full sm:w-auto gap-2 shadow-lg shadow-cyan-500/20 font-bold">
                  <Zap className="h-4 w-4" />
                  <span>Execute AI Inference Job</span>
                </Button>
              </Link>
            </div>
          </DialogContent>
        )}
      </Dialog>
    </div>
  );
}
