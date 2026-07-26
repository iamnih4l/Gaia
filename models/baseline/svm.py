"""SVM baseline for climate tipping point detection."""

from __future__ import annotations

import numpy as np
from loguru import logger
from omegaconf import DictConfig
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


class SVMBaseline:
    """Support Vector Machine classifier with RBF kernel.

    Args:
        cfg: Model config from ``configs/model/svm.yaml``.
    """

    def __init__(self, cfg: DictConfig) -> None:
        arch = cfg.architecture
        self.model = SVC(
            kernel=arch.kernel,
            C=arch.C,
            gamma=arch.gamma,
            class_weight=arch.class_weight,
            probability=arch.probability,
            max_iter=arch.max_iter,
            random_state=42,
        )
        self.scaler = StandardScaler()
        self._fitted = False
        logger.info("Initialized SVMBaseline")

    def fit(self, X: np.ndarray, y: np.ndarray) -> SVMBaseline:
        mask = ~np.isnan(X).any(axis=1) & ~np.isnan(y)
        X_clean, y_clean = X[mask], y[mask]
        X_scaled = self.scaler.fit_transform(X_clean)
        self.model.fit(X_scaled, y_clean)
        self._fitted = True
        logger.info(f"Fitted SVM: {X_clean.shape[0]} samples")
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(self.scaler.transform(np.nan_to_num(X)))

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(self.scaler.transform(np.nan_to_num(X)))[:, 1]
