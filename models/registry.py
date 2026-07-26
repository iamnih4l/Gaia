"""Model registry — factory pattern for dynamic model instantiation."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from omegaconf import DictConfig

import torch.nn as nn

_MODEL_REGISTRY: dict[str, type[nn.Module]] = {}


def register_model(name: str):
    """Register a model class. Usage: ``@register_model("transformer")``."""
    def decorator(cls: type[nn.Module]) -> type[nn.Module]:
        if name in _MODEL_REGISTRY:
            raise ValueError(f"Model '{name}' already registered by {_MODEL_REGISTRY[name].__name__}")
        _MODEL_REGISTRY[name] = cls
        return cls
    return decorator


def get_model(name: str) -> type[nn.Module]:
    """Retrieve a registered model class by name."""
    if name not in _MODEL_REGISTRY:
        available = ", ".join(sorted(_MODEL_REGISTRY.keys()))
        raise KeyError(f"Model '{name}' not found. Available: [{available}]")
    return _MODEL_REGISTRY[name]


def create_model(cfg: DictConfig) -> nn.Module:
    """Factory: instantiate a model from Hydra config."""
    model_cls = get_model(cfg.type)
    return model_cls(cfg)


def list_models() -> list[str]:
    return sorted(_MODEL_REGISTRY.keys())


class ModelRegistry:
    register = staticmethod(register_model)
    get = staticmethod(get_model)
    create = staticmethod(create_model)
    list = staticmethod(list_models)
