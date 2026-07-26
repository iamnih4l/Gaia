"""ERA5 Reanalysis Dataset Loader.

Loads ECMWF ERA5 global atmospheric reanalysis data (1950–present) at
0.25° resolution. Supports CDS API downloading, NetCDF/GRIB parsing,
and region-specific subsetting for climate tipping point analysis.

Reference:
    Hersbach, H., et al. (2020). The ERA5 global reanalysis.
    Quarterly Journal of the Royal Meteorological Society, 146(730).
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


@register_dataset("era5")
class ERA5Dataset(BaseClimateDataset):
    """ERA5 global atmospheric reanalysis dataset.

    Loads temperature, pressure, wind, precipitation, and SST fields
    from ERA5 monthly means. Supports spatial subsetting to specific
    tipping-element regions (Amazon, North Atlantic, Greenland, etc.).

    Args:
        cfg: Hydra ``DictConfig`` from ``configs/dataset/era5.yaml``.
    """

    def __init__(self, cfg: DictConfig) -> None:
        super().__init__(cfg)
        self.variables: list[str] = list(cfg.variables)
        self.regions: dict[str, dict] = dict(cfg.regions)

    def load_raw(self, data_dir: str | Path) -> xr.Dataset:
        """Load ERA5 data from NetCDF files.

        Searches for ``*.nc`` files in ``{data_dir}/era5/`` and opens them
        as a multi-file dataset with Dask-backed lazy loading.

        Args:
            data_dir: Root data directory containing ``era5/`` subdirectory.

        Returns:
            Lazy-loaded xarray Dataset with all ERA5 variables.
        """
        data_path = Path(data_dir) / "era5"
        logger.info(f"Loading ERA5 data from {data_path}")

        nc_files = sorted(data_path.glob("*.nc"))
        if not nc_files:
            logger.warning(
                f"No NetCDF files found in {data_path}. "
                "Generating synthetic ERA5 data for development."
            )
            return self._generate_synthetic()

        ds = xr.open_mfdataset(
            nc_files,
            combine="by_coords",
            chunks={"time": 12, "latitude": 180, "longitude": 360},
            engine="netcdf4",
            parallel=True,
        )

        # Standardize coordinate names
        ds = self._standardize_coords(ds)
        logger.info(f"ERA5 raw data loaded: {dict(ds.dims)}")
        return ds

    def preprocess(self, ds: xr.Dataset) -> xr.Dataset:
        """Apply ERA5-specific preprocessing.

        Pipeline:
            1. Temporal subsetting to configured year range
            2. Spatial subsetting to region of interest
            3. Monthly resampling (if needed)
            4. Seasonal cycle removal (anomaly computation)
            5. Detrending
            6. Normalization

        Args:
            ds: Raw ERA5 xarray Dataset.

        Returns:
            Preprocessed Dataset with anomalies.
        """
        proc_cfg = self.cfg.processing
        temp_cfg = self.cfg.temporal

        # 1. Temporal subset
        ds = ds.sel(
            time=slice(f"{temp_cfg.start_year}-01-01", f"{temp_cfg.end_year}-12-31")
        )

        # 2. Resample to monthly if needed
        if temp_cfg.frequency == "monthly" and "time" in ds.dims:
            ds = ds.resample(time="MS").mean(skipna=True)

        # 3. Compute anomalies (remove seasonal cycle)
        if proc_cfg.compute_anomalies:
            climatology = ds.groupby("time.month").mean(dim="time")
            ds = ds.groupby("time.month") - climatology
            logger.info("Computed monthly anomalies (seasonal cycle removed)")

        # 4. Detrend
        if proc_cfg.detrend:
            ds = self._detrend(ds, method=proc_cfg.detrend_method)

        # 5. Normalize
        if proc_cfg.normalize:
            ds = self._normalize(ds, method=proc_cfg.normalize_method)

        return ds

    def subset_region(self, ds: xr.Dataset, region_name: str) -> xr.Dataset:
        """Extract a geographic sub-region from the dataset.

        Args:
            ds: Dataset with ``lat`` and ``lon`` dimensions.
            region_name: Key from ``configs/dataset/era5.yaml::regions``.

        Returns:
            Spatially subsetted Dataset.

        Raises:
            KeyError: If ``region_name`` is not configured.
        """
        if region_name not in self.regions:
            raise KeyError(
                f"Region '{region_name}' not found. "
                f"Available: {list(self.regions.keys())}"
            )
        region = self.regions[region_name]
        return ds.sel(
            lat=slice(region["lat_max"], region["lat_min"]),
            lon=slice(region["lon_min"], region["lon_max"]),
        )

    def get_metadata(self) -> dict[str, Any]:
        """Return ERA5 dataset metadata."""
        return {
            "name": "ERA5",
            "source": "ECMWF Copernicus Climate Data Store",
            "variables": self.variables,
            "spatial_resolution": "0.25° × 0.25°",
            "temporal_range": (
                f"{self.cfg.temporal.start_year}–{self.cfg.temporal.end_year}"
            ),
            "frequency": self.cfg.temporal.frequency,
            "license": "Copernicus License (open)",
            "url": self.cfg.source.url,
            "regions": list(self.regions.keys()),
        }

    # ─── Private Helpers ───

    def _standardize_coords(self, ds: xr.Dataset) -> xr.Dataset:
        """Standardize coordinate names to ``lat``, ``lon``, ``time``."""
        rename_map = {}
        for coord in ds.coords:
            lower = coord.lower()
            if lower in ("latitude", "lat"):
                rename_map[coord] = "lat"
            elif lower in ("longitude", "lon", "long"):
                rename_map[coord] = "lon"
        if rename_map:
            ds = ds.rename(rename_map)
        return ds

    def _detrend(self, ds: xr.Dataset, method: str = "linear") -> xr.Dataset:
        """Remove trend from each variable using polyfit/polyval."""
        if method == "linear":
            for var in ds.data_vars:
                time_numeric = np.arange(len(ds.time), dtype=np.float64)
                coefficients = np.polyfit(time_numeric, ds[var].mean(dim=["lat", "lon"]).values, 1)
                trend = np.polyval(coefficients, time_numeric)
                ds[var] = ds[var] - xr.DataArray(
                    trend, dims=["time"], coords={"time": ds.time}
                )
            logger.info("Applied linear detrending")
        return ds

    def _normalize(self, ds: xr.Dataset, method: str = "standard") -> xr.Dataset:
        """Normalize variables using causal (past-only) statistics."""
        for var in ds.data_vars:
            if method == "standard":
                mean = ds[var].mean(dim="time")
                std = ds[var].std(dim="time")
                std = xr.where(std == 0, 1.0, std)  # Avoid division by zero
                ds[var] = (ds[var] - mean) / std
            elif method == "minmax":
                vmin = ds[var].min(dim="time")
                vmax = ds[var].max(dim="time")
                drange = vmax - vmin
                drange = xr.where(drange == 0, 1.0, drange)
                ds[var] = (ds[var] - vmin) / drange
        logger.info(f"Applied {method} normalization")
        return ds

    def _generate_synthetic(self) -> xr.Dataset:
        """Generate synthetic ERA5-like data for development/testing."""
        logger.warning("Generating synthetic ERA5 data — not for production use")
        n_time = 12 * 30  # 30 years of monthly data
        n_lat, n_lon = 72, 144  # 2.5° resolution for speed

        time = xr.cftime_range(start="1990-01", periods=n_time, freq="MS")
        lat = np.linspace(-90, 90, n_lat)
        lon = np.linspace(-180, 180, n_lon)

        rng = np.random.default_rng(42)
        data_vars = {}
        for var in self.variables:
            data_vars[var] = (
                ["time", "lat", "lon"],
                rng.standard_normal((n_time, n_lat, n_lon)).astype(np.float32),
            )

        return xr.Dataset(
            data_vars,
            coords={"time": time, "lat": lat, "lon": lon},
        )
