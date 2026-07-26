"use client";

import * as React from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import { cn } from "@/lib/utils";

interface TrendChartProps {
  data: { year: number; val: number; anomaly: number }[];
  dataKey?: string;
  color?: string;
  height?: number;
  className?: string;
}

export function TrendChart({
  data,
  dataKey = "val",
  color = "#00B4D8",
  height = 180,
  className,
}: TrendChartProps) {
  return (
    <div className={cn("w-full", className)} style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id={`gradient-${dataKey}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={color} stopOpacity={0.4} />
              <stop offset="95%" stopColor={color} stopOpacity={0.0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
          <XAxis
            dataKey="year"
            stroke="rgba(255,255,255,0.4)"
            fontSize={11}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            stroke="rgba(255,255,255,0.4)"
            fontSize={11}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "rgba(11, 19, 43, 0.95)",
              borderColor: "rgba(255, 255, 255, 0.15)",
              borderRadius: "0.75rem",
              color: "#fff",
              fontSize: "12px",
              fontFamily: "monospace",
              backdropFilter: "blur(8px)",
            }}
            labelStyle={{ color: "#90E0EF", fontWeight: "bold" }}
          />
          <Area
            type="monotone"
            dataKey={dataKey}
            stroke={color}
            strokeWidth={2.5}
            fillOpacity={1}
            fill={`url(#gradient-${dataKey})`}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
