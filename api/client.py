"""Python SDK Client for querying the Gaia Inference Server.

Provides a clean, programmatic interface for researchers and automated systems
to submit climate time series and receive tipping risk predictions.
"""

from __future__ import annotations

from typing import Any
import httpx
from loguru import logger
from api.schemas import PredictionRequest, PredictionResponse, TimeSeriesDataPoint


class GaiaClient:
    """Python SDK client for communicating with the Gaia API.

    Args:
        base_url: Root URL of the deployed API (default: 'http://localhost:8000').
        timeout: Request timeout in seconds.
    """

    def __init__(self, base_url: str = "http://localhost:8000", timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = httpx.Client(base_url=self.base_url, timeout=self.timeout)
        logger.info(f"Initialized GaiaClient connected to {self.base_url}")

    def health(self) -> dict[str, Any]:
        """Check API liveness and GPU availability."""
        response = self._client.get("/health")
        response.raise_for_status()
        return response.json()

    def list_models(self) -> list[str]:
        """Retrieve available model architectures from the server."""
        response = self._client.get("/models")
        response.raise_for_status()
        return response.json().get("models", [])

    def predict(
        self,
        sequence: list[dict[str, Any]],
        tipping_element: str = "amoc",
        model_name: str = "temporal_fusion_transformer",
        return_attention_weights: bool = True,
        return_uncertainty: bool = True,
    ) -> PredictionResponse:
        """Submit time series data and receive tipping probability and alarms.

        Args:
            sequence: List of dicts with 'timestamp' and 'features' mappings.
            tipping_element: Target tipping element ('amoc', 'amazon', etc.).
            model_name: Neural network or baseline architecture name.
            return_attention_weights: Include interpretability weights in response.
            return_uncertainty: Include 95% confidence intervals in response.

        Returns:
            Pydantic PredictionResponse object.
        """
        data_points = [
            TimeSeriesDataPoint(timestamp=str(pt["timestamp"]), features=pt["features"])
            for pt in sequence
        ]

        payload = PredictionRequest(
            model_name=model_name,
            tipping_element=tipping_element,
            sequence=data_points,
            return_attention_weights=return_attention_weights,
            return_uncertainty=return_uncertainty,
        )

        response = self._client.post("/predict", json=payload.model_dump())
        response.raise_for_status()
        return PredictionResponse.model_validate(response.json())

    def close(self) -> None:
        """Close underlying HTTP connections."""
        self._client.close()

    def __enter__(self) -> GaiaClient:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()
