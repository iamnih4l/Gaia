"use client";

import * as React from "react";
import { motion } from "framer-motion";
import { LucideIcon, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { cn, formatNumber } from "@/lib/utils";
import { Card } from "@/components/ui/card";

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  change?: string;
  trend?: "up" | "down" | "neutral";
  icon: LucideIcon;
  iconColor?: string;
  className?: string;
  glow?: "cyan" | "purple" | "danger" | "none";
}

export function MetricCard({
  title,
  value,
  subtitle,
  change,
  trend = "neutral",
  icon: Icon,
  iconColor = "text-cyan-400",
  className,
  glow = "none",
}: MetricCardProps) {
  return (
    <motion.div
      whileHover={{ y: -3, transition: { duration: 0.2 } }}
      className={cn("h-full", className)}
    >
      <Card
        className={cn(
          "h-full p-6 flex flex-col justify-between relative overflow-hidden bg-slate-900/50 backdrop-blur-xl border border-white/10 hover:border-white/20 transition-all",
          glow === "cyan" && "hover:shadow-[0_0_30px_-5px_rgba(0,180,216,0.3)]",
          glow === "purple" && "hover:shadow-[0_0_30px_-5px_rgba(114,9,183,0.3)]",
          glow === "danger" && "hover:shadow-[0_0_30px_-5px_rgba(247,127,0,0.3)]"
        )}
      >
        {/* Decorative subtle gradient background blob */}
        <div className="absolute -right-6 -top-6 h-24 w-24 rounded-full bg-gradient-to-br from-white/5 to-transparent blur-xl pointer-events-none" />

        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              {title}
            </span>
            <div className="text-2xl md:text-3xl font-bold tracking-tight text-white font-mono">
              {typeof value === "number" ? formatNumber(value) : value}
            </div>
          </div>
          <div className={cn("rounded-xl p-2.5 bg-white/5 border border-white/10", iconColor)}>
            <Icon className="h-6 w-6" />
          </div>
        </div>

        {(subtitle || change) && (
          <div className="mt-4 flex items-center justify-between text-xs pt-3 border-t border-white/5">
            {subtitle && <span className="text-slate-400 truncate">{subtitle}</span>}
            {change && (
              <div
                className={cn(
                  "flex items-center gap-1 font-semibold font-mono",
                  trend === "up" && "text-emerald-400",
                  trend === "down" && "text-orange-400",
                  trend === "neutral" && "text-slate-400"
                )}
              >
                {trend === "up" && <TrendingUp className="h-3.5 w-3.5" />}
                {trend === "down" && <TrendingDown className="h-3.5 w-3.5" />}
                {trend === "neutral" && <Minus className="h-3.5 w-3.5" />}
                <span>{change}</span>
              </div>
            )}
          </div>
        )}
      </Card>
    </motion.div>
  );
}
