"""Optimizer and scheduler factories."""

from __future__ import annotations

import torch.nn as nn
import torch.optim as optim
from loguru import logger
from omegaconf import DictConfig


def get_optimizer(model: nn.Module, cfg: DictConfig) -> optim.Optimizer:
    """Create optimizer from config.

    Args:
        model: Model whose parameters to optimize.
        cfg: Optimizer config section.

    Returns:
        PyTorch optimizer.
    """
    name = cfg.name.lower()
    params = filter(lambda p: p.requires_grad, model.parameters())

    if name == "adam":
        optimizer = optim.Adam(params, lr=cfg.lr, betas=tuple(cfg.betas),
                               eps=cfg.eps, weight_decay=cfg.weight_decay)
    elif name == "adamw":
        optimizer = optim.AdamW(params, lr=cfg.lr, betas=tuple(cfg.betas),
                                eps=cfg.eps, weight_decay=cfg.weight_decay)
    elif name == "sgd":
        optimizer = optim.SGD(params, lr=cfg.lr, momentum=0.9,
                              weight_decay=cfg.weight_decay)
    else:
        raise ValueError(f"Unknown optimizer: {name}")

    logger.info(f"Optimizer: {name}, lr={cfg.lr}")
    return optimizer


def get_scheduler(
    optimizer: optim.Optimizer,
    cfg: DictConfig,
) -> optim.lr_scheduler.LRScheduler | None:
    """Create LR scheduler from config.

    Args:
        optimizer: Optimizer to schedule.
        cfg: Scheduler config section.

    Returns:
        LR scheduler or None.
    """
    name = cfg.name.lower()

    if name == "cosine_annealing":
        scheduler = optim.lr_scheduler.CosineAnnealingLR(
            optimizer, T_max=cfg.get("T_max", 100), eta_min=cfg.eta_min,
        )
    elif name == "cosine_annealing_warm_restarts":
        scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
            optimizer, T_0=cfg.T_0, T_mult=cfg.T_mult, eta_min=cfg.eta_min,
        )
    elif name == "step":
        scheduler = optim.lr_scheduler.StepLR(
            optimizer, step_size=cfg.get("step_size", 30), gamma=cfg.get("gamma", 0.1),
        )
    elif name == "one_cycle":
        scheduler = optim.lr_scheduler.OneCycleLR(
            optimizer, max_lr=cfg.get("max_lr", 1e-3),
            total_steps=cfg.get("total_steps", 1000),
        )
    elif name == "none":
        return None
    else:
        raise ValueError(f"Unknown scheduler: {name}")

    logger.info(f"LR Scheduler: {name}")
    return scheduler
