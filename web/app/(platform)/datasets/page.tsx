"use client";

import * as React from "react";
import { motion } from "framer-motion";
import {
  Database,
  Search,
  Filter,
  Download,
  ExternalLink,
  CheckCircle2,
  RefreshCw,
  Eye,
  Calendar,
  Globe,
  Layers,
  FileSpreadsheet,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { DATASET_CATALOG } from "@/constants";
import { DatasetMetadata } from "@/types/api";
import { cn, formatNumber } from "@/lib/utils";

export default function DatasetsPage() {
  const [search, setSearch] = React.useState("");
  const [selectedStatus, setSelectedStatus] = React.useState<string>("all");
  const [selectedDataset, setSelectedDataset] = React.useState<DatasetMetadata | null>(null);

  const filteredDatasets = React.useMemo(() => {
    return DATASET_CATALOG.filter((ds) => {
      const matchesSearch =
        ds.name.toLowerCase().includes(search.toLowerCase()) ||
        ds.source.toLowerCase().includes(search.toLowerCase()) ||
        ds.coverage.toLowerCase().includes(search.toLowerCase()) ||
        ds.variables.some((v) => v.toLowerCase().includes(search.toLowerCase()));
      const matchesStatus = selectedStatus === "all" || ds.status.toLowerCase() === selectedStatus.toLowerCase();
      return matchesSearch && matchesStatus;
    });
  }, [search, selectedStatus]);

  return (
    <div className="space-y-8 animate-in fade-in-50 duration-300">
      {/* Title Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-white/10 pb-6">
        <div className="space-y-1">
          <Badge variant="success" className="px-2.5 py-0.5 text-xs">Observational & Simulation Data</Badge>
          <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white">
            Dataset Catalog & Pipeline Ingestor
          </h2>
          <p className="text-sm text-slate-300 max-w-3xl">
            Central repository of satellite telemetry, oceanographic mooring arrays, atmospheric reanalysis, and CMIP6 climate model projections powering Gaia’s neural training and live inference engines.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="gap-2 border-white/20">
            <RefreshCw className="h-3.5 w-3.5 text-cyan-400" />
            <span>Sync Catalog</span>
          </Button>
          <Button variant="gradient" size="sm" className="gap-2 shadow-lg shadow-cyan-500/20">
            <Download className="h-3.5 w-3.5" />
            <span>Export Metadata (CSV)</span>
          </Button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <Card className="p-4 bg-slate-900/60 border-white/10 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="relative w-full sm:w-80">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search dataset name, source, or variables..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-xl border border-white/10 bg-slate-950/60 py-2 pl-9 pr-4 text-xs text-white placeholder:text-slate-500 focus:border-cyan-500 focus:outline-none"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
          <span className="text-xs text-slate-400 font-mono hidden md:inline">Filter Status:</span>
          <div className="flex rounded-xl bg-slate-950/80 p-1 border border-white/10 text-xs font-semibold">
            {["all", "active", "syncing"].map((status) => (
              <button
                key={status}
                onClick={() => setSelectedStatus(status)}
                className={cn(
                  "rounded-lg px-3 py-1 capitalize transition-all cursor-pointer",
                  selectedStatus === status ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30" : "text-slate-400 hover:text-white"
                )}
              >
                {status}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {/* Main Datasets Table */}
      <Card className="bg-slate-900/60 border-white/10 overflow-hidden shadow-xl">
        <Table>
          <TableHeader className="bg-slate-950/60">
            <TableRow>
              <TableHead className="w-[280px]">Dataset Name & Source</TableHead>
              <TableHead>Spatial / Temporal Resolution</TableHead>
              <TableHead>Date Range</TableHead>
              <TableHead>Records</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredDatasets.map((ds) => (
              <TableRow key={ds.id} className="hover:bg-white/5 transition-colors group">
                <TableCell className="font-medium text-white">
                  <div className="flex items-start gap-3">
                    <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                      <Database className="h-4 w-4" />
                    </div>
                    <div>
                      <div className="font-bold group-hover:text-cyan-300 transition-colors">{ds.name}</div>
                      <div className="text-[11px] text-slate-400 font-mono mt-0.5">{ds.source}</div>
                    </div>
                  </div>
                </TableCell>
                <TableCell className="text-xs text-slate-300">
                  <div className="font-semibold">{ds.spatialResolution}</div>
                  <div className="text-[11px] text-slate-400 font-mono mt-0.5">{ds.temporalResolution}</div>
                </TableCell>
                <TableCell className="text-xs font-mono text-cyan-300">{ds.dateRange}</TableCell>
                <TableCell className="text-xs font-mono font-bold text-white">
                  {formatNumber(ds.records)}
                  <div className="text-[10px] text-slate-400 font-normal">{ds.size}</div>
                </TableCell>
                <TableCell>
                  <Badge variant={ds.status === "Active" ? "success" : "warning"} className="font-mono text-[10px]">
                    {ds.status}
                  </Badge>
                </TableCell>
                <TableCell className="text-right">
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => setSelectedDataset(ds)}
                    className="text-xs gap-1.5 cursor-pointer"
                  >
                    <Eye className="h-3.5 w-3.5 text-cyan-400" />
                    <span>Inspect</span>
                  </Button>
                </TableCell>
              </TableRow>
            ))}
            {filteredDatasets.length === 0 && (
              <TableRow>
                <TableCell colSpan={6} className="h-32 text-center text-slate-500 text-sm">
                  No datasets match the current filter criteria.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </Card>

      {/* Dataset Preview Modal */}
      <Dialog open={!!selectedDataset} onOpenChange={(open) => !open && setSelectedDataset(null)}>
        {selectedDataset && (
          <DialogContent className="max-w-2xl p-6 bg-slate-900/95 border-white/10 space-y-6">
            <DialogHeader>
              <div className="flex items-center justify-between pr-8">
                <span className="text-xs font-mono text-emerald-400 uppercase tracking-wider">{selectedDataset.source}</span>
                <Badge variant="success" className="font-mono text-xs">{selectedDataset.status}</Badge>
              </div>
              <DialogTitle className="text-2xl font-extrabold text-white mt-1">
                {selectedDataset.name}
              </DialogTitle>
              <DialogDescription className="text-sm text-slate-300 leading-relaxed mt-2">
                Spatial coverage: <strong>{selectedDataset.coverage}</strong> with <strong>{selectedDataset.temporalResolution}</strong> sampling intervals.
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 pt-2">
              <div className="grid grid-cols-3 gap-3 font-mono text-xs">
                <div className="p-3 rounded-xl bg-slate-950/80 border border-white/10">
                  <span className="text-slate-500 block text-[10px]">Total Volume</span>
                  <span className="font-bold text-white text-base">{selectedDataset.size}</span>
                </div>
                <div className="p-3 rounded-xl bg-slate-950/80 border border-white/10">
                  <span className="text-slate-500 block text-[10px]">Temporal Range</span>
                  <span className="font-bold text-cyan-400 text-base">{selectedDataset.dateRange}</span>
                </div>
                <div className="p-3 rounded-xl bg-slate-950/80 border border-white/10">
                  <span className="text-slate-500 block text-[10px]">Record Count</span>
                  <span className="font-bold text-emerald-400 text-base">{formatNumber(selectedDataset.records)}</span>
                </div>
              </div>

              <div className="space-y-2">
                <span className="text-xs font-bold text-slate-300 uppercase tracking-wider block">
                  Extracted Telemetry Variables ({selectedDataset.variables.length})
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {selectedDataset.variables.map((v) => (
                    <span key={v} className="px-2.5 py-1 rounded-lg bg-white/5 border border-white/10 text-xs font-mono text-cyan-300">
                      {v}
                    </span>
                  ))}
                </div>
              </div>

              {/* Sample Data Snippet Box */}
              <div className="space-y-2">
                <span className="text-xs font-bold text-slate-300 uppercase tracking-wider block">
                  Sample Parquet Header / Schema Preview
                </span>
                <div className="bg-black/80 rounded-xl p-3.5 border border-white/10 font-mono text-[11px] text-emerald-400 overflow-x-auto">
                  <div>timestamp | lat | lon | {selectedDataset.variables[0]} | {selectedDataset.variables[1] || "val_1"}</div>
                  <div className="text-slate-500">-----------------------------------------------------------------------</div>
                  <div>2024-01-01T00:00:00Z | 26.50 | -76.20 | 16.42 | 0.854</div>
                  <div>2024-01-02T00:00:00Z | 26.50 | -76.20 | 16.39 | 0.851</div>
                  <div>2024-01-03T00:00:00Z | 26.50 | -76.20 | 16.45 | 0.862</div>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-4 border-t border-white/10">
              <Button variant="outline" size="sm" onClick={() => setSelectedDataset(null)} className="text-xs">
                Close
              </Button>
              <Button variant="gradient" size="sm" className="gap-2 text-xs shadow-md shadow-cyan-500/20 font-bold">
                <FileSpreadsheet className="h-3.5 w-3.5" />
                <span>Download Sample Slice (NetCDF/Parquet)</span>
              </Button>
            </div>
          </DialogContent>
        )}
      </Dialog>
    </div>
  );
}
