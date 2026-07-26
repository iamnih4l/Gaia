"""Model comparison — statistical tests, comparison tables, LaTeX output."""

from __future__ import annotations

import numpy as np
from loguru import logger

from evaluation.metrics import MetricResults


class ModelComparison:
    """Compare multiple models using statistical tests and summary tables."""

    @staticmethod
    def comparison_table(
        results: dict[str, MetricResults],
        metrics: list[str] | None = None,
    ) -> str:
        """Generate a markdown comparison table.

        Args:
            results: Dict mapping model names to ``MetricResults``.
            metrics: Metrics to include. Uses defaults if None.

        Returns:
            Markdown-formatted table string.
        """
        if metrics is None:
            metrics = ["roc_auc", "pr_auc", "f1", "precision", "recall", "false_alarm_rate", "mean_lead_time"]

        header = "| Model | " + " | ".join(m.replace("_", " ").title() for m in metrics) + " |"
        separator = "|" + "|".join(["---"] * (len(metrics) + 1)) + "|"

        rows = [header, separator]
        for name, result in results.items():
            values = result.to_dict()
            row = f"| {name} | " + " | ".join(f"{values.get(m, 0):.4f}" for m in metrics) + " |"
            rows.append(row)

        return "\n".join(rows)

    @staticmethod
    def paired_bootstrap_test(
        y_true: np.ndarray,
        scores_a: np.ndarray,
        scores_b: np.ndarray,
        n_bootstrap: int = 1000,
        metric: str = "roc_auc",
    ) -> dict[str, float]:
        """Paired bootstrap test for comparing two models.

        Args:
            y_true: Ground truth labels.
            scores_a: Predictions from model A.
            scores_b: Predictions from model B.
            n_bootstrap: Number of bootstrap iterations.
            metric: Metric to compare.

        Returns:
            Dict with ``delta``, ``p_value``, ``ci_lower``, ``ci_upper``.
        """
        from sklearn.metrics import roc_auc_score

        n = len(y_true)
        rng = np.random.default_rng(42)
        deltas = []

        for _ in range(n_bootstrap):
            idx = rng.choice(n, n, replace=True)
            try:
                if len(np.unique(y_true[idx])) < 2:
                    continue
                score_a = roc_auc_score(y_true[idx], scores_a[idx])
                score_b = roc_auc_score(y_true[idx], scores_b[idx])
                deltas.append(score_a - score_b)
            except ValueError:
                continue

        if not deltas:
            return {"delta": 0.0, "p_value": 1.0, "ci_lower": 0.0, "ci_upper": 0.0}

        deltas = np.array(deltas)
        p_value = 2 * min(np.mean(deltas > 0), np.mean(deltas < 0))

        result = {
            "delta": float(np.mean(deltas)),
            "p_value": float(p_value),
            "ci_lower": float(np.percentile(deltas, 2.5)),
            "ci_upper": float(np.percentile(deltas, 97.5)),
        }

        logger.info(f"Bootstrap test: Δ={result['delta']:.4f}, p={result['p_value']:.4f}")
        return result
