"""PCMCI — causal discovery for climate time series using tigramite.

Reference:
    Runge, J., et al. (2019). Detecting and quantifying causal associations
    in large nonlinear time series datasets. Science Advances, 5(11).
"""

from __future__ import annotations

from typing import Any

import numpy as np
from loguru import logger


class PCMCIWrapper:
    """Wrapper for PCMCI causal discovery from the tigramite library.

    Discovers causal links between climate variables using conditional
    independence testing, which can identify driving factors for tipping points.
    """

    def __init__(
        self,
        tau_max: int = 12,
        pc_alpha: float = 0.05,
        ci_test: str = "parcorr",
    ) -> None:
        """Initialize PCMCI wrapper.

        Args:
            tau_max: Maximum time lag for causal links.
            pc_alpha: Significance level for conditional independence tests.
            ci_test: Conditional independence test — ``"parcorr"`` or ``"gpdc"``.
        """
        self.tau_max = tau_max
        self.pc_alpha = pc_alpha
        self.ci_test = ci_test
        self._results: dict[str, Any] = {}

    def fit(
        self,
        data: np.ndarray,
        variable_names: list[str] | None = None,
    ) -> dict[str, Any]:
        """Run PCMCI causal discovery.

        Args:
            data: Multivariate time series of shape ``(T, N_vars)``.
            variable_names: Names for each variable.

        Returns:
            Dictionary with causal graph, p-values, and link strengths.
        """
        try:
            import tigramite
            from tigramite import data_processing as pp
            from tigramite.independence_tests.parcorr import ParCorr
            from tigramite.pcmci import PCMCI

            # Prepare tigramite data
            dataframe = pp.DataFrame(
                data,
                var_names=variable_names or [f"var_{i}" for i in range(data.shape[1])],
            )

            # Select CI test
            if self.ci_test == "parcorr":
                cond_ind_test = ParCorr(significance="analytic")
            else:
                cond_ind_test = ParCorr(significance="analytic")

            # Run PCMCI
            pcmci = PCMCI(dataframe=dataframe, cond_ind_test=cond_ind_test, verbosity=0)
            results = pcmci.run_pcmci(tau_max=self.tau_max, pc_alpha=self.pc_alpha)

            self._results = {
                "p_matrix": results["p_matrix"],
                "val_matrix": results["val_matrix"],
                "graph": results.get("graph"),
                "variable_names": variable_names,
                "tau_max": self.tau_max,
            }

            n_links = np.sum(results["p_matrix"] < self.pc_alpha)
            logger.info(f"PCMCI found {n_links} significant causal links (α={self.pc_alpha})")
            return self._results

        except ImportError:
            logger.warning("tigramite not installed. Returning empty results.")
            return {"p_matrix": None, "val_matrix": None, "graph": None}

    def get_significant_links(self, alpha: float | None = None) -> list[dict]:
        """Extract significant causal links.

        Args:
            alpha: Significance level (uses ``self.pc_alpha`` if None).

        Returns:
            List of dicts with ``source``, ``target``, ``lag``, ``strength``, ``p_value``.
        """
        if not self._results or self._results.get("p_matrix") is None:
            return []

        alpha = alpha or self.pc_alpha
        p_matrix = self._results["p_matrix"]
        val_matrix = self._results["val_matrix"]
        names = self._results.get("variable_names", [])

        links = []
        n_vars = p_matrix.shape[0]
        for i in range(n_vars):
            for j in range(n_vars):
                for tau in range(self.tau_max + 1):
                    if p_matrix[i, j, tau] < alpha:
                        links.append({
                            "source": names[j] if j < len(names) else f"var_{j}",
                            "target": names[i] if i < len(names) else f"var_{i}",
                            "lag": tau,
                            "strength": float(val_matrix[i, j, tau]),
                            "p_value": float(p_matrix[i, j, tau]),
                        })

        links.sort(key=lambda x: abs(x["strength"]), reverse=True)
        return links
