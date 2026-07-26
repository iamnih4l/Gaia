# Gaia 🌍 — Orbital Command Deck Frontend

[![Live Demo - Vercel](https://img.shields.io/badge/Live_Demo-Vercel_Simulation-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://gaia-navy.vercel.app/)
[![Next.js 16](https://img.shields.io/badge/Next.js-16.2.12-black?logo=next.js&logoColor=white)](https://nextjs.org/)
[![Tailwind CSS v4](https://img.shields.io/badge/Tailwind_CSS-v4-06B6D4?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)

The research-grade, sci-fi **Orbital Command Deck** frontend for **Gaia**, built with Next.js 16 App Router, Tailwind CSS v4, Three.js 3D Earth visualization, and Recharts telemetry dashboards.

---

> [!IMPORTANT]
> **🌐 Live Demo vs. Real-Time Data**
> * **Vercel Live Deployment**: Explore the live online demo at **[https://gaia-navy.vercel.app/](https://gaia-navy.vercel.app/)**. 
>   *(Note: The online Vercel deployment runs in **High-Fidelity Research Simulation Mode** so visitors can explore 3D Earth visualizations, risk telemetry, and model architectures without needing a local GPU cluster or Python runtime).*
> * **⚡ 100% Real-Time Data & Live AI Inference**: When running locally, our automated dual-server pipeline starts both this frontend and the Python FastAPI backend simultaneously so you get live real-time climate predictions!

---

## 🚀 Quick Start (Concurrent Full-Stack Mode)

To launch BOTH the Next.js frontend and Python FastAPI backend simultaneously:

```bash
# From the project root (Gaia/) or inside this directory (web/):
npm install
npm run dev
```

This automatically starts:
1. **Next.js Orbital Command Deck**: [http://localhost:3000](http://localhost:3000)
2. **FastAPI Inference Engine**: [http://localhost:8000](http://localhost:8000)

When accessed locally on port 3000, the frontend automatically detects the live FastAPI backend on port 8000 and streams 100% real-time AI predictions!
