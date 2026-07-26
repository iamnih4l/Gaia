"""Tipping event label generation.

Creates binary and continuous labels for supervised training of tipping
point detectors. Supports window-based, proximity-based, and threshold-based
labeling strategies.
"""

from __future__ import annotations

import numpy as np
from loguru import logger


class LabelGenerator:
    """Generate labels for climate tipping point detection.

    Provides multiple labeling strategies:
    - **binary_window**: Labels a fixed window before known tipping events as positive.
    - **proximity_continuous**: Continuous labels that increase as tipping approaches.
    - **threshold_based**: Labels based on variable exceeding a threshold.
    """

    @staticmethod
    def binary_window(
        n_timesteps: int,
        event_indices: list[int],
        window_before: int = 12,
        window_after: int = 0,
    ) -> np.ndarray:
        """Create binary labels with a warning window before each event.

        Args:
            n_timesteps: Total number of time steps.
            event_indices: Indices of known tipping events.
            window_before: Number of time steps before the event to label as positive.
            window_after: Number of time steps after the event to label as positive.

        Returns:
            Binary label array of shape ``(n_timesteps,)``.
        """
        labels = np.zeros(n_timesteps, dtype=np.float32)
        for idx in event_indices:
            start = max(0, idx - window_before)
            end = min(n_timesteps, idx + window_after + 1)
            labels[start:end] = 1.0

        positive_rate = labels.mean()
        logger.info(
            f"Generated binary window labels: {labels.sum():.0f}/{n_timesteps} positive "
            f"({positive_rate:.1%}), window=[-{window_before}, +{window_after}]"
        )
        return labels

    @staticmethod
    def proximity_continuous(
        n_timesteps: int,
        event_indices: list[int],
        max_distance: int = 60,
        decay: str = "linear",
    ) -> np.ndarray:
        """Create continuous labels that increase as tipping approaches.

        Args:
            n_timesteps: Total number of time steps.
            event_indices: Indices of known tipping events.
            max_distance: Maximum distance (in time steps) at which label > 0.
            decay: Decay function — ``"linear"`` or ``"exponential"``.

        Returns:
            Continuous label array in [0, 1] of shape ``(n_timesteps,)``.
        """
        labels = np.zeros(n_timesteps, dtype=np.float32)

        for t in range(n_timesteps):
            min_dist = min(
                (abs(t - event_idx) for event_idx in event_indices),
                default=max_distance + 1,
            )
            if min_dist <= max_distance:
                if decay == "linear":
                    labels[t] = 1.0 - (min_dist / max_distance)
                elif decay == "exponential":
                    labels[t] = np.exp(-3.0 * min_dist / max_distance)

        logger.info(
            f"Generated proximity labels: decay={decay}, max_distance={max_distance}, "
            f"mean={labels.mean():.3f}"
        )
        return labels

    @staticmethod
    def threshold_based(
        values: np.ndarray,
        threshold: float,
        direction: str = "above",
        sustained_periods: int = 1,
    ) -> np.ndarray:
        """Label time steps where a variable exceeds/falls below a threshold.

        Args:
            values: 1-D array of the monitored variable.
            threshold: Threshold value.
            direction: ``"above"`` or ``"below"``.
            sustained_periods: Minimum consecutive periods above/below threshold.

        Returns:
            Binary label array.
        """
        if direction == "above":
            raw_labels = (values >= threshold).astype(np.float32)
        else:
            raw_labels = (values <= threshold).astype(np.float32)

        if sustained_periods > 1:
            labels = np.zeros_like(raw_labels)
            count = 0
            for i in range(len(raw_labels)):
                if raw_labels[i] == 1.0:
                    count += 1
                    if count >= sustained_periods:
                        labels[i - sustained_periods + 1 : i + 1] = 1.0
                else:
                    count = 0
        else:
            labels = raw_labels

        logger.info(
            f"Generated threshold labels: threshold={threshold}, direction={direction}, "
            f"positive={labels.sum():.0f}/{len(labels)}"
        )
        return labels

    @staticmethod
    def from_ews_indicator(
        indicator: np.ndarray,
        percentile: float = 95,
        reference_period: tuple[int, int] | None = None,
    ) -> np.ndarray:
        """Label based on early-warning signal indicator exceeding a percentile.

        Args:
            indicator: 1-D array of an EWS indicator (e.g., AR(1), variance).
            percentile: Percentile threshold for alarm.
            reference_period: ``(start_idx, end_idx)`` for computing the
                reference distribution. Uses entire series if None.

        Returns:
            Binary label array.
        """
        if reference_period is not None:
            ref_values = indicator[reference_period[0] : reference_period[1]]
        else:
            ref_values = indicator

        valid = ref_values[~np.isnan(ref_values)]
        if len(valid) == 0:
            return np.zeros_like(indicator, dtype=np.float32)

        threshold = np.percentile(valid, percentile)
        labels = (indicator >= threshold).astype(np.float32)
        labels[np.isnan(indicator)] = 0.0

        logger.info(
            f"Generated EWS labels: percentile={percentile}, threshold={threshold:.4f}, "
            f"positive={labels.sum():.0f}/{len(labels)}"
        )
        return labels
