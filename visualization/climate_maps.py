"""Climate maps — geospatial heatmaps, risk maps, anomaly visualizations."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from loguru import logger


class ClimateMapPlotter:
    """Publication-quality geospatial climate visualizations."""

    STYLE_DEFAULTS = {
        "figure.facecolor": "#0a0a0a",
        "axes.facecolor": "#0a0a0a",
        "text.color": "#e0e0e0",
        "axes.labelcolor": "#e0e0e0",
        "xtick.color": "#e0e0e0",
        "ytick.color": "#e0e0e0",
    }

    @staticmethod
    def plot_spatial_heatmap(
        data: np.ndarray,
        lat: np.ndarray,
        lon: np.ndarray,
        title: str = "Climate Anomaly Map",
        cmap: str = "RdBu_r",
        save_path: str | Path | None = None,
        use_cartopy: bool = True,
    ) -> plt.Figure:
        """Plot a geospatial heatmap.

        Args:
            data: 2-D array ``(lat, lon)`` of values.
            lat: Latitude coordinates.
            lon: Longitude coordinates.
            title: Plot title.
            cmap: Colormap name.
            save_path: Optional path to save figure.
            use_cartopy: Use cartopy for map projection.

        Returns:
            Matplotlib Figure.
        """
        with plt.rc_context(ClimateMapPlotter.STYLE_DEFAULTS):
            fig, ax = plt.subplots(1, 1, figsize=(14, 8))

            if use_cartopy:
                try:
                    import cartopy.crs as ccrs
                    import cartopy.feature as cfeature

                    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
                    ax.add_feature(cfeature.COASTLINE, linewidth=0.5, color="#888888")
                    ax.add_feature(cfeature.BORDERS, linewidth=0.3, color="#666666")
                    im = ax.pcolormesh(lon, lat, data, cmap=cmap, transform=ccrs.PlateCarree())
                    ax.gridlines(draw_labels=True, alpha=0.3)
                except ImportError:
                    im = ax.pcolormesh(lon, lat, data, cmap=cmap)
                    ax.set_xlabel("Longitude")
                    ax.set_ylabel("Latitude")
            else:
                im = ax.pcolormesh(lon, lat, data, cmap=cmap)
                ax.set_xlabel("Longitude")
                ax.set_ylabel("Latitude")

            cbar = plt.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
            cbar.ax.tick_params(colors="#e0e0e0")
            ax.set_title(title, fontsize=16, fontweight="bold", pad=15)

            plt.tight_layout()

            if save_path:
                fig.savefig(save_path, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
                logger.info(f"Saved map: {save_path}")

            return fig

    @staticmethod
    def plot_risk_map(
        risk_values: np.ndarray,
        lat: np.ndarray,
        lon: np.ndarray,
        title: str = "Tipping Risk Map",
        save_path: str | Path | None = None,
    ) -> plt.Figure:
        """Plot tipping point risk concentration map.

        Args:
            risk_values: 2-D risk probability array ``(lat, lon)``.
            lat: Latitude coordinates.
            lon: Longitude coordinates.
            title: Plot title.
            save_path: Optional save path.

        Returns:
            Matplotlib Figure.
        """
        return ClimateMapPlotter.plot_spatial_heatmap(
            data=risk_values,
            lat=lat,
            lon=lon,
            title=title,
            cmap="YlOrRd",
            save_path=save_path,
        )
