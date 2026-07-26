"""Foundation Model Adapter — interface for integrating pretrained climate models.

Provides an abstract adapter interface for plugging in pretrained foundation
models (e.g., Aurora, ClimaX, Pangu-Weather) and fine-tuning them for
tipping point detection. The adapter handles:

1. Loading pretrained weights
2. Freezing/unfreezing backbone layers
3. Adding task-specific classification heads
4. Feature extraction mode for transfer learning
"""

from __future__ import annotations

import abc
from typing import Any

import torch
import torch.nn as nn
from loguru import logger


class FoundationModelAdapter(abc.ABC, nn.Module):
    """Abstract adapter for pretrained climate foundation models.

    Subclass this to integrate a specific foundation model (Aurora, ClimaX, etc.).
    The adapter wraps the pretrained backbone and adds a classification head
    for tipping point detection.
    """

    def __init__(self, backbone_name: str, pretrained_path: str | None = None) -> None:
        super().__init__()
        self.backbone_name = backbone_name
        self.pretrained_path = pretrained_path
        self._backbone: nn.Module | None = None
        self._head: nn.Module | None = None
        self._feature_dim: int = 0

    @abc.abstractmethod
    def load_backbone(self) -> nn.Module:
        """Load the pretrained backbone model.

        Returns:
            The backbone ``nn.Module`` (frozen or unfrozen).
        """

    @abc.abstractmethod
    def get_feature_dim(self) -> int:
        """Return the output feature dimension of the backbone."""

    def build_head(self, output_dim: int = 1, hidden_dim: int = 256) -> None:
        """Build a classification head on top of the backbone.

        Args:
            output_dim: Number of output classes (1 for binary).
            hidden_dim: Hidden layer dimension.
        """
        feature_dim = self.get_feature_dim()
        self._head = nn.Sequential(
            nn.Linear(feature_dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim // 2, output_dim),
        )
        logger.info(f"Built classification head: {feature_dim} → {hidden_dim} → {output_dim}")

    def freeze_backbone(self) -> None:
        """Freeze all backbone parameters for feature extraction."""
        if self._backbone is not None:
            for param in self._backbone.parameters():
                param.requires_grad = False
            logger.info(f"Frozen backbone: {self.backbone_name}")

    def unfreeze_backbone(self, n_layers: int | None = None) -> None:
        """Unfreeze backbone parameters for fine-tuning.

        Args:
            n_layers: Number of final layers to unfreeze. Unfreezes all if None.
        """
        if self._backbone is None:
            return

        if n_layers is None:
            for param in self._backbone.parameters():
                param.requires_grad = True
            logger.info(f"Unfrozen entire backbone: {self.backbone_name}")
        else:
            params = list(self._backbone.parameters())
            for param in params[-n_layers:]:
                param.requires_grad = True
            logger.info(f"Unfrozen last {n_layers} layers of {self.backbone_name}")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass: backbone → pooling → head → sigmoid.

        Args:
            x: Input tensor (format depends on backbone).

        Returns:
            Tipping probability ``(B, 1)``.
        """
        features = self._backbone(x)

        # Pool if needed (handle spatial outputs)
        if features.dim() > 2:
            features = features.mean(dim=list(range(1, features.dim() - 1)))

        if self._head is not None:
            logits = self._head(features)
            return torch.sigmoid(logits)
        return features

    def get_config(self) -> dict[str, Any]:
        """Return adapter configuration for logging."""
        return {
            "backbone": self.backbone_name,
            "pretrained_path": self.pretrained_path,
            "feature_dim": self._feature_dim,
            "head_params": sum(p.numel() for p in self._head.parameters()) if self._head else 0,
            "backbone_frozen": not any(
                p.requires_grad for p in self._backbone.parameters()
            ) if self._backbone else True,
        }


class PlaceholderFoundationModel(FoundationModelAdapter):
    """Placeholder adapter — demonstrates the interface for future integration.

    Replace this with a concrete adapter (e.g., ``AuroraAdapter``) once
    pretrained weights become available.
    """

    def __init__(self, input_dim: int = 7, feature_dim: int = 512, **kwargs) -> None:
        super().__init__(backbone_name="placeholder", **kwargs)
        self._feature_dim = feature_dim
        self._backbone = nn.Sequential(
            nn.Linear(input_dim, feature_dim),
            nn.GELU(),
            nn.Linear(feature_dim, feature_dim),
            nn.GELU(),
        )
        self.build_head(output_dim=1, hidden_dim=256)
        logger.info("Initialized PlaceholderFoundationModel (replace with real model)")

    def load_backbone(self) -> nn.Module:
        return self._backbone

    def get_feature_dim(self) -> int:
        return self._feature_dim
