"""Random Forest baseline for climate tipping point detection."""

from __future__ import annotations

import numpy as np
from loguru import logger
from omegaconf import DictConfig
from sklearn.ensemble import RandomForestClassifier


class RandomForestBaseline:
    """Random forest classifier on EWS features.

    Args:
        cfg: Model config from ``configs/model/random_forest.yaml``.
    """

    def __init__(self, cfg: DictConfig) -> None:
        arch = cfg.architecture
        self.model = RandomForestClassifier(
            n_estimators=arch.n_estimators,
            max_depth=arch.max_depth,
            min_samples_split=arch.min_samples_split,
            min_samples_leaf=arch.min_samples_leaf,
            max_features=arch.max_features,
            class_weight=arch.class_weight,
            n_jobs=arch.n_jobs,
            random_state=arch.random_state,
        )
        self._fitted = False
        logger.info("Initialized RandomForestBaseline")

    def fit(self, X: np.ndarray, y: np.ndarray) -> RandomForestBaseline:
        mask = ~np.isnan(X).any(axis=1) & ~np.isnan(y)
        X_clean, y_clean = X[mask], y[mask]
        self.model.fit(X_clean, y_clean)
        self._fitted = True
        logger.info(f"Fitted RandomForest: {X_clean.shape[0]} samples")
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(np.nan_to_num(X))

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(np.nan_to_num(X))[:, 1]

    def get_feature_importance(self) -> np.ndarray:
        return self.model.feature_importances_
