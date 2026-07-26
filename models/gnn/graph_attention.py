"""Graph Attention Network for climate tipping point detection."""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F
from loguru import logger
from omegaconf import DictConfig

from models.registry import register_model

try:
    from torch_geometric.nn import GATConv, global_mean_pool
    HAS_PYG = True
except ImportError:
    HAS_PYG = False

if HAS_PYG:

    @register_model("graph_attention")
    class GraphAttentionNetwork(nn.Module):
        """Multi-head Graph Attention Network.

        Args:
            cfg: Model config from ``configs/model/gat.yaml``.
        """

        def __init__(self, cfg: DictConfig) -> None:
            super().__init__()
            arch = cfg.architecture

            self.convs = nn.ModuleList()
            self.bns = nn.ModuleList()

            # First layer
            self.convs.append(GATConv(
                arch.node_features, arch.hidden_channels,
                heads=arch.n_heads, dropout=arch.dropout, concat=arch.concat_heads,
            ))
            first_out = arch.hidden_channels * arch.n_heads if arch.concat_heads else arch.hidden_channels
            self.bns.append(nn.BatchNorm1d(first_out))

            # Hidden layers
            for _ in range(arch.n_layers - 1):
                self.convs.append(GATConv(
                    first_out, arch.hidden_channels,
                    heads=arch.n_heads, dropout=arch.dropout, concat=arch.concat_heads,
                ))
                self.bns.append(nn.BatchNorm1d(first_out))

            self.classifier = nn.Sequential(
                nn.Linear(first_out, first_out // 2),
                nn.GELU(),
                nn.Dropout(arch.dropout),
                nn.Linear(first_out // 2, arch.output_dim),
            )
            self.dropout = arch.dropout

            n_params = sum(p.numel() for p in self.parameters())
            logger.info(f"GraphAttentionNetwork: {n_params:,} parameters")

        def forward(self, x: torch.Tensor, edge_index: torch.Tensor,
                    batch: torch.Tensor | None = None, **kwargs) -> torch.Tensor:
            for conv, bn in zip(self.convs, self.bns):
                x = conv(x, edge_index)
                x = bn(x)
                x = F.elu(x)
                x = F.dropout(x, p=self.dropout, training=self.training)

            if batch is None:
                batch = torch.zeros(x.size(0), dtype=torch.long, device=x.device)
            pooled = global_mean_pool(x, batch)

            logits = self.classifier(pooled)
            return torch.sigmoid(logits)

        def get_attention_weights(self, x: torch.Tensor, edge_index: torch.Tensor) -> list[torch.Tensor]:
            """Extract GAT attention weights for edge visualization."""
            weights = []
            for conv in self.convs:
                x, (edge_idx, alpha) = conv(x, edge_index, return_attention_weights=True)
                weights.append(alpha.detach())
                x = F.elu(x)
            return weights
