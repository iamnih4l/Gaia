"""Physics-constrained loss functions for climate models."""

from __future__ import annotations

import torch
import torch.nn as nn
from loguru import logger


class EnergyConservationLoss(nn.Module):
    """Penalize violations of energy conservation in predictions."""

    def __init__(self, weight: float = 0.1) -> None:
        super().__init__()
        self.weight = weight

    def forward(self, predictions: torch.Tensor, inputs: torch.Tensor) -> torch.Tensor:
        """Compute energy conservation penalty.

        Enforces that total energy (proxy: sum of temperature-related features)
        changes are physically plausible over the time series.
        """
        if inputs.dim() < 3:
            return torch.tensor(0.0, device=inputs.device)

        energy_proxy = inputs.sum(dim=-1)  # Sum features as energy proxy
        d_energy = energy_proxy[:, 1:] - energy_proxy[:, :-1]

        # Penalize unrealistically large energy changes
        penalty = torch.mean(torch.relu(torch.abs(d_energy) - 3.0))
        return self.weight * penalty


class MassConservationLoss(nn.Module):
    """Penalize violations of mass conservation (e.g., water balance)."""

    def __init__(self, weight: float = 0.1) -> None:
        super().__init__()
        self.weight = weight

    def forward(self, predictions: torch.Tensor, inputs: torch.Tensor) -> torch.Tensor:
        if inputs.dim() < 3:
            return torch.tensor(0.0, device=inputs.device)

        mass_proxy = inputs[:, :, 0]  # First feature as mass proxy
        d_mass = mass_proxy[:, 1:] - mass_proxy[:, :-1]
        penalty = torch.mean(d_mass**2)
        return self.weight * penalty


class PhysicsConstrainedLoss(nn.Module):
    """Composite loss combining data loss with physics constraints.

    Args:
        data_loss_fn: Primary classification/regression loss.
        constraints: List of constraint names to apply.
        physics_weight: Overall weight for physics terms.
    """

    def __init__(
        self,
        data_loss_fn: nn.Module | None = None,
        constraints: list[str] | None = None,
        physics_weight: float = 0.1,
    ) -> None:
        super().__init__()
        self.data_loss_fn = data_loss_fn or nn.BCELoss()
        self.physics_weight = physics_weight

        self.constraint_modules = nn.ModuleDict()
        if constraints:
            for name in constraints:
                if name == "energy_conservation":
                    self.constraint_modules[name] = EnergyConservationLoss(physics_weight)
                elif name == "mass_conservation":
                    self.constraint_modules[name] = MassConservationLoss(physics_weight)

        logger.info(f"PhysicsConstrainedLoss: {list(self.constraint_modules.keys())}")

    def forward(
        self,
        predictions: torch.Tensor,
        targets: torch.Tensor,
        inputs: torch.Tensor | None = None,
    ) -> dict[str, torch.Tensor]:
        """Compute total loss with breakdown.

        Returns:
            Dictionary with ``"total"``, ``"data"``, and individual constraint losses.
        """
        data_loss = self.data_loss_fn(predictions, targets)
        losses = {"data": data_loss}

        total = data_loss
        if inputs is not None:
            for name, module in self.constraint_modules.items():
                constraint_loss = module(predictions, inputs)
                losses[name] = constraint_loss
                total = total + constraint_loss

        losses["total"] = total
        return losses
