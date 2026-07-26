"use client";

import * as React from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface RiskGaugeProps {
  score: number; // 0.0 to 1.0
  title?: string;
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
}

export function RiskGauge({ score, title = "Planetary Risk Level", size = "md", showLabel = true }: RiskGaugeProps) {
  const percentage = Math.min(100, Math.max(0, Math.round(score * 100)));

  const getStatus = (val: number) => {
    if (val >= 80) return { label: "CRITICAL ALERT", color: "#F77F00", textClass: "text-orange-400", bgClass: "bg-orange-500/20 border-orange-500/40" };
    if (val >= 65) return { label: "WARNING", color: "#FCBF49", textClass: "text-amber-400", bgClass: "bg-amber-500/20 border-amber-500/40" };
    if (val >= 50) return { label: "WATCH", color: "#00B4D8", textClass: "text-cyan-400", bgClass: "bg-cyan-500/20 border-cyan-500/40" };
    return { label: "NORMAL STABLE", color: "#2A9D8F", textClass: "text-emerald-400", bgClass: "bg-emerald-500/20 border-emerald-500/40" };
  };

  const status = getStatus(percentage);

  // SVG Gauge Math
  const radius = size === "lg" ? 80 : size === "md" ? 60 : 40;
  const strokeWidth = size === "lg" ? 14 : size === "md" ? 10 : 8;
  const circumference = 2 * Math.PI * radius;
  // Semi-circle gauge (180 deg)
  const arcLength = circumference / 2;
  const strokeDashoffset = arcLength - (percentage / 100) * arcLength;

  return (
    <div className="flex flex-col items-center justify-center p-4">
      <div className="relative flex flex-col items-center">
        <svg
          width={radius * 2 + strokeWidth * 2}
          height={radius + strokeWidth * 2}
          className="overflow-visible"
        >
          <defs>
            <linearGradient id="risk-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#2A9D8F" />
              <stop offset="50%" stopColor="#FCBF49" />
              <stop offset="100%" stopColor="#F77F00" />
            </linearGradient>
          </defs>
          {/* Background Track */}
          <circle
            cx={radius + strokeWidth}
            cy={radius + strokeWidth}
            r={radius}
            fill="transparent"
            stroke="rgba(255, 255, 255, 0.1)"
            strokeWidth={strokeWidth}
            strokeDasharray={`${arcLength} ${circumference}`}
            strokeLinecap="round"
            transform={`rotate(-180 ${radius + strokeWidth} ${radius + strokeWidth})`}
          />
          {/* Animated Progress Arc */}
          <motion.circle
            cx={radius + strokeWidth}
            cy={radius + strokeWidth}
            r={radius}
            fill="transparent"
            stroke="url(#risk-gradient)"
            strokeWidth={strokeWidth}
            strokeDasharray={`${arcLength} ${circumference}`}
            initial={{ strokeDashoffset: arcLength }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.2, ease: "easeOut" }}
            strokeLinecap="round"
            transform={`rotate(-180 ${radius + strokeWidth} ${radius + strokeWidth})`}
          />
        </svg>

        {/* Center Text */}
        <div className="absolute bottom-1 flex flex-col items-center">
          <motion.span
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.5 }}
            className={cn(
              "font-mono font-bold tracking-tight",
              size === "lg" ? "text-4xl" : size === "md" ? "text-3xl" : "text-xl",
              status.textClass
            )}
          >
            {percentage}%
          </motion.span>
          <span className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold">
            {title}
          </span>
        </div>
      </div>

      {showLabel && (
        <div className="mt-4 flex items-center gap-2">
          <span
            className={cn(
              "inline-flex items-center rounded-full px-3 py-1 text-xs font-bold border",
              status.bgClass,
              status.textClass
            )}
          >
            <span className="mr-1.5 h-2 w-2 rounded-full bg-current animate-ping" />
            {status.label}
          </span>
        </div>
      )}
    </div>
  );
}
