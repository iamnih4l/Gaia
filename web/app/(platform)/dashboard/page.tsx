"use client";

import * as React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  BarChart3,
  CheckCircle2,
  Cpu,
  Database,
  Globe,
  Play,
  RefreshCw,
  Sparkles,
  TrendingDown,
  TrendingUp,
  Zap,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { MetricCard } from "@/components/shared/MetricCard";
import { RiskGauge } from "@/components/shared/RiskGauge";
import { useGlobalStore } from "@/store";
import { TIPPING_ELEMENTS, MODEL_ZOO, DATASET_CATALOG } from "@/constants";
import { useHealthQuery } from "@/hooks/useApi";

export default function DashboardPage() {
  const { activeAlerts, dismissAlert, jobQueue } = useGlobalStore();
  const { data: health, isLoading } = useHealthQuery();

  // Composite global risk score average
  const avgRisk = TIPPING_ELEMENTS.reduce((acc, el) => acc + el.riskScore, 0) / TIPPING_ELEMENTS.length;

  return (
    <div className="space-y-8 animate-in fade-in-50 duration-300">
      {/* Top Welcome / Status Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 rounded-2xl border border-white/10 bg-gradient-to-r from-slate-900/80 via-slate-900/40 to-slate-950 p-6 backdrop-blur-xl shadow-xl">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Badge variant="default" className="px-2.5 py-0.5 text-xs">Mission Control Active</Badge>
            <span className="text-xs text-slate-400 font-mono">Last synced: {new Date().toLocaleTimeString()}</span>
          </div>
          <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white">
            Planetary Health & Early Warning Overview
          </h2>
          <p className="text-sm text-slate-300 max-w-3xl">
            Monitoring 5 critical planetary boundaries in real-time. System intelligence is currently synthesizing ERA5 atmospheric reanalysis and RAPID-MOCHA ocean transport arrays.
          </p>
        </div>
        <div className="flex items-center gap-3 shrink-0">
          <Link href="/predict">
            <Button variant="gradient" className="gap-2 shadow-lg shadow-cyan-500/20">
              <Zap className="h-4 w-4" />
              <span>Run Prediction Job</span>
            </Button>
          </Link>
          <Link href="/earth">
            <Button variant="outline" className="gap-2 border-white/20">
              <Globe className="h-4 w-4 text-cyan-400" />
              <span>3D Globe</span>
            </Button>
          </Link>
        </div>
      </div>

      {/* Primary Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Active Tipping Warnings"
          value={activeAlerts.length}
          subtitle="Elements crossing 0.50 risk threshold"
          change={activeAlerts.length > 0 ? "+1 this month" : "All stable"}
          trend={activeAlerts.length > 0 ? "down" : "up"}
          icon={AlertTriangle}
          iconColor="text-orange-400"
          glow={activeAlerts.length > 0 ? "danger" : "none"}
        />
        <MetricCard
          title="TFT Inference Latency"
          value="42.5 ms"
          subtitle="A100-SXM4-80GB Hardware Acceleration"
          change="-3.2 ms vs baseline"
          trend="up"
          icon={Zap}
          iconColor="text-cyan-400"
          glow="cyan"
        />
        <MetricCard
          title="Active Neural Models"
          value={MODEL_ZOO.length}
          subtitle="Transformers, GNNs, PINNs, Baselines"
          change="All weights loaded"
          trend="neutral"
          icon={Cpu}
          iconColor="text-purple-400"
          glow="purple"
        />
        <MetricCard
          title="Ingested Data Volume"
          value="70.8 TB"
          subtitle="ERA5, CMIP6, MODIS, GRACE Mascons"
          change="99.98% pipeline uptime"
          trend="up"
          icon={Database}
          iconColor="text-emerald-400"
        />
      </div>

      {/* Middle Section: Planetary Risk Gauge + Active Alerts Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Gauge Card (1 Col) */}
        <Card className="p-6 flex flex-col items-center justify-between bg-slate-900/60 border-white/10 lg:col-span-1">
          <div className="w-full flex items-center justify-between border-b border-white/5 pb-3">
            <h3 className="font-bold text-white flex items-center gap-2">
              <Activity className="h-4 w-4 text-cyan-400" />
              Global Planetary Risk Level
            </h3>
            <Badge variant="warning" className="font-mono text-[10px]">COMPOSITE</Badge>
          </div>
          <div className="py-6 flex-1 flex items-center justify-center">
            <RiskGauge score={avgRisk} title="Mean Tipping Probability" size="lg" />
          </div>
          <div className="w-full text-center text-xs text-slate-400 pt-3 border-t border-white/5 font-mono">
            Based on AR(1) autocorrelation and PINN residuals across 5 elements
          </div>
        </Card>

        {/* Active Alerts Feed (2 Col) */}
        <Card className="p-6 flex flex-col justify-between bg-slate-900/60 border-white/10 lg:col-span-2">
          <div className="flex items-center justify-between border-b border-white/5 pb-3">
            <h3 className="font-bold text-white flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-orange-400 animate-bounce" />
              Active Planetary Warning Feed ({activeAlerts.length})
            </h3>
            <Link href="/explorer">
              <Button variant="ghost" size="sm" className="text-xs text-cyan-400">View All Elements →</Button>
            </Link>
          </div>

          <div className="py-4 space-y-3 flex-1 overflow-y-auto max-h-[300px]">
            {activeAlerts.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center py-12 text-slate-500">
                <CheckCircle2 className="h-10 w-10 text-emerald-500 mb-2" />
                <span className="font-medium">All planetary elements stable below warning thresholds.</span>
              </div>
            ) : (
              activeAlerts.map((item) => {
                const el = TIPPING_ELEMENTS.find((e) => e.id === item.elementId);
                if (!el) return null;
                return (
                  <div
                    key={item.elementId}
                    className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-xl border border-orange-500/30 bg-orange-500/10 p-4 transition-all hover:border-orange-500/50"
                  >
                    <div className="flex items-start gap-3.5">
                      <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-orange-500/20 text-orange-400">
                        <AlertTriangle className="h-4 w-4" />
                      </div>
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-white">{el.name}</span>
                          <Badge variant="destructive" className="text-[10px] py-0 font-mono">
                            {item.alert.alert_level}
                          </Badge>
                        </div>
                        <p className="text-xs text-slate-300 leading-relaxed">
                          {el.recentAnomalies}
                        </p>
                        <div className="text-[11px] font-mono text-orange-300 flex items-center gap-3 pt-1">
                          <span>Risk: {(el.riskScore * 100).toFixed(0)}%</span>
                          <span>•</span>
                          <span>Est. Lead Time: ~{item.alert.estimated_lead_time_steps || el.leadTimeMonths} months</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 sm:self-center">
                      <Link href={`/earth?element=${el.id}`}>
                        <Button size="sm" variant="secondary" className="text-xs gap-1">
                          <Globe className="h-3.5 w-3.5 text-cyan-400" />
                          <span>Inspect 3D</span>
                        </Button>
                      </Link>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => dismissAlert(item.elementId)}
                        className="text-xs text-slate-400 hover:text-white"
                      >
                        Dismiss
                      </Button>
                    </div>
                  </div>
                );
              })
            )}
          </div>

          <div className="pt-3 border-t border-white/5 flex items-center justify-between text-xs text-slate-400">
            <span>Automated EWS triggers evaluated on 24-month sliding window</span>
            <span className="font-mono text-cyan-400">Threshold: P(tip) ≥ 0.50</span>
          </div>
        </Card>
      </div>

      {/* Bottom Tables: Recent Model Runs & Dataset Catalog Preview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Model Jobs Table */}
        <Card className="p-6 bg-slate-900/60 border-white/10 space-y-4">
          <div className="flex items-center justify-between border-b border-white/5 pb-3">
            <h3 className="font-bold text-white flex items-center gap-2">
              <Cpu className="h-4 w-4 text-purple-400" />
              Recent AI Model Execution Runs
            </h3>
            <Link href="/predict">
              <Button variant="ghost" size="sm" className="text-xs text-cyan-400">Prediction Studio →</Button>
            </Link>
          </div>

          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Job / Element</TableHead>
                <TableHead>Architecture</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Risk Output</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {jobQueue.map((job) => {
                const el = TIPPING_ELEMENTS.find((e) => e.id === job.elementId);
                const mod = MODEL_ZOO.find((m) => m.id === job.modelId);
                return (
                  <TableRow key={job.id}>
                    <TableCell className="font-medium text-white">
                      <div>{el?.shortName || job.elementId}</div>
                      <div className="text-[10px] text-slate-400 font-mono">{new Date(job.startTime).toLocaleTimeString()}</div>
                    </TableCell>
                    <TableCell>
                      <span className="text-xs text-slate-300">{mod?.name || job.modelId}</span>
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          job.status === "completed"
                            ? "success"
                            : job.status === "running"
                            ? "default"
                            : job.status === "failed"
                            ? "destructive"
                            : "secondary"
                        }
                        className="text-[10px] py-0 font-mono uppercase"
                      >
                        {job.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right font-mono font-bold">
                      {job.result ? (
                        <span className={job.result.tipping_probability >= 0.5 ? "text-orange-400" : "text-emerald-400"}>
                          {(job.result.tipping_probability * 100).toFixed(1)}%
                        </span>
                      ) : (
                        <span className="text-slate-500">—</span>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </Card>

        {/* Recent Uploaded / Ingested Datasets */}
        <Card className="p-6 bg-slate-900/60 border-white/10 space-y-4">
          <div className="flex items-center justify-between border-b border-white/5 pb-3">
            <h3 className="font-bold text-white flex items-center gap-2">
              <Database className="h-4 w-4 text-emerald-400" />
              Active Observational & Simulation Datasets
            </h3>
            <Link href="/datasets">
              <Button variant="ghost" size="sm" className="text-xs text-cyan-400">Dataset Manager →</Button>
            </Link>
          </div>

          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Dataset Name</TableHead>
                <TableHead>Resolution</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Size</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {DATASET_CATALOG.slice(0, 4).map((ds) => (
                <TableRow key={ds.id}>
                  <TableCell className="font-medium text-white max-w-[180px] truncate">
                    <div className="truncate">{ds.name}</div>
                    <div className="text-[10px] text-slate-400 truncate">{ds.source}</div>
                  </TableCell>
                  <TableCell className="text-xs text-slate-300">{ds.temporalResolution}</TableCell>
                  <TableCell>
                    <Badge variant={ds.status === "Active" ? "success" : "warning"} className="text-[10px] py-0 font-mono">
                      {ds.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right font-mono text-xs text-slate-300">{ds.size}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      </div>
    </div>
  );
}
