"""Pydantic schemas for the Climate Tipping Point Detection API.

Defines strict request/response data validation models for production inference.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field, conlist


class TimeSeriesDataPoint(BaseModel):
    """Single time step observation of climate features."""

    timestamp: str = Field(..., description="ISO 8601 timestamp or period identifier (e.g., '2024-01-01')")
    features: dict[str, float] = Field(..., description="Feature name to value mapping")


class PredictionRequest(BaseModel):
    """Request schema for tipping point risk prediction."""

    model_name: str = Field(
        default="temporal_fusion_transformer",
        description="Registered model architecture name to use for inference",
    )
    tipping_element: str = Field(
        default="amoc",
        description="Target tipping element (e.g., 'amoc', 'amazon', 'greenland', 'coral', 'sea_ice')",
    )
    sequence: list[TimeSeriesDataPoint] = Field(
        ...,
        min_length=12,
        description="Temporal sequence of historical observations (minimum 12 steps)",
    )
    return_attention_weights: bool = Field(
        default=False,
        description="Whether to return interpretability attention weights/feature importance",
    )
    return_uncertainty: bool = Field(
        default=True,
        description="Whether to compute Monte Carlo dropout uncertainty estimates",
    )


class TippingAlert(BaseModel):
    """Early warning alarm trigger details."""

    alarm_triggered: bool = Field(..., description="True if risk exceeds critical threshold")
    alert_level: str = Field(..., description="Alert severity: 'NORMAL', 'WATCH', 'WARNING', or 'CRITICAL'")
    threshold: float = Field(0.5, description="Decision threshold used for triggering alarm")
    estimated_lead_time_steps: int | None = Field(
        None, description="Estimated time steps before critical transition if alarm is triggered"
    )


class PredictionResponse(BaseModel):
    """Response schema containing prediction results, uncertainty, and alerts."""

    model_name: str = Field(..., description="Model architecture used for inference")
    tipping_element: str = Field(..., description="Target tipping element")
    tipping_probability: float = Field(..., ge=0.0, le=1.0, description="Predicted probability of tipping point transition")
    alert: TippingAlert = Field(..., description="Alert status and lead time estimation")
    uncertainty: dict[str, float] | None = Field(
        None, description="Uncertainty statistics (std, lower_95, upper_95) if requested"
    )
    interpretability: dict[str, Any] | None = Field(
        None, description="Feature importances or attention weights if requested"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Execution metadata (latency_ms, timestamp, model_version)"
    )
