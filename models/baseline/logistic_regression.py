"""Logistic Regression baseline for EWS-based tipping point detection."""

from __future__ import annotations

import numpy as np
from loguru import logger
from omegaconf import DictConfig
from sklearn.linear_model import LogisticRegression as SklearnLR
from sklearn.preprocessing import StandardScaler


class LogisticRegressionBaseline:
    """Logistic regression classifier on handcrafted EWS features.

    Wraps scikit-learn's LogisticRegression with standardized preprocessing
    and a predict_proba interface consistent with deep learning models.

    Args:
        cfg: Model config from ``configs/model/logistic.yaml``.
    """

    def __init__(self, cfg: DictConfig) -> None:
        arch = cfg.architecture
        self.model = SklearnLR(
            penalty=arch.penalty,
            C=arch.C,
            max_iter=arch.max_iter,
            solver=arch.solver,
            class_weight=arch.class_weight,
            random_state=42,
        )
        self.scaler = StandardScaler()
        self._fitted = False
        logger.info("Initialized LogisticRegressionBaseline")

    def fit(self, X: np.ndarray, y: np.ndarray) -> LogisticRegressionBaseline:
        """Fit the model on training features and labels.

        Args:
            X: Feature matrix of shape ``(N, F)``.
            y: Binary labels of shape ``(N,)``.

        Returns:
            Self.
        """
        # Remove NaN rows
        mask = ~np.isnan(X).any(axis=1) & ~np.isnan(y)
        X_clean, y_clean = X[mask], y[mask]

        X_scaled = self.scaler.fit_transform(X_clean)
        self.model.fit(X_scaled, y_clean)
        self._fitted = True

        logger.info(f"Fitted LogisticRegression: {X_clean.shape[0]} samples, {X_clean.shape[1]} features")
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict binary labels."""
        X_scaled = self.scaler.transform(np.nan_to_num(X))
        return self.model.predict(X_scaled)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict tipping probabilities."""
        X_scaled = self.scaler.transform(np.nan_to_num(X))
        return self.model.predict_proba(X_scaled)[:, 1]

    def get_feature_importance(self) -> np.ndarray:
        """Return model coefficients as feature importance."""
        return np.abs(self.model.coef_[0])
