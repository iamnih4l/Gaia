"""CMIP6 Multi-Model Climate Projection Dataset Loader.

Loads CMIP6 multi-model ensemble output from ESGF nodes, supporting
historical, SSP245, and SSP585 scenarios for climate tipping point analysis.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import xarray as xr
from loguru import logger
from omegaconf import DictConfig

from datasets.base import BaseClimateDataset
from datasets.registry import register_dataset


@register_dataset("cmip6")
class CMIP6Dataset(BaseClimateDataset):
    """CMIP6 climate model output dataset.

    Provides access to multi-model ensemble projections for variables
    including temperature, precipitation, AMOC streamfunction, sea ice
    concentration, and ocean heat content.

    Args:
        cfg: Hydra config from ``configs/dataset/cmip6.yaml``.
    """

    def __init__(self, cfg: DictConfig) -> None:
        super().__init__(cfg)
        self.variables: list[str] = list(cfg.variables)
        self.experiments: list[str] = list(cfg.experiments)
        self.models: list[str] = list(cfg.models)

    def load_raw(self, data_dir: str | Path) -> xr.Dataset:
        """Load CMIP6 NetCDF files from local storage.

        Searches ``{data_dir}/cmip6/`` for NetCDF files organized by
        model/experiment/variable.

        Args:
            data_dir: Root data directory.

        Returns:
            Merged xarray Dataset across models and experiments.
        """
        data_path = Path(data_dir) / "cmip6"
        logger.info(f"Loading CMIP6 data from {data_path}")

        nc_files = sorted(data_path.glob("**/*.nc"))
        if not nc_files:
            logger.warning("No CMIP6 NetCDF files found. Generating synthetic data.")
            return self._generate_synthetic()

        ds = xr.open_mfdataset(
            nc_files,
            combine="by_coords",
            chunks={"time": 12},
            engine="netcdf4",
            parallel=True,
        )
        return self._standardize_coords(ds)

    def preprocess(self, ds: xr.Dataset) -> xr.Dataset:
        """Apply CMIP6-specific preprocessing.

        Pipeline:
            1. Temporal subset
            2. Regrid to target resolution
            3. Compute anomalies relative to baseline period
            4. Normalize

        Args:
            ds: Raw xarray Dataset.

        Returns:
            Preprocessed Dataset.
        """
        proc_cfg = self.cfg.processing
        temp_cfg = self.cfg.temporal

        # Temporal subset
        ds = ds.sel(
            time=slice(f"{temp_cfg.start_year}-01-01", f"{temp_cfg.end_year}-12-31")
        )

        # Compute anomalies against baseline
        if proc_cfg.compute_anomalies:
            baseline = proc_cfg.baseline_period
            baseline_clim = ds.sel(
                time=slice(f"{baseline[0]}-01-01", f"{baseline[1]}-12-31")
            ).groupby("time.month").mean(dim="time")
            ds = ds.groupby("time.month") - baseline_clim
            logger.info(f"Computed anomalies relative to {baseline[0]}-{baseline[1]}")

        # Normalize
        if proc_cfg.normalize:
            for var in ds.data_vars:
                mean = ds[var].mean()
                std = ds[var].std()
                if std > 0:
                    ds[var] = (ds[var] - mean) / std
            logger.info("Applied standard normalization")

        return ds

    def get_metadata(self) -> dict[str, Any]:
        """Return CMIP6 dataset metadata."""
        return {
            "name": "CMIP6",
            "source": "WCRP/ESGF",
            "variables": self.variables,
            "experiments": self.experiments,
            "models": self.models,
            "temporal_range": f"{self.cfg.temporal.start_year}–{self.cfg.temporal.end_year}",
            "license": "CMIP6 Terms of Use (open)",
        }

    def _standardize_coords(self, ds: xr.Dataset) -> xr.Dataset:
        rename_map = {}
        for coord in ds.coords:
            lower = coord.lower()
            if lower in ("latitude", "lat"):
                rename_map[coord] = "lat"
            elif lower in ("longitude", "lon"):
                rename_map[coord] = "lon"
        return ds.rename(rename_map) if rename_map else ds

    def _generate_synthetic(self) -> xr.Dataset:
        logger.warning("Generating synthetic CMIP6 data — not for production")
        n_time = 12 * 50
        n_lat, n_lon = 36, 72
        time = xr.cftime_range(start="1950-01", periods=n_time, freq="MS")
        lat = np.linspace(-90, 90, n_lat)
        lon = np.linspace(-180, 180, n_lon)
        rng = np.random.default_rng(42)

        data_vars = {}
        for var in self.variables:
            data = rng.standard_normal((n_time, n_lat, n_lon)).astype(np.float32)
            # Add a slow trend to simulate climate change
            trend = np.linspace(0, 2, n_time)[:, None, None]
            data += trend
            data_vars[var] = (["time", "lat", "lon"], data)

        return xr.Dataset(data_vars, coords={"time": time, "lat": lat, "lon": lon})
