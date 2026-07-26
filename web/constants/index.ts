export * from "./elements";
export * from "./models";
export * from "./datasets";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const RESEARCH_HIGHLIGHTS = [
  {
    title: "Zero Look-Ahead Bias Preprocessing",
    description: "All time-series normalizers and feature extraction algorithms execute causally on historical training windows only, eliminating data leakage.",
    impact: "Prevents artificial AUC inflation in production",
  },
  {
    title: "Thermodynamic PINN Residuals",
    description: "Embedding Navier-Stokes and energy balance PDEs directly into neural network loss functions ensures conservation of mass and heat.",
    impact: "+18% out-of-distribution stability under abrupt CMIP6 forcing",
  },
  {
    title: "Multi-Horizon Lead Time Estimation",
    description: "Temporal Fusion Transformers predict fold bifurcation transitions up to 28 months in advance with quantile confidence intervals.",
    impact: "Enables early policy interventions before irreversible collapse",
  },
];
