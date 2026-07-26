"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import {
  Search,
  Globe,
  LayoutDashboard,
  Compass,
  Cpu,
  Database,
  BarChart3,
  BookOpen,
  Settings,
  Zap,
  AlertTriangle,
  ArrowRight,
} from "lucide-react";
import { Dialog } from "@/components/ui/dialog";
import { TIPPING_ELEMENTS, MODEL_ZOO, DATASET_CATALOG } from "@/constants";
import { useGlobalStore } from "@/store";
import { cn } from "@/lib/utils";

interface CommandPaletteProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CommandPalette({ open, onOpenChange }: CommandPaletteProps) {
  const router = useRouter();
  const [search, setSearch] = React.useState("");
  const { setSelectedElementId, activeAlerts } = useGlobalStore();

  const handleSelect = (url: string, elementId?: string) => {
    if (elementId) {
      setSelectedElementId(elementId);
    }
    onOpenChange(false);
    router.push(url);
  };

  const filteredElements = TIPPING_ELEMENTS.filter((e) =>
    e.name.toLowerCase().includes(search.toLowerCase()) ||
    e.shortName.toLowerCase().includes(search.toLowerCase()) ||
    e.region.toLowerCase().includes(search.toLowerCase())
  );

  const filteredModels = MODEL_ZOO.filter((m) =>
    m.name.toLowerCase().includes(search.toLowerCase()) ||
    m.category.toLowerCase().includes(search.toLowerCase()) ||
    m.description.toLowerCase().includes(search.toLowerCase())
  );

  const filteredDatasets = DATASET_CATALOG.filter((d) =>
    d.name.toLowerCase().includes(search.toLowerCase()) ||
    d.source.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      {open && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 p-4 animate-in fade-in-0 duration-150">
          <div
            className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm"
            onClick={() => onOpenChange(false)}
          />
          <div className="relative z-50 w-full max-w-2xl overflow-hidden rounded-2xl border border-white/10 bg-slate-900/95 shadow-2xl backdrop-blur-xl animate-in zoom-in-95 duration-150 text-white">
            {/* Search Input Header */}
            <div className="flex items-center border-b border-white/10 px-4 py-3">
              <Search className="h-5 w-5 text-cyan-400 mr-3 shrink-0" />
              <input
                type="text"
                placeholder="Type a command or search models, datasets, tipping elements..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                autoFocus
                className="w-full bg-transparent text-sm text-white placeholder:text-slate-500 focus:outline-none font-medium"
              />
              <kbd className="rounded border border-white/10 bg-slate-800 px-2 py-0.5 font-mono text-[10px] font-bold text-slate-400">
                ESC
              </kbd>
            </div>

            {/* Results List */}
            <div className="max-h-[60vh] overflow-y-auto p-3 space-y-4">
              {/* Active Alerts Section */}
              {activeAlerts.length > 0 && !search && (
                <div className="space-y-1">
                  <div className="px-2 text-[11px] font-bold uppercase tracking-wider text-orange-400 flex items-center gap-1.5">
                    <AlertTriangle className="h-3.5 w-3.5 animate-bounce" /> Active Planetary Warnings
                  </div>
                  {activeAlerts.map((alertItem) => {
                    const el = TIPPING_ELEMENTS.find((e) => e.id === alertItem.elementId);
                    if (!el) return null;
                    return (
                      <button
                        key={alertItem.elementId}
                        onClick={() => handleSelect("/earth", el.id)}
                        className="flex w-full items-center justify-between rounded-xl p-2.5 text-left text-sm hover:bg-orange-500/15 border border-transparent hover:border-orange-500/30 transition-all cursor-pointer group"
                      >
                        <div className="flex items-center gap-3">
                          <span className="flex h-2 w-2 rounded-full bg-orange-500 animate-ping" />
                          <div>
                            <div className="font-semibold text-white">{el.name}</div>
                            <div className="text-xs text-orange-300 font-mono">
                              Status: {alertItem.alert.alert_level} • Lead time: ~{alertItem.alert.estimated_lead_time_steps} mo
                            </div>
                          </div>
                        </div>
                        <ArrowRight className="h-4 w-4 text-slate-400 group-hover:text-orange-400 group-hover:translate-x-1 transition-all" />
                      </button>
                    );
                  })}
                </div>
              )}

              {/* Tipping Elements Section */}
              {filteredElements.length > 0 && (
                <div className="space-y-1">
                  <div className="px-2 text-[11px] font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-1.5">
                    <Globe className="h-3 w-3" /> Tipping Elements ({filteredElements.length})
                  </div>
                  {filteredElements.map((el) => (
                    <button
                      key={el.id}
                      onClick={() => handleSelect("/earth", el.id)}
                      className="flex w-full items-center justify-between rounded-xl p-2.5 text-left text-sm hover:bg-white/5 border border-transparent hover:border-white/10 transition-all cursor-pointer group"
                    >
                      <div>
                        <div className="font-semibold text-white group-hover:text-cyan-300 transition-colors">
                          {el.name}
                        </div>
                        <div className="text-xs text-slate-400">
                          {el.region} • Risk Score: {(el.riskScore * 100).toFixed(0)}% ({el.status})
                        </div>
                      </div>
                      <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-white/5">
                        Explore 3D
                      </span>
                    </button>
                  ))}
                </div>
              )}

              {/* Models Section */}
              {filteredModels.length > 0 && (
                <div className="space-y-1">
                  <div className="px-2 text-[11px] font-bold uppercase tracking-wider text-purple-400 flex items-center gap-1.5">
                    <Cpu className="h-3 w-3" /> Neural Model Zoo ({filteredModels.length})
                  </div>
                  {filteredModels.map((mod) => (
                    <button
                      key={mod.id}
                      onClick={() => handleSelect("/models")}
                      className="flex w-full items-center justify-between rounded-xl p-2.5 text-left text-sm hover:bg-white/5 border border-transparent hover:border-white/10 transition-all cursor-pointer group"
                    >
                      <div>
                        <div className="font-semibold text-white group-hover:text-purple-300 transition-colors">
                          {mod.name}
                        </div>
                        <div className="text-xs text-slate-400">
                          {mod.category} • {mod.parameters} params • AUC: {mod.rocAuc}
                        </div>
                      </div>
                      <span className="text-xs font-mono px-2 py-0.5 rounded bg-purple-500/10 text-purple-300 border border-purple-500/20">
                        Run Inference
                      </span>
                    </button>
                  ))}
                </div>
              )}

              {/* Datasets Section */}
              {filteredDatasets.length > 0 && (
                <div className="space-y-1">
                  <div className="px-2 text-[11px] font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
                    <Database className="h-3 w-3" /> Datasets & Reanalysis ({filteredDatasets.length})
                  </div>
                  {filteredDatasets.map((ds) => (
                    <button
                      key={ds.id}
                      onClick={() => handleSelect("/datasets")}
                      className="flex w-full items-center justify-between rounded-xl p-2.5 text-left text-sm hover:bg-white/5 border border-transparent hover:border-white/10 transition-all cursor-pointer group"
                    >
                      <div>
                        <div className="font-semibold text-white group-hover:text-emerald-300 transition-colors">
                          {ds.name}
                        </div>
                        <div className="text-xs text-slate-400">
                          {ds.source} • {ds.temporalResolution}
                        </div>
                      </div>
                      <span className="text-xs font-mono text-slate-400">{ds.size}</span>
                    </button>
                  ))}
                </div>
              )}

              {/* Quick Navigation Shortcuts */}
              {!search && (
                <div className="space-y-1 pt-2 border-t border-white/10">
                  <div className="px-2 text-[11px] font-bold uppercase tracking-wider text-slate-400">
                    Quick Navigation
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      onClick={() => handleSelect("/dashboard")}
                      className="flex items-center gap-2 rounded-xl p-2.5 text-left text-sm hover:bg-white/5 border border-white/5 transition-all cursor-pointer"
                    >
                      <LayoutDashboard className="h-4 w-4 text-cyan-400" />
                      <span>Mission Control</span>
                    </button>
                    <button
                      onClick={() => handleSelect("/predict")}
                      className="flex items-center gap-2 rounded-xl p-2.5 text-left text-sm hover:bg-white/5 border border-white/5 transition-all cursor-pointer"
                    >
                      <Zap className="h-4 w-4 text-purple-400" />
                      <span>Prediction Studio</span>
                    </button>
                    <button
                      onClick={() => handleSelect("/analytics")}
                      className="flex items-center gap-2 rounded-xl p-2.5 text-left text-sm hover:bg-white/5 border border-white/5 transition-all cursor-pointer"
                    >
                      <BarChart3 className="h-4 w-4 text-emerald-400" />
                      <span>Scientific Analytics</span>
                    </button>
                    <button
                      onClick={() => handleSelect("/research")}
                      className="flex items-center gap-2 rounded-xl p-2.5 text-left text-sm hover:bg-white/5 border border-white/5 transition-all cursor-pointer"
                    >
                      <BookOpen className="h-4 w-4 text-amber-400" />
                      <span>Methodology & Papers</span>
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="border-t border-white/10 bg-slate-950/60 px-4 py-2 text-xs text-slate-400 flex items-center justify-between">
              <span>Press <kbd className="font-mono text-slate-300">↑↓</kbd> to navigate, <kbd className="font-mono text-slate-300">ENTER</kbd> to select</span>
              <span className="font-mono text-[10px] text-cyan-400">Gaia OS Intelligence</span>
            </div>
          </div>
        </div>
      )}
    </Dialog>
  );
}
