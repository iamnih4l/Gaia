"""NOAA Coral Reef Watch Dataset Loader.

Loads SST anomalies, Degree Heating Weeks, and bleaching alert data
from NOAA CRW for coral reef tipping point detection.
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


@register_dataset("coral")
class CoralReefDataset(BaseClimateDataset):
    """NOAA Coral Reef Watch SST and DHW dataset.

    Args:
        cfg: Hydra config from ``configs/dataset/coral.yaml``.
    """

    def __init__(self, cfg: DictConfig) -> None:
        super().__init__(cfg)
        self.variables: list[str] = list(cfg.variables)
        self.reef_regions: dict = dict(cfg.spatial.reef_regions)

    def load_raw(self, data_dir: str | Path) -> xr.Dataset:
        data_path = Path(data_dir) / "coral_reef_watch"
        logger.info(f"Loading Coral Reef Watch data from {data_path}")

        nc_files = sorted(data_path.glob("*.nc"))
        if not nc_files:
            logger.warning("No CRW files found. Generating synthetic data.")
            return self._generate_synthetic()

        ds = xr.open_mfdataset(nc_files, combine="by_coords", chunks={"time": 52})
        return self._standardize_coords(ds)

    def preprocess(self, ds: xr.Dataset) -> xr.Dataset:
        proc_cfg = self.cfg.processing
        temp_cfg = self.cfg.temporal

        # Aggregate to weekly if daily
        if temp_cfg.get("aggregate_to") == "weekly":
            ds = ds.resample(time="W").mean(skipna=True)
            logger.info("Aggregated daily data to weekly")

        # Normalize
        if proc_cfg.normalize:
            for var in ds.data_vars:
                mean = ds[var].mean()
                std = ds[var].std()
                if std > 0:
                    ds[var] = (ds[var] - mean) / std

        return ds

    def compute_bleaching_labels(self, ds: xr.Dataset) -> np.ndarray:
        """Generate binary bleaching labels from DHW thresholds.

        Args:
            ds: Dataset containing ``degree_heating_week`` variable.

        Returns:
            Binary label array — 1 if DHW ≥ threshold, else 0.
        """
        dhw_threshold = self.cfg.processing.dhw_threshold
        if "degree_heating_week" in ds:
            dhw = ds["degree_heating_week"].mean(dim=["lat", "lon"]).values
            labels = (dhw >= dhw_threshold).astype(np.float32)
        else:
            labels = np.zeros(len(ds.time), dtype=np.float32)
        logger.info(f"Bleaching labels: {labels.sum():.0f}/{len(labels)} positive (DHW≥{dhw_threshold})")
        return labels

    def subset_reef(self, ds: xr.Dataset, reef_name: str) -> xr.Dataset:
        if reef_name not in self.reef_regions:
            raise KeyError(f"Reef region '{reef_name}' not found. Available: {list(self.reef_regions.keys())}")
        region = self.reef_regions[reef_name]
        return ds.sel(
            lat=slice(region["lat_min"], region["lat_max"]),
            lon=slice(region["lon_min"], region["lon_max"]),
        )

    def get_metadata(self) -> dict[str, Any]:
        return {
            "name": "NOAA Coral Reef Watch",
            "source": "NOAA",
            "product": "CRW v3.1",
            "variables": self.variables,
            "spatial_resolution": "0.05° (~5 km)",
            "temporal_range": f"{self.cfg.temporal.start_year}–{self.cfg.temporal.end_year}",
            "license": "NOAA (open)",
            "reef_regions": list(self.reef_regions.keys()),
            "bleaching_threshold": f"{self.cfg.processing.dhw_threshold} °C-weeks",
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
        logger.warning("Generating synthetic CRW data")
        n_time = 52 * 10  # 10 years of weekly data
        n_lat, n_lon = 30, 30
        time = xr.cftime_range(start="2010-01-01", periods=n_time, freq="W")
        lat = np.linspace(-25, -10, n_lat)
        lon = np.linspace(142, 155, n_lon)
        rng = np.random.default_rng(42)

        sst_anom = rng.standard_normal((n_time, n_lat, n_lon)).astype(np.float32) * 0.5
        # Simulate warming events
        for year_offset in [3, 6, 9]:
            start = year_offset * 52
            end = min(start + 20, n_time)
            sst_anom[start:end] += 2.0

        dhw = np.cumsum(np.maximum(sst_anom - 1.0, 0), axis=0).astype(np.float32)
        dhw = np.clip(dhw, 0, 20)

        return xr.Dataset(
            {
                "sst_anomaly": (["time", "lat", "lon"], sst_anom),
                "degree_heating_week": (["time", "lat", "lon"], dhw),
                "hotspot": (["time", "lat", "lon"], np.maximum(sst_anom, 0)),
            },
            coords={"time": time, "lat": lat, "lon": lon},
        )
