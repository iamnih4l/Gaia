"""Climate GNN — Graph Convolutional Network for spatial climate data.

Uses message passing on a spatial climate graph to detect spatially
distributed early-warning signals of tipping points.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F
from loguru import logger
from omegaconf import DictConfig

from models.registry import register_model

try:
    from torch_geometric.nn import GCNConv, SAGEConv, global_add_pool, global_max_pool, global_mean_pool
    HAS_PYG = True
except ImportError:
    HAS_PYG = False
    logger.warning("torch_geometric not installed. GNN models unavailable.")


if HAS_PYG:

    @register_model("climate_gnn")
    class ClimateGNN(nn.Module):
        """Graph Convolutional Network for spatially-distributed climate data.

        Architecture:
            N × (GCNConv → BatchNorm → ReLU → Dropout) → Global Pooling → MLP Head

        Args:
            cfg: Model config from ``configs/model/gnn.yaml``.
        """

        def __init__(self, cfg: DictConfig) -> None:
            super().__init__()
            arch = cfg.architecture

            conv_cls = GCNConv if arch.conv_type == "GCN" else SAGEConv

            self.convs = nn.ModuleList()
            self.bns = nn.ModuleList()

            # First layer
            self.convs.append(conv_cls(arch.node_features, arch.hidden_channels))
            self.bns.append(nn.BatchNorm1d(arch.hidden_channels))

            # Hidden layers
            for _ in range(arch.n_layers - 1):
                self.convs.append(conv_cls(arch.hidden_channels, arch.hidden_channels))
                self.bns.append(nn.BatchNorm1d(arch.hidden_channels))

            # Pooling
            pool_map = {
                "global_mean": global_mean_pool,
                "global_max": global_max_pool,
                "global_add": global_add_pool,
            }
            self.pool = pool_map.get(arch.pool_type, global_mean_pool)

            # Classification head
            self.classifier = nn.Sequential(
                nn.Linear(arch.hidden_channels, arch.hidden_channels // 2),
                nn.GELU(),
                nn.Dropout(arch.dropout),
                nn.Linear(arch.hidden_channels // 2, arch.output_dim),
            )

            self.dropout = arch.dropout
            self.residual = arch.residual

            n_params = sum(p.numel() for p in self.parameters())
            logger.info(f"ClimateGNN: {n_params:,} parameters")

        def forward(self, x: torch.Tensor, edge_index: torch.Tensor,
                    batch: torch.Tensor | None = None, **kwargs) -> torch.Tensor:
            """Forward pass.

            Args:
                x: Node features ``(N, F)``.
                edge_index: Edge indices ``(2, E)``.
                batch: Batch assignment vector ``(N,)``.

            Returns:
                Tipping probability ``(B, 1)``.
            """
            for i, (conv, bn) in enumerate(zip(self.convs, self.bns)):
                identity = x if (self.residual and x.shape[-1] == conv.out_channels) else None
                x = conv(x, edge_index)
                x = bn(x)
                x = F.relu(x)
                x = F.dropout(x, p=self.dropout, training=self.training)
                if identity is not None:
                    x = x + identity

            # Global pooling
            if batch is None:
                batch = torch.zeros(x.size(0), dtype=torch.long, device=x.device)
            pooled = self.pool(x, batch)

            logits = self.classifier(pooled)
            return torch.sigmoid(logits)
