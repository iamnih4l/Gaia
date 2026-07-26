"""Gaia Datasets — Climate data loaders for tipping point detection.

This package provides unified interfaces for loading and preprocessing major
climate datasets including ERA5, CMIP6, MODIS, GRACE, NOAA Coral Reef Watch,
NSIDC Sea Ice Index, and RAPID AMOC measurements.

All loaders inherit from :class:`BaseClimateDataset` and return xarray-native
data structures with lazy loading and Dask-backed parallel processing.
"""

from datasets.base import BaseClimateDataset
from datasets.registry import DatasetRegistry
import datasets.era5
import datasets.cmip6
import datasets.amoc
import datasets.coral_reef
import datasets.sea_ice
import datasets.grace
import datasets.modis

__all__ = [
    "BaseClimateDataset",
    "DatasetRegistry",
]
