"""Graph construction — build spatial graphs from climate data.

Creates PyTorch Geometric graph objects from gridded climate data
for use with GNN-based tipping point detectors.
"""

from __future__ import annotations

import numpy as np
import torch
from loguru import logger

try:
    from torch_geometric.data import Data
    HAS_TORCH_GEOMETRIC = True
except ImportError:
    HAS_TORCH_GEOMETRIC = False
    logger.warning("torch_geometric not installed — graph construction will return dicts")


class GraphConstructor:
    """Construct spatial graphs from gridded climate data.

    Supports multiple graph construction strategies:
    - **knn**: K-nearest neighbors by geographic distance
    - **radius**: Connect nodes within a geographic radius
    - **correlation**: Connect nodes with high temporal correlation
    - **teleconnection**: Use known climate teleconnection patterns
    """

    @staticmethod
    def from_grid(
        lat: np.ndarray,
        lon: np.ndarray,
        features: np.ndarray,
        method: str = "knn",
        k: int = 8,
        radius: float = 5.0,
        correlation_threshold: float = 0.5,
        include_self_loops: bool = True,
    ) -> Data | dict:
        """Construct a graph from a spatial grid.

        Args:
            lat: Latitude values, shape ``(N_lat,)``.
            lon: Longitude values, shape ``(N_lon,)``.
            features: Node feature array, shape ``(N_nodes, F)`` where
                ``N_nodes = N_lat × N_lon``.
            method: Graph construction method.
            k: Number of neighbors for KNN.
            radius: Radius in degrees for radius graph.
            correlation_threshold: Threshold for correlation-based edges.
            include_self_loops: Whether to add self-loop edges.

        Returns:
            PyTorch Geometric ``Data`` object (or dict if PyG unavailable).
        """
        # Build node positions
        lat_grid, lon_grid = np.meshgrid(lat, lon, indexing="ij")
        positions = np.stack([lat_grid.ravel(), lon_grid.ravel()], axis=1)
        n_nodes = positions.shape[0]

        # Build edges based on method
        if method == "knn":
            edge_index, edge_attr = GraphConstructor._knn_edges(positions, k)
        elif method == "radius":
            edge_index, edge_attr = GraphConstructor._radius_edges(positions, radius)
        elif method == "correlation":
            edge_index, edge_attr = GraphConstructor._correlation_edges(
                features, correlation_threshold
            )
        else:
            raise ValueError(f"Unknown graph construction method: {method}")

        # Add self-loops
        if include_self_loops:
            self_loops = np.arange(n_nodes)
            self_loop_edges = np.stack([self_loops, self_loops], axis=0)
            self_loop_weights = np.ones(n_nodes, dtype=np.float32)
            edge_index = np.concatenate([edge_index, self_loop_edges], axis=1)
            edge_attr = np.concatenate([edge_attr, self_loop_weights])

        logger.info(
            f"Built {method} graph: {n_nodes} nodes, {edge_index.shape[1]} edges"
        )

        x = torch.as_tensor(features, dtype=torch.float32)
        edge_index_t = torch.as_tensor(edge_index, dtype=torch.long)
        edge_attr_t = torch.as_tensor(edge_attr, dtype=torch.float32).unsqueeze(-1)
        pos = torch.as_tensor(positions, dtype=torch.float32)

        if HAS_TORCH_GEOMETRIC:
            return Data(
                x=x,
                edge_index=edge_index_t,
                edge_attr=edge_attr_t,
                pos=pos,
                num_nodes=n_nodes,
            )
        else:
            return {
                "x": x,
                "edge_index": edge_index_t,
                "edge_attr": edge_attr_t,
                "pos": pos,
                "num_nodes": n_nodes,
            }

    @staticmethod
    def _knn_edges(
        positions: np.ndarray,
        k: int,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Build K-nearest neighbor graph edges."""
        from scipy.spatial import KDTree

        tree = KDTree(positions)
        distances, indices = tree.query(positions, k=k + 1)  # +1 for self

        n = positions.shape[0]
        src, dst, weights = [], [], []
        for i in range(n):
            for j_idx in range(1, k + 1):  # Skip self (index 0)
                if j_idx < len(indices[i]):
                    j = indices[i][j_idx]
                    src.append(i)
                    dst.append(j)
                    weights.append(1.0 / max(distances[i][j_idx], 1e-6))

        edge_index = np.array([src, dst], dtype=np.int64)
        edge_attr = np.array(weights, dtype=np.float32)
        return edge_index, edge_attr

    @staticmethod
    def _radius_edges(
        positions: np.ndarray,
        radius: float,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Build radius-based graph edges."""
        from scipy.spatial import KDTree

        tree = KDTree(positions)
        pairs = tree.query_pairs(radius)

        src, dst, weights = [], [], []
        for i, j in pairs:
            dist = np.linalg.norm(positions[i] - positions[j])
            w = 1.0 / max(dist, 1e-6)
            src.extend([i, j])
            dst.extend([j, i])
            weights.extend([w, w])

        edge_index = np.array([src, dst], dtype=np.int64) if src else np.zeros((2, 0), dtype=np.int64)
        edge_attr = np.array(weights, dtype=np.float32) if weights else np.zeros(0, dtype=np.float32)
        return edge_index, edge_attr

    @staticmethod
    def _correlation_edges(
        features: np.ndarray,
        threshold: float,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Build correlation-based graph edges.

        Connects nodes whose feature time series are highly correlated.
        """
        n_nodes = features.shape[0]

        # Compute correlation matrix
        corr_matrix = np.corrcoef(features)
        corr_matrix = np.nan_to_num(corr_matrix)

        # Threshold
        src, dst, weights = [], [], []
        for i in range(n_nodes):
            for j in range(i + 1, n_nodes):
                if abs(corr_matrix[i, j]) >= threshold:
                    src.extend([i, j])
                    dst.extend([j, i])
                    w = abs(corr_matrix[i, j])
                    weights.extend([w, w])

        edge_index = np.array([src, dst], dtype=np.int64) if src else np.zeros((2, 0), dtype=np.int64)
        edge_attr = np.array(weights, dtype=np.float32) if weights else np.zeros(0, dtype=np.float32)
        return edge_index, edge_attr

    @staticmethod
    def build_temporal_graph_sequence(
        lat: np.ndarray,
        lon: np.ndarray,
        feature_sequence: np.ndarray,
        method: str = "knn",
        k: int = 8,
    ) -> list[Data | dict]:
        """Build a sequence of graphs for dynamic graph networks.

        Args:
            lat: Latitude values.
            lon: Longitude values.
            feature_sequence: Shape ``(T, N_nodes, F)`` — features over time.
            method: Edge construction method.
            k: KNN parameter.

        Returns:
            List of graph objects, one per time step.
        """
        graphs = []
        for t in range(feature_sequence.shape[0]):
            graph = GraphConstructor.from_grid(
                lat, lon, feature_sequence[t], method=method, k=k
            )
            graphs.append(graph)

        logger.info(f"Built temporal graph sequence: {len(graphs)} time steps")
        return graphs
