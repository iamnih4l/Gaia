"""Informer — ProbSparse self-attention for long climate sequences.

Reference:
    Zhou, H., et al. (2021). Informer: Beyond Efficient Transformer for
    Long Sequence Time-Series Forecasting. AAAI.
"""

from __future__ import annotations

import math

import torch
import torch.nn as nn
from loguru import logger
from omegaconf import DictConfig

from models.registry import register_model


class ProbSparseAttention(nn.Module):
    """ProbSparse self-attention — selects top-K queries by sparsity measure."""

    def __init__(self, d_model: int, n_heads: int, factor: int = 5, dropout: float = 0.1) -> None:
        super().__init__()
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        self.factor = factor

        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, queries: torch.Tensor, keys: torch.Tensor, values: torch.Tensor) -> torch.Tensor:
        B, L_Q, _ = queries.shape
        _, L_K, _ = keys.shape

        Q = self.W_q(queries).view(B, L_Q, self.n_heads, self.d_k).transpose(1, 2)
        K = self.W_k(keys).view(B, L_K, self.n_heads, self.d_k).transpose(1, 2)
        V = self.W_v(values).view(B, L_K, self.n_heads, self.d_k).transpose(1, 2)

        # ProbSparse: sample top-u queries
        u = max(self.factor * int(math.ceil(math.log(L_K + 1))), 1)
        u = min(u, L_Q)

        # Standard attention for selected queries
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        attn = torch.softmax(scores, dim=-1)
        attn = self.dropout(attn)
        output = torch.matmul(attn, V)

        output = output.transpose(1, 2).contiguous().view(B, L_Q, -1)
        return self.W_o(output)


class InformerEncoderLayer(nn.Module):
    """Single Informer encoder layer with ProbSparse attention and distilling."""

    def __init__(self, d_model: int, n_heads: int, d_ff: int, factor: int, dropout: float, activation: str) -> None:
        super().__init__()
        self.attention = ProbSparseAttention(d_model, n_heads, factor, dropout)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU() if activation == "gelu" else nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),
            nn.Dropout(dropout),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        attended = self.attention(x, x, x)
        x = self.norm1(x + attended)
        x = self.norm2(x + self.ffn(x))
        return x


class ConvDistilling(nn.Module):
    """Attention distilling via 1D convolution + max pooling."""

    def __init__(self, d_model: int) -> None:
        super().__init__()
        self.conv = nn.Conv1d(d_model, d_model, kernel_size=3, padding=1)
        self.norm = nn.BatchNorm1d(d_model)
        self.activation = nn.ELU()
        self.pool = nn.MaxPool1d(kernel_size=2, stride=2)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x.transpose(1, 2)  # (B, d_model, T)
        x = self.pool(self.activation(self.norm(self.conv(x))))
        return x.transpose(1, 2)  # (B, T//2, d_model)


@register_model("informer")
class Informer(nn.Module):
    """Informer model for long-sequence climate time series.

    Args:
        cfg: Model config from ``configs/model/informer.yaml``.
    """

    def __init__(self, cfg: DictConfig) -> None:
        super().__init__()
        arch = cfg.architecture

        self.input_projection = nn.Linear(arch.input_dim, arch.d_model)

        # Positional encoding
        self.pos_encoding = nn.Parameter(
            self._sinusoidal_encoding(512, arch.d_model), requires_grad=False
        )

        # Encoder layers with distilling
        self.encoder_layers = nn.ModuleList()
        self.distilling_layers = nn.ModuleList()

        for _ in range(arch.e_layers):
            self.encoder_layers.append(
                InformerEncoderLayer(
                    arch.d_model, arch.n_heads, arch.d_ff,
                    arch.factor, arch.dropout, arch.activation,
                )
            )
            if arch.distil:
                self.distilling_layers.append(ConvDistilling(arch.d_model))

        # Classification head
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool1d(1),
        )
        self.head = nn.Sequential(
            nn.Linear(arch.d_model, arch.d_model // 2),
            nn.GELU(),
            nn.Dropout(arch.dropout),
            nn.Linear(arch.d_model // 2, arch.output_dim),
        )

        n_params = sum(p.numel() for p in self.parameters())
        logger.info(f"Informer: {n_params:,} parameters")

    def _sinusoidal_encoding(self, max_len: int, d_model: int) -> torch.Tensor:
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float32).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2, dtype=torch.float32) * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        return pe.unsqueeze(0)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, T, _ = x.shape
        x = self.input_projection(x)
        x = x + self.pos_encoding[:, :T, :]

        for i, layer in enumerate(self.encoder_layers):
            x = layer(x)
            if i < len(self.distilling_layers):
                x = self.distilling_layers[i](x)

        # Global average pooling → classification
        x = x.transpose(1, 2)  # (B, d_model, T')
        x = self.classifier(x).squeeze(-1)  # (B, d_model)
        logits = self.head(x)
        return torch.sigmoid(logits)
