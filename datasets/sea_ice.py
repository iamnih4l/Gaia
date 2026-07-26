"""NSIDC Sea Ice Index Dataset Loader.

Loads Arctic and Antarctic sea ice extent and area time series from the
National Snow and Ice Data Center for sea ice loss tipping point detection.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import xarray as xr
from loguru import logger
from omegaconf import DictConfig

from datasets.base import BaseClimateDataset
from datasets.registry import register_dataset


@register_dataset("sea_ice")
class SeaIceDataset(BaseClimateDataset):
    """NSIDC Sea Ice Index dataset for Arctic/Antarctic monitoring.

    Args:
        cfg: Hydra config from ``configs/dataset/sea_ice.yaml``.
    """

    def __init__(self, cfg: DictConfig) -> None:
        super().__init__(cfg)
        self.variables: list[str] = list(cfg.variables)

    def load_raw(self, data_dir: str | Path) -> xr.Dataset:
        data_path = Path(data_dir) / "sea_ice"
        logger.info(f"Loading sea ice data from {data_path}")

        # Try CSV format first (Sea Ice Index is often distributed as CSV)
        csv_files = sorted(data_path.glob("*.csv"))
        nc_files = sorted(data_path.glob("*.nc"))

        if nc_files:
            ds = xr.open_mfdataset(nc_files, combine="by_coords")
            return ds
        elif csv_files:
            return self._load_from_csv(csv_files)
        else:
            logger.warning("No sea ice files found. Generating synthetic data.")
            return self._generate_synthetic()

    def _load_from_csv(self, csv_files: list[Path]) -> xr.Dataset:
        """Load sea ice extent from CSV files into xarray."""
        dfs = [pd.read_csv(f, parse_dates=["date"]) for f in csv_files]
        df = pd.concat(dfs, ignore_index=True).sort_values("date")
        df = df.set_index("date")

        ds = xr.Dataset.from_dataframe(df)
        ds = ds.rename({"date": "time"})
        return ds

    def preprocess(self, ds: xr.Dataset) -> xr.Dataset:
        proc_cfg = self.cfg.processing
        temp_cfg = self.cfg.temporal

        ds = ds.sel(
            time=slice(f"{temp_cfg.start_year}-01-01", f"{temp_cfg.end_year}-12-31")
        )

        if proc_cfg.compute_anomalies:
            baseline = proc_cfg.baseline_period
            clim = ds.sel(
                time=slice(f"{baseline[0]}-01-01", f"{baseline[1]}-12-31")
            ).groupby("time.month").mean("time")
            ds = ds.groupby("time.month") - clim

        if proc_cfg.detrend:
            for var in ds.data_vars:
                vals = ds[var].values
                t = np.arange(len(vals), dtype=np.float64)
                valid = ~np.isnan(vals)
                if valid.sum() > 2:
                    coeffs = np.polyfit(t[valid], vals[valid], 1)
                    trend = np.polyval(coeffs, t)
                    ds[var] = ds[var] - xr.DataArray(trend, dims=["time"], coords={"time": ds.time})

        if proc_cfg.normalize:
            for var in ds.data_vars:
                mean = float(ds[var].mean())
                std = float(ds[var].std())
                if std > 0:
                    ds[var] = (ds[var] - mean) / std

        return ds

    def get_metadata(self) -> dict[str, Any]:
        return {
            "name": "NSIDC Sea Ice Index",
            "source": "NSIDC",
            "product": "G02135",
            "variables": self.variables,
            "temporal_range": f"{self.cfg.temporal.start_year}–{self.cfg.temporal.end_year}",
            "license": "NSIDC (open)",
        }

    def _generate_synthetic(self) -> xr.Dataset:
        logger.warning("Generating synthetic sea ice data")
        n_time = 12 * 45  # 1979–2024
        time = pd.date_range(start="1979-01", periods=n_time, freq="MS")
        rng = np.random.default_rng(42)

        # Declining Arctic sea ice trend
        t = np.arange(n_time, dtype=np.float64)
        seasonal = 3.0 * np.sin(2 * np.pi * t / 12)
        trend = -0.02 * t
        noise = rng.standard_normal(n_time) * 0.3
        extent = 12.0 + seasonal + trend + noise

        return xr.Dataset(
            {
                "sea_ice_extent": (["time"], extent.astype(np.float32)),
                "sea_ice_area": (["time"], (extent * 0.85).astype(np.float32)),
            },
            coords={"time": time},
        )
