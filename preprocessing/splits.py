"""Data splitting utilities — temporal splits and cross-validation.

Climate data requires temporal splitting (no random shuffling) to avoid
look-ahead bias. This module provides temporal train/val/test splits,
time-block cross-validation, and leave-one-event-out cross-validation.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from loguru import logger


@dataclass
class SplitResult:
    """Container for a single data split."""

    train_indices: np.ndarray
    val_indices: np.ndarray
    test_indices: np.ndarray

    @property
    def n_train(self) -> int:
        return len(self.train_indices)

    @property
    def n_val(self) -> int:
        return len(self.val_indices)

    @property
    def n_test(self) -> int:
        return len(self.test_indices)


class DataSplitter:
    """Temporal data splitting for climate time series."""

    @staticmethod
    def temporal_split(
        n_samples: int,
        train_ratio: float = 0.7,
        val_ratio: float = 0.15,
        gap: int = 0,
    ) -> SplitResult:
        """Split data temporally into train/val/test.

        Args:
            n_samples: Total number of samples.
            train_ratio: Fraction for training.
            val_ratio: Fraction for validation.
            gap: Number of samples to skip between splits (to reduce leakage).

        Returns:
            ``SplitResult`` with index arrays.
        """
        train_end = int(n_samples * train_ratio)
        val_start = train_end + gap
        val_end = val_start + int(n_samples * val_ratio)
        test_start = val_end + gap

        result = SplitResult(
            train_indices=np.arange(0, train_end),
            val_indices=np.arange(val_start, min(val_end, n_samples)),
            test_indices=np.arange(test_start, n_samples),
        )

        logger.info(
            f"Temporal split: train={result.n_train}, "
            f"val={result.n_val}, test={result.n_test}, gap={gap}"
        )
        return result

    @staticmethod
    def time_block_cv(
        n_samples: int,
        n_splits: int = 5,
        min_train_size: int | None = None,
    ) -> list[SplitResult]:
        """Time-block cross-validation (expanding window).

        Each fold uses all data up to a point for training and the next
        block for validation/testing.

        Args:
            n_samples: Total number of samples.
            n_splits: Number of CV folds.
            min_train_size: Minimum training set size.

        Returns:
            List of ``SplitResult`` objects, one per fold.
        """
        block_size = n_samples // (n_splits + 1)
        if min_train_size is None:
            min_train_size = block_size

        folds = []
        for i in range(n_splits):
            train_end = min_train_size + i * block_size
            val_start = train_end
            val_end = min(val_start + block_size, n_samples)

            if val_end > n_samples:
                break

            folds.append(
                SplitResult(
                    train_indices=np.arange(0, train_end),
                    val_indices=np.arange(val_start, val_end),
                    test_indices=np.arange(val_end, min(val_end + block_size, n_samples)),
                )
            )

        logger.info(f"Time-block CV: {len(folds)} folds, block_size={block_size}")
        return folds

    @staticmethod
    def leave_one_event_out(
        n_samples: int,
        event_indices: list[int],
        event_window: int = 12,
    ) -> list[SplitResult]:
        """Leave-one-event-out cross-validation.

        Each fold holds out one tipping event (and its surrounding window)
        for testing, trains on everything else.

        Args:
            n_samples: Total number of samples.
            event_indices: Indices of tipping events.
            event_window: Half-window around each event to hold out.

        Returns:
            List of ``SplitResult`` objects, one per event.
        """
        all_indices = np.arange(n_samples)
        folds = []

        for event_idx in event_indices:
            test_start = max(0, event_idx - event_window)
            test_end = min(n_samples, event_idx + event_window + 1)
            test_indices = np.arange(test_start, test_end)
            train_indices = np.setdiff1d(all_indices, test_indices)

            # Use last 15% of training as validation
            val_size = max(1, int(len(train_indices) * 0.15))
            val_indices = train_indices[-val_size:]
            train_indices = train_indices[:-val_size]

            folds.append(
                SplitResult(
                    train_indices=train_indices,
                    val_indices=val_indices,
                    test_indices=test_indices,
                )
            )

        logger.info(
            f"Leave-one-event-out CV: {len(folds)} folds, "
            f"events at indices {event_indices}"
        )
        return folds
