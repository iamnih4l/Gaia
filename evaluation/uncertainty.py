"""Uncertainty estimation — MC Dropout, ensemble, prediction intervals."""

from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
from loguru import logger


class UncertaintyEstimator:
    """Estimate prediction uncertainty via MC Dropout or ensemble methods."""

    @staticmethod
    @torch.no_grad()
    def mc_dropout_predict(
        model: nn.Module,
        x: torch.Tensor,
        n_samples: int = 50,
    ) -> dict[str, np.ndarray]:
        """Run MC Dropout inference for uncertainty estimation.

        Enables dropout at inference and runs multiple forward passes
        to estimate predictive distribution.

        Args:
            model: Trained model with dropout layers.
            x: Input tensor ``(B, T, F)``.
            n_samples: Number of stochastic forward passes.

        Returns:
            Dict with ``mean``, ``std``, ``samples`` arrays.
        """
        model.train()  # Enable dropout
        predictions = []

        for _ in range(n_samples):
            pred = model(x).cpu().numpy()
            predictions.append(pred)

        model.eval()
        predictions = np.array(predictions)  # (n_samples, B, output_dim)

        return {
            "mean": predictions.mean(axis=0),
            "std": predictions.std(axis=0),
            "samples": predictions,
            "lower_95": np.percentile(predictions, 2.5, axis=0),
            "upper_95": np.percentile(predictions, 97.5, axis=0),
        }

    @staticmethod
    @torch.no_grad()
    def ensemble_predict(
        models: list[nn.Module],
        x: torch.Tensor,
    ) -> dict[str, np.ndarray]:
        """Run ensemble prediction for uncertainty estimation.

        Args:
            models: List of trained models.
            x: Input tensor.

        Returns:
            Dict with ``mean``, ``std``, ``samples`` arrays.
        """
        predictions = []

        for model in models:
            model.eval()
            pred = model(x).cpu().numpy()
            predictions.append(pred)

        predictions = np.array(predictions)

        return {
            "mean": predictions.mean(axis=0),
            "std": predictions.std(axis=0),
            "samples": predictions,
            "lower_95": np.percentile(predictions, 2.5, axis=0),
            "upper_95": np.percentile(predictions, 97.5, axis=0),
        }

    @staticmethod
    def prediction_interval_coverage(
        y_true: np.ndarray,
        lower: np.ndarray,
        upper: np.ndarray,
    ) -> float:
        """Compute prediction interval coverage probability (PICP).

        Args:
            y_true: True values.
            lower: Lower bound of prediction interval.
            upper: Upper bound of prediction interval.

        Returns:
            Coverage probability (fraction of true values within interval).
        """
        covered = ((y_true >= lower) & (y_true <= upper)).mean()
        logger.debug(f"PICP: {covered:.3f}")
        return float(covered)
