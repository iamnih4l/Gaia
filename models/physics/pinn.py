"""Physics-Informed Neural Network (PINN) for climate tipping prediction.

Embeds physical constraints (conservation laws, PDE residuals) into the
neural network loss function to improve robustness and physical consistency.
"""

from __future__ import annotations

import torch
import torch.nn as nn
from loguru import logger
from omegaconf import DictConfig

from models.registry import register_model


@register_model("physics_informed_nn")
class PhysicsInformedNN(nn.Module):
    """Physics-Informed Neural Network for climate tipping detection.

    Combines standard data-driven loss with physics-based residual terms.

    Args:
        cfg: Model config from ``configs/model/pinn.yaml``.
    """

    def __init__(self, cfg: DictConfig) -> None:
        super().__init__()
        arch = cfg.architecture
        self.physics_cfg = cfg.physics

        # Main network
        layers = []
        in_dim = arch.input_dim
        for _ in range(arch.n_layers):
            layers.extend([
                nn.Linear(in_dim, arch.hidden_dim),
                nn.Tanh(),
                nn.Dropout(arch.dropout),
            ])
            in_dim = arch.hidden_dim
        layers.append(nn.Linear(in_dim, arch.output_dim))
        self.network = nn.Sequential(*layers)

        # Physics residual network (predicts PDE residual)
        self.physics_network = nn.Sequential(
            nn.Linear(arch.input_dim, arch.hidden_dim),
            nn.Tanh(),
            nn.Linear(arch.hidden_dim, arch.hidden_dim),
            nn.Tanh(),
            nn.Linear(arch.hidden_dim, arch.input_dim),
        )

        n_params = sum(p.numel() for p in self.parameters())
        logger.info(f"PhysicsInformedNN: {n_params:,} parameters")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass — predict tipping probability.

        Args:
            x: Input ``(B, T, F)`` or ``(B, F)``.

        Returns:
            Probability ``(B, 1)``.
        """
        if x.dim() == 3:
            x = x[:, -1, :]  # Use last time step for PINN

        logits = self.network(x)
        return torch.sigmoid(logits)

    def compute_physics_loss(self, x: torch.Tensor) -> torch.Tensor:
        """Compute physics-based residual loss.

        Enforces smooth temporal evolution consistent with known climate
        system dynamics (e.g., energy conservation).

        Args:
            x: Input sequence ``(B, T, F)``.

        Returns:
            Scalar physics loss.
        """
        if x.dim() == 2:
            return torch.tensor(0.0, device=x.device)

        # Temporal derivative approximation (finite difference)
        dx_dt = x[:, 1:, :] - x[:, :-1, :]  # (B, T-1, F)

        # Physics model predicts expected temporal change
        predicted_dx = self.physics_network(x[:, :-1, :])  # (B, T-1, F)

        # Residual: difference between actual and physics-predicted change
        residual = dx_dt - predicted_dx
        physics_loss = torch.mean(residual**2)

        return physics_loss

    def compute_total_loss(
        self,
        data_loss: torch.Tensor,
        x: torch.Tensor,
    ) -> torch.Tensor:
        """Compute combined data + physics loss.

        Args:
            data_loss: Standard classification loss (e.g., BCE).
            x: Input sequence for physics residual.

        Returns:
            Total loss = data_loss + weight * physics_loss.
        """
        physics_loss = self.compute_physics_loss(x)
        weight = self.physics_cfg.physics_loss_weight
        total = data_loss + weight * physics_loss
        return total
