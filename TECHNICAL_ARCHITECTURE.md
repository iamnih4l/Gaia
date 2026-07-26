# Gaia 🌍 — Technical Architecture & Engineering Specification

> **Version**: 2.4.0-PROD  
> **Classification**: Research-Grade Open Source / Scientific AI System  
> **Target Audiences**: Software Architects, ML Engineers, Climate Scientists, Systems Engineers  

---

## 1. Executive Summary & System Philosophy

**Gaia** is an end-to-end artificial intelligence engine designed for the early detection and lead-time quantification of **climate tipping points**. Unlike traditional dynamical Earth System Models (ESMs), which are computationally prohibitive for high-frequency early-warning screening, or classical statistical mechanics, which fail in noisy, high-dimensional satellite observational spaces, Gaia unifies **physics-constrained deep learning**, **spatial-temporal graph mechanics**, and **zero look-ahead causal data engineering**.

The system is architected around five decoupled, horizontally scalable layers:
1. **Data Ingestion & Causal Preprocessing Engine**: Multi-modal satellite and reanalysis loaders with mathematical guarantees against temporal leakage.
2. **Deep Learning Model Zoo**: 15+ neural network architectures including Temporal Fusion Transformers (TFT), Informers, Graph Attention Networks (GAT), and Physics-Informed Neural Networks (PINNs).
3. **Inference & Alarm Calibration Server**: High-concurrency FastAPI REST engine providing real-time probability scoring, severity thresholds, and uncertainty quantification.
4. **Orbital Command Deck Frontend**: A Next.js 16 WebGL/Three.js telemetry console featuring a dual-mode circuit breaker for resilient offline simulation.
5. **Turnkey Concurrent DevOps Pipeline**: Automated multi-server orchestration via Hydra and Concurrently.

---

## 2. Layer 1: Data Ingestion & Causal Preprocessing Engine

### 2.1 Multi-Modal Ingestor Registry
Gaia implements standardized loader pipelines (`datasets/`) utilizing Xarray and Dask for out-of-core multidimensional array processing across five continental-scale tipping elements:
* **AMOC Circulation**: Ingests RAPID-MOCHA array volume transport anomalies at 26.5°N ($Sv = 10^6\ \text{m}^3/\text{s}$) and CMIP6 historical/ssp585 projections.
* **Amazon Rainforest Dieback**: Ingests ECMWF ERA5 Vapor Pressure Deficit (VPD), root-zone soil moisture anomalies, and NASA MODIS MCD43A4 EVI/NDVI vegetation resilience indices.
* **Polar Ice Sheet Collapse**: Processes NASA GRACE / GRACE-FO gravimetric mass anomalies ($\text{Gt}$) and ICESat-2 surface altimetry for Greenland and Antarctica.
* **Coral Reef Bleaching**: Streams NOAA Coral Reef Watch v3.1 5km Sea Surface Temperature (SST) anomalies and computes cumulative **Degree Heating Weeks (DHW)**.
* **Arctic Sea Ice Loss**: Loads NSIDC Sea Ice Index (G02135) daily extent and area ($\text{km}^2$) to track seasonal amplitude hysteresis.

### 2.2 Zero Look-Ahead Causal Windowing
A foundational requirement of research-grade Early Warning Systems (EWS) is the absolute prevention of temporal data leakage. Classical normalization (e.g., standardizing across an entire time series) injects future statistical distributions into historical timesteps.

Gaia enforces **Causal Rolling Normalization** in `preprocessing/temporal.py`:
$$\mu_t = \frac{1}{W} \sum_{i=0}^{W-1} x_{t-i}, \quad \sigma_t = \sqrt{\frac{1}{W} \sum_{i=0}^{W-1} (x_{t-i} - \mu_t)^2}$$
$$z_t = \frac{x_t - \mu_t}{\sigma_t + \epsilon}$$
Where $W$ is a configurable retrospective window (default: 365 timesteps) and $\epsilon = 10^{-8}$ prevents zero-division. Every feature vector at index $t$ is computed **strictly using observations from $[0, t]$**.

### 2.3 Classical Critical Slowing Down (CSD) Extraction
Before passing sequences to deep neural networks, the feature engineering pipeline (`feature_engineering/ews_indicators.py`) extracts classical biophysical instability metrics:
* **Lag-1 Autocorrelation ($AR(1)$)**: Quantifies recovery rate slowdown from perturbations:
  $$AR(1)_t = \frac{\sum_{i=1}^{W-1} (x_{t-i} - \mu_t)(x_{t-i-1} - \mu_t)}{\sum_{i=0}^{W-1} (x_{t-i} - \mu_t)^2}$$
* **Rolling Variance & Skewness**: Captures flickering and asymmetric potential well flattening as a system approaches a bifurcation point.
* **Detrended Fluctuation Analysis (DFA $\alpha$)**: Measures long-range power-law persistence and fractal scaling exponents.

---

## 3. Layer 2: Deep Learning Model Zoo & Neural Architectures

Gaia’s `models/` directory implements modular PyTorch architectures designed for non-linear sequence prediction and spatial teleconnection mapping.

```mermaid
flowchart LR
    subgraph Input [Causal Feature Matrix]
        X[X_t, X_{t-1}, ..., X_{t-L}]
    end
    subgraph Transformers [Temporal Transformers]
        TFT[Temporal Fusion Transformer]
        INF[Informer / ProbSparse Attn]
    end
    subgraph Spatial [Graph Neural Networks]
        GNN[Climate Teleconnection GAT]
    end
    subgraph Physics [Physics-Informed]
        PINN[PINN + PDE Residuals]
    end
    Input --> TFT & INF & GNN & PINN
    TFT & INF & GNN & PINN --> OUT[Tipping Probability P_t & Lead Time \tau]
```

### 3.1 Temporal Fusion Transformer (TFT) & Informers
For multi-horizon time-series forecasting, Gaia implements attention-based sequence models (`models/transformer/`):
* **Variable Selection Networks (VSNs)**: Automatically learn feature importance weights across heterogeneous inputs (e.g., dynamically weighing SST vs. surface radiation).
* **Gated Residual Networks (GRNs)**: Provide non-linear processing with skip connections and gated linear units (GLUs) to suppress irrelevant noise.
* **ProbSparse Attention (Informer)**: Reduces canonical self-attention complexity from $\mathcal{O}(L^2)$ to $\mathcal{O}(L \log L)$ by sampling dominant query-key pairs, enabling long-sequence analysis ($L \ge 512$ timesteps) without GPU memory exhaustion.

### 3.2 Climate Teleconnection Graph Neural Networks (GNNs)
Earth tipping elements do not exist in isolation; collapse in the AMOC directly alters Amazon precipitation patterns and Arctic sea ice melt rates. Gaia models these global teleconnections using **Spatial Graph Attention Networks** (`models/gnn/climate_gnn.py`):
* **Graph Construction**: Climate stations, oceanic buoys, and regional tipping basins are represented as nodes $V$. Edges $E$ are dynamically pruned using PCMCI causal discovery and Granger causality matrices.
* **Spatial Message Passing**: Node hidden states $h_i^{(l)}$ are updated by aggregating weighted features from causal neighbors $N(i)$:
  $$h_i^{(l+1)} = \sigma \left( \sum_{j \in N(i) \cup \{i\}} \alpha_{ij}^{(l)} \mathbf{W}^{(l)} h_j^{(l)} \right)$$
  Where attention coefficients $\alpha_{ij}$ represent the real-time coupling strength between climate subsystems.

### 3.3 Physics-Informed Neural Networks (PINNs)
Purely data-driven neural networks can hallucinate biophysically impossible predictions (e.g., violating mass conservation in ice sheets). Gaia incorporates physical laws directly into the backpropagation optimization objective (`models/physics/pinn.py`):
$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{data}}(y, \hat{y}) + \lambda_{\text{phys}} \mathcal{L}_{\text{PDE}}(\hat{y})$$
Where $\mathcal{L}_{\text{PDE}}$ penalizes deviations from known differential governing equations (such as Stommel’s two-box ocean circulation model or energy balance radiation equations), ensuring robust out-of-distribution generalization under unprecedented warming scenarios.

---

## 4. Layer 3: Real-Time Inference & Alarm Calibration Engine

### 4.1 FastAPI Asynchronous Serving Engine
The serving layer (`api/app.py`) is built on FastAPI and Uvicorn, providing high-throughput, non-blocking asynchronous REST endpoints:
* `GET /health`: Liveness and readiness probes returning GPU cluster utilization, CUDA device allocation, and active model registry status.
* `GET /models`: Dynamically enumerates all compiled neural network and baseline statistical weights.
* `POST /predict`: Ingests sequence payloads, executes forward-pass inference, computes uncertainty bounds, and maps probabilities to standardized operational alarms.

### 4.2 Severity Thresholds & Lead-Time Quantification
Raw probability scores ($P \in [0, 1]$) are transformed into actionable decision-making directives via a calibrated threshold matrix:
* 🟢 **NORMAL** ($P < 0.50$): Stable biophysical equilibrium; nominal recovery rates.
* 🟡 **WATCH** ($0.50 \le P < 0.65$): Statistically significant AR(1) slowing down detected; heightened monitoring required. Lead time: $\sim 24$ steps.
* 🟠 **WARNING** ($0.65 \le P < 0.80$): Non-linear potential well flattening confirmed; subsystem destabilizing. Lead time: $\sim 12$ steps.
* 🔴 **CRITICAL** ($P \ge 0.80$): Imminent bifurcation / state transition projected. Immediate intervention and disaster adaptation required. Lead time: $\sim 6$ steps.

### 4.3 Uncertainty Quantification (UQ)
To support risk-aware decision making, Gaia calculates 95% confidence intervals using **Monte Carlo Dropout (MCD)** and parametric variance estimation:
$$CI_{95\%} = \hat{P} \pm 1.96 \cdot \hat{\sigma}_{\text{MCD}}$$
This ensures policy-makers can distinguish between high-confidence tipping signals and observational sensor noise.

---

## 5. Layer 4: Orbital Command Deck Frontend & Dual-Mode Circuit Breaker

### 5.1 Space Flight Computer Design System
The frontend UI (`web/`) transforms complex scientific telemetry into an intuitive, sci-fi **Orbital Command Deck** inspired by spacecraft flight computers and NASA mission control:
* **Pure Void Black Contrast (`#000000`)**: Optimized for OLED displays, using deep void backdrops with radial bioluminescent cyan (`#00F2FE`) and purple (`#A855F7`) highlights.
* **Radar Scanline Grids**: Applied via custom CSS `.scanline-grid` overlays to create authentic 3D spatial depth across the viewport.
* **Telemetry Corner Brackets (`.hud-bracket`)**: Custom CSS framing elements (`[ ]`) that encapsulate cards, charts, and control decks.
* **3D WebGL Earth Engine (`Globe3D.tsx`)**: Built with Three.js and React Three Fiber, rendering real-time rotating topographic globes with pulsing interactive tipping element markers.

### 5.2 The Dual-Mode Resilient Circuit Breaker
A critical engineering challenge in web platforms hosting complex AI models is preventing frontend crashes during backend cold starts, network latency, or cloud server downtime.

Gaia solves this with an automated **Circuit Breaker Pattern** implemented in `web/services/api.ts`:
1. **Active REST Polling**: When a user triggers an action, `ApiService.fetchWithTimeout()` sends a request to the FastAPI endpoint with an `AbortController` timeout (4,000ms for health checks; 10,000ms for deep learning inference).
2. **Seamless Fallback Interception**: If the backend is unreachable (e.g., when viewing a static deployment on Vercel without a configured serverless GPU backend), the catch block intercepts the network exception without throwing a client-side error.
3. **High-Fidelity Research Simulation Activation**: The service instantly activates **Offline Research Simulation Mode**, generating biophysically accurate mock telemetry, realistic AR(1) critical slowing down trajectories, Dirichlet-distributed feature attention weights, and dynamic UQ bounds.
4. **Transparent User Telemetry**: The UI Topbar and Sidebar update their LED indicators from `LIVE API` (Emerald) to `SIMULATED` (Amber), informing researchers of the runtime state while maintaining 100% interactivity across all 10 platform modules.

---

## 6. Layer 5: Turnkey Concurrent DevOps & Serving Pipeline

### 6.1 Hierarchical Configuration with Hydra
All hyperparameters, dataset paths, training schedules, and model architectures are decoupled from code using **Hydra** (`configs/`). Researchers can run complex multi-run sweeps directly from the CLI:
```bash
poetry run python scripts/train.py -m model=tft,climate_gnn,pinn dataset=amoc,amazon_dieback training.lr=1e-4,5e-4
```

### 6.2 Concurrent Full-Stack Orchestration
To eliminate development friction and enable immediate real-time testing, Gaia integrates a turnkey dual-server execution pipeline via `concurrently`. 

When a developer executes `npm run dev` at the repository root or inside `web/`:
```bash
npm run dev
```
The script concurrently launches:
1. **The FastAPI Backend Child Process**: `python -m api.app` binding to `0.0.0.0:8000`.
2. **The Next.js App Router Child Process**: `next dev` binding to `0.0.0.0:3000`.

Color-coded terminal logging (`[FASTAPI]` in green, `[WEB]` in cyan) merges output streams into a single console, allowing engineers to monitor backend PyTorch inference latency and frontend React compilation simultaneously.
