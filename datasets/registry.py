"""Dataset registry for dynamic dataset instantiation via configuration."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from omegaconf import DictConfig

    from datasets.base import BaseClimateDataset

# ─── Global Registry ───
_DATASET_REGISTRY: dict[str, type[BaseClimateDataset]] = {}


def register_dataset(name: str):
    """Decorator to register a dataset class in the global registry.

    Args:
        name: Unique identifier for the dataset (e.g., ``"era5"``).

    Returns:
        Decorator function that registers the class and returns it unchanged.

    Example::

        @register_dataset("era5")
        class ERA5Dataset(BaseClimateDataset):
            ...
    """

    def decorator(cls: type[BaseClimateDataset]) -> type[BaseClimateDataset]:
        if name in _DATASET_REGISTRY:
            raise ValueError(
                f"Dataset '{name}' is already registered by {_DATASET_REGISTRY[name].__name__}."
            )
        _DATASET_REGISTRY[name] = cls
        return cls

    return decorator


def get_dataset(name: str) -> type[BaseClimateDataset]:
    """Retrieve a registered dataset class by name.

    Args:
        name: Registered dataset identifier.

    Returns:
        The dataset class.

    Raises:
        KeyError: If the dataset name is not registered.
    """
    if name not in _DATASET_REGISTRY:
        available = ", ".join(sorted(_DATASET_REGISTRY.keys()))
        raise KeyError(
            f"Dataset '{name}' not found. Available datasets: [{available}]"
        )
    return _DATASET_REGISTRY[name]


def create_dataset(cfg: DictConfig) -> BaseClimateDataset:
    """Factory function to create a dataset from a Hydra config.

    Args:
        cfg: Hydra ``DictConfig`` with a ``name`` key matching a registered dataset.

    Returns:
        An instantiated dataset object.
    """
    dataset_cls = get_dataset(cfg.name)
    return dataset_cls(cfg)


def list_datasets() -> list[str]:
    """Return sorted list of all registered dataset names."""
    return sorted(_DATASET_REGISTRY.keys())


class DatasetRegistry:
    """Namespace for dataset registry operations."""

    register = staticmethod(register_dataset)
    get = staticmethod(get_dataset)
    create = staticmethod(create_dataset)
    list = staticmethod(list_datasets)
