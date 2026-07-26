"""ARIMA/AR(1) baseline for tipping point detection via statistical indicators."""

from __future__ import annotations

import numpy as np
from loguru import logger
from omegaconf import DictConfig


class ARIMABaseline:
    """ARIMA-based tipping detection using AR(1) coefficient monitoring.

    Triggers an alarm when the rolling AR(1) coefficient or variance
    exceeds a percentile threshold computed from the reference period.

    Args:
        cfg: Model config from ``configs/model/arima.yaml``.
    """

    def __init__(self, cfg: DictConfig) -> None:
        det = cfg.detection
        self.ar1_percentile = det.ar1_threshold_percentile
        self.var_percentile = det.variance_threshold_percentile
        self.window = det.window_size
        self.min_periods = det.min_periods
        self._ar1_threshold: float | None = None
        self._var_threshold: float | None = None
        logger.info("Initialized ARIMABaseline")

    def fit(self, data: np.ndarray, reference_end_idx: int | None = None) -> ARIMABaseline:
        """Compute threshold from reference period.

        Args:
            data: 1-D time series.
            reference_end_idx: End index of the reference (baseline) period.
                Uses first half of data if None.
        """
        if reference_end_idx is None:
            reference_end_idx = len(data) // 2

        ref = data[:reference_end_idx]

        # Compute rolling AR(1) and variance on reference period
        ar1_values = self._rolling_ar1(ref)
        var_values = self._rolling_variance(ref)

        ar1_valid = ar1_values[~np.isnan(ar1_values)]
        var_valid = var_values[~np.isnan(var_values)]

        self._ar1_threshold = float(np.percentile(ar1_valid, self.ar1_percentile)) if len(ar1_valid) > 0 else 0.95
        self._var_threshold = float(np.percentile(var_valid, self.var_percentile)) if len(var_valid) > 0 else np.inf

        logger.info(f"ARIMA thresholds: AR(1) > {self._ar1_threshold:.4f}, Var > {self._var_threshold:.4f}")
        return self

    def predict(self, data: np.ndarray) -> np.ndarray:
        """Predict binary tipping alerts."""
        proba = self.predict_proba(data)
        return (proba >= 0.5).astype(np.float32)

    def predict_proba(self, data: np.ndarray) -> np.ndarray:
        """Predict tipping probability based on AR(1) and variance thresholds.

        Returns the fraction of indicators exceeding their threshold.
        """
        ar1 = self._rolling_ar1(data)
        var = self._rolling_variance(data)

        ar1_alarm = (ar1 > self._ar1_threshold).astype(np.float32)
        var_alarm = (var > self._var_threshold).astype(np.float32)

        # Combine: average of both indicators
        proba = (ar1_alarm + var_alarm) / 2.0
        proba[np.isnan(ar1) | np.isnan(var)] = 0.0

        return proba

    def _rolling_ar1(self, data: np.ndarray) -> np.ndarray:
        n = len(data)
        result = np.full(n, np.nan)
        for i in range(self.window - 1, n):
            seg = data[i - self.window + 1 : i + 1]
            valid = seg[~np.isnan(seg)]
            if len(valid) >= self.min_periods and np.std(valid) > 0:
                result[i] = np.corrcoef(valid[:-1], valid[1:])[0, 1]
        return result

    def _rolling_variance(self, data: np.ndarray) -> np.ndarray:
        n = len(data)
        result = np.full(n, np.nan)
        for i in range(self.window - 1, n):
            seg = data[i - self.window + 1 : i + 1]
            valid = seg[~np.isnan(seg)]
            if len(valid) >= self.min_periods:
                result[i] = np.var(valid, ddof=1)
        return result
