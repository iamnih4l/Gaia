"""Gaia Models — ML architectures for tipping point detection.

Includes baselines, time-series transformers, graph neural networks,
physics-informed models, causal discovery, and foundation model adapters.
"""

from models.registry import ModelRegistry
import models.baseline.arima
import models.baseline.logistic_regression
import models.baseline.random_forest
import models.baseline.svm
import models.transformer.time_series_transformer
import models.transformer.temporal_fusion_transformer
import models.transformer.informer
import models.transformer.lstm
import models.gnn.climate_gnn
import models.gnn.graph_attention
import models.gnn.dynamic_graph
import models.physics.pinn
import models.causal.pcmci
import models.causal.granger
import models.causal.causal_discovery
import models.foundation.adapter

__all__ = ["ModelRegistry"]
