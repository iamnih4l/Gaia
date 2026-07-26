"""GRACE/GRACE-FO Ice Mass Change Dataset Loader.

Loads gravity-derived land ice mass anomalies for Greenland and Antarctica
from GRACE (2002–2017) and GRACE-FO (2018–present) missions.
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


@register_dataset("grace")
class GRACEDataset(BaseClimateDataset):
    """GRACE/GRACE-FO ice mass change dataset.

    Args:
        cfg: Hydra config from ``configs/dataset/grace.yaml``.
    """

    def __init__(self, cfg: DictConfig) -> None:
        super().__init__(cfg)
        self.variables: list[str] = list(cfg.variables)
        self.regions: dict = dict(cfg.spatial.regions)

    def load_raw(self, data_dir: str | Path) -> xr.Dataset:
        data_path = Path(data_dir) / "grace"
        logger.info(f"Loading GRACE data from {data_path}")

        nc_files = sorted(data_path.glob("*.nc"))
        if not nc_files:
            logger.warning("No GRACE files found. Generating synthetic data.")
            return self._generate_synthetic()

        ds = xr.open_mfdataset(nc_files, combine="by_coords", chunks={"time": 12})
        return self._standardize_coords(ds)

    def preprocess(self, ds: xr.Dataset) -> xr.Dataset:
        proc_cfg = self.cfg.processing

        if proc_cfg.compute_anomalies:
            baseline = proc_cfg.baseline_period
            clim = ds.sel(
                time=slice(f"{baseline[0]}-01-01", f"{baseline[1]}-12-31")
            ).mean(dim="time")
            ds = ds - clim
            logger.info(f"Computed anomalies relative to {baseline[0]}-{baseline[1]}")

        if proc_cfg.normalize:
            for var in ds.data_vars:
                mean = ds[var].mean()
                std = ds[var].std()
                if std > 0:
                    ds[var] = (ds[var] - mean) / std

        return ds

    def subset_region(self, ds: xr.Dataset, region_name: str) -> xr.Dataset:
        if region_name not in self.regions:
            raise KeyError(f"Region '{region_name}' not found. Available: {list(self.regions.keys())}")
        region = self.regions[region_name]
        return ds.sel(
            lat=slice(region["lat_max"], region["lat_min"]),
            lon=slice(region["lon_min"], region["lon_max"]),
        )

    def get_metadata(self) -> dict[str, Any]:
        return {
            "name": "GRACE/GRACE-FO",
            "source": "NASA JPL/CSR",
            "variables": self.variables,
            "spatial_resolution": "~1° (native ~300 km)",
            "temporal_range": "2002–present",
            "license": "NASA PO.DAAC (open)",
            "regions": list(self.regions.keys()),
        }

    def _standardize_coords(self, ds: xr.Dataset) -> xr.Dataset:
        rename_map = {}
        for coord in ds.coords:
            lower = coord.lower()
            if lower in ("latitude",):
                rename_map[coord] = "lat"
            elif lower in ("longitude",):
                rename_map[coord] = "lon"
        return ds.rename(rename_map) if rename_map else ds

    def _generate_synthetic(self) -> xr.Dataset:
        logger.warning("Generating synthetic GRACE data")
        n_time = 12 * 20
        n_lat, n_lon = 30, 60
        time = xr.cftime_range(start="2002-04", periods=n_time, freq="MS")
        lat = np.linspace(-90, 90, n_lat)
        lon = np.linspace(-180, 180, n_lon)
        rng = np.random.default_rng(42)

        # Simulate accelerating ice mass loss
        t = np.arange(n_time, dtype=np.float64)
        trend = -0.5 * t - 0.01 * t**2
        lwe = rng.standard_normal((n_time, n_lat, n_lon)).astype(np.float32) * 10
        lwe += trend[:, None, None]

        return xr.Dataset(
            {
                "lwe_thickness": (["time", "lat", "lon"], lwe),
                "uncertainty": (["time", "lat", "lon"], np.abs(rng.standard_normal((n_time, n_lat, n_lon)).astype(np.float32)) * 2),
            },
            coords={"time": time, "lat": lat, "lon": lon},
        )
