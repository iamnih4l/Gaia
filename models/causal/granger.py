"""Granger Causality testing for climate time series."""

from __future__ import annotations

import numpy as np
from loguru import logger


class GrangerCausality:
    """Granger causality testing using VAR models.

    Tests whether past values of variable X help predict variable Y
    beyond what Y's own past values predict.
    """

    def __init__(self, max_lag: int = 12, significance: float = 0.05) -> None:
        self.max_lag = max_lag
        self.significance = significance

    def test_pairwise(
        self,
        data: np.ndarray,
        variable_names: list[str] | None = None,
    ) -> list[dict]:
        """Test Granger causality for all variable pairs.

        Args:
            data: Multivariate time series ``(T, N_vars)``.
            variable_names: Variable labels.

        Returns:
            List of significant causal links.
        """
        try:
            from statsmodels.tsa.stattools import grangercausalitytests

            n_vars = data.shape[1]
            if variable_names is None:
                variable_names = [f"var_{i}" for i in range(n_vars)]

            links = []
            for i in range(n_vars):
                for j in range(n_vars):
                    if i == j:
                        continue

                    pair_data = np.column_stack([data[:, i], data[:, j]])
                    valid = ~np.isnan(pair_data).any(axis=1)
                    if valid.sum() < self.max_lag + 10:
                        continue

                    try:
                        results = grangercausalitytests(
                            pair_data[valid], maxlag=self.max_lag, verbose=False
                        )

                        for lag in range(1, self.max_lag + 1):
                            p_value = results[lag][0]["ssr_ftest"][1]
                            f_stat = results[lag][0]["ssr_ftest"][0]

                            if p_value < self.significance:
                                links.append({
                                    "source": variable_names[j],
                                    "target": variable_names[i],
                                    "lag": lag,
                                    "f_statistic": float(f_stat),
                                    "p_value": float(p_value),
                                })
                    except Exception:
                        continue

            links.sort(key=lambda x: x["p_value"])
            logger.info(f"Granger causality: {len(links)} significant links found")
            return links

        except ImportError:
            logger.warning("statsmodels not available for Granger causality")
            return []
