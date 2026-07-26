"""Early Warning Signal (EWS) indicators.

Computes classical critical slowing down indicators: lag-1 autocorrelation,
variance, skewness, kurtosis, and Detrended Fluctuation Analysis (DFA).
These are the foundational features for tipping point detection.

Reference:
    Scheffer, M., et al. (2009). Early-warning signals for critical transitions.
    Nature, 461(7260), 53–59.
"""

from __future__ import annotations

import numpy as np
from loguru import logger
from scipy import stats


class EWSIndicators:
    """Compute early-warning signal indicators over rolling windows.

    All methods accept 1-D time series and return arrays of the same length
    (padded with NaN for initial incomplete windows).
    """

    @staticmethod
    def autocorrelation_lag1(
        data: np.ndarray,
        window: int = 50,
        min_periods: int = 25,
    ) -> np.ndarray:
        """Compute rolling lag-1 autocorrelation (AR(1) coefficient).

        Rising AR(1) toward 1 indicates critical slowing down — the system
        is losing its ability to recover from perturbations.

        Args:
            data: 1-D time series array.
            window: Rolling window size.
            min_periods: Minimum valid observations in window.

        Returns:
            Rolling AR(1) values (same length as input, NaN-padded).
        """
        n = len(data)
        result = np.full(n, np.nan, dtype=np.float64)

        for i in range(window - 1, n):
            segment = data[i - window + 1 : i + 1]
            valid = ~np.isnan(segment)
            if valid.sum() < min_periods:
                continue
            seg = segment[valid]
            if len(seg) < 2 or np.std(seg) == 0:
                result[i] = 0.0
                continue
            result[i] = np.corrcoef(seg[:-1], seg[1:])[0, 1]

        logger.debug(f"Computed AR(1): window={window}, valid={np.sum(~np.isnan(result))}")
        return result

    @staticmethod
    def variance(
        data: np.ndarray,
        window: int = 50,
        min_periods: int = 25,
    ) -> np.ndarray:
        """Compute rolling variance.

        Increasing variance indicates growing fluctuations near a tipping point.

        Args:
            data: 1-D time series.
            window: Rolling window size.
            min_periods: Minimum valid observations.

        Returns:
            Rolling variance values.
        """
        n = len(data)
        result = np.full(n, np.nan, dtype=np.float64)

        for i in range(window - 1, n):
            segment = data[i - window + 1 : i + 1]
            valid = segment[~np.isnan(segment)]
            if len(valid) >= min_periods:
                result[i] = np.var(valid, ddof=1)

        return result

    @staticmethod
    def skewness(
        data: np.ndarray,
        window: int = 50,
        min_periods: int = 25,
    ) -> np.ndarray:
        """Compute rolling skewness.

        Increasing skewness can indicate asymmetric fluctuations near
        a fold bifurcation.

        Args:
            data: 1-D time series.
            window: Rolling window size.
            min_periods: Minimum valid observations.

        Returns:
            Rolling skewness values.
        """
        n = len(data)
        result = np.full(n, np.nan, dtype=np.float64)

        for i in range(window - 1, n):
            segment = data[i - window + 1 : i + 1]
            valid = segment[~np.isnan(segment)]
            if len(valid) >= min_periods:
                result[i] = float(stats.skew(valid, bias=False))

        return result

    @staticmethod
    def kurtosis(
        data: np.ndarray,
        window: int = 50,
        min_periods: int = 25,
    ) -> np.ndarray:
        """Compute rolling excess kurtosis.

        Args:
            data: 1-D time series.
            window: Rolling window size.
            min_periods: Minimum valid observations.

        Returns:
            Rolling kurtosis values.
        """
        n = len(data)
        result = np.full(n, np.nan, dtype=np.float64)

        for i in range(window - 1, n):
            segment = data[i - window + 1 : i + 1]
            valid = segment[~np.isnan(segment)]
            if len(valid) >= min_periods:
                result[i] = float(stats.kurtosis(valid, bias=False))

        return result

    @staticmethod
    def detrended_fluctuation_analysis(
        data: np.ndarray,
        window: int = 50,
        min_periods: int = 25,
        scales: list[int] | None = None,
    ) -> np.ndarray:
        """Compute rolling Detrended Fluctuation Analysis (DFA) exponent.

        DFA exponent α > 0.5 indicates long-range correlations (memory),
        which increase near tipping points.

        Args:
            data: 1-D time series.
            window: Rolling window size.
            min_periods: Minimum valid observations.
            scales: Box sizes for DFA. Auto-computed if None.

        Returns:
            Rolling DFA exponent values.
        """
        n = len(data)
        result = np.full(n, np.nan, dtype=np.float64)

        for i in range(window - 1, n):
            segment = data[i - window + 1 : i + 1]
            valid = segment[~np.isnan(segment)]
            if len(valid) < min_periods:
                continue
            result[i] = EWSIndicators._dfa_exponent(valid, scales)

        return result

    @staticmethod
    def _dfa_exponent(
        data: np.ndarray,
        scales: list[int] | None = None,
    ) -> float:
        """Compute DFA exponent for a single segment."""
        n = len(data)
        if scales is None:
            max_scale = n // 4
            min_scale = 4
            if max_scale < min_scale:
                return np.nan
            scales = np.unique(
                np.logspace(np.log10(min_scale), np.log10(max_scale), num=10).astype(int)
            ).tolist()

        # Integrate the time series
        y = np.cumsum(data - np.mean(data))

        fluctuations = []
        valid_scales = []

        for scale in scales:
            if scale < 4 or scale > n // 2:
                continue

            n_segments = n // scale
            if n_segments == 0:
                continue

            rms_values = []
            for seg in range(n_segments):
                start = seg * scale
                end = start + scale
                segment = y[start:end]
                t = np.arange(scale, dtype=np.float64)

                # Linear fit and detrend
                coeffs = np.polyfit(t, segment, 1)
                trend = np.polyval(coeffs, t)
                residual = segment - trend
                rms_values.append(np.sqrt(np.mean(residual**2)))

            if rms_values:
                fluctuations.append(np.mean(rms_values))
                valid_scales.append(scale)

        if len(valid_scales) < 3:
            return np.nan

        # Log-log regression for exponent
        log_scales = np.log(valid_scales)
        log_fluct = np.log(fluctuations)
        coeffs = np.polyfit(log_scales, log_fluct, 1)
        return coeffs[0]  # DFA exponent α

    @staticmethod
    def compute_all(
        data: np.ndarray,
        window: int = 50,
        min_periods: int = 25,
    ) -> dict[str, np.ndarray]:
        """Compute all EWS indicators at once.

        Args:
            data: 1-D time series.
            window: Rolling window size.
            min_periods: Minimum valid observations.

        Returns:
            Dictionary mapping indicator names to value arrays.
        """
        indicators = {
            "autocorrelation_lag1": EWSIndicators.autocorrelation_lag1(data, window, min_periods),
            "variance": EWSIndicators.variance(data, window, min_periods),
            "skewness": EWSIndicators.skewness(data, window, min_periods),
            "kurtosis": EWSIndicators.kurtosis(data, window, min_periods),
            "dfa_exponent": EWSIndicators.detrended_fluctuation_analysis(data, window, min_periods),
        }
        logger.info(f"Computed all EWS indicators: window={window}")
        return indicators
