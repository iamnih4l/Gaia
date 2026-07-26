"""Calibration analysis — reliability diagrams, Platt scaling, ECE."""

from __future__ import annotations

import numpy as np
from loguru import logger
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression


class CalibrationAnalyzer:
    """Analyze and improve model calibration."""

    @staticmethod
    def reliability_diagram(
        y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10,
    ) -> dict[str, np.ndarray]:
        """Compute reliability diagram data.

        Args:
            y_true: Binary labels.
            y_prob: Predicted probabilities.
            n_bins: Number of probability bins.

        Returns:
            Dict with ``bin_centers``, ``bin_accuracies``, ``bin_counts``.
        """
        bins = np.linspace(0, 1, n_bins + 1)
        bin_centers = (bins[:-1] + bins[1:]) / 2
        bin_accuracies = np.zeros(n_bins)
        bin_counts = np.zeros(n_bins, dtype=int)

        for i in range(n_bins):
            mask = (y_prob >= bins[i]) & (y_prob < bins[i + 1])
            if mask.sum() > 0:
                bin_accuracies[i] = y_true[mask].mean()
                bin_counts[i] = mask.sum()

        return {"bin_centers": bin_centers, "bin_accuracies": bin_accuracies, "bin_counts": bin_counts}

    @staticmethod
    def expected_calibration_error(
        y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10,
    ) -> float:
        """Compute Expected Calibration Error (ECE)."""
        diagram = CalibrationAnalyzer.reliability_diagram(y_true, y_prob, n_bins)
        total = diagram["bin_counts"].sum()
        if total == 0:
            return 0.0
        ece = np.sum(
            diagram["bin_counts"] * np.abs(diagram["bin_accuracies"] - diagram["bin_centers"])
        ) / total
        return float(ece)

    @staticmethod
    def platt_scaling(y_prob_train: np.ndarray, y_true_train: np.ndarray,
                      y_prob_test: np.ndarray) -> np.ndarray:
        """Apply Platt scaling for probability calibration."""
        lr = LogisticRegression(C=1e10, solver="lbfgs")
        lr.fit(y_prob_train.reshape(-1, 1), y_true_train)
        return lr.predict_proba(y_prob_test.reshape(-1, 1))[:, 1]

    @staticmethod
    def isotonic_calibration(y_prob_train: np.ndarray, y_true_train: np.ndarray,
                             y_prob_test: np.ndarray) -> np.ndarray:
        """Apply isotonic regression for probability calibration."""
        iso = IsotonicRegression(out_of_bounds="clip")
        iso.fit(y_prob_train, y_true_train)
        return iso.predict(y_prob_test)
