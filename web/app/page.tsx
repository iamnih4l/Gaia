"use client";

import * as React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Globe,
  ArrowRight,
  Cpu,
  ShieldAlert,
  Activity,
  Layers,
  Sparkles,
  Terminal,
  Database,
  BarChart2,
  CheckCircle2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Globe3D } from "@/components/earth/Globe3D";
import { TIPPING_ELEMENTS, MODEL_ZOO, RESEARCH_HIGHLIGHTS } from "@/constants";

export default function LandingPage() {
  const [selectedHotspot, setSelectedHotspot] = React.useState("amoc");
  const currentHotspot = TIPPING_ELEMENTS.find((e) => e.id === selectedHotspot) || TIPPING_ELEMENTS[0];

  return (
    <div className="min-h-screen bg-black scanline-grid text-[#F8F9FA] flex flex-col font-sans overflow-x-hidden selection:bg-cyan-500/30 selection:text-cyan-200 relative">
      {/* Top Navigation Bar */}
      <header className="sticky top-0 z-50 flex h-16 w-full items-center justify-between border-b border-white/15 bg-black/90 px-6 lg:px-12 backdrop-blur-2xl shadow-[0_4px_30px_rgba(0,0,0,0.9)]">
        <Link href="/" className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-cyan-400/50 bg-gradient-to-tr from-cyan-500/20 to-emerald-500/20 shadow-[0_0_15px_rgba(0,242,254,0.25)]">
            <Globe className="h-5 w-5 text-cyan-400 animate-pulse" />
          </div>
          <span className="text-sm sm:text-base font-mono font-bold tracking-wider text-white uppercase flex items-center gap-2 drop-shadow-[0_0_8px_rgba(255,255,255,0.3)]">
            GAIA <span className="text-[9px] uppercase font-mono px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">SYS v2.4 ORBITAL COMMAND</span>
          </span>
        </Link>

        <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-slate-300">
          <a href="#mission" className="hover:text-cyan-400 transition-colors">Mission</a>
          <a href="#architecture" className="hover:text-cyan-400 transition-colors">AI Architecture</a>
          <a href="#hotspots" className="hover:text-cyan-400 transition-colors">Tipping Elements</a>
          <a href="#research" className="hover:text-cyan-400 transition-colors">Research Highlights</a>
        </nav>

        <div className="flex items-center gap-3">
          <Link href="/dashboard">
            <Button variant="gradient" className="gap-2 shadow-lg shadow-cyan-500/20">
              <span>Launch Mission Control</span>
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative px-6 lg:px-12 py-12 md:py-20 flex flex-col lg:flex-row items-center justify-between gap-12 max-w-7xl mx-auto w-full">
        {/* Background glow blob */}
        <div className="absolute top-1/4 left-1/4 h-96 w-96 rounded-full bg-cyan-500/10 blur-3xl pointer-events-none" />
        <div className="absolute bottom-1/3 right-1/4 h-96 w-96 rounded-full bg-purple-600/10 blur-3xl pointer-events-none" />

        {/* Left Column / Typography & CTAs */}
        <div className="flex-1 space-y-6 z-10 text-center lg:text-left">
          <div className="inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-500/10 px-3 py-1 text-xs font-semibold text-cyan-300 backdrop-blur-md">
            <Sparkles className="h-3.5 w-3.5 text-cyan-400 animate-spin" style={{ animationDuration: "8s" }} />
            <span>Research-Grade Earth System Intelligence</span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-[1.1]">
            Early Detection of <br />
            <span className="bg-gradient-to-r from-cyan-400 via-teal-300 to-emerald-400 bg-clip-text text-transparent">
              Climate Tipping Points
            </span>
          </h1>

          <p className="text-base sm:text-lg text-slate-300 max-w-2xl font-normal leading-relaxed">
            Gaia bridges atmospheric physics and advanced deep learning to forecast fold bifurcations and critical transitions in global climate elements up to <strong className="text-white font-mono">28 months in advance</strong> with zero look-ahead bias.
          </p>

          <div className="flex flex-wrap items-center justify-center lg:justify-start gap-4 pt-4">
            <Link href="/dashboard">
              <Button size="lg" variant="gradient" className="gap-2 shadow-xl shadow-cyan-500/25">
                <Activity className="h-5 w-5" />
                <span>Enter Mission Control</span>
              </Button>
            </Link>
            <Link href="/earth">
              <Button size="lg" variant="outline" className="gap-2 border-white/20 hover:bg-white/10">
                <Globe className="h-5 w-5 text-cyan-400" />
                <span>Explore 3D Interactive Earth</span>
              </Button>
            </Link>
          </div>

          {/* Key Live Telemetry Stats */}
          <div className="grid grid-cols-3 gap-4 pt-8 border-t border-white/10 max-w-lg mx-auto lg:mx-0">
            <div>
              <div className="text-2xl lg:text-3xl font-bold font-mono text-white">15+</div>
              <div className="text-xs text-slate-400 font-medium mt-0.5">Neural Architectures</div>
            </div>
            <div>
              <div className="text-2xl lg:text-3xl font-bold font-mono text-cyan-400">98.4%</div>
              <div className="text-xs text-slate-400 font-medium mt-0.5">TFT ROC-AUC Score</div>
            </div>
            <div>
              <div className="text-2xl lg:text-3xl font-bold font-mono text-emerald-400">&lt; 45ms</div>
              <div className="text-xs text-slate-400 font-medium mt-0.5">Real-Time Inference</div>
            </div>
          </div>
        </div>

        {/* Right Column / Interactive 3D Globe */}
        <div className="flex-1 w-full h-[450px] sm:h-[550px] relative flex items-center justify-center">
          <div className="absolute inset-0 rounded-3xl border border-white/10 bg-gradient-to-b from-slate-900/40 to-slate-950/80 backdrop-blur-xl p-4 shadow-2xl flex flex-col">
            <div className="flex items-center justify-between border-b border-white/10 pb-3 px-2">
              <div className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full bg-red-500" />
                <span className="h-3 w-3 rounded-full bg-amber-500" />
                <span className="h-3 w-3 rounded-full bg-emerald-500" />
                <span className="ml-2 font-mono text-xs text-slate-400">gaia-globe-viewport.glsl</span>
              </div>
              <Badge variant="outline" className="font-mono text-[10px] text-cyan-400 border-cyan-500/30">
                Live Interactive 3D
              </Badge>
            </div>
            
            <div className="flex-1 relative">
              <Globe3D onSelectElement={(id) => setSelectedHotspot(id)} />
            </div>

            {/* Selected Hotspot Bottom Info Strip */}
            <div className="border-t border-white/10 pt-3 px-2 flex items-center justify-between bg-slate-950/50 rounded-xl p-2.5 mt-2">
              <div className="flex items-center gap-2">
                <span
                  className="h-2.5 w-2.5 rounded-full animate-ping"
                  style={{
                    backgroundColor: currentHotspot.status === "CRITICAL" ? "#F77F00" : currentHotspot.status === "WARNING" ? "#FCBF49" : "#00B4D8",
                  }}
                />
                <span className="font-bold text-sm text-white">{currentHotspot.name}</span>
              </div>
              <Link href={`/earth?element=${currentHotspot.id}`}>
                <Button size="sm" variant="ghost" className="text-xs text-cyan-400 hover:text-cyan-300">
                  Inspect Telemetry →
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Mission Statement & Why Gaia Matters */}
      <section id="mission" className="py-20 px-6 lg:px-12 border-t border-white/10 bg-slate-950/50">
        <div className="max-w-5xl mx-auto text-center space-y-6">
          <Badge variant="purple" className="px-3 py-1 text-xs">Scientific Foundation</Badge>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            Why We Built Gaia: Avoiding Irreversible Planetary Transitions
          </h2>
          <p className="text-base sm:text-lg text-slate-300 leading-relaxed">
            Climate tipping points represent critical thresholds where Earth systems undergo self-reinforcing, abrupt transitions. Traditional Earth System Models (CMIP6) struggle with computational latency and parameterization limits when forecasting these rare non-linear bifurcations.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-8 text-left">
            <Card className="p-6 bg-slate-900/40 border-white/10 space-y-3">
              <div className="h-10 w-10 rounded-lg bg-cyan-500/15 text-cyan-400 flex items-center justify-center font-bold">
                01
              </div>
              <h3 className="text-lg font-bold text-white">Critical Slowing Down</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                As a dynamical system approaches a bifurcation threshold, its recovery rate from perturbations approaches zero—evidenced by rising Lag-1 autocorrelation and rolling variance.
              </p>
            </Card>

            <Card className="p-6 bg-slate-900/40 border-white/10 space-y-3">
              <div className="h-10 w-10 rounded-lg bg-purple-500/15 text-purple-400 flex items-center justify-center font-bold">
                02
              </div>
              <h3 className="text-lg font-bold text-white">Physics-Informed Deep Learning</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                We embed Navier-Stokes fluid dynamics and thermodynamic energy conservation directly into neural network loss residuals, ensuring models respect physical laws under extreme climate forcing.
              </p>
            </Card>

            <Card className="p-6 bg-slate-900/40 border-white/10 space-y-3">
              <div className="h-10 w-10 rounded-lg bg-emerald-500/15 text-emerald-400 flex items-center justify-center font-bold">
                03
              </div>
              <h3 className="text-lg font-bold text-white">Actionable Lead Times</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                By detecting pre-bifurcation anomalies up to 28 months prior to structural collapse, Gaia provides policymakers and scientific institutions critical lead time to enact mitigation strategies.
              </p>
            </Card>
          </div>
        </div>
      </section>

      {/* AI Architecture & Technology Stack Showcase */}
      <section id="architecture" className="py-20 px-6 lg:px-12 max-w-7xl mx-auto w-full space-y-12">
        <div className="text-center space-y-4 max-w-3xl mx-auto">
          <Badge variant="default" className="px-3 py-1">Enterprise & Research Stack</Badge>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white">
            Powered by 15+ Specialized AI Architectures
          </h2>
          <p className="text-slate-400">
            From Temporal Fusion Transformers with Variable Selection Networks to Graph Convolutional Networks modeling global atmospheric teleconnections.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {MODEL_ZOO.slice(0, 4).map((mod) => (
            <Card key={mod.id} className="p-6 flex flex-col justify-between hover:border-cyan-500/40 transition-all bg-slate-900/60">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Badge variant="secondary" className="font-mono text-[10px]">{mod.category}</Badge>
                  <span className="text-xs font-mono text-cyan-400 font-bold">{mod.parameters} params</span>
                </div>
                <h3 className="text-lg font-bold text-white leading-tight">{mod.name}</h3>
                <p className="text-xs text-slate-400 line-clamp-3">{mod.description}</p>
              </div>

              <div className="mt-6 pt-4 border-t border-white/5 space-y-2">
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-slate-400">ROC-AUC:</span>
                  <span className="text-emerald-400 font-bold">{mod.rocAuc}</span>
                </div>
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-slate-400">Lead Time:</span>
                  <span className="text-white font-semibold">{mod.leadTimeAccuracy}</span>
                </div>
                <Link href="/models">
                  <Button variant="outline" size="sm" className="w-full mt-2 text-xs border-white/10 hover:bg-white/5">
                    Inspect Architecture →
                  </Button>
                </Link>
              </div>
            </Card>
          ))}
        </div>
      </section>

      {/* Tipping Elements Interactive Grid */}
      <section id="hotspots" className="py-20 px-6 lg:px-12 bg-slate-950/80 border-t border-white/10">
        <div className="max-w-7xl mx-auto space-y-12">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
            <div className="space-y-3">
              <Badge variant="destructive" className="px-3 py-1">Planetary Boundaries</Badge>
              <h2 className="text-3xl sm:text-4xl font-extrabold text-white">
                Global Tipping Elements Monitored
              </h2>
              <p className="text-slate-400 max-w-2xl">
                Continuous real-time anomaly tracking across ocean circulation, polar ice sheets, and tropical ecosystems.
              </p>
            </div>
            <Link href="/explorer">
              <Button variant="outline" className="gap-2 border-white/20">
                <span>View All Elements in Explorer</span>
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {TIPPING_ELEMENTS.slice(0, 3).map((el) => (
              <Card key={el.id} className="p-6 space-y-4 hover:border-white/20 transition-all bg-slate-900/50">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono text-slate-400">{el.region}</span>
                  <Badge
                    variant={el.status === "CRITICAL" ? "destructive" : el.status === "WARNING" ? "warning" : "default"}
                    className="font-bold text-[10px]"
                  >
                    {el.status}
                  </Badge>
                </div>

                <div>
                  <h3 className="text-xl font-bold text-white">{el.name}</h3>
                  <p className="text-xs text-slate-400 mt-1 line-clamp-2">{el.description}</p>
                </div>

                <div className="grid grid-cols-2 gap-3 p-3 rounded-xl bg-slate-950/60 border border-white/5 text-xs font-mono">
                  <div>
                    <span className="text-slate-500 block">Risk Score</span>
                    <span className="text-base font-bold text-orange-400">{(el.riskScore * 100).toFixed(0)}%</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Lead Time</span>
                    <span className="text-base font-bold text-cyan-400">~{el.leadTimeMonths} mo</span>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-2">
                  <Link href={`/earth?element=${el.id}`} className="w-full">
                    <Button variant="secondary" size="sm" className="w-full text-xs gap-1.5">
                      <Globe className="h-3.5 w-3.5 text-cyan-400" />
                      <span>Explore 3D Region</span>
                    </Button>
                  </Link>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Research Highlights Section */}
      <section id="research" className="py-20 px-6 lg:px-12 max-w-7xl mx-auto w-full space-y-12">
        <div className="text-center space-y-3 max-w-3xl mx-auto">
          <Badge variant="purple" className="px-3 py-1">Publication & Methodology</Badge>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white">
            Research-Grade Standards
          </h2>
          <p className="text-slate-400">
            Engineered to meet the rigorous publication criteria of NeurIPS, ICML, ICLR, CVPR EarthVision, NASA, and ISRO.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {RESEARCH_HIGHLIGHTS.map((hl, idx) => (
            <Card key={idx} className="p-6 bg-slate-900/40 border-white/10 space-y-4">
              <div className="flex items-center gap-3">
                <div className="h-8 w-8 rounded-lg bg-cyan-500/20 text-cyan-400 flex items-center justify-center">
                  <CheckCircle2 className="h-5 w-5" />
                </div>
                <h3 className="text-lg font-bold text-white">{hl.title}</h3>
              </div>
              <p className="text-sm text-slate-400 leading-relaxed">{hl.description}</p>
              <div className="rounded-lg bg-cyan-500/10 border border-cyan-500/20 p-2.5 text-xs text-cyan-300 font-mono">
                💡 Impact: {hl.impact}
              </div>
            </Card>
          ))}
        </div>
      </section>

      {/* CTA Footer Section */}
      <section className="py-20 px-6 lg:px-12 border-t border-white/10 bg-gradient-to-b from-slate-950 to-[#070C1B] text-center space-y-8">
        <div className="max-w-3xl mx-auto space-y-4">
          <Globe className="h-12 w-12 text-cyan-400 mx-auto animate-pulse" />
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white">
            Ready to Explore the Platform?
          </h2>
          <p className="text-slate-300 text-base">
            Access real-time inference endpoints, inspect attention maps, and download PDF/JSON research reports.
          </p>
          <div className="pt-4 flex justify-center gap-4">
            <Link href="/dashboard">
              <Button size="lg" variant="gradient" className="gap-2 shadow-xl shadow-cyan-500/30 px-8">
                <span>Enter Mission Control Dashboard</span>
                <ArrowRight className="h-5 w-5" />
              </Button>
            </Link>
          </div>
        </div>

        <footer className="pt-16 border-t border-white/10 text-xs text-slate-500 flex flex-col sm:flex-row items-center justify-between gap-4 max-w-7xl mx-auto">
          <div className="flex items-center gap-2">
            <span className="font-bold text-slate-400">Gaia OS v1.0</span>
            <span>•</span>
            <span>Advanced Agentic Coding & Climate Intelligence</span>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/research" className="hover:text-slate-300 transition-colors">Methodology</Link>
            <Link href="/models" className="hover:text-slate-300 transition-colors">Model Zoo</Link>
            <Link href="/datasets" className="hover:text-slate-300 transition-colors">Datasets</Link>
            <Link href="/settings" className="hover:text-slate-300 transition-colors">Settings</Link>
          </div>
        </footer>
      </section>
    </div>
  );
}
