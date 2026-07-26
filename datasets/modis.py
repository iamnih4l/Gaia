"""MODIS/VIIRS Vegetation Index Dataset Loader.

Loads MODIS MOD13C2 monthly vegetation indices (NDVI, EVI) for
Amazon rainforest dieback monitoring.
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


@register_dataset("modis")
class MODISDataset(BaseClimateDataset):
    """MODIS/VIIRS vegetation index dataset for Amazon monitoring.

    Args:
        cfg: Hydra config from ``configs/dataset/modis.yaml``.
    """

    def __init__(self, cfg: DictConfig) -> None:
        super().__init__(cfg)
        self.variables: list[str] = list(cfg.variables)

    def load_raw(self, data_dir: str | Path) -> xr.Dataset:
        data_path = Path(data_dir) / "modis"
        logger.info(f"Loading MODIS data from {data_path}")

        nc_files = sorted(data_path.glob("*.nc"))
        if not nc_files:
            hdf_files = sorted(data_path.glob("*.hdf"))
            if not hdf_files:
                logger.warning("No MODIS files found. Generating synthetic data.")
                return self._generate_synthetic()
            ds = xr.open_mfdataset(hdf_files, engine="netcdf4", combine="by_coords")
        else:
            ds = xr.open_mfdataset(nc_files, combine="by_coords", chunks={"time": 12})

        return self._standardize_coords(ds)

    def preprocess(self, ds: xr.Dataset) -> xr.Dataset:
        proc_cfg = self.cfg.processing
        bounds = self.cfg.spatial.bounds

        # Spatial subset to Amazon
        ds = ds.sel(
            lat=slice(bounds.lat_max, bounds.lat_min),
            lon=slice(bounds.lon_min, bounds.lon_max),
        )

        # Quality filtering
        if proc_cfg.quality_filter and "pixel_reliability" in ds.data_vars:
            mask = ds["pixel_reliability"] <= proc_cfg.min_reliability
            for var in ["NDVI", "EVI"]:
                if var in ds:
                    ds[var] = ds[var].where(mask)

        # Compute anomalies
        if proc_cfg.compute_anomalies:
            baseline = proc_cfg.baseline_period
            clim = ds.sel(
                time=slice(f"{baseline[0]}-01-01", f"{baseline[1]}-12-31")
            ).groupby("time.month").mean("time")
            ds = ds.groupby("time.month") - clim

        # Detrend
        if proc_cfg.detrend:
            for var in ["NDVI", "EVI"]:
                if var in ds:
                    spatial_mean = ds[var].mean(dim=["lat", "lon"])
                    t = np.arange(len(spatial_mean), dtype=np.float64)
                    valid = ~np.isnan(spatial_mean.values)
                    if valid.sum() > 2:
                        coeffs = np.polyfit(t[valid], spatial_mean.values[valid], 1)
                        trend = np.polyval(coeffs, t)
                        ds[var] = ds[var] - xr.DataArray(
                            trend, dims=["time"], coords={"time": ds.time}
                        )

        # Normalize
        if proc_cfg.normalize:
            for var in ds.data_vars:
                mean = ds[var].mean()
                std = ds[var].std()
                if std > 0:
                    ds[var] = (ds[var] - mean) / std

        return ds

    def get_metadata(self) -> dict[str, Any]:
        return {
            "name": "MODIS/VIIRS",
            "source": "NASA LP DAAC",
            "product": "MOD13C2",
            "variables": self.variables,
            "spatial_resolution": "0.05° (~5.6 km)",
            "region": "Amazon Basin",
            "temporal_range": f"{self.cfg.temporal.start_year}–{self.cfg.temporal.end_year}",
            "license": "NASA LP DAAC (open)",
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
        logger.warning("Generating synthetic MODIS data — not for production")
        n_time = 12 * 24  # 24 years
        n_lat, n_lon = 50, 60
        time = xr.cftime_range(start="2000-01", periods=n_time, freq="MS")
        lat = np.linspace(-20, 5, n_lat)
        lon = np.linspace(-75, -45, n_lon)
        rng = np.random.default_rng(42)

        # Simulate NDVI with declining trend (dieback signal)
        base_ndvi = 0.7 + rng.standard_normal((n_time, n_lat, n_lon)).astype(np.float32) * 0.05
        trend = np.linspace(0, -0.1, n_time)[:, None, None]
        ndvi = np.clip(base_ndvi + trend, 0, 1)

        return xr.Dataset(
            {
                "NDVI": (["time", "lat", "lon"], ndvi),
                "EVI": (["time", "lat", "lon"], ndvi * 0.8),
            },
            coords={"time": time, "lat": lat, "lon": lon},
        )
