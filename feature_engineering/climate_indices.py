"""Climate indices — domain-specific feature computations.

Computes climate indices relevant to each tipping element:
- Degree Heating Weeks (DHW) for coral bleaching
- Palmer Drought Severity Index proxy for Amazon drought
- ENSO, AMO, NAO teleconnection indices
"""

from __future__ import annotations

import numpy as np
from loguru import logger


class ClimateIndices:
    """Compute domain-specific climate indices for tipping point detection."""

    @staticmethod
    def degree_heating_weeks(
        sst_anomaly: np.ndarray,
        threshold: float = 1.0,
        accumulation_window: int = 12,
    ) -> np.ndarray:
        """Compute Degree Heating Weeks (DHW) for coral bleaching risk.

        DHW accumulates positive SST anomalies above the bleaching threshold
        over the past ``accumulation_window`` weeks.

        Args:
            sst_anomaly: SST anomaly time series (°C above climatology).
            threshold: Temperature above which stress accumulates (default 1°C).
            accumulation_window: Window size for accumulation (weeks).

        Returns:
            DHW values in °C-weeks.
        """
        hotspots = np.maximum(sst_anomaly - threshold, 0.0)

        n = len(hotspots)
        dhw = np.zeros(n, dtype=np.float64)
        for i in range(n):
            start = max(0, i - accumulation_window + 1)
            dhw[i] = np.sum(hotspots[start : i + 1])

        logger.debug(f"Computed DHW: max={dhw.max():.1f} °C-weeks")
        return dhw

    @staticmethod
    def drought_severity_proxy(
        precipitation: np.ndarray,
        temperature: np.ndarray,
        window: int = 12,
    ) -> np.ndarray:
        """Compute a simplified drought severity proxy (PDSI-like).

        Uses the balance between precipitation and temperature-driven
        evapotranspiration as a drought indicator.

        Args:
            precipitation: Precipitation anomaly series.
            temperature: Temperature anomaly series.
            window: Smoothing window (months).

        Returns:
            Drought severity index (negative = dry).
        """
        # Simplified water balance: P - f(T)
        pet_proxy = 0.5 * temperature  # Simplified potential ET
        water_balance = precipitation - pet_proxy

        # Rolling mean
        n = len(water_balance)
        result = np.full(n, np.nan, dtype=np.float64)
        for i in range(window - 1, n):
            result[i] = np.nanmean(water_balance[i - window + 1 : i + 1])

        logger.debug(f"Computed drought severity proxy: window={window}")
        return result

    @staticmethod
    def enso_index(
        sst_nino34: np.ndarray,
        window: int = 5,
    ) -> np.ndarray:
        """Compute ENSO index from Niño 3.4 SST anomalies.

        Args:
            sst_nino34: SST anomaly in the Niño 3.4 region (5°N-5°S, 170°W-120°W).
            window: Running mean window (months) for smoothing.

        Returns:
            ENSO index (positive = El Niño, negative = La Niña).
        """
        n = len(sst_nino34)
        result = np.full(n, np.nan, dtype=np.float64)
        for i in range(window - 1, n):
            result[i] = np.nanmean(sst_nino34[i - window + 1 : i + 1])
        return result

    @staticmethod
    def atlantic_multidecadal_oscillation(
        sst_north_atlantic: np.ndarray,
        sst_global: np.ndarray,
    ) -> np.ndarray:
        """Compute AMO index as detrended North Atlantic SST anomaly.

        Args:
            sst_north_atlantic: Area-averaged SST anomaly for North Atlantic.
            sst_global: Global mean SST anomaly (for detrending).

        Returns:
            AMO index values.
        """
        amo = sst_north_atlantic - sst_global
        logger.debug("Computed AMO index")
        return amo

    @staticmethod
    def ice_mass_rate(
        mass_anomaly: np.ndarray,
        dt: float = 1.0,
    ) -> np.ndarray:
        """Compute ice mass loss rate (first derivative).

        Args:
            mass_anomaly: Ice mass anomaly time series (Gt).
            dt: Time step (e.g., 1 month).

        Returns:
            Rate of mass change (Gt/month).
        """
        rate = np.gradient(mass_anomaly, dt)
        logger.debug(f"Computed ice mass rate: mean={np.nanmean(rate):.2f} Gt/month")
        return rate

    @staticmethod
    def ice_mass_acceleration(
        mass_anomaly: np.ndarray,
        dt: float = 1.0,
    ) -> np.ndarray:
        """Compute ice mass acceleration (second derivative).

        Acceleration indicates whether ice loss is speeding up.

        Args:
            mass_anomaly: Ice mass anomaly time series.
            dt: Time step.

        Returns:
            Mass acceleration (Gt/month²).
        """
        rate = np.gradient(mass_anomaly, dt)
        acceleration = np.gradient(rate, dt)
        return acceleration
