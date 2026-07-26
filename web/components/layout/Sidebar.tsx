"use client";

import * as React from "react";
import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Globe,
  LayoutDashboard,
  Compass,
  Cpu,
  Database,
  BarChart3,
  BookOpen,
  Settings,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Zap,
  ShieldCheck,
  Terminal,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useGlobalStore } from "@/store";
import { Badge } from "@/components/ui/badge";

const CORE_NAV_ITEMS = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard, code: "CMD_01" },
  { name: "Interactive Earth", href: "/earth", icon: Globe, badge: "LIVE 3D", code: "GEO_02" },
  { name: "Risk Explorer", href: "/explorer", icon: Compass, code: "RSK_03" },
  { name: "Prediction Studio", href: "/predict", icon: Zap, badge: "AI CORE", code: "INF_04" },
];

const SYS_NAV_ITEMS = [
  { name: "Dataset Manager", href: "/datasets", icon: Database, code: "DAT_05" },
  { name: "Model Zoo", href: "/models", icon: Cpu, code: "NET_06" },
  { name: "Scientific Analytics", href: "/analytics", icon: BarChart3, code: "TEL_07" },
  { name: "Research & Citations", href: "/research", icon: BookOpen, code: "BIB_08" },
  { name: "Settings & System", href: "/settings", icon: Settings, code: "CFG_09" },
];

export function Sidebar() {
  const pathname = usePathname();
  const [isCollapsed, setIsCollapsed] = React.useState(false);
  const { simulationMode, activeAlerts } = useGlobalStore();

  const criticalAlertsCount = activeAlerts.filter((a) => a.alert.alert_level === "CRITICAL" || a.alert.alert_level === "WARNING").length;

  return (
    <motion.aside
      initial={{ width: 270 }}
      animate={{ width: isCollapsed ? 80 : 270 }}
      transition={{ duration: 0.25, ease: "easeInOut" }}
      className="relative z-40 flex flex-col border-r border-white/15 bg-black/95 backdrop-blur-2xl h-screen sticky top-0 shrink-0 select-none shadow-[4px_0_30px_rgba(0,0,0,0.9)]"
    >
      {/* Brand Header */}
      <div className="flex h-16 items-center justify-between px-4 border-b border-white/15 bg-gradient-to-b from-white/[0.03] to-transparent">
        <Link href="/" className="flex items-center gap-3 overflow-hidden">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-cyan-400/60 bg-black shadow-[0_0_15px_rgba(0,242,254,0.3)] overflow-hidden">
            <Image src="/logo.svg" width={36} height={36} alt="Gaia Logo" className="h-full w-full object-cover" />
          </div>
          <AnimatePresence>
            {!isCollapsed && (
              <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                transition={{ duration: 0.15 }}
                className="flex flex-col truncate"
              >
                <span className="font-mono font-bold tracking-wider text-white text-sm flex items-center gap-1.5 drop-shadow-[0_0_8px_rgba(255,255,255,0.3)]">
                  GAIA <span className="text-[9px] uppercase font-mono px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">SYS v2.4</span>
                </span>
                <span className="text-[10px] text-slate-400 font-mono tracking-widest uppercase">ORBITAL COMMAND</span>
              </motion.div>
            )}
          </AnimatePresence>
        </Link>
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="flex h-7 w-7 items-center justify-center rounded-lg border border-white/15 bg-white/[0.04] text-slate-400 hover:border-cyan-400/60 hover:bg-cyan-500/15 hover:text-cyan-300 transition-all cursor-pointer shadow-sm"
          title={isCollapsed ? "Expand Command Deck" : "Collapse Command Deck"}
        >
          {isCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </button>
      </div>

      {/* Navigation List */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-4">
        {/* Module 1: Core Navigation */}
        <div className="space-y-1">
          {!isCollapsed && (
            <div className="px-3 py-1.5 text-[10px] font-mono font-bold tracking-widest text-cyan-400/80 uppercase flex items-center gap-1.5">
              <Terminal className="h-3 w-3 inline" />
              <span>{"// 01 :: CORE MODULES"}</span>
            </div>
          )}
          {CORE_NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "group relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-xs font-mono tracking-wide transition-all duration-200",
                  isActive
                    ? "bg-gradient-to-r from-cyan-500/20 via-cyan-500/5 to-transparent text-cyan-300 border border-cyan-500/50 shadow-[inset_0_0_15px_rgba(0,242,254,0.15)] font-bold"
                    : "text-slate-400 hover:bg-white/[0.04] hover:text-slate-200 hover:border-white/20 border border-transparent"
                )}
              >
                <Icon
                  className={cn(
                    "h-4 w-4 shrink-0 transition-transform duration-200 group-hover:scale-110",
                    isActive ? "text-cyan-400 drop-shadow-[0_0_6px_rgba(0,242,254,0.8)]" : "text-slate-400 group-hover:text-cyan-300"
                  )}
                />
                <AnimatePresence>
                  {!isCollapsed && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.15 }}
                      className="flex flex-1 items-center justify-between overflow-hidden whitespace-nowrap"
                    >
                      <span className="truncate">{item.name}</span>
                      {item.badge ? (
                        <span className="ml-auto rounded bg-cyan-500/20 px-1.5 py-0.5 text-[9px] font-mono font-bold text-cyan-300 border border-cyan-500/40">
                          {item.badge}
                        </span>
                      ) : (
                        <span className="ml-auto text-[9px] font-mono text-slate-600 group-hover:text-slate-400 transition-colors">
                          [{item.code}]
                        </span>
                      )}
                    </motion.div>
                  )}
                </AnimatePresence>
                {isActive && (
                  <div className="absolute left-0 top-1.5 bottom-1.5 w-1 rounded-r-full bg-cyan-400 shadow-[0_0_8px_rgba(0,242,254,0.8)]" />
                )}
              </Link>
            );
          })}
        </div>

        {/* Module 2: System & Research */}
        <div className="space-y-1">
          {!isCollapsed && (
            <div className="px-3 py-1.5 text-[10px] font-mono font-bold tracking-widest text-purple-400/80 uppercase flex items-center gap-1.5 border-t border-white/[0.06] pt-3">
              <ShieldCheck className="h-3 w-3 inline" />
              <span>{"// 02 :: RESEARCH & SYS"}</span>
            </div>
          )}
          {SYS_NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "group relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-xs font-mono tracking-wide transition-all duration-200",
                  isActive
                    ? "bg-gradient-to-r from-purple-500/20 via-purple-500/5 to-transparent text-purple-300 border border-purple-500/50 shadow-[inset_0_0_15px_rgba(168,85,247,0.15)] font-bold"
                    : "text-slate-400 hover:bg-white/[0.04] hover:text-slate-200 hover:border-white/20 border border-transparent"
                )}
              >
                <Icon
                  className={cn(
                    "h-4 w-4 shrink-0 transition-transform duration-200 group-hover:scale-110",
                    isActive ? "text-purple-400 drop-shadow-[0_0_6px_rgba(168,85,247,0.8)]" : "text-slate-400 group-hover:text-purple-300"
                  )}
                />
                <AnimatePresence>
                  {!isCollapsed && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.15 }}
                      className="flex flex-1 items-center justify-between overflow-hidden whitespace-nowrap"
                    >
                      <span className="truncate">{item.name}</span>
                      <span className="ml-auto text-[9px] font-mono text-slate-600 group-hover:text-slate-400 transition-colors">
                        [{item.code}]
                      </span>
                    </motion.div>
                  )}
                </AnimatePresence>
                {isActive && (
                  <div className="absolute left-0 top-1.5 bottom-1.5 w-1 rounded-r-full bg-purple-400 shadow-[0_0_8px_rgba(168,85,247,0.8)]" />
                )}
              </Link>
            );
          })}
        </div>
      </div>

      {/* Sidebar Footer / Orbital Telemetry Diagnostic Console */}
      <div className="border-t border-white/15 p-3 bg-black/90">
        <AnimatePresence>
          {!isCollapsed ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="rounded-lg border border-white/15 bg-white/[0.03] p-3 space-y-2 backdrop-blur-xl shadow-inner"
            >
              <div className="flex items-center justify-between text-xs font-mono font-bold text-slate-200 uppercase tracking-wider">
                <span className="flex items-center gap-1.5 text-cyan-300">
                  <Sparkles className="h-3.5 w-3.5 text-cyan-400 animate-spin" style={{ animationDuration: "8s" }} />
                  SYS_HEALTH
                </span>
                <Badge variant={simulationMode ? "warning" : "success"} className="text-[9px] font-mono px-1.5 py-0 uppercase">
                  {simulationMode ? "SIMULATED" : "ONLINE"}
                </Badge>
              </div>
              <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono tracking-wider">
                <span>ALARMS:</span>
                <span className={cn("font-bold", criticalAlertsCount > 0 ? "text-orange-400 animate-pulse" : "text-emerald-400")}>
                  {criticalAlertsCount > 0 ? `[ ${criticalAlertsCount} CRITICAL ]` : "[ 0 NOMINAL ]"}
                </span>
              </div>
              <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono tracking-wider">
                <span>GPU_CLUSTER:</span>
                <span className="text-cyan-400 font-bold">[ 2X A100-80G ]</span>
              </div>
            </motion.div>
          ) : (
            <div className="flex flex-col items-center gap-2 py-1">
              <div className="h-2.5 w-2.5 rounded-full bg-emerald-400 animate-ping shadow-[0_0_8px_rgba(16,185,129,0.8)]" title="System Nominal" />
              <span className="text-[9px] font-mono text-slate-500 font-bold uppercase">OK</span>
            </div>
          )}
        </AnimatePresence>
      </div>
    </motion.aside>
  );
}
