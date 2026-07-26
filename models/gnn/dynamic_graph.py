"""Dynamic Graph Network — temporal GNN with evolving adjacency."""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F
from loguru import logger
from omegaconf import DictConfig

from models.registry import register_model

try:
    from torch_geometric.nn import GCNConv, global_mean_pool
    HAS_PYG = True
except ImportError:
    HAS_PYG = False

if HAS_PYG:

    @register_model("dynamic_graph")
    class DynamicGraphNetwork(nn.Module):
        """Temporal GNN that processes a sequence of time-varying graphs.

        Combines GNN message passing per time step with a GRU to model
        the temporal evolution of graph-level representations.

        Args:
            cfg: Model config.
        """

        def __init__(self, cfg: DictConfig) -> None:
            super().__init__()
            arch = cfg.architecture

            self.gcn = GCNConv(arch.node_features, arch.hidden_channels)
            self.bn = nn.BatchNorm1d(arch.hidden_channels)

            self.temporal_gru = nn.GRU(
                input_size=arch.hidden_channels,
                hidden_size=arch.hidden_channels,
                num_layers=2,
                batch_first=True,
                dropout=arch.dropout,
            )

            self.classifier = nn.Sequential(
                nn.Linear(arch.hidden_channels, arch.hidden_channels // 2),
                nn.GELU(),
                nn.Dropout(arch.dropout),
                nn.Linear(arch.hidden_channels // 2, arch.output_dim),
            )

            n_params = sum(p.numel() for p in self.parameters())
            logger.info(f"DynamicGraphNetwork: {n_params:,} parameters")

        def forward(self, graph_sequence: list, batch: torch.Tensor | None = None) -> torch.Tensor:
            """Forward pass over a sequence of graph snapshots.

            Args:
                graph_sequence: List of (x, edge_index) tuples or PyG Data objects.
                batch: Batch assignment.

            Returns:
                Tipping probability ``(B, 1)``.
            """
            graph_embeddings = []

            for graph_data in graph_sequence:
                if isinstance(graph_data, dict):
                    x, edge_index = graph_data["x"], graph_data["edge_index"]
                elif hasattr(graph_data, "x"):
                    x, edge_index = graph_data.x, graph_data.edge_index
                else:
                    x, edge_index = graph_data

                h = self.gcn(x, edge_index)
                h = self.bn(h)
                h = F.relu(h)

                # Global mean pool for this time step
                if batch is None:
                    b = torch.zeros(h.size(0), dtype=torch.long, device=h.device)
                else:
                    b = batch
                pooled = global_mean_pool(h, b)
                graph_embeddings.append(pooled)

            # Stack into temporal sequence
            temporal = torch.stack(graph_embeddings, dim=1)  # (B, T, hidden)

            # Temporal GRU
            gru_out, _ = self.temporal_gru(temporal)
            final = gru_out[:, -1]  # Last time step

            logits = self.classifier(final)
            return torch.sigmoid(logits)
