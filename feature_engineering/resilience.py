"""Resilience metrics — recovery rate, return time, CSD composite indicators."""

from __future__ import annotations

import numpy as np
from loguru import logger


class ResilienceMetrics:
    """Compute system resilience metrics from climate time series.

    These metrics quantify how quickly a system recovers from perturbations.
    Loss of resilience (critical slowing down) is a key precursor to tipping.
    """

    @staticmethod
    def recovery_rate(
        data: np.ndarray,
        perturbation_threshold: float = 1.5,
        window: int = 50,
    ) -> np.ndarray:
        """Estimate system recovery rate from perturbation responses.

        Identifies perturbation events (exceedances above threshold std)
        and measures how quickly the system returns to its mean state.

        Args:
            data: Detrended, de-seasonalized time series.
            perturbation_threshold: Number of std deviations to qualify as perturbation.
            window: Rolling window for local statistics.

        Returns:
            Rolling recovery rate estimates (higher = more resilient).
        """
        n = len(data)
        result = np.full(n, np.nan, dtype=np.float64)

        for i in range(window, n):
            segment = data[i - window : i]
            valid = segment[~np.isnan(segment)]
            if len(valid) < window // 2:
                continue

            mean = np.mean(valid)
            std = np.std(valid)
            if std == 0:
                continue

            # Find perturbation events
            deviations = np.abs(valid - mean) / std
            perturbation_mask = deviations > perturbation_threshold

            if not np.any(perturbation_mask):
                result[i] = 1.0  # No perturbation = assume high resilience
                continue

            # Estimate recovery: exponential decay rate
            recovery_times = []
            in_perturbation = False
            start_idx = 0

            for j in range(len(valid)):
                if perturbation_mask[j] and not in_perturbation:
                    in_perturbation = True
                    start_idx = j
                elif not perturbation_mask[j] and in_perturbation:
                    recovery_times.append(j - start_idx)
                    in_perturbation = False

            if recovery_times:
                mean_recovery = np.mean(recovery_times)
                result[i] = 1.0 / max(mean_recovery, 1.0)
            else:
                result[i] = 0.5  # Uncertain

        logger.debug(f"Computed recovery rate: threshold={perturbation_threshold}")
        return result

    @staticmethod
    def return_time(
        data: np.ndarray,
        window: int = 50,
    ) -> np.ndarray:
        """Estimate return time from autocorrelation structure.

        Return time τ ≈ -1/ln(AR(1)). As the system approaches a tipping
        point, AR(1) → 1 and return time → ∞.

        Args:
            data: 1-D time series.
            window: Rolling window size.

        Returns:
            Rolling return time estimates.
        """
        n = len(data)
        result = np.full(n, np.nan, dtype=np.float64)

        for i in range(window, n):
            segment = data[i - window : i]
            valid = segment[~np.isnan(segment)]
            if len(valid) < window // 2:
                continue
            if np.std(valid) == 0:
                continue

            ar1 = np.corrcoef(valid[:-1], valid[1:])[0, 1]
            if 0 < ar1 < 1:
                result[i] = -1.0 / np.log(ar1)
            elif ar1 >= 1:
                result[i] = np.inf
            else:
                result[i] = 1.0  # Negative AR(1) = fast recovery

        logger.debug("Computed return time from AR(1)")
        return result

    @staticmethod
    def csd_composite(
        ar1: np.ndarray,
        variance: np.ndarray,
        weights: tuple[float, float] = (0.5, 0.5),
    ) -> np.ndarray:
        """Compute composite Critical Slowing Down indicator.

        Combines normalized AR(1) and variance into a single CSD score.

        Args:
            ar1: Lag-1 autocorrelation time series.
            variance: Variance time series.
            weights: Weights for (AR1, variance) combination.

        Returns:
            Composite CSD indicator (higher = closer to tipping).
        """
        # Normalize both to [0, 1]
        def _normalize(x: np.ndarray) -> np.ndarray:
            valid = x[~np.isnan(x)]
            if len(valid) == 0:
                return np.zeros_like(x)
            xmin, xmax = np.min(valid), np.max(valid)
            if xmax == xmin:
                return np.zeros_like(x)
            return (x - xmin) / (xmax - xmin)

        ar1_norm = _normalize(ar1)
        var_norm = _normalize(variance)

        composite = weights[0] * ar1_norm + weights[1] * var_norm
        logger.debug(f"Computed CSD composite: weights={weights}")
        return composite

    @staticmethod
    def restoring_force(
        data: np.ndarray,
        window: int = 50,
    ) -> np.ndarray:
        """Estimate the restoring force from consecutive differences.

        The restoring force λ is estimated from the slope of Δx(t) vs x(t)
        in a local window. More negative λ = stronger restoring force.

        Args:
            data: 1-D time series.
            window: Rolling window size.

        Returns:
            Rolling restoring force estimates.
        """
        n = len(data)
        result = np.full(n, np.nan, dtype=np.float64)

        for i in range(window, n):
            segment = data[i - window : i]
            valid = segment[~np.isnan(segment)]
            if len(valid) < window // 2:
                continue

            x = valid[:-1]
            dx = np.diff(valid)

            if np.std(x) == 0:
                continue

            # Linear regression: dx = λ * x + noise
            coeffs = np.polyfit(x, dx, 1)
            result[i] = coeffs[0]  # λ (negative = restoring)

        logger.debug("Computed restoring force estimates")
        return result
