"""Unit tests for neural network architectures, baselines, and evaluation metrics."""

import numpy as np
import pytest
import torch
from omegaconf import OmegaConf

from models.registry import ModelRegistry
from evaluation.metrics import TippingPointMetrics
import models.transformer.time_series_transformer
import models.transformer.temporal_fusion_transformer
import models.baseline.logistic_regression
import models.baseline.arima


def test_model_registry():
    available = ModelRegistry.list()
    assert "time_series_transformer" in available
    assert "temporal_fusion_transformer" in available


def test_transformer_forward_shape():
    cfg = OmegaConf.create({
        "type": "time_series_transformer",
        "architecture": {
            "input_dim": 6,
            "d_model": 32,
            "n_heads": 4,
            "d_ff": 64,
            "n_encoder_layers": 2,
            "dropout": 0.1,
            "max_seq_len": 50,
            "output_dim": 1,
            "pool_strategy": "cls",
            "activation": "gelu"
        }
    })
    model = ModelRegistry.create(cfg)
    x = torch.randn(4, 20, 6)
    out = model(x)
    assert out.shape == (4, 1)
    assert (out >= 0.0).all() and (out <= 1.0).all()


def test_logistic_regression_baseline():
    cfg = OmegaConf.create({
        "architecture": {
            "penalty": "l2",
            "C": 1.0,
            "max_iter": 100,
            "solver": "lbfgs",
            "class_weight": "balanced"
        }
    })
    model = models.baseline.logistic_regression.LogisticRegressionBaseline(cfg)
    X = np.random.randn(50, 5)
    y = np.random.randint(0, 2, size=50)
    model.fit(X, y)
    preds = model.predict_proba(X)
    assert len(preds) == 50
    assert (preds >= 0.0).all() and (preds <= 1.0).all()


def test_tipping_point_metrics():
    y_true = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    y_prob = np.array([0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9])
    
    metrics = TippingPointMetrics.compute_all(y_true, y_prob, threshold=0.5, event_indices=[6])
    assert metrics.roc_auc == 1.0
    assert metrics.f1 == 1.0
    assert metrics.false_alarm_rate == 0.0
    assert metrics.mean_lead_time > 0
