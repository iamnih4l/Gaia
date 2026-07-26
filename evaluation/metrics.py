"""Evaluation metrics for climate tipping point detection.

Includes standard classification metrics plus tipping-specific metrics:
lead time, false alarm rate, detection rate, and calibration error.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from loguru import logger
from sklearn.metrics import (
    accuracy_score,
    auc,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)


@dataclass
class MetricResults:
    """Container for all evaluation metrics."""

    roc_auc: float = 0.0
    pr_auc: float = 0.0
    f1: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    accuracy: float = 0.0
    false_alarm_rate: float = 0.0
    brier_score: float = 0.0
    mean_lead_time: float = 0.0
    median_lead_time: float = 0.0
    confusion_matrix: np.ndarray = field(default_factory=lambda: np.zeros((2, 2)))
    roc_curve: dict = field(default_factory=dict)
    pr_curve: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, float]:
        return {
            "roc_auc": self.roc_auc,
            "pr_auc": self.pr_auc,
            "f1": self.f1,
            "precision": self.precision,
            "recall": self.recall,
            "accuracy": self.accuracy,
            "false_alarm_rate": self.false_alarm_rate,
            "brier_score": self.brier_score,
            "mean_lead_time": self.mean_lead_time,
            "median_lead_time": self.median_lead_time,
        }


class TippingPointMetrics:
    """Compute all evaluation metrics for tipping point detection."""

    @staticmethod
    def compute_all(
        y_true: np.ndarray,
        y_prob: np.ndarray,
        threshold: float = 0.5,
        event_indices: list[int] | None = None,
    ) -> MetricResults:
        """Compute comprehensive evaluation metrics.

        Args:
            y_true: Ground truth binary labels ``(N,)``.
            y_prob: Predicted probabilities ``(N,)``.
            threshold: Classification threshold.
            event_indices: Indices of actual tipping events for lead time.

        Returns:
            ``MetricResults`` with all metrics.
        """
        y_pred = (y_prob >= threshold).astype(float)
        results = MetricResults()

        # Standard classification
        try:
            if len(np.unique(y_true)) > 1:
                results.roc_auc = roc_auc_score(y_true, y_prob)
                fpr, tpr, _ = roc_curve(y_true, y_prob)
                results.roc_curve = {"fpr": fpr, "tpr": tpr}
        except ValueError:
            pass

        try:
            results.pr_auc = average_precision_score(y_true, y_prob)
            prec, rec, _ = precision_recall_curve(y_true, y_prob)
            results.pr_curve = {"precision": prec, "recall": rec}
        except ValueError:
            pass

        results.f1 = f1_score(y_true, y_pred, zero_division=0)
        results.precision = precision_score(y_true, y_pred, zero_division=0)
        results.recall = recall_score(y_true, y_pred, zero_division=0)
        results.accuracy = accuracy_score(y_true, y_pred)
        results.confusion_matrix = confusion_matrix(y_true, y_pred, labels=[0, 1])
        results.brier_score = brier_score_loss(y_true, y_prob)

        # False alarm rate
        cm = results.confusion_matrix
        if cm.shape == (2, 2):
            fp, tn = cm[0, 1], cm[0, 0]
            results.false_alarm_rate = fp / max(fp + tn, 1)

        # Lead time
        if event_indices:
            lead_times = TippingPointMetrics.compute_lead_time(y_prob, event_indices, threshold)
            if lead_times:
                results.mean_lead_time = float(np.mean(lead_times))
                results.median_lead_time = float(np.median(lead_times))

        logger.info(
            f"Metrics: ROC-AUC={results.roc_auc:.4f}, F1={results.f1:.4f}, "
            f"FAR={results.false_alarm_rate:.4f}, Lead={results.mean_lead_time:.1f}"
        )
        return results

    @staticmethod
    def compute_lead_time(
        y_prob: np.ndarray,
        event_indices: list[int],
        threshold: float = 0.5,
    ) -> list[float]:
        """Compute lead time for each tipping event.

        Lead time = number of time steps between first alarm and event.

        Args:
            y_prob: Predicted probabilities.
            event_indices: Indices of actual events.
            threshold: Alarm threshold.

        Returns:
            List of lead times (positive = early warning).
        """
        y_pred = (y_prob >= threshold).astype(bool)
        lead_times = []

        for event_idx in event_indices:
            # Search backward from event for first alarm
            for t in range(event_idx - 1, -1, -1):
                if not y_pred[t]:
                    first_alarm = t + 1
                    lead_time = event_idx - first_alarm
                    if lead_time > 0:
                        lead_times.append(lead_time)
                    break
            else:
                # Alarm was on from the beginning
                lead_times.append(event_idx)

        return lead_times

    @staticmethod
    def find_optimal_threshold(
        y_true: np.ndarray,
        y_prob: np.ndarray,
        metric: str = "f1",
        n_thresholds: int = 100,
    ) -> tuple[float, float]:
        """Find optimal classification threshold.

        Args:
            y_true: Ground truth labels.
            y_prob: Predicted probabilities.
            metric: Metric to optimize — ``"f1"`` or ``"youden"`` (J statistic).
            n_thresholds: Number of thresholds to evaluate.

        Returns:
            Tuple of (optimal_threshold, best_metric_value).
        """
        thresholds = np.linspace(0.01, 0.99, n_thresholds)
        best_threshold, best_value = 0.5, 0.0

        for thresh in thresholds:
            y_pred = (y_prob >= thresh).astype(float)
            if metric == "f1":
                value = f1_score(y_true, y_pred, zero_division=0)
            elif metric == "youden":
                recall_val = recall_score(y_true, y_pred, zero_division=0)
                specificity = 1 - (y_pred[y_true == 0].sum() / max((y_true == 0).sum(), 1))
                value = recall_val + specificity - 1
            else:
                value = f1_score(y_true, y_pred, zero_division=0)

            if value > best_value:
                best_value = value
                best_threshold = thresh

        logger.info(f"Optimal threshold ({metric}): {best_threshold:.3f} → {best_value:.4f}")
        return best_threshold, best_value
