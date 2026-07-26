"""Normalization utilities — causal (past-only) scaling for climate data.

All normalizers ensure no look-ahead bias: statistics are computed only
from the training split and applied to validation/test splits.
"""

from __future__ import annotations

import numpy as np
from loguru import logger


class Normalizer:
    """Stateful normalizer that fits on training data and transforms any split.

    Supports standard (z-score), min-max, and robust normalization.

    Args:
        method: Normalization method — ``"standard"``, ``"minmax"``, ``"robust"``.
    """

    def __init__(self, method: str = "standard") -> None:
        self.method = method
        self._fitted = False
        self._params: dict[str, np.ndarray] = {}

    def fit(self, data: np.ndarray) -> Normalizer:
        """Compute normalization statistics from training data.

        Args:
            data: Training data of shape ``(T, F)`` or ``(T,)``.

        Returns:
            Self (for method chaining).
        """
        if data.ndim == 1:
            data = data[:, np.newaxis]

        if self.method == "standard":
            self._params["mean"] = np.nanmean(data, axis=0)
            self._params["std"] = np.nanstd(data, axis=0)
            self._params["std"] = np.where(self._params["std"] == 0, 1.0, self._params["std"])

        elif self.method == "minmax":
            self._params["min"] = np.nanmin(data, axis=0)
            self._params["max"] = np.nanmax(data, axis=0)
            data_range = self._params["max"] - self._params["min"]
            self._params["range"] = np.where(data_range == 0, 1.0, data_range)

        elif self.method == "robust":
            self._params["median"] = np.nanmedian(data, axis=0)
            q75 = np.nanpercentile(data, 75, axis=0)
            q25 = np.nanpercentile(data, 25, axis=0)
            iqr = q75 - q25
            self._params["iqr"] = np.where(iqr == 0, 1.0, iqr)

        else:
            raise ValueError(f"Unknown normalization method: {self.method}")

        self._fitted = True
        logger.debug(f"Fitted {self.method} normalizer on shape {data.shape}")
        return self

    def transform(self, data: np.ndarray) -> np.ndarray:
        """Apply normalization using fitted parameters.

        Args:
            data: Data to normalize, shape ``(T, F)`` or ``(T,)``.

        Returns:
            Normalized array of the same shape.

        Raises:
            RuntimeError: If ``fit()`` hasn't been called.
        """
        if not self._fitted:
            raise RuntimeError("Normalizer not fitted. Call fit() first.")

        squeeze = False
        if data.ndim == 1:
            data = data[:, np.newaxis]
            squeeze = True

        if self.method == "standard":
            result = (data - self._params["mean"]) / self._params["std"]
        elif self.method == "minmax":
            result = (data - self._params["min"]) / self._params["range"]
        elif self.method == "robust":
            result = (data - self._params["median"]) / self._params["iqr"]
        else:
            result = data

        return result.squeeze() if squeeze else result

    def inverse_transform(self, data: np.ndarray) -> np.ndarray:
        """Reverse the normalization.

        Args:
            data: Normalized data.

        Returns:
            Data in original scale.
        """
        if not self._fitted:
            raise RuntimeError("Normalizer not fitted. Call fit() first.")

        squeeze = False
        if data.ndim == 1:
            data = data[:, np.newaxis]
            squeeze = True

        if self.method == "standard":
            result = data * self._params["std"] + self._params["mean"]
        elif self.method == "minmax":
            result = data * self._params["range"] + self._params["min"]
        elif self.method == "robust":
            result = data * self._params["iqr"] + self._params["median"]
        else:
            result = data

        return result.squeeze() if squeeze else result

    def fit_transform(self, data: np.ndarray) -> np.ndarray:
        """Fit and transform in a single call.

        Args:
            data: Training data.

        Returns:
            Normalized data.
        """
        return self.fit(data).transform(data)

    def get_params(self) -> dict[str, np.ndarray]:
        """Return fitted parameters for serialization."""
        return dict(self._params)

    def __repr__(self) -> str:
        status = "fitted" if self._fitted else "not fitted"
        return f"Normalizer(method='{self.method}', {status})"
