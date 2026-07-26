/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars */
"use client";

import { create } from "zustand";
import { JobItem, TippingAlert } from "@/types/api";
import { TIPPING_ELEMENTS } from "@/constants";
import { apiService } from "@/services/api";

interface GlobalState {
  theme: "dark" | "light";
  simulationMode: boolean;
  selectedElementId: string;
  activeAlerts: { elementId: string; alert: TippingAlert; timestamp: string }[];
  jobQueue: JobItem[];
  
  // Actions
  toggleTheme: () => void;
  setSimulationMode: (enabled: boolean) => void;
  setSelectedElementId: (id: string) => void;
  addAlert: (elementId: string, alert: TippingAlert) => void;
  dismissAlert: (elementId: string) => void;
  addJob: (job: Omit<JobItem, "id" | "status" | "progress" | "startTime" | "logs">) => string;
  updateJobProgress: (id: string, progress: number, log?: string) => void;
  completeJob: (id: string, result: any) => void;
  failJob: (id: string, errorLog: string) => void;
  clearJobs: () => void;
}

export const useGlobalStore = create<GlobalState>((set, get) => ({
  theme: "dark",
  simulationMode: false,
  selectedElementId: "amoc",
  activeAlerts: [
    {
      elementId: "coral",
      alert: {
        alarm_triggered: true,
        alert_level: "CRITICAL",
        threshold: 0.5,
        estimated_lead_time_steps: 3,
      },
      timestamp: new Date().toISOString(),
    },
    {
      elementId: "greenland",
      alert: {
        alarm_triggered: true,
        alert_level: "WARNING",
        threshold: 0.5,
        estimated_lead_time_steps: 9,
      },
      timestamp: new Date().toISOString(),
    },
  ],
  jobQueue: [
    {
      id: "job-initial-1",
      elementId: "amoc",
      modelId: "temporal_fusion_transformer",
      status: "completed",
      progress: 100,
      startTime: new Date(Date.now() - 3600000).toISOString(),
      logs: [
        "[00:00.12] Initializing dataset windowing (seq_len=24)...",
        "[00:00.45] Loading weights for Temporal Fusion Transformer (3.2M params)...",
        "[00:01.89] Executing attention extraction & MC Dropout (n=50)...",
        "[00:02.15] Inference complete. Probability: 68.4% (WARNING)",
      ],
    },
  ],

  toggleTheme: () =>
    set((state) => {
      const next = state.theme === "dark" ? "light" : "dark";
      if (typeof document !== "undefined") {
        document.documentElement.classList.toggle("dark", next === "dark");
      }
      return { theme: next };
    }),

  setSimulationMode: (enabled) => {
    apiService.setSimulationMode(enabled);
    set({ simulationMode: enabled });
  },

  setSelectedElementId: (id) => set({ selectedElementId: id }),

  addAlert: (elementId, alert) =>
    set((state) => ({
      activeAlerts: [
        { elementId, alert, timestamp: new Date().toISOString() },
        ...state.activeAlerts.filter((a) => a.elementId !== elementId),
      ],
    })),

  dismissAlert: (elementId) =>
    set((state) => ({
      activeAlerts: state.activeAlerts.filter((a) => a.elementId !== elementId),
    })),

  addJob: (jobData) => {
    const id = `job-${Date.now().toString(36)}`;
    const newJob: JobItem = {
      ...jobData,
      id,
      status: "queued",
      progress: 0,
      startTime: new Date().toISOString(),
      logs: [`[${new Date().toLocaleTimeString()}] Job queued for execution...`],
    };
    set((state) => ({ jobQueue: [newJob, ...state.jobQueue] }));
    return id;
  },

  updateJobProgress: (id, progress, log) =>
    set((state) => ({
      jobQueue: state.jobQueue.map((job) => {
        if (job.id !== id) return job;
        const newLogs = log ? [...job.logs, `[${new Date().toLocaleTimeString()}] ${log}`] : job.logs;
        return {
          ...job,
          status: progress < 100 ? "running" : job.status,
          progress,
          logs: newLogs,
        };
      }),
    })),

  completeJob: (id, result) =>
    set((state) => ({
      jobQueue: state.jobQueue.map((job) => {
        if (job.id !== id) return job;
        return {
          ...job,
          status: "completed",
          progress: 100,
          result,
          logs: [...job.logs, `[${new Date().toLocaleTimeString()}] Execution completed successfully. Result: ${(result.tipping_probability * 100).toFixed(1)}% risk.`],
        };
      }),
    })),

  failJob: (id, errorLog) =>
    set((state) => ({
      jobQueue: state.jobQueue.map((job) => {
        if (job.id !== id) return job;
        return {
          ...job,
          status: "failed",
          progress: 0,
          logs: [...job.logs, `[${new Date().toLocaleTimeString()}] ERROR: ${errorLog}`],
        };
      }),
    })),

  clearJobs: () => set({ jobQueue: [] }),
}));
