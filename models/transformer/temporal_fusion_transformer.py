"""Temporal Fusion Transformer (TFT) for climate tipping point prediction.

Implements variable selection, gated residual networks, and interpretable
multi-head attention for time series classification.

Reference:
    Lim, B., et al. (2021). Temporal Fusion Transformers for Interpretable
    Multi-horizon Time Series Forecasting. International Journal of Forecasting.
"""

from __future__ import annotations

import torch
import torch.nn as nn
from loguru import logger
from omegaconf import DictConfig

from models.registry import register_model


class GatedResidualNetwork(nn.Module):
    """Gated Residual Network (GRN) — core building block of TFT."""

    def __init__(
        self, input_dim: int, hidden_dim: int, output_dim: int, dropout: float = 0.1,
        context_dim: int | None = None,
    ) -> None:
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.elu = nn.ELU()
        self.fc2 = nn.Linear(hidden_dim, output_dim)
        self.dropout = nn.Dropout(dropout)
        self.gate = nn.Linear(output_dim, output_dim)
        self.layer_norm = nn.LayerNorm(output_dim)
        self.skip = nn.Linear(input_dim, output_dim) if input_dim != output_dim else nn.Identity()

        self.context_projection = None
        if context_dim is not None:
            self.context_projection = nn.Linear(context_dim, hidden_dim, bias=False)

    def forward(self, x: torch.Tensor, context: torch.Tensor | None = None) -> torch.Tensor:
        residual = self.skip(x)
        hidden = self.fc1(x)
        if self.context_projection is not None and context is not None:
            hidden = hidden + self.context_projection(context)
        hidden = self.elu(hidden)
        hidden = self.fc2(hidden)
        hidden = self.dropout(hidden)
        gating = torch.sigmoid(self.gate(hidden))
        output = self.layer_norm(gating * hidden + residual)
        return output


class VariableSelectionNetwork(nn.Module):
    """Variable Selection Network — learns feature importance weights."""

    def __init__(self, input_dim: int, n_features: int, hidden_dim: int, dropout: float = 0.1) -> None:
        super().__init__()
        self.n_features = n_features
        self.feature_dim = input_dim // n_features

        self.grns = nn.ModuleList([
            GatedResidualNetwork(self.feature_dim, hidden_dim, hidden_dim, dropout)
            for _ in range(n_features)
        ])
        self.softmax_grn = GatedResidualNetwork(input_dim, hidden_dim, n_features, dropout)
        self.softmax = nn.Softmax(dim=-1)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        # Split into individual features
        feature_list = torch.chunk(x, self.n_features, dim=-1)

        # Process each feature through its own GRN
        processed = [grn(feat) for grn, feat in zip(self.grns, feature_list)]
        processed = torch.stack(processed, dim=-2)  # (B, T, n_features, hidden)

        # Compute selection weights
        weights = self.softmax(self.softmax_grn(x))  # (B, T, n_features)
        weights = weights.unsqueeze(-1)  # (B, T, n_features, 1)

        # Weighted combination
        selected = (processed * weights).sum(dim=-2)  # (B, T, hidden)

        return selected, weights.squeeze(-1)


@register_model("temporal_fusion_transformer")
class TemporalFusionTransformer(nn.Module):
    """Temporal Fusion Transformer for interpretable tipping prediction.

    Args:
        cfg: Model config from ``configs/model/tft.yaml``.
    """

    def __init__(self, cfg: DictConfig) -> None:
        super().__init__()
        arch = cfg.architecture

        self.input_dim = arch.input_dim
        self.hidden_dim = arch.hidden_dim
        self.n_heads = arch.n_heads
        self.dropout = arch.dropout

        # Variable selection
        self.var_selection = VariableSelectionNetwork(
            input_dim=arch.input_dim,
            n_features=arch.input_dim,  # Each input channel is a feature
            hidden_dim=arch.hidden_dim,
            dropout=arch.dropout,
        )

        # LSTM encoder for local temporal patterns
        self.lstm_encoder = nn.LSTM(
            input_size=arch.hidden_dim,
            hidden_size=arch.hidden_dim,
            num_layers=arch.n_layers,
            batch_first=True,
            dropout=arch.dropout if arch.n_layers > 1 else 0.0,
        )

        # Gated skip connection after LSTM
        self.post_lstm_grn = GatedResidualNetwork(
            arch.hidden_dim, arch.hidden_dim, arch.hidden_dim, arch.dropout
        )

        # Multi-head attention for long-range dependencies
        self.multihead_attn = nn.MultiheadAttention(
            embed_dim=arch.hidden_dim,
            num_heads=arch.n_heads,
            dropout=arch.dropout,
            batch_first=True,
        )
        self.attn_layer_norm = nn.LayerNorm(arch.hidden_dim)

        # Output GRN
        self.output_grn = GatedResidualNetwork(
            arch.hidden_dim, arch.hidden_dim, arch.hidden_dim, arch.dropout
        )

        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(arch.hidden_dim, arch.hidden_dim // 2),
            nn.GELU(),
            nn.Dropout(arch.dropout),
            nn.Linear(arch.hidden_dim // 2, arch.output_dim),
        )

        n_params = sum(p.numel() for p in self.parameters())
        logger.info(f"TemporalFusionTransformer: {n_params:,} parameters")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass.

        Args:
            x: Input of shape ``(B, T, input_dim)``.

        Returns:
            Tipping probability of shape ``(B, 1)``.
        """
        # Variable selection
        selected, var_weights = self.var_selection(x)  # (B, T, hidden)

        # LSTM encoding
        lstm_out, _ = self.lstm_encoder(selected)

        # Gated skip connection
        temporal = self.post_lstm_grn(lstm_out)

        # Self-attention for long-range
        attn_out, attn_weights = self.multihead_attn(temporal, temporal, temporal)
        temporal = self.attn_layer_norm(temporal + attn_out)

        # Output GRN
        output = self.output_grn(temporal)

        # Pool and classify
        pooled = output.mean(dim=1)
        logits = self.classifier(pooled)
        return torch.sigmoid(logits)
