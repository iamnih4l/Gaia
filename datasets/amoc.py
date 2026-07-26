"""RAPID/MOCHA/OSNAP AMOC Transport Dataset Loader.

Loads Atlantic Meridional Overturning Circulation measurements from
the RAPID array at 26.5°N for AMOC slowdown/collapse detection.
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


@register_dataset("amoc")
class AMOCDataset(BaseClimateDataset):
    """RAPID-MOCHA AMOC transport dataset.

    Args:
        cfg: Hydra config from ``configs/dataset/amoc.yaml``.
    """

    def __init__(self, cfg: DictConfig) -> None:
        super().__init__(cfg)
        self.variables: list[str] = list(cfg.variables)

    def load_raw(self, data_dir: str | Path) -> xr.Dataset:
        data_path = Path(data_dir) / "amoc"
        logger.info(f"Loading AMOC data from {data_path}")

        nc_files = sorted(data_path.glob("*.nc"))
        csv_files = sorted(data_path.glob("*.csv"))

        if nc_files:
            ds = xr.open_mfdataset(nc_files, combine="by_coords")
            return ds
        elif csv_files:
            return self._load_from_csv(csv_files)
        else:
            logger.warning("No AMOC files found. Generating synthetic data.")
            return self._generate_synthetic()

    def _load_from_csv(self, csv_files: list[Path]) -> xr.Dataset:
        dfs = [pd.read_csv(f, parse_dates=["date"]) for f in csv_files]
        df = pd.concat(dfs, ignore_index=True).sort_values("date")
        df = df.set_index("date")
        ds = xr.Dataset.from_dataframe(df)
        ds = ds.rename({"date": "time"})
        return ds

    def preprocess(self, ds: xr.Dataset) -> xr.Dataset:
        proc_cfg = self.cfg.processing

        # Resample to monthly if higher frequency
        if "time" in ds.dims:
            ds = ds.resample(time="MS").mean(skipna=True)

        # Smooth with moving average
        smooth_window = proc_cfg.smooth_window
        if smooth_window > 1:
            for var in ds.data_vars:
                ds[var] = ds[var].rolling(time=smooth_window, center=True, min_periods=1).mean()
            logger.info(f"Applied {smooth_window}-month moving average smoothing")

        # Compute anomalies
        if proc_cfg.compute_anomalies:
            baseline = proc_cfg.baseline_period
            mean_val = ds.sel(
                time=slice(f"{baseline[0]}-01-01", f"{baseline[1]}-12-31")
            ).mean(dim="time")
            ds = ds - mean_val

        # Detrend
        if proc_cfg.detrend:
            for var in ds.data_vars:
                vals = ds[var].values
                t = np.arange(len(vals), dtype=np.float64)
                valid = ~np.isnan(vals)
                if valid.sum() > 2:
                    coeffs = np.polyfit(t[valid], vals[valid], 1)
                    trend = np.polyval(coeffs, t)
                    ds[var] = ds[var] - xr.DataArray(trend, dims=["time"], coords={"time": ds.time})

        # Normalize
        if proc_cfg.normalize:
            for var in ds.data_vars:
                mean = float(ds[var].mean())
                std = float(ds[var].std())
                if std > 0:
                    ds[var] = (ds[var] - mean) / std

        return ds

    def get_metadata(self) -> dict[str, Any]:
        return {
            "name": "RAPID-MOCHA AMOC",
            "source": "RAPID/National Oceanography Centre",
            "latitude": f"{self.cfg.spatial.latitude}°N",
            "variables": self.variables,
            "temporal_range": f"{self.cfg.temporal.start_year}–{self.cfg.temporal.end_year}",
            "license": "RAPID (open)",
        }

    def _generate_synthetic(self) -> xr.Dataset:
        logger.warning("Generating synthetic AMOC data")
        n_time = 12 * 20  # 2004–2024
        time = pd.date_range(start="2004-04", periods=n_time, freq="MS")
        rng = np.random.default_rng(42)

        # AMOC ~17 Sv with declining trend and variability
        t = np.arange(n_time, dtype=np.float64)
        seasonal = 2.0 * np.sin(2 * np.pi * t / 12)
        trend = -0.05 * t
        noise = rng.standard_normal(n_time) * 1.5
        moc = 17.0 + seasonal + trend + noise

        return xr.Dataset(
            {
                "moc_transports": (["time"], moc.astype(np.float32)),
                "florida_current": (["time"], (31.0 + rng.standard_normal(n_time) * 2).astype(np.float32)),
                "ekman_transport": (["time"], (3.5 + rng.standard_normal(n_time) * 1).astype(np.float32)),
            },
            coords={"time": time},
        )
