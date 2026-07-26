"""Metrics plots — ROC, PR curves, confusion matrices, reliability diagrams."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from loguru import logger


class MetricsPlotter:
    """Publication-quality evaluation metric plots."""

    @staticmethod
    def plot_roc_curve(
        fpr: np.ndarray, tpr: np.ndarray, auc_score: float,
        title: str = "ROC Curve", save_path: str | Path | None = None,
    ) -> plt.Figure:
        fig, ax = plt.subplots(figsize=(8, 8))
        fig.patch.set_facecolor("#0a0a0a")
        ax.set_facecolor("#111111")

        ax.plot(fpr, tpr, color="#00d4ff", linewidth=2, label=f"AUC = {auc_score:.4f}")
        ax.plot([0, 1], [0, 1], color="#555555", linestyle="--", linewidth=1, label="Random")
        ax.fill_between(fpr, tpr, alpha=0.1, color="#00d4ff")

        ax.set_xlabel("False Positive Rate", color="#e0e0e0", fontsize=12)
        ax.set_ylabel("True Positive Rate", color="#e0e0e0", fontsize=12)
        ax.set_title(title, color="#e0e0e0", fontsize=14, fontweight="bold")
        ax.legend(facecolor="#1a1a1a", edgecolor="#333333", labelcolor="#e0e0e0", fontsize=11)
        ax.tick_params(colors="#e0e0e0")
        ax.set_xlim([-0.02, 1.02])
        ax.set_ylim([-0.02, 1.02])
        ax.grid(True, alpha=0.15, color="#333333")

        plt.tight_layout()
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
        return fig

    @staticmethod
    def plot_precision_recall(
        precision: np.ndarray, recall: np.ndarray, ap_score: float,
        title: str = "Precision-Recall Curve", save_path: str | Path | None = None,
    ) -> plt.Figure:
        fig, ax = plt.subplots(figsize=(8, 8))
        fig.patch.set_facecolor("#0a0a0a")
        ax.set_facecolor("#111111")

        ax.plot(recall, precision, color="#ff6b35", linewidth=2, label=f"AP = {ap_score:.4f}")
        ax.fill_between(recall, precision, alpha=0.1, color="#ff6b35")

        ax.set_xlabel("Recall", color="#e0e0e0", fontsize=12)
        ax.set_ylabel("Precision", color="#e0e0e0", fontsize=12)
        ax.set_title(title, color="#e0e0e0", fontsize=14, fontweight="bold")
        ax.legend(facecolor="#1a1a1a", edgecolor="#333333", labelcolor="#e0e0e0", fontsize=11)
        ax.tick_params(colors="#e0e0e0")
        ax.grid(True, alpha=0.15, color="#333333")

        plt.tight_layout()
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
        return fig

    @staticmethod
    def plot_confusion_matrix(
        cm: np.ndarray, labels: list[str] | None = None,
        title: str = "Confusion Matrix", save_path: str | Path | None = None,
    ) -> plt.Figure:
        if labels is None:
            labels = ["Safe", "Tipping"]

        fig, ax = plt.subplots(figsize=(8, 6))
        fig.patch.set_facecolor("#0a0a0a")
        ax.set_facecolor("#111111")

        import seaborn as sns
        sns.heatmap(cm, annot=True, fmt="d", cmap="YlOrRd", ax=ax,
                    xticklabels=labels, yticklabels=labels,
                    linewidths=2, linecolor="#333333",
                    annot_kws={"fontsize": 16, "fontweight": "bold"})

        ax.set_xlabel("Predicted", color="#e0e0e0", fontsize=12)
        ax.set_ylabel("Actual", color="#e0e0e0", fontsize=12)
        ax.set_title(title, color="#e0e0e0", fontsize=14, fontweight="bold")
        ax.tick_params(colors="#e0e0e0")

        plt.tight_layout()
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
        return fig

    @staticmethod
    def plot_reliability_diagram(
        bin_centers: np.ndarray, bin_accuracies: np.ndarray, bin_counts: np.ndarray,
        title: str = "Reliability Diagram", save_path: str | Path | None = None,
    ) -> plt.Figure:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 10), gridspec_kw={"height_ratios": [3, 1]})
        fig.patch.set_facecolor("#0a0a0a")

        for ax in [ax1, ax2]:
            ax.set_facecolor("#111111")
            ax.tick_params(colors="#e0e0e0")

        ax1.plot([0, 1], [0, 1], color="#555555", linestyle="--", label="Perfect calibration")
        ax1.bar(bin_centers, bin_accuracies, width=0.08, alpha=0.8, color="#00d4ff",
                edgecolor="#0099cc", label="Model")
        ax1.set_xlabel("Mean Predicted Probability", color="#e0e0e0")
        ax1.set_ylabel("Fraction of Positives", color="#e0e0e0")
        ax1.set_title(title, color="#e0e0e0", fontsize=14, fontweight="bold")
        ax1.legend(facecolor="#1a1a1a", edgecolor="#333333", labelcolor="#e0e0e0")

        ax2.bar(bin_centers, bin_counts, width=0.08, color="#ff6b35", alpha=0.8)
        ax2.set_xlabel("Mean Predicted Probability", color="#e0e0e0")
        ax2.set_ylabel("Count", color="#e0e0e0")

        plt.tight_layout()
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
        return fig
