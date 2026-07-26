"""Temporal preprocessing — resampling, seasonal cycle removal, detrending.

All operations preserve xarray metadata and operate lazily where possible.
Detrending and anomaly computation use only past data to avoid look-ahead bias.
"""

from __future__ import annotations

import numpy as np
import xarray as xr
from loguru import logger


class TemporalProcessor:
    """Stateless temporal preprocessing operations for climate data.

    Methods are designed to be composable and can be chained in any order,
    though the recommended pipeline is:
    ``resample → remove_seasonal_cycle → detrend``.
    """

    @staticmethod
    def resample(
        ds: xr.Dataset,
        target_freq: str = "MS",
        method: str = "mean",
    ) -> xr.Dataset:
        """Resample dataset to a target temporal frequency.

        Args:
            ds: Input xarray Dataset with a ``time`` dimension.
            target_freq: Pandas frequency alias (e.g., ``"MS"`` for month start,
                ``"QS"`` for quarter start, ``"YS"`` for year start).
            method: Aggregation method — ``"mean"``, ``"sum"``, ``"max"``, ``"min"``.

        Returns:
            Resampled Dataset.
        """
        resampler = ds.resample(time=target_freq)
        aggregator = getattr(resampler, method)
        result = aggregator(skipna=True)
        logger.info(f"Resampled to {target_freq} using {method}: {len(ds.time)} → {len(result.time)} steps")
        return result

    @staticmethod
    def remove_seasonal_cycle(
        ds: xr.Dataset,
        reference_period: tuple[int, int] | None = None,
    ) -> xr.Dataset:
        """Remove the mean seasonal cycle to compute anomalies.

        Args:
            ds: Input Dataset.
            reference_period: Optional ``(start_year, end_year)`` tuple for
                computing climatology. Uses entire record if None.

        Returns:
            Anomaly Dataset (original minus climatology).
        """
        if reference_period is not None:
            clim_ds = ds.sel(
                time=slice(
                    f"{reference_period[0]}-01-01",
                    f"{reference_period[1]}-12-31",
                )
            )
        else:
            clim_ds = ds

        climatology = clim_ds.groupby("time.month").mean(dim="time")
        anomalies = ds.groupby("time.month") - climatology

        logger.info(
            f"Removed seasonal cycle"
            + (f" (reference: {reference_period[0]}–{reference_period[1]})" if reference_period else "")
        )
        return anomalies

    @staticmethod
    def detrend(
        ds: xr.Dataset,
        method: str = "linear",
        degree: int = 1,
    ) -> xr.Dataset:
        """Remove trend from all data variables.

        Args:
            ds: Input Dataset.
            method: Detrending method — ``"linear"``, ``"polynomial"``, ``"loess"``.
            degree: Polynomial degree (only for ``"polynomial"`` method).

        Returns:
            Detrended Dataset.
        """
        if method == "loess":
            return TemporalProcessor._detrend_loess(ds)

        poly_degree = 1 if method == "linear" else degree

        for var in ds.data_vars:
            data = ds[var]
            # Handle spatial dimensions by iterating over them
            if set(data.dims) == {"time"}:
                ds[var] = TemporalProcessor._detrend_1d(data, poly_degree)
            else:
                # Spatial mean detrending (broadcasts back)
                spatial_dims = [d for d in data.dims if d != "time"]
                spatial_mean = data.mean(dim=spatial_dims)
                detrended_mean = TemporalProcessor._detrend_1d(spatial_mean, poly_degree)
                adjustment = detrended_mean - spatial_mean
                ds[var] = data + adjustment

        logger.info(f"Applied {method} detrending (degree={poly_degree})")
        return ds

    @staticmethod
    def _detrend_1d(da: xr.DataArray, degree: int) -> xr.DataArray:
        """Detrend a 1-D time series DataArray."""
        values = da.values.astype(np.float64)
        t = np.arange(len(values), dtype=np.float64)
        valid = ~np.isnan(values)

        if valid.sum() <= degree + 1:
            return da

        coeffs = np.polyfit(t[valid], values[valid], degree)
        trend = np.polyval(coeffs, t)
        detrended = values - trend
        return xr.DataArray(detrended, dims=da.dims, coords=da.coords, name=da.name)

    @staticmethod
    def _detrend_loess(ds: xr.Dataset, frac: float = 0.3) -> xr.Dataset:
        """LOESS detrending using locally weighted regression.

        Falls back to linear detrending if statsmodels is unavailable.
        """
        try:
            from statsmodels.nonparametric.smoothers_lowess import lowess

            for var in ds.data_vars:
                if set(ds[var].dims) == {"time"}:
                    values = ds[var].values.astype(np.float64)
                    t = np.arange(len(values), dtype=np.float64)
                    valid = ~np.isnan(values)
                    if valid.sum() > 10:
                        smoothed = lowess(values[valid], t[valid], frac=frac, return_sorted=True)
                        trend = np.interp(t, smoothed[:, 0], smoothed[:, 1])
                        ds[var] = xr.DataArray(
                            values - trend, dims=["time"], coords={"time": ds.time}
                        )
            logger.info(f"Applied LOESS detrending (frac={frac})")
        except ImportError:
            logger.warning("statsmodels not available, falling back to linear detrending")
            ds = TemporalProcessor.detrend(ds, method="linear")

        return ds

    @staticmethod
    def compute_rolling_statistics(
        ds: xr.Dataset,
        window: int = 12,
        min_periods: int = 6,
        statistics: list[str] | None = None,
    ) -> xr.Dataset:
        """Compute rolling window statistics for all variables.

        Args:
            ds: Input Dataset.
            window: Rolling window size in time steps.
            min_periods: Minimum number of valid observations in window.
            statistics: List of statistics — ``"mean"``, ``"std"``, ``"min"``, ``"max"``.

        Returns:
            Dataset with new variables named ``{var}_rolling_{stat}_{window}``.
        """
        if statistics is None:
            statistics = ["mean", "std"]

        new_vars = {}
        for var in ds.data_vars:
            roller = ds[var].rolling(time=window, min_periods=min_periods, center=False)
            for stat in statistics:
                new_name = f"{var}_rolling_{stat}_{window}"
                new_vars[new_name] = getattr(roller, stat)()

        for name, data in new_vars.items():
            ds[name] = data

        logger.info(f"Computed rolling statistics: {statistics}, window={window}")
        return ds
