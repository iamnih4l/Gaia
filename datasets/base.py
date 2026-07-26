"""Base climate dataset — abstract interface for all data loaders.

Every dataset in the project must inherit from :class:`BaseClimateDataset`
and implement the required abstract methods. This ensures a consistent API
across ERA5, CMIP6, MODIS, GRACE, Coral, Sea Ice, and AMOC loaders.
"""

from __future__ import annotations

import abc
from pathlib import Path
from typing import Any

import numpy as np
import torch
import xarray as xr
from loguru import logger
from omegaconf import DictConfig
from torch.utils.data import DataLoader, Dataset


class ClimateTimeSeriesDataset(Dataset):
    """PyTorch dataset wrapping windowed climate time series for model training.

    Converts an (N, T, F) numpy array of pre-processed climate features into
    overlapping windows of length ``seq_len`` with associated binary labels.

    Args:
        features: Array of shape ``(T, F)`` — time steps × feature channels.
        labels: Array of shape ``(T,)`` — binary tipping labels per time step.
        seq_len: Number of time steps per input window.
        stride: Stride between consecutive windows.
    """

    def __init__(
        self,
        features: np.ndarray,
        labels: np.ndarray,
        seq_len: int = 60,
        stride: int = 1,
    ) -> None:
        super().__init__()
        if features.shape[0] != labels.shape[0]:
            raise ValueError(
                f"Feature length {features.shape[0]} != label length {labels.shape[0]}"
            )
        self.features = torch.as_tensor(features, dtype=torch.float32)
        self.labels = torch.as_tensor(labels, dtype=torch.float32)
        self.seq_len = seq_len
        self.stride = stride

        # Pre-compute valid window indices
        n_samples = features.shape[0]
        self.indices = list(range(0, n_samples - seq_len + 1, stride))
        logger.debug(
            f"Created ClimateTimeSeriesDataset: {len(self.indices)} windows, "
            f"seq_len={seq_len}, stride={stride}, features={features.shape[1]}"
        )

    def __len__(self) -> int:
        return len(self.indices)

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
        start = self.indices[idx]
        end = start + self.seq_len
        return {
            "input": self.features[start:end],        # (seq_len, F)
            "label": self.labels[end - 1 : end],       # (1,)
            "timestamp_idx": torch.tensor(end - 1),    # for lead-time computation
        }


class BaseClimateDataset(abc.ABC):
    """Abstract base class for all climate dataset loaders.

    Subclasses must implement :meth:`load_raw`, :meth:`preprocess`, and
    :meth:`get_metadata`. The base class provides shared utilities for
    splitting, DataLoader creation, and caching.

    Args:
        cfg: Hydra ``DictConfig`` containing dataset-specific parameters.
    """

    def __init__(self, cfg: DictConfig) -> None:
        self.cfg = cfg
        self.name: str = cfg.name
        self._raw_data: xr.Dataset | None = None
        self._processed_data: xr.Dataset | None = None
        self._features: np.ndarray | None = None
        self._labels: np.ndarray | None = None
        logger.info(f"Initializing dataset: {self.name}")

    # ─── Abstract Methods ───

    @abc.abstractmethod
    def load_raw(self, data_dir: str | Path) -> xr.Dataset:
        """Load raw data from disk or remote source.

        Args:
            data_dir: Root directory for raw data files.

        Returns:
            Raw xarray Dataset with original resolution and variables.
        """

    @abc.abstractmethod
    def preprocess(self, ds: xr.Dataset) -> xr.Dataset:
        """Apply dataset-specific preprocessing.

        Includes temporal harmonization, spatial subsetting, anomaly
        computation, detrending, and normalization — all configured
        via the Hydra config.

        Args:
            ds: Raw xarray Dataset.

        Returns:
            Preprocessed xarray Dataset ready for feature engineering.
        """

    @abc.abstractmethod
    def get_metadata(self) -> dict[str, Any]:
        """Return dataset metadata for documentation and logging.

        Returns:
            Dictionary with keys like ``source``, ``variables``,
            ``spatial_resolution``, ``temporal_range``, etc.
        """

    # ─── Concrete Methods ───

    def load(self, data_dir: str | Path) -> xr.Dataset:
        """Load and preprocess the dataset (with caching).

        Args:
            data_dir: Root directory for raw data files.

        Returns:
            Preprocessed xarray Dataset.
        """
        logger.info(f"Loading dataset '{self.name}' from {data_dir}")
        self._raw_data = self.load_raw(data_dir)
        self._processed_data = self.preprocess(self._raw_data)
        logger.info(
            f"Dataset '{self.name}' loaded: "
            f"{dict(self._processed_data.dims)}"
        )
        return self._processed_data

    def to_numpy(
        self,
        ds: xr.Dataset | None = None,
        variables: list[str] | None = None,
    ) -> np.ndarray:
        """Convert xarray Dataset to numpy array.

        Args:
            ds: Dataset to convert. Uses ``self._processed_data`` if None.
            variables: Specific variables to include. Uses all if None.

        Returns:
            Array of shape ``(T, N_vars)`` for univariate spatial mean,
            or ``(T, lat, lon, N_vars)`` for spatial data.
        """
        if ds is None:
            if self._processed_data is None:
                raise RuntimeError("No processed data available. Call load() first.")
            ds = self._processed_data

        if variables is None:
            variables = list(ds.data_vars)

        arrays = [ds[var].values for var in variables]
        return np.stack(arrays, axis=-1)

    def get_splits(
        self,
        features: np.ndarray,
        labels: np.ndarray,
        train_ratio: float = 0.7,
        val_ratio: float = 0.15,
    ) -> dict[str, tuple[np.ndarray, np.ndarray]]:
        """Split data temporally into train/val/test sets.

        Uses temporal ordering (no shuffling) to prevent data leakage.

        Args:
            features: Array of shape ``(T, F)``.
            labels: Array of shape ``(T,)``.
            train_ratio: Fraction of data for training.
            val_ratio: Fraction of data for validation.

        Returns:
            Dictionary with ``"train"``, ``"val"``, ``"test"`` keys,
            each mapping to ``(features, labels)`` tuple.
        """
        n = len(features)
        train_end = int(n * train_ratio)
        val_end = int(n * (train_ratio + val_ratio))

        splits = {
            "train": (features[:train_end], labels[:train_end]),
            "val": (features[train_end:val_end], labels[train_end:val_end]),
            "test": (features[val_end:], labels[val_end:]),
        }

        for split_name, (feat, lab) in splits.items():
            logger.info(
                f"  {split_name}: {len(feat)} samples, "
                f"positive rate: {lab.mean():.3f}"
            )

        return splits

    def to_dataloaders(
        self,
        features: np.ndarray,
        labels: np.ndarray,
        seq_len: int = 60,
        stride: int = 1,
        batch_size: int = 32,
        num_workers: int = 4,
        pin_memory: bool = True,
    ) -> dict[str, DataLoader]:
        """Create train/val/test DataLoaders from features and labels.

        Args:
            features: Array of shape ``(T, F)``.
            labels: Array of shape ``(T,)``.
            seq_len: Window length for each sample.
            stride: Stride between consecutive windows.
            batch_size: Batch size for DataLoaders.
            num_workers: Number of data loading workers.
            pin_memory: Whether to pin memory for GPU transfer.

        Returns:
            Dictionary with ``"train"``, ``"val"``, ``"test"`` DataLoaders.
        """
        train_ratio = self.cfg.loader.get("train_ratio", 0.7)
        val_ratio = self.cfg.loader.get("val_ratio", 0.15)
        splits = self.get_splits(features, labels, train_ratio, val_ratio)

        loaders = {}
        for split_name, (feat, lab) in splits.items():
            dataset = ClimateTimeSeriesDataset(
                features=feat,
                labels=lab,
                seq_len=seq_len,
                stride=stride if split_name == "train" else seq_len,
            )
            loaders[split_name] = DataLoader(
                dataset,
                batch_size=batch_size,
                shuffle=(split_name == "train"),
                num_workers=num_workers,
                pin_memory=pin_memory,
                drop_last=(split_name == "train"),
            )

        return loaders

    def __repr__(self) -> str:
        status = "loaded" if self._processed_data is not None else "not loaded"
        return f"{self.__class__.__name__}(name='{self.name}', status={status})"
