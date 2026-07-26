"""Loss functions — BCE, focal, weighted, physics-constrained."""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F
from loguru import logger
from omegaconf import DictConfig


class FocalLoss(nn.Module):
    """Focal Loss for handling class imbalance in tipping detection.

    Reference:
        Lin, T. Y., et al. (2017). Focal Loss for Dense Object Detection. ICCV.
    """

    def __init__(self, alpha: float = 0.75, gamma: float = 2.0, label_smoothing: float = 0.0) -> None:
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.label_smoothing = label_smoothing

    def forward(self, inputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        if self.label_smoothing > 0:
            targets = targets * (1 - self.label_smoothing) + 0.5 * self.label_smoothing

        bce_loss = F.binary_cross_entropy(inputs, targets, reduction="none")
        p_t = inputs * targets + (1 - inputs) * (1 - targets)
        alpha_t = self.alpha * targets + (1 - self.alpha) * (1 - targets)
        focal_weight = alpha_t * (1 - p_t) ** self.gamma
        return (focal_weight * bce_loss).mean()


class WeightedBCELoss(nn.Module):
    """Weighted Binary Cross-Entropy with optional label smoothing."""

    def __init__(self, pos_weight: float = 2.0, label_smoothing: float = 0.0) -> None:
        super().__init__()
        self.pos_weight = torch.tensor([pos_weight])
        self.label_smoothing = label_smoothing

    def forward(self, inputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        if self.label_smoothing > 0:
            targets = targets * (1 - self.label_smoothing) + 0.5 * self.label_smoothing
        return F.binary_cross_entropy_with_logits(
            torch.logit(inputs.clamp(1e-7, 1 - 1e-7)),
            targets,
            pos_weight=self.pos_weight.to(inputs.device),
        )


def get_loss_function(cfg: DictConfig) -> nn.Module:
    """Factory for loss functions from config.

    Args:
        cfg: Loss config section.

    Returns:
        Loss module.
    """
    name = cfg.name
    if name == "focal":
        loss = FocalLoss(
            alpha=cfg.get("alpha", 0.75),
            gamma=cfg.get("gamma", 2.0),
            label_smoothing=cfg.get("label_smoothing", 0.0),
        )
    elif name == "bce":
        loss = nn.BCELoss()
    elif name == "weighted_bce":
        loss = WeightedBCELoss(
            pos_weight=cfg.get("alpha", 2.0),
            label_smoothing=cfg.get("label_smoothing", 0.0),
        )
    elif name == "mse":
        loss = nn.MSELoss()
    else:
        raise ValueError(f"Unknown loss: {name}")

    logger.info(f"Loss function: {name}")
    return loss
