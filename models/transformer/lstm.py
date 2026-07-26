"""LSTM with attention for climate time series classification."""

from __future__ import annotations

import torch
import torch.nn as nn
from loguru import logger
from omegaconf import DictConfig

from models.registry import register_model


class TemporalAttention(nn.Module):
    """Additive attention over LSTM hidden states."""

    def __init__(self, hidden_dim: int, attention_dim: int) -> None:
        super().__init__()
        self.W = nn.Linear(hidden_dim, attention_dim, bias=False)
        self.v = nn.Linear(attention_dim, 1, bias=False)

    def forward(self, hidden_states: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        energy = torch.tanh(self.W(hidden_states))  # (B, T, attn_dim)
        scores = self.v(energy).squeeze(-1)  # (B, T)
        weights = torch.softmax(scores, dim=-1)  # (B, T)
        context = torch.bmm(weights.unsqueeze(1), hidden_states).squeeze(1)  # (B, hidden)
        return context, weights


@register_model("lstm")
class LSTMModel(nn.Module):
    """Stacked LSTM with optional attention for tipping point detection.

    Args:
        cfg: Model config from ``configs/model/lstm.yaml``.
    """

    def __init__(self, cfg: DictConfig) -> None:
        super().__init__()
        arch = cfg.architecture

        self.lstm = nn.LSTM(
            input_size=arch.input_dim,
            hidden_size=arch.hidden_dim,
            num_layers=arch.n_layers,
            batch_first=True,
            dropout=arch.dropout if arch.n_layers > 1 else 0.0,
            bidirectional=arch.bidirectional,
        )

        lstm_output_dim = arch.hidden_dim * (2 if arch.bidirectional else 1)
        self.use_attention = arch.attention
        self.pool_strategy = arch.pool_strategy

        if self.use_attention:
            self.attention = TemporalAttention(lstm_output_dim, arch.attention_dim)

        self.mc_dropout = nn.Dropout(cfg.uncertainty.dropout_rate)

        self.classifier = nn.Sequential(
            nn.Linear(lstm_output_dim, lstm_output_dim // 2),
            nn.GELU(),
            nn.Dropout(arch.dropout),
            nn.Linear(lstm_output_dim // 2, arch.output_dim),
        )

        n_params = sum(p.numel() for p in self.parameters())
        logger.info(f"LSTMModel: {n_params:,} parameters")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        lstm_out, _ = self.lstm(x)  # (B, T, hidden)
        lstm_out = self.mc_dropout(lstm_out)

        if self.use_attention and self.pool_strategy == "attention":
            pooled, _ = self.attention(lstm_out)
        elif self.pool_strategy == "mean":
            pooled = lstm_out.mean(dim=1)
        else:
            pooled = lstm_out[:, -1]

        logits = self.classifier(pooled)
        return torch.sigmoid(logits)


@register_model("gru")
class GRUModel(nn.Module):
    """Stacked GRU with optional attention for tipping point detection.

    Args:
        cfg: Model config from ``configs/model/gru.yaml``.
    """

    def __init__(self, cfg: DictConfig) -> None:
        super().__init__()
        arch = cfg.architecture

        self.gru = nn.GRU(
            input_size=arch.input_dim,
            hidden_size=arch.hidden_dim,
            num_layers=arch.n_layers,
            batch_first=True,
            dropout=arch.dropout if arch.n_layers > 1 else 0.0,
            bidirectional=arch.bidirectional,
        )

        gru_output_dim = arch.hidden_dim * (2 if arch.bidirectional else 1)
        self.use_attention = arch.attention

        if self.use_attention:
            self.attention = TemporalAttention(gru_output_dim, arch.attention_dim)

        self.mc_dropout = nn.Dropout(cfg.uncertainty.dropout_rate)

        self.classifier = nn.Sequential(
            nn.Linear(gru_output_dim, gru_output_dim // 2),
            nn.GELU(),
            nn.Dropout(arch.dropout),
            nn.Linear(gru_output_dim // 2, arch.output_dim),
        )

        n_params = sum(p.numel() for p in self.parameters())
        logger.info(f"GRUModel: {n_params:,} parameters")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        gru_out, _ = self.gru(x)
        gru_out = self.mc_dropout(gru_out)

        if self.use_attention:
            pooled, _ = self.attention(gru_out)
        else:
            pooled = gru_out[:, -1]

        logits = self.classifier(pooled)
        return torch.sigmoid(logits)
