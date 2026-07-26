"""Lag features and rolling statistics — temporal feature engineering.

Generates lagged values, rolling statistics, and seasonal decomposition
features for time series classification.
"""

from __future__ import annotations

import numpy as np
from loguru import logger


class LagFeatureGenerator:
    """Generate lag-based and rolling temporal features."""

    @staticmethod
    def create_lag_features(
        data: np.ndarray,
        lags: list[int] | None = None,
        max_lag: int = 12,
    ) -> np.ndarray:
        """Create lagged versions of the input features.

        Args:
            data: Input array of shape ``(T, F)``.
            lags: Specific lag values. If None, uses ``range(1, max_lag + 1)``.
            max_lag: Maximum lag (used if ``lags`` is None).

        Returns:
            Array of shape ``(T, F * n_lags)`` with lagged features.
        """
        if lags is None:
            lags = list(range(1, max_lag + 1))

        if data.ndim == 1:
            data = data[:, np.newaxis]

        n_time, n_features = data.shape
        n_lags = len(lags)
        result = np.full((n_time, n_features * n_lags), np.nan, dtype=np.float64)

        for i, lag in enumerate(lags):
            start_col = i * n_features
            end_col = start_col + n_features
            if lag < n_time:
                result[lag:, start_col:end_col] = data[:-lag] if lag > 0 else data

        logger.debug(f"Created lag features: lags={lags}, output shape={result.shape}")
        return result

    @staticmethod
    def rolling_statistics(
        data: np.ndarray,
        windows: list[int] | None = None,
        statistics: list[str] | None = None,
    ) -> np.ndarray:
        """Compute rolling window statistics over the time dimension.

        Args:
            data: Input array of shape ``(T,)`` or ``(T, F)``.
            windows: Window sizes (default: ``[6, 12, 24]``).
            statistics: Statistics to compute (default: ``["mean", "std", "min", "max"]``).

        Returns:
            Array with all rolling statistics concatenated along feature axis.
        """
        if windows is None:
            windows = [6, 12, 24]
        if statistics is None:
            statistics = ["mean", "std", "min", "max"]

        if data.ndim == 1:
            data = data[:, np.newaxis]

        n_time, n_features = data.shape
        all_features = []

        stat_funcs = {
            "mean": np.nanmean,
            "std": np.nanstd,
            "min": np.nanmin,
            "max": np.nanmax,
            "median": np.nanmedian,
        }

        for window in windows:
            for stat_name in statistics:
                func = stat_funcs.get(stat_name)
                if func is None:
                    continue

                result = np.full((n_time, n_features), np.nan, dtype=np.float64)
                for i in range(window - 1, n_time):
                    segment = data[i - window + 1 : i + 1]
                    result[i] = func(segment, axis=0)

                all_features.append(result)

        output = np.concatenate(all_features, axis=1)
        logger.debug(
            f"Computed rolling statistics: windows={windows}, "
            f"stats={statistics}, output shape={output.shape}"
        )
        return output

    @staticmethod
    def trend_features(
        data: np.ndarray,
        windows: list[int] | None = None,
    ) -> np.ndarray:
        """Compute rolling trend (linear regression slope) features.

        Args:
            data: Input array of shape ``(T,)`` or ``(T, F)``.
            windows: Window sizes for trend computation.

        Returns:
            Array of trend slopes.
        """
        if windows is None:
            windows = [12, 24, 60]

        if data.ndim == 1:
            data = data[:, np.newaxis]

        n_time, n_features = data.shape
        all_trends = []

        for window in windows:
            result = np.full((n_time, n_features), np.nan, dtype=np.float64)
            t = np.arange(window, dtype=np.float64)

            for i in range(window - 1, n_time):
                for f in range(n_features):
                    segment = data[i - window + 1 : i + 1, f]
                    valid = ~np.isnan(segment)
                    if valid.sum() > 2:
                        coeffs = np.polyfit(t[valid], segment[valid], 1)
                        result[i, f] = coeffs[0]  # Slope

            all_trends.append(result)

        output = np.concatenate(all_trends, axis=1)
        logger.debug(f"Computed trend features: windows={windows}, output shape={output.shape}")
        return output

    @staticmethod
    def seasonal_decomposition_features(
        data: np.ndarray,
        period: int = 12,
    ) -> dict[str, np.ndarray]:
        """Decompose time series into trend, seasonal, and residual components.

        Uses STL-like additive decomposition.

        Args:
            data: 1-D time series.
            period: Seasonal period (e.g., 12 for monthly data).

        Returns:
            Dictionary with ``"trend"``, ``"seasonal"``, ``"residual"`` arrays.
        """
        try:
            from statsmodels.tsa.seasonal import seasonal_decompose

            valid_mask = ~np.isnan(data)
            if valid_mask.sum() < 2 * period:
                return {
                    "trend": np.full_like(data, np.nan),
                    "seasonal": np.full_like(data, np.nan),
                    "residual": np.full_like(data, np.nan),
                }

            # Fill NaN temporarily for decomposition
            filled = data.copy()
            filled[~valid_mask] = np.nanmean(data)

            result = seasonal_decompose(filled, model="additive", period=period)

            logger.debug(f"Computed seasonal decomposition: period={period}")
            return {
                "trend": result.trend,
                "seasonal": result.seasonal,
                "residual": result.resid,
            }
        except ImportError:
            logger.warning("statsmodels not available, returning empty decomposition")
            return {
                "trend": np.full_like(data, np.nan),
                "seasonal": np.full_like(data, np.nan),
                "residual": np.full_like(data, np.nan),
            }
