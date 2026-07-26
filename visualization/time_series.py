"""Time series visualization — predictions, EWS indicators, lead time annotations."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from loguru import logger


class TimeSeriesPlotter:
    """Publication-quality time series visualizations for tipping detection."""

    @staticmethod
    def plot_prediction_overlay(
        time: np.ndarray, observed: np.ndarray, predicted_prob: np.ndarray,
        event_indices: list[int] | None = None, threshold: float = 0.5,
        title: str = "Tipping Point Prediction", save_path: str | Path | None = None,
        uncertainty_lower: np.ndarray | None = None, uncertainty_upper: np.ndarray | None = None,
    ) -> plt.Figure:
        """Plot observed time series with predicted tipping probability.

        Args:
            time: Time axis values.
            observed: Observed climate variable.
            predicted_prob: Predicted tipping probability.
            event_indices: Indices of actual tipping events.
            threshold: Classification threshold line.
            title: Plot title.
            save_path: Optional save path.
            uncertainty_lower: Lower confidence bound.
            uncertainty_upper: Upper confidence bound.

        Returns:
            Matplotlib Figure.
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 8), sharex=True,
                                        gridspec_kw={"height_ratios": [1, 1]})
        fig.patch.set_facecolor("#0a0a0a")
        for ax in [ax1, ax2]:
            ax.set_facecolor("#111111")
            ax.tick_params(colors="#e0e0e0")
            ax.spines["bottom"].set_color("#333333")
            ax.spines["left"].set_color("#333333")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

        # Top: observed variable
        ax1.plot(time, observed, color="#00d4ff", linewidth=1, alpha=0.9, label="Observed")
        ax1.set_ylabel("Climate Variable", color="#e0e0e0", fontsize=12)
        ax1.legend(facecolor="#1a1a1a", edgecolor="#333333", labelcolor="#e0e0e0")

        # Bottom: predicted probability
        ax2.plot(time, predicted_prob, color="#ff6b35", linewidth=1.5, label="Tipping Probability")
        ax2.axhline(y=threshold, color="#ffcc00", linestyle="--", alpha=0.7, label=f"Threshold ({threshold})")

        if uncertainty_lower is not None and uncertainty_upper is not None:
            ax2.fill_between(time, uncertainty_lower, uncertainty_upper,
                           color="#ff6b35", alpha=0.15, label="95% CI")

        # Mark events
        if event_indices:
            for idx in event_indices:
                if idx < len(time):
                    for ax in [ax1, ax2]:
                        ax.axvline(x=time[idx], color="#ff0055", linestyle=":", alpha=0.8)

        ax2.set_ylabel("Probability", color="#e0e0e0", fontsize=12)
        ax2.set_xlabel("Time", color="#e0e0e0", fontsize=12)
        ax2.set_ylim(-0.05, 1.05)
        ax2.legend(facecolor="#1a1a1a", edgecolor="#333333", labelcolor="#e0e0e0")

        fig.suptitle(title, color="#e0e0e0", fontsize=16, fontweight="bold")
        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
            logger.info(f"Saved time series plot: {save_path}")

        return fig

    @staticmethod
    def plot_ews_indicators(
        time: np.ndarray, indicators: dict[str, np.ndarray],
        title: str = "Early Warning Signal Indicators", save_path: str | Path | None = None,
    ) -> plt.Figure:
        """Plot multiple EWS indicators over time."""
        n_indicators = len(indicators)
        fig, axes = plt.subplots(n_indicators, 1, figsize=(16, 3 * n_indicators), sharex=True)
        fig.patch.set_facecolor("#0a0a0a")

        if n_indicators == 1:
            axes = [axes]

        colors = ["#00d4ff", "#ff6b35", "#00ff88", "#ffcc00", "#ff0055"]

        for i, (name, values) in enumerate(indicators.items()):
            ax = axes[i]
            ax.set_facecolor("#111111")
            ax.tick_params(colors="#e0e0e0")
            ax.plot(time[:len(values)], values, color=colors[i % len(colors)], linewidth=1)
            ax.set_ylabel(name.replace("_", " ").title(), color="#e0e0e0", fontsize=10)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["bottom"].set_color("#333333")
            ax.spines["left"].set_color("#333333")

        axes[-1].set_xlabel("Time", color="#e0e0e0")
        fig.suptitle(title, color="#e0e0e0", fontsize=14, fontweight="bold")
        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())

        return fig
