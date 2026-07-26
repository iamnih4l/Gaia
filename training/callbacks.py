"""Training callbacks — early stopping, checkpointing, logging."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch
import torch.nn as nn
from loguru import logger


class EarlyStopping:
    """Stop training when a monitored metric stops improving."""

    def __init__(
        self, monitor: str = "val/loss", patience: int = 10,
        mode: str = "min", min_delta: float = 0.0,
    ) -> None:
        self.monitor = monitor
        self.patience = patience
        self.mode = mode
        self.min_delta = min_delta
        self.counter = 0
        self.best_value = float("inf") if mode == "min" else float("-inf")
        self.should_stop = False

    def __call__(self, metrics: dict[str, float]) -> bool:
        value = metrics.get(self.monitor)
        if value is None:
            return False

        improved = (
            (self.mode == "min" and value < self.best_value - self.min_delta) or
            (self.mode == "max" and value > self.best_value + self.min_delta)
        )

        if improved:
            self.best_value = value
            self.counter = 0
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.should_stop = True
                return True
        return False


class ModelCheckpoint:
    """Save model checkpoints based on monitored metric."""

    def __init__(
        self, dirpath: str | Path = "checkpoints", monitor: str = "val/roc_auc",
        mode: str = "max", save_top_k: int = 3,
    ) -> None:
        self.dirpath = Path(dirpath)
        self.dirpath.mkdir(parents=True, exist_ok=True)
        self.monitor = monitor
        self.mode = mode
        self.save_top_k = save_top_k
        self.best_models: list[tuple[float, Path]] = []

    def __call__(self, epoch: int, metrics: dict[str, float], model: nn.Module) -> None:
        value = metrics.get(self.monitor)
        if value is None:
            return

        path = self.dirpath / f"epoch_{epoch:03d}_{self.monitor.replace('/', '_')}_{value:.4f}.pt"
        torch.save(model.state_dict(), path)
        self.best_models.append((value, path))

        # Sort and keep top-k
        reverse = self.mode == "max"
        self.best_models.sort(key=lambda x: x[0], reverse=reverse)

        while len(self.best_models) > self.save_top_k:
            _, old_path = self.best_models.pop()
            if old_path.exists():
                old_path.unlink()


class CallbackList:
    """Container for managing multiple callbacks."""

    def __init__(self, callbacks: list | None = None) -> None:
        self._callbacks: list = callbacks or []

    def add(self, callback: Any) -> None:
        self._callbacks.append(callback)

    def on_train_begin(self) -> None:
        pass

    def on_train_end(self) -> None:
        pass

    def on_epoch_end(self, epoch: int, metrics: dict[str, float], model: nn.Module) -> bool:
        should_stop = False
        for cb in self._callbacks:
            if isinstance(cb, EarlyStopping):
                if cb(metrics):
                    should_stop = True
            elif isinstance(cb, ModelCheckpoint):
                cb(epoch, metrics, model)
        return should_stop
