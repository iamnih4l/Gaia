"use client";

import * as React from "react";
import { usePathname } from "next/navigation";
import {
  Search,
  Activity,
  Bell,
  Cpu,
  Radio,
  SlidersHorizontal,
  RefreshCw,
  AlertTriangle,
  Terminal,
  Orbit,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useHealthQuery } from "@/hooks/useApi";
import { useGlobalStore } from "@/store";
import { Badge } from "@/components/ui/badge";

export function Topbar({ onOpenCommandPalette }: { onOpenCommandPalette: () => void }) {
  const pathname = usePathname();
  const { data: healthData, isLoading, refetch, isRefetching } = useHealthQuery();
  const { simulationMode, setSimulationMode, activeAlerts } = useGlobalStore();
  const [utcTime, setUtcTime] = React.useState<string>("");

  React.useEffect(() => {
    const updateClock = () => {
      const now = new Date();
      const formatted = now.toISOString().replace("T", " // ").replace(/\.\d+Z$/, " UTC");
      setUtcTime(formatted);
    };
    updateClock();
    const timer = setInterval(updateClock, 1000);
    return () => clearInterval(timer);
  }, []);

  const getPageTitle = () => {
    if (pathname === "/dashboard") return "SYS_CMD :: MISSION CONTROL DASHBOARD";
    if (pathname === "/earth") return "OPTICAL_RADAR :: PLANETARY TIP_HOTSPOTS";
    if (pathname === "/explorer") return "DATA_BANK :: CLIMATE RISK EXPLORER";
    if (pathname === "/predict") return "AI_CORE :: PREDICTION STUDIO INFERENCE";
    if (pathname === "/datasets") return "INGEST_PIPE :: DATASET CATALOG MATRIX";
    if (pathname === "/models") return "NEURAL_NET :: ARCHITECTURE ZOO";
    if (pathname === "/analytics") return "TELEMETRY :: SCIENTIFIC BENCHMARKS";
    if (pathname === "/research") return "ARCHIVE :: METHODOLOGY & CITATIONS";
    if (pathname === "/settings") return "DIAGNOSTIC :: SYSTEM CONFIG & GPU CLUSTER";
    return "GAIA ORBITAL RESEARCH STATION";
  };

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-white/15 bg-black/90 px-6 backdrop-blur-2xl shrink-0 shadow-[0_4px_30px_rgba(0,0,0,0.9)]">
      {/* Left / Title & Flight HUD */}
      <div className="flex items-center gap-4 overflow-hidden">
        <div className="hidden sm:flex items-center justify-center h-8 w-8 rounded-lg border border-cyan-500/40 bg-cyan-500/10 text-cyan-400 shrink-0">
          <Terminal className="h-4 w-4 animate-pulse" />
        </div>
        <div className="flex flex-col">
          <h1 className="text-xs sm:text-sm font-mono font-bold tracking-wider text-white uppercase flex items-center gap-2 drop-shadow-[0_0_10px_rgba(0,242,254,0.3)] truncate">
            {getPageTitle()}
          </h1>
          <div className="flex items-center gap-3 text-[10px] font-mono text-slate-400 tracking-widest uppercase">
            <span className="hidden md:inline-flex items-center gap-1 text-cyan-400/80">
              <Orbit className="h-3 w-3 inline" /> LEO // ALT: 408.2 KM // INCL: 51.6°
            </span>
            <span className="hidden xl:inline text-slate-600">|</span>
            <span className="text-purple-400/90">{utcTime || "SYNCHRONIZING UTC..."}</span>
          </div>
        </div>
      </div>

      {/* Right / Telemetry & Controls */}
      <div className="flex items-center gap-2 sm:gap-3 shrink-0">
        {/* Command Palette Trigger */}
        <button
          onClick={onOpenCommandPalette}
          className="flex items-center gap-2 rounded-lg border border-white/15 bg-white/[0.04] px-3 py-1.5 text-xs text-slate-300 transition-all hover:border-cyan-400/60 hover:bg-cyan-500/10 hover:text-cyan-300 cursor-pointer shadow-sm backdrop-blur-md"
          title="Search telemetry, models, regions (Cmd+K)"
        >
          <Search className="h-3.5 w-3.5 text-cyan-400" />
          <span className="hidden lg:inline font-mono text-[11px] font-semibold tracking-wider uppercase">SCAN_RADAR (⌘K)</span>
          <kbd className="hidden md:inline-flex items-center gap-0.5 rounded border border-cyan-500/30 bg-black/60 px-1.5 py-0.5 font-mono text-[10px] font-bold text-cyan-400">
            ⌘K
          </kbd>
        </button>

        {/* Simulation Mode Toggle */}
        <div className="flex items-center gap-2 rounded-lg border border-white/15 bg-white/[0.04] px-3 py-1.5 text-xs backdrop-blur-md">
          <SlidersHorizontal className="h-3.5 w-3.5 text-purple-400 animate-pulse" />
          <span className="hidden xl:inline font-mono text-[11px] text-purple-300 font-bold tracking-wider uppercase">SIM_MODE</span>
          <button
            type="button"
            onClick={() => setSimulationMode(!simulationMode)}
            className={cn(
              "relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-300 ease-in-out focus:outline-none",
              simulationMode ? "bg-purple-600 shadow-[0_0_12px_rgba(168,85,247,0.8)]" : "bg-slate-800 border-white/20"
            )}
            title="Toggle between live FastAPI server and offline research simulation mode"
          >
            <span
              className={cn(
                "inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-300 ease-in-out",
                simulationMode ? "translate-x-4 bg-cyan-200" : "translate-x-0"
              )}
            />
          </button>
        </div>

        {/* Live Status Pill */}
        <div className="flex items-center gap-2 rounded-lg border border-white/15 bg-white/[0.04] px-3 py-1.5 text-xs backdrop-blur-md">
          <div className="relative flex h-2.5 w-2.5 items-center justify-center">
            <span
              className={cn(
                "absolute inline-flex h-full w-full rounded-full opacity-80 animate-ping",
                simulationMode
                  ? "bg-purple-400"
                  : healthData
                  ? "bg-emerald-400"
                  : "bg-orange-400"
              )}
            />
            <span
              className={cn(
                "relative inline-flex rounded-full h-2 w-2 shadow-sm",
                simulationMode
                  ? "bg-purple-500 shadow-purple-500/80"
                  : healthData
                  ? "bg-emerald-500 shadow-emerald-500/80"
                  : "bg-orange-500 shadow-orange-500/80"
              )}
            />
          </div>
          <span className="font-mono text-[11px] text-slate-200 font-bold tracking-wider uppercase hidden sm:inline">
            SYS::{isLoading ? "PROBING" : simulationMode ? "SIMULATED" : healthData?.status || "OFFLINE"}
          </span>
          <button
            onClick={() => refetch()}
            disabled={isRefetching}
            className="text-slate-400 hover:text-cyan-400 transition-colors ml-1 cursor-pointer"
            title="Re-probe API telemetry"
          >
            <RefreshCw className={cn("h-3 w-3", isRefetching && "animate-spin text-cyan-400")} />
          </button>
        </div>

        {/* Alerts Bell Button */}
        <div className="relative">
          <button
            onClick={() => onOpenCommandPalette()}
            className="flex h-9 w-9 items-center justify-center rounded-lg border border-white/15 bg-white/[0.04] text-slate-300 hover:border-orange-500/50 hover:bg-orange-500/15 hover:text-orange-400 transition-all cursor-pointer relative backdrop-blur-md shadow-sm"
            title="View Critical System Alarms"
          >
            <Bell className="h-4 w-4" />
            {activeAlerts.length > 0 && (
              <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-orange-600 text-[10px] font-mono font-bold text-white animate-bounce shadow-[0_0_10px_rgba(249,115,22,0.8)]">
                {activeAlerts.length}
              </span>
            )}
          </button>
        </div>
      </div>
    </header>
  );
}
