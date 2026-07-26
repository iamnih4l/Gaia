"use client";

import * as React from "react";
import { motion } from "framer-motion";
import {
  BookOpen,
  FileText,
  Download,
  ExternalLink,
  CheckCircle2,
  ShieldCheck,
  Award,
  GitCommit,
  Layers,
  Sparkles,
  Quote,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { RESEARCH_HIGHLIGHTS } from "@/constants";

export default function ResearchPage() {
  const citations = [
    {
      title: "Early-warning signals for critical transitions in complex systems",
      authors: "Scheffer, M., Bascompte, J., Brock, W. A., Brovkin, V., Carpenter, S. R., Dakos, V., ... & Sugihara, G.",
      journal: "Nature, 461(7260), 53-59",
      year: "2009",
      doi: "10.1038/nature08227",
    },
    {
      title: "Tipping elements in the Earth's climate system",
      authors: "Lenton, T. M., Held, H., Kriegler, E., Hall, J. W., Lucht, W., Rahmstorf, S., & Schellnhuber, H. J.",
      journal: "Proceedings of the National Academy of Sciences, 105(6), 1786-1793",
      year: "2008",
      doi: "10.1073/pnas.0705414105",
    },
    {
      title: "Physics-informed neural networks: A deep learning framework for solving forward and inverse problems involving nonlinear partial differential equations",
      authors: "Raissi, M., Perdikaris, P., & Karniadakis, G. E.",
      journal: "Journal of Computational Physics, 378, 686-707",
      year: "2019",
      doi: "10.1016/j.jcp.2018.10.045",
    },
    {
      title: "Temporal Fusion Transformers for Interpretable Multi-horizon Time Series Forecasting",
      authors: "Lim, B., Arık, S. Ö., Loeff, N., & Pfister, T.",
      journal: "International Journal of Forecasting, 37(4), 1748-1764",
      year: "2021",
      doi: "10.1016/j.ijforecast.2021.03.012",
    },
    {
      title: "Exceeding 1.5°C global warming could trigger multiple climate tipping points",
      authors: "Armstrong McKay, D. I., Staal, A., Abrams, J. F., Winkelmann, R., Sakschewski, B., Loriani, S., ... & Lenton, T. M.",
      journal: "Science, 377(6611), eabn7950",
      year: "2022",
      doi: "10.1126/science.abn7950",
    },
  ];

  return (
    <div className="space-y-8 animate-in fade-in-50 duration-300 max-w-5xl mx-auto">
      {/* Title Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-white/10 pb-6">
        <div className="space-y-1">
          <Badge variant="purple" className="px-2.5 py-0.5 text-xs">Methodology & Publications</Badge>
          <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white">
            Research Foundations & Academic Citations
          </h2>
          <p className="text-sm text-slate-300 max-w-3xl">
            Gaia’s theoretical framework synthesizes classical dynamical systems theory with state-of-the-art physics-informed deep learning. Below are our foundational principles, architectural specifications, and peer-reviewed bibliographic references.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button variant="gradient" size="sm" className="gap-2 shadow-lg shadow-purple-500/20 font-bold">
            <Download className="h-3.5 w-3.5" />
            <span>Download Whitepaper (PDF)</span>
          </Button>
        </div>
      </div>

      {/* 3 Core Methodology Pillars */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {RESEARCH_HIGHLIGHTS.map((hl, idx) => (
          <Card key={idx} className="p-6 bg-slate-900/60 border-white/10 space-y-4 flex flex-col justify-between">
            <div className="space-y-3">
              <div className="h-10 w-10 rounded-xl bg-purple-500/15 text-purple-400 flex items-center justify-center font-bold border border-purple-500/30">
                <ShieldCheck className="h-5 w-5" />
              </div>
              <h3 className="text-lg font-bold text-white">{hl.title}</h3>
              <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">{hl.description}</p>
            </div>
            <div className="mt-4 rounded-xl bg-slate-950/80 p-3 border border-white/5 text-xs font-mono text-cyan-300">
              💡 {hl.impact}
            </div>
          </Card>
        ))}
      </div>

      {/* Physics-Informed Formulation Callout */}
      <Card className="p-8 bg-gradient-to-r from-slate-900/90 via-slate-900/60 to-slate-950 border-white/15 shadow-xl space-y-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 h-48 w-48 rounded-full bg-cyan-500/10 blur-3xl pointer-events-none" />

        <div className="space-y-2">
          <Badge variant="outline" className="font-mono text-xs text-cyan-300 border-cyan-500/30">
            Mathematical formulation
          </Badge>
          <h3 className="text-2xl font-extrabold text-white">
            Thermodynamic Physics-Informed Loss Formulation
          </h3>
          <p className="text-sm text-slate-300 max-w-3xl leading-relaxed">
            Standard data-driven neural networks often violate conservation of mass, momentum, and heat when predicting out-of-distribution climate bifurcations. Gaia solves this by incorporating differential equations directly into the gradient descent optimization objective.
          </p>
        </div>

        {/* Equation Box */}
        <div className="rounded-xl bg-black/80 p-5 border border-white/15 font-mono text-sm sm:text-base text-emerald-400 space-y-3 overflow-x-auto shadow-inner">
          <div className="text-slate-500 text-xs"># Complete composite loss function minimized during training</div>
          <div className="font-bold">
            <span className="text-white">L_total(θ)</span> = <span className="text-cyan-400">L_supervised(y, y_hat)</span> +{" "}
            <span className="text-purple-400">λ_1 · ||∂u/∂t + (u·∇)u + ∇p/ρ - ν∇²u||²</span> +{" "}
            <span className="text-amber-400">λ_2 · ||∂T/∂t + u·∇T - α∇²T - Q_rad||²</span>
          </div>
          <div className="text-xs text-slate-400 pt-2 border-t border-white/10 flex flex-wrap gap-4">
            <span>where <strong className="text-white">u</strong> = ocean transport velocity</span>
            <span><strong className="text-white">T</strong> = temperature field</span>
            <span><strong className="text-white">Q_rad</strong> = radiative forcing flux</span>
          </div>
        </div>
      </Card>

      {/* Citations & Bibliography Table */}
      <Card className="p-6 bg-slate-900/60 border-white/10 space-y-6">
        <div className="flex items-center justify-between border-b border-white/5 pb-3">
          <h3 className="font-bold text-white flex items-center gap-2">
            <BookOpen className="h-4 w-4 text-cyan-400" />
            Peer-Reviewed Bibliography & Reference Library
          </h3>
          <Badge variant="secondary" className="font-mono text-[10px]">CITATIONS</Badge>
        </div>

        <div className="space-y-4">
          {citations.map((cite, i) => (
            <div
              key={i}
              className="p-4 rounded-xl bg-slate-950/60 border border-white/5 hover:border-white/15 transition-all space-y-1.5 group"
            >
              <div className="flex items-start justify-between gap-4">
                <h4 className="font-bold text-sm text-white group-hover:text-cyan-300 transition-colors">
                  {i + 1}. {cite.title}
                </h4>
                <Badge variant="outline" className="font-mono text-[10px] shrink-0 text-slate-400 border-white/10">
                  {cite.year}
                </Badge>
              </div>
              <p className="text-xs text-slate-400 italic">{cite.authors}</p>
              <div className="flex items-center justify-between text-xs font-mono pt-1">
                <span className="text-purple-300">{cite.journal}</span>
                <span className="text-slate-500">DOI: {cite.doi}</span>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
