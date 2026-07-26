"""Experiment management — reproducibility, config capture, tracking."""

from __future__ import annotations

import os
import random
from typing import Any

import numpy as np
import torch
from loguru import logger
from omegaconf import DictConfig, OmegaConf


class ExperimentManager:
    """Manage experiment reproducibility and tracking.

    Handles seed management, deterministic mode, config serialization,
    and integration with experiment tracking backends (W&B, MLflow).
    """

    def __init__(self, cfg: DictConfig) -> None:
        self.cfg = cfg
        self._tracker = None

    def setup(self) -> ExperimentManager:
        """Initialize reproducibility and tracking."""
        # Set seeds
        seed = self.cfg.project.seed
        self.set_seed(seed)

        # Deterministic mode
        if self.cfg.project.deterministic:
            torch.use_deterministic_algorithms(True, warn_only=True)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False

        # Setup tracking
        tracking_cfg = self.cfg.tracking
        if tracking_cfg.backend == "wandb":
            self._setup_wandb(tracking_cfg.wandb)
        elif tracking_cfg.backend == "mlflow":
            self._setup_mlflow(tracking_cfg.mlflow)

        logger.info(f"Experiment setup complete: seed={seed}, tracking={tracking_cfg.backend}")
        return self

    @staticmethod
    def set_seed(seed: int) -> None:
        """Set all random seeds for reproducibility."""
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        os.environ["PYTHONHASHSEED"] = str(seed)
        logger.debug(f"Set random seed: {seed}")

    def log_metrics(self, metrics: dict[str, float], step: int | None = None) -> None:
        """Log metrics to tracking backend."""
        if self._tracker is not None:
            try:
                if hasattr(self._tracker, "log"):
                    self._tracker.log(metrics, step=step)
            except Exception as e:
                logger.warning(f"Failed to log metrics: {e}")

    def log_config(self) -> None:
        """Log full config to tracking backend."""
        config_dict = OmegaConf.to_container(self.cfg, resolve=True)
        if self._tracker is not None:
            try:
                if hasattr(self._tracker, "config"):
                    self._tracker.config.update(config_dict)
            except Exception:
                pass

    def finish(self) -> None:
        """Finalize experiment tracking."""
        if self._tracker is not None:
            try:
                if hasattr(self._tracker, "finish"):
                    self._tracker.finish()
            except Exception:
                pass

    def _setup_wandb(self, cfg: DictConfig) -> None:
        try:
            import wandb
            self._tracker = wandb.init(
                project=cfg.project,
                entity=cfg.entity,
                tags=list(cfg.tags) if cfg.tags else [],
                notes=cfg.notes or "",
                config=OmegaConf.to_container(self.cfg, resolve=True),
            )
            logger.info(f"W&B initialized: {cfg.project}")
        except ImportError:
            logger.warning("wandb not installed, skipping W&B tracking")

    def _setup_mlflow(self, cfg: DictConfig) -> None:
        try:
            import mlflow
            mlflow.set_tracking_uri(cfg.tracking_uri)
            mlflow.set_experiment(cfg.experiment_name)
            mlflow.start_run()
            mlflow.log_params(OmegaConf.to_container(self.cfg, resolve=True))
            self._tracker = mlflow
            logger.info(f"MLflow initialized: {cfg.experiment_name}")
        except ImportError:
            logger.warning("mlflow not installed, skipping MLflow tracking")
