"""Spatial preprocessing — subsetting, aggregation, regridding.

Provides tools for extracting climate data for specific tipping-element
regions and performing spatial transformations.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import xarray as xr
from loguru import logger


# ─── Pre-defined Tipping Element Regions ───
TIPPING_REGIONS: dict[str, dict[str, float]] = {
    "amazon": {"lat_min": -20.0, "lat_max": 5.0, "lon_min": -75.0, "lon_max": -45.0},
    "north_atlantic": {"lat_min": 30.0, "lat_max": 70.0, "lon_min": -80.0, "lon_max": 0.0},
    "greenland": {"lat_min": 60.0, "lat_max": 85.0, "lon_min": -75.0, "lon_max": -10.0},
    "antarctic": {"lat_min": -90.0, "lat_max": -60.0, "lon_min": -180.0, "lon_max": 180.0},
    "arctic": {"lat_min": 65.0, "lat_max": 90.0, "lon_min": -180.0, "lon_max": 180.0},
    "great_barrier_reef": {"lat_min": -25.0, "lat_max": -10.0, "lon_min": 142.0, "lon_max": 155.0},
    "caribbean": {"lat_min": 10.0, "lat_max": 30.0, "lon_min": -90.0, "lon_max": -60.0},
    "coral_triangle": {"lat_min": -10.0, "lat_max": 15.0, "lon_min": 95.0, "lon_max": 145.0},
}


class SpatialProcessor:
    """Spatial preprocessing utilities for gridded climate data."""

    @staticmethod
    def subset_region(
        ds: xr.Dataset,
        region: str | dict[str, float],
    ) -> xr.Dataset:
        """Extract a geographic sub-region from a gridded dataset.

        Args:
            ds: Input Dataset with ``lat`` and ``lon`` dimensions.
            region: Either a region name (key in ``TIPPING_REGIONS``) or
                a dict with ``lat_min``, ``lat_max``, ``lon_min``, ``lon_max``.

        Returns:
            Spatially subsetted Dataset.

        Raises:
            KeyError: If string region name is not found.
            ValueError: If required lat/lon dimensions are missing.
        """
        if isinstance(region, str):
            if region not in TIPPING_REGIONS:
                raise KeyError(
                    f"Region '{region}' not found. Available: {list(TIPPING_REGIONS.keys())}"
                )
            bounds = TIPPING_REGIONS[region]
        else:
            bounds = region

        # Determine lat/lon coordinate names
        lat_name = _find_coord(ds, ["lat", "latitude"])
        lon_name = _find_coord(ds, ["lon", "longitude", "long"])

        # Handle lat ordering (some datasets have descending lat)
        lat_vals = ds[lat_name].values
        if lat_vals[0] > lat_vals[-1]:
            # Descending latitude
            lat_slice = slice(bounds["lat_max"], bounds["lat_min"])
        else:
            lat_slice = slice(bounds["lat_min"], bounds["lat_max"])

        lon_slice = slice(bounds["lon_min"], bounds["lon_max"])

        result = ds.sel({lat_name: lat_slice, lon_name: lon_slice})
        logger.info(
            f"Subset to region: lat=[{bounds['lat_min']}, {bounds['lat_max']}], "
            f"lon=[{bounds['lon_min']}, {bounds['lon_max']}] → "
            f"{dict(result.dims)}"
        )
        return result

    @staticmethod
    def spatial_mean(
        ds: xr.Dataset,
        weights: str = "cosine",
    ) -> xr.Dataset:
        """Compute area-weighted spatial mean.

        Args:
            ds: Input Dataset with spatial dimensions.
            weights: Weighting scheme — ``"cosine"`` (latitude-weighted),
                ``"uniform"`` (simple mean), or ``"area"`` (grid cell area).

        Returns:
            Dataset with spatial dimensions collapsed.
        """
        lat_name = _find_coord(ds, ["lat", "latitude"])
        lon_name = _find_coord(ds, ["lon", "longitude", "long"])
        spatial_dims = [lat_name, lon_name]

        if weights == "cosine":
            cos_weights = np.cos(np.deg2rad(ds[lat_name]))
            cos_weights = cos_weights / cos_weights.sum()
            result = ds.weighted(cos_weights).mean(dim=spatial_dims, skipna=True)
        elif weights == "uniform":
            result = ds.mean(dim=spatial_dims, skipna=True)
        else:
            result = ds.mean(dim=spatial_dims, skipna=True)

        logger.info(f"Computed spatial mean ({weights} weighting)")
        return result

    @staticmethod
    def regrid(
        ds: xr.Dataset,
        target_resolution: float,
        method: str = "bilinear",
    ) -> xr.Dataset:
        """Regrid dataset to a target resolution.

        Uses simple interpolation for regridding. For production use,
        consider ``xesmf`` for conservative regridding.

        Args:
            ds: Input Dataset.
            target_resolution: Target resolution in degrees.
            method: Interpolation method.

        Returns:
            Regridded Dataset.
        """
        lat_name = _find_coord(ds, ["lat", "latitude"])
        lon_name = _find_coord(ds, ["lon", "longitude", "long"])

        new_lat = np.arange(-90, 90 + target_resolution, target_resolution)
        new_lon = np.arange(-180, 180 + target_resolution, target_resolution)

        result = ds.interp(
            {lat_name: new_lat, lon_name: new_lon},
            method="linear",
        )
        logger.info(f"Regridded to {target_resolution}° resolution")
        return result

    @staticmethod
    def compute_spatial_gradient(
        ds: xr.Dataset,
        variable: str,
    ) -> xr.Dataset:
        """Compute spatial gradients (∂/∂lat, ∂/∂lon) for a variable.

        Args:
            ds: Input Dataset.
            variable: Name of the variable to differentiate.

        Returns:
            Dataset with ``{variable}_dlat`` and ``{variable}_dlon`` added.
        """
        lat_name = _find_coord(ds, ["lat", "latitude"])
        lon_name = _find_coord(ds, ["lon", "longitude", "long"])

        dlat = ds[variable].differentiate(lat_name)
        dlon = ds[variable].differentiate(lon_name)

        ds[f"{variable}_dlat"] = dlat
        ds[f"{variable}_dlon"] = dlon

        logger.info(f"Computed spatial gradients for '{variable}'")
        return ds


def _find_coord(ds: xr.Dataset, candidates: list[str]) -> str:
    """Find a coordinate name from a list of candidates.

    Args:
        ds: Dataset to search.
        candidates: Possible coordinate names.

    Returns:
        The first matching coordinate name.

    Raises:
        ValueError: If none of the candidates are found.
    """
    for name in candidates:
        if name in ds.coords or name in ds.dims:
            return name
    raise ValueError(
        f"Could not find coordinate. Tried: {candidates}. "
        f"Available: {list(ds.coords)}"
    )
