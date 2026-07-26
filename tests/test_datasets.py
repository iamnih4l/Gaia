"""Unit tests for climate dataset loaders and preprocessing."""

import numpy as np
import pytest
from omegaconf import OmegaConf

from datasets.base import ClimateTimeSeriesDataset
from datasets.registry import DatasetRegistry
from preprocessing.temporal import TemporalProcessor
from preprocessing.normalization import Normalizer
from feature_engineering.ews_indicators import EWSIndicators
from feature_engineering.climate_indices import ClimateIndices
import datasets.era5
import datasets.amoc


def test_dataset_registry_listing():
    models = DatasetRegistry.list()
    assert "era5" in models
    assert "amoc" in models


def test_time_series_dataset_windowing():
    features = np.random.randn(100, 5).astype(np.float32)
    labels = np.zeros(100, dtype=np.float32)
    labels[-20:] = 1.0

    ds = ClimateTimeSeriesDataset(features, labels, seq_len=10)
    assert len(ds) == 91
    sample = ds[0]
    assert sample["input"].shape == (10, 5)
    assert sample["label"].shape == (1,)


def test_normalizer_causal_fit_transform():
    train_data = np.random.randn(50, 3) * 10.0 + 5.0
    val_data = np.random.randn(20, 3) * 10.0 + 5.0

    norm = Normalizer(method="standard")
    norm.fit(train_data)
    
    train_scaled = norm.transform(train_data)
    val_scaled = norm.transform(val_data)

    assert np.allclose(np.mean(train_scaled, axis=0), 0.0, atol=1e-5)
    assert np.allclose(np.std(train_scaled, axis=0), 1.0, atol=1e-5)
    assert norm.inverse_transform(train_scaled).shape == train_data.shape


def test_ews_indicators_ar1():
    # Simulate rising autocorrelation
    data = np.sin(np.linspace(0, 10, 100)) + np.random.randn(100) * 0.1
    ar1 = EWSIndicators.autocorrelation_lag1(data, window=20, min_periods=10)
    assert len(ar1) == 100
    assert np.isnan(ar1[0])  # Padding before window fills


def test_climate_indices_dhw():
    sst_anomaly = np.array([0.0, 0.5, 1.2, 1.5, 2.0, 0.8, 1.1, 0.0])
    dhw = ClimateIndices.degree_heating_weeks(sst_anomaly, threshold=1.0, accumulation_window=4)
    assert len(dhw) == 8
    assert dhw[4] > 0.0
