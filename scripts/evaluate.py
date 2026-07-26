"""CLI script for model evaluation, benchmark metrics, and publication plotting."""

from __future__ import annotations

from pathlib import Path
import hydra
import numpy as np
import torch
from loguru import logger
from omegaconf import DictConfig
from torch.utils.data import DataLoader

from datasets.base import ClimateTimeSeriesDataset
from evaluation.metrics import TippingPointMetrics
from evaluation.comparison import ModelComparison
from models.registry import ModelRegistry
from visualization.metrics_plots import MetricsPlotter
from visualization.time_series import TimeSeriesPlotter


@hydra.main(version_base="1.3", config_path="../configs", config_name="config")
def main(cfg: DictConfig) -> None:
    """Evaluation CLI entrypoint."""
    logger.info("Starting Gaia Model Evaluation...")

    # Generate synthetic test set for evaluation demonstration
    n_steps = 200
    n_features = cfg.model.architecture.input_dim
    seq_len = cfg.model.architecture.get("max_seq_len", 24)
    
    rng = np.random.default_rng(42)
    test_features = rng.standard_normal((n_steps, n_features)).astype(np.float32)
    test_labels = np.zeros(n_steps, dtype=np.float32)
    test_labels[-40:] = 1.0  # Tipping event in last 20%

    test_ds = ClimateTimeSeriesDataset(test_features, test_labels, seq_len=seq_len)
    test_loader = DataLoader(test_ds, batch_size=32, shuffle=False)

    # Instantiate model and evaluate
    model = ModelRegistry.create(cfg.model)
    model.eval()

    all_prob = []
    all_targets = []

    with torch.no_grad():
        for batch in test_loader:
            inputs = batch["input"]
            labels = batch["label"]
            probs = model(inputs).squeeze(-1)
            all_prob.append(probs.numpy())
            all_targets.append(labels.numpy())

    y_prob = np.concatenate(all_prob)
    y_true = np.concatenate(all_targets)

    # Compute comprehensive evaluation metrics
    metrics = TippingPointMetrics.compute_all(y_true, y_prob, threshold=0.5, event_indices=[160])
    logger.info(f"\nEvaluation Results:\n{metrics.to_dict()}")

    # Generate output directory for figures
    output_dir = Path(cfg.paths.output_dir) / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Plot ROC Curve
    if metrics.roc_curve:
        MetricsPlotter.plot_roc_curve(
            metrics.roc_curve["fpr"], metrics.roc_curve["tpr"], metrics.roc_auc,
            save_path=output_dir / "roc_curve.png"
        )

    # Plot Prediction Overlay
    time_axis = np.arange(len(y_prob))
    TimeSeriesPlotter.plot_prediction_overlay(
        time=time_axis, observed=test_features[-len(y_prob):, 0], predicted_prob=y_prob,
        event_indices=[160], threshold=0.5, save_path=output_dir / "tipping_prediction_overlay.png"
    )

    logger.info(f"Evaluation figures saved to {output_dir}")


if __name__ == "__main__":
    main()
