"""Time Series Transformer — multi-head self-attention for climate sequences.

Implements a standard encoder-only Transformer with positional encoding
for binary classification of tipping point risk from climate time series.
"""

from __future__ import annotations

import math

import torch
import torch.nn as nn
from loguru import logger
from omegaconf import DictConfig

from models.registry import register_model


class PositionalEncoding(nn.Module):
    """Sinusoidal positional encoding for transformer inputs."""

    def __init__(self, d_model: int, max_len: int = 5000, dropout: float = 0.1) -> None:
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)

        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float32).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, d_model, 2, dtype=torch.float32) * (-math.log(10000.0) / d_model)
        )
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)  # (1, max_len, d_model)
        self.register_buffer("pe", pe)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.pe[:, : x.size(1)]
        return self.dropout(x)


@register_model("time_series_transformer")
class TimeSeriesTransformer(nn.Module):
    """Encoder-only Transformer for climate time series classification.

    Architecture:
        Input projection → Positional encoding → N × TransformerEncoder →
        Pooling → Classification head → Sigmoid

    Args:
        cfg: Model config from ``configs/model/transformer.yaml``.
    """

    def __init__(self, cfg: DictConfig) -> None:
        super().__init__()
        arch = cfg.architecture
        self.pool_strategy = arch.pool_strategy

        # Input projection
        self.input_projection = nn.Linear(arch.input_dim, arch.d_model)

        # CLS token for classification (if using cls pooling)
        if self.pool_strategy == "cls":
            self.cls_token = nn.Parameter(torch.randn(1, 1, arch.d_model))

        # Positional encoding
        self.pos_encoding = PositionalEncoding(
            d_model=arch.d_model,
            max_len=arch.max_seq_len,
            dropout=arch.dropout,
        )

        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=arch.d_model,
            nhead=arch.n_heads,
            dim_feedforward=arch.d_ff,
            dropout=arch.dropout,
            activation=arch.activation,
            batch_first=True,
            norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(
            encoder_layer,
            num_layers=arch.n_encoder_layers,
            norm=nn.LayerNorm(arch.d_model),
        )

        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(arch.d_model, arch.d_model // 2),
            nn.GELU(),
            nn.Dropout(arch.dropout),
            nn.Linear(arch.d_model // 2, arch.output_dim),
        )

        self._init_weights()
        n_params = sum(p.numel() for p in self.parameters())
        logger.info(f"TimeSeriesTransformer: {n_params:,} parameters")

    def _init_weights(self) -> None:
        """Xavier uniform initialization."""
        for p in self.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)

    def forward(
        self,
        x: torch.Tensor,
        mask: torch.Tensor | None = None,
    ) -> torch.Tensor:
        """Forward pass.

        Args:
            x: Input tensor of shape ``(B, T, input_dim)``.
            mask: Optional attention mask of shape ``(B, T)``.

        Returns:
            Tipping probability of shape ``(B, 1)``.
        """
        # Project input to d_model
        x = self.input_projection(x)  # (B, T, d_model)

        # Prepend CLS token if needed
        if self.pool_strategy == "cls":
            batch_size = x.size(0)
            cls_tokens = self.cls_token.expand(batch_size, -1, -1)
            x = torch.cat([cls_tokens, x], dim=1)  # (B, T+1, d_model)

        # Add positional encoding
        x = self.pos_encoding(x)

        # Create attention mask if provided
        src_key_padding_mask = None
        if mask is not None and self.pool_strategy == "cls":
            # Prepend False for CLS token
            cls_mask = torch.zeros(mask.size(0), 1, dtype=torch.bool, device=mask.device)
            src_key_padding_mask = torch.cat([cls_mask, mask], dim=1)
        elif mask is not None:
            src_key_padding_mask = mask

        # Encoder
        encoded = self.encoder(x, src_key_padding_mask=src_key_padding_mask)

        # Pool
        if self.pool_strategy == "cls":
            pooled = encoded[:, 0]  # CLS token output
        elif self.pool_strategy == "mean":
            pooled = encoded.mean(dim=1)
        elif self.pool_strategy == "max":
            pooled = encoded.max(dim=1).values
        else:
            pooled = encoded[:, -1]  # Last token

        # Classify
        logits = self.classifier(pooled)
        return torch.sigmoid(logits)

    def get_attention_weights(self, x: torch.Tensor) -> list[torch.Tensor]:
        """Extract attention weights from all encoder layers.

        Useful for interpretability and attention map visualization.

        Args:
            x: Input tensor of shape ``(B, T, input_dim)``.

        Returns:
            List of attention weight tensors, one per layer.
        """
        x = self.input_projection(x)
        if self.pool_strategy == "cls":
            batch_size = x.size(0)
            cls_tokens = self.cls_token.expand(batch_size, -1, -1)
            x = torch.cat([cls_tokens, x], dim=1)
        x = self.pos_encoding(x)

        attention_weights = []
        for layer in self.encoder.layers:
            # Access multi-head attention
            attn_output, attn_weight = layer.self_attn(
                x, x, x, need_weights=True, average_attn_weights=False
            )
            attention_weights.append(attn_weight.detach())
            # Continue forward pass through the rest of the layer
            x = layer(x)

        return attention_weights
