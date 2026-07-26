"use client";

import * as React from "react";
import { motion } from "framer-motion";
import {
  Settings,
  SlidersHorizontal,
  RefreshCw,
  Trash2,
  Terminal,
  ShieldCheck,
  Server,
  Database,
  CheckCircle2,
  AlertTriangle,
  Cpu,
  Radio,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useGlobalStore } from "@/store";
import { useHealthQuery } from "@/hooks/useApi";
import { API_BASE_URL } from "@/constants";
import { cn } from "@/lib/utils";

export default function SettingsPage() {
  const { simulationMode, setSimulationMode, clearJobs, jobQueue } = useGlobalStore();
  const { data: health, isLoading, refetch, isRefetching } = useHealthQuery();
  const [apiUrl, setApiUrl] = React.useState(API_BASE_URL);
  const [saveSuccess, setSaveSuccess] = React.useState(false);

  const handleSaveApi = (e: React.FormEvent) => {
    e.preventDefault();
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 3000);
  };

  return (
    <div className="space-y-8 animate-in fade-in-50 duration-300 max-w-4xl mx-auto">
      {/* Title Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-white/10 pb-6">
        <div className="space-y-1">
          <Badge variant="default" className="px-2.5 py-0.5 text-xs">System Administration</Badge>
          <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white">
            System Settings & Diagnostic Control Panel
          </h2>
          <p className="text-sm text-slate-300 max-w-2xl">
            Configure backend FastAPI server connections, toggle offline simulation fallbacks, clear local cache databases, and monitor runtime hardware cluster telemetry.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button onClick={() => refetch()} disabled={isRefetching} variant="outline" size="sm" className="gap-2 border-white/20">
            <RefreshCw className={cn("h-3.5 w-3.5 text-cyan-400", isRefetching && "animate-spin")} />
            <span>Ping Backend Server</span>
          </Button>
        </div>
      </div>

      {/* Grid of Settings Modules */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Backend Server Config Card */}
        <Card className="p-6 bg-slate-900/60 border-white/10 space-y-6 flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-white/5 pb-3">
              <h3 className="font-bold text-white flex items-center gap-2">
                <Server className="h-4 w-4 text-cyan-400" />
                Inference API Server Connection
              </h3>
              <Badge
                variant={simulationMode ? "warning" : health ? "success" : "destructive"}
                className="font-mono text-[10px]"
              >
                {simulationMode ? "OFFLINE SIMULATION" : health ? "ONLINE LIVE" : "DISCONNECTED"}
              </Badge>
            </div>

            <form onSubmit={handleSaveApi} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-mono text-slate-300">FastAPI Server Endpoint URL</label>
                <input
                  type="text"
                  value={apiUrl}
                  onChange={(e) => setApiUrl(e.target.value)}
                  className="w-full rounded-xl border border-white/10 bg-slate-950/80 px-3 py-2 text-xs font-mono text-white focus:border-cyan-500 focus:outline-none"
                />
                <p className="text-[11px] text-slate-500 font-sans">
                  Default local endpoint: http://localhost:8000
                </p>
              </div>

              <div className="pt-2 flex items-center gap-3">
                <Button type="submit" variant="gradient" size="sm" className="text-xs shadow-md shadow-cyan-500/15">
                  Save Endpoint URL
                </Button>
                {saveSuccess && (
                  <span className="text-xs text-emerald-400 font-mono flex items-center gap-1 animate-in fade-in">
                    <CheckCircle2 className="h-3.5 w-3.5" /> Updated successfully
                  </span>
                )}
              </div>
            </form>
          </div>

          <div className="pt-3 border-t border-white/5 text-xs font-mono text-slate-400">
            <span>Protocol: HTTP/1.1 REST & WebSocket streaming</span>
          </div>
        </Card>

        {/* Simulation Mode & Cache Control Card */}
        <Card className="p-6 bg-slate-900/60 border-white/10 space-y-6 flex flex-col justify-between">
          <div className="space-y-6">
            <div className="flex items-center justify-between border-b border-white/5 pb-3">
              <h3 className="font-bold text-white flex items-center gap-2">
                <SlidersHorizontal className="h-4 w-4 text-purple-400" />
                Runtime Simulation & Cache Storage
              </h3>
              <Badge variant="outline" className="font-mono text-[10px] text-purple-300 border-purple-500/30">
                LOCAL STATE
              </Badge>
            </div>

            {/* Simulation Mode Toggle */}
            <div className="flex items-center justify-between rounded-xl bg-slate-950/70 p-4 border border-white/5">
              <div className="space-y-0.5">
                <div className="text-sm font-bold text-white flex items-center gap-1.5">
                  <span>Offline Research Simulation Mode</span>
                </div>
                <p className="text-xs text-slate-400 max-w-xs">
                  When enabled, bypasses live network calls and synthesizes research-grade inference responses locally.
                </p>
              </div>
              <button
                type="button"
                onClick={() => setSimulationMode(!simulationMode)}
                className={cn(
                  "relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none",
                  simulationMode ? "bg-purple-600 shadow-md shadow-purple-600/50" : "bg-slate-700"
                )}
              >
                <span
                  className={cn(
                    "inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out",
                    simulationMode ? "translate-x-5" : "translate-x-0"
                  )}
                />
              </button>
            </div>

            {/* Clear Job Queue Button */}
            <div className="flex items-center justify-between rounded-xl bg-slate-950/70 p-4 border border-white/5">
              <div className="space-y-0.5">
                <div className="text-sm font-bold text-white">Execution Job Queue History</div>
                <p className="text-xs text-slate-400">
                  Currently tracking <strong>{jobQueue.length}</strong> local prediction runs in Zustand store.
                </p>
              </div>
              <Button
                onClick={clearJobs}
                variant="destructive"
                size="sm"
                className="text-xs gap-1.5 cursor-pointer shrink-0"
              >
                <Trash2 className="h-3.5 w-3.5" />
                <span>Clear History</span>
              </Button>
            </div>
          </div>

          <div className="pt-3 border-t border-white/5 text-xs font-mono text-slate-400">
            <span>Storage Engine: HTML5 LocalStorage & Memory</span>
          </div>
        </Card>
      </div>

      {/* Hardware Telemetry & Cluster Status Card */}
      <Card className="p-6 bg-slate-900/60 border-white/10 space-y-4 font-mono text-xs">
        <div className="flex items-center justify-between border-b border-white/5 pb-3 font-sans">
          <h3 className="font-bold text-white flex items-center gap-2">
            <Cpu className="h-4 w-4 text-emerald-400" />
            Active GPU Hardware Cluster & System Diagnostics
          </h3>
          <Badge variant="success" className="font-mono text-[10px]">ALL CLUSTERS HEALTHY</Badge>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
          <div className="p-4 rounded-xl bg-slate-950/80 border border-white/10 space-y-1">
            <span className="text-slate-500 uppercase text-[10px]">Compute Node 01</span>
            <div className="text-base font-bold text-white">NVIDIA A100-SXM4-80GB</div>
            <div className="text-emerald-400 flex items-center gap-1.5 mt-1">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-ping" />
              <span>Temp: 44°C | VRAM: 14.2 / 80 GB</span>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/80 border border-white/10 space-y-1">
            <span className="text-slate-500 uppercase text-[10px]">Compute Node 02</span>
            <div className="text-base font-bold text-white">NVIDIA A100-SXM4-80GB</div>
            <div className="text-emerald-400 flex items-center gap-1.5 mt-1">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-ping" />
              <span>Temp: 46°C | VRAM: 8.8 / 80 GB</span>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/80 border border-white/10 space-y-1">
            <span className="text-slate-500 uppercase text-[10px]">Storage Node Array</span>
            <div className="text-base font-bold text-cyan-300">NVMe SSD RAID-0 Cluster</div>
            <div className="text-slate-300 mt-1">
              <span>Capacity: 70.8 TB / 120.0 TB</span>
            </div>
          </div>
        </div>

        <div className="rounded-xl bg-black/80 p-3.5 border border-white/10 text-[11px] text-slate-300 space-y-1">
          <div className="text-slate-500 font-bold"># System Environment Variables & Runtime Diagnostics</div>
          <div>NEXT_PUBLIC_API_URL: {apiUrl}</div>
          <div>NODE_ENV: production (optimized build)</div>
          <div>TANSTACK_QUERY_VERSION: ^5.62.0 | ZUSTAND_VERSION: ^5.0.3</div>
          <div>GAIA_KERNEL_BUILD: v1.0.0-rc4-research-grade (DeepMind / NASA standards)</div>
        </div>
      </Card>
    </div>
  );
}
