"""Causal Discovery — PC algorithm and causal graph construction."""

from __future__ import annotations

import numpy as np
from loguru import logger


class CausalDiscovery:
    """Constraint-based causal discovery using the PC algorithm.

    Discovers the causal DAG structure among climate variables.
    """

    def __init__(self, alpha: float = 0.05, max_cond_set: int = 3) -> None:
        self.alpha = alpha
        self.max_cond_set = max_cond_set
        self.adjacency_matrix: np.ndarray | None = None

    def fit(
        self,
        data: np.ndarray,
        variable_names: list[str] | None = None,
    ) -> dict:
        """Run PC algorithm for causal discovery.

        Args:
            data: ``(T, N_vars)`` multivariate time series.
            variable_names: Variable labels.

        Returns:
            Dictionary with adjacency matrix and edge list.
        """
        n_vars = data.shape[1]
        if variable_names is None:
            variable_names = [f"var_{i}" for i in range(n_vars)]

        # Initialize fully connected graph
        adj = np.ones((n_vars, n_vars), dtype=bool)
        np.fill_diagonal(adj, False)

        # PC skeleton discovery via conditional independence tests
        from scipy.stats import pearsonr

        for depth in range(self.max_cond_set + 1):
            for i in range(n_vars):
                for j in range(i + 1, n_vars):
                    if not adj[i, j]:
                        continue

                    neighbors = [k for k in range(n_vars) if k != i and k != j and adj[i, k]]

                    if len(neighbors) < depth:
                        continue

                    from itertools import combinations
                    for cond_set in combinations(neighbors, depth):
                        if self._conditional_independence(data, i, j, list(cond_set)):
                            adj[i, j] = False
                            adj[j, i] = False
                            break

        self.adjacency_matrix = adj

        # Build edge list
        edges = []
        for i in range(n_vars):
            for j in range(i + 1, n_vars):
                if adj[i, j]:
                    edges.append({
                        "source": variable_names[i],
                        "target": variable_names[j],
                        "undirected": True,
                    })

        logger.info(f"Causal discovery: {len(edges)} edges in skeleton")
        return {"adjacency_matrix": adj, "edges": edges, "variable_names": variable_names}

    def _conditional_independence(
        self,
        data: np.ndarray,
        i: int,
        j: int,
        cond_set: list[int],
    ) -> bool:
        """Test conditional independence of variables i and j given cond_set."""
        from scipy.stats import pearsonr

        if not cond_set:
            valid = ~(np.isnan(data[:, i]) | np.isnan(data[:, j]))
            if valid.sum() < 10:
                return False
            _, p_val = pearsonr(data[valid, i], data[valid, j])
            return p_val > self.alpha

        # Partial correlation via regression residuals
        from numpy.linalg import lstsq

        cond_data = data[:, cond_set]
        valid = ~np.isnan(data[:, [i, j]]).any(axis=1) & ~np.isnan(cond_data).any(axis=1)
        if valid.sum() < len(cond_set) + 5:
            return False

        X = cond_data[valid]
        X = np.column_stack([X, np.ones(X.shape[0])])

        res_i = data[valid, i] - X @ lstsq(X, data[valid, i], rcond=None)[0]
        res_j = data[valid, j] - X @ lstsq(X, data[valid, j], rcond=None)[0]

        _, p_val = pearsonr(res_i, res_j)
        return p_val > self.alpha
