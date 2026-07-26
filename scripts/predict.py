"""CLI script for running inference on new climate time series data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from loguru import logger
from api.client import GaiaClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Gaia — CLI Prediction Client")
    parser.add_argument("--url", default="http://localhost:8000", help="API server base URL")
    parser.add_argument("--model", default="temporal_fusion_transformer", help="Model architecture")
    parser.add_argument("--element", default="amoc", help="Tipping element (amoc, amazon, etc.)")
    parser.add_argument("--input", type=str, required=True, help="Path to JSON input file containing sequence")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    sequence = data if isinstance(data, list) else data.get("sequence", [])
    logger.info(f"Loaded sequence with {len(sequence)} time steps from {input_path}")

    with GaiaClient(base_url=args.url) as client:
        logger.info(f"Submitting request to {args.url}/predict using model '{args.model}'...")
        response = client.predict(
            sequence=sequence,
            tipping_element=args.element,
            model_name=args.model,
            return_attention_weights=True,
            return_uncertainty=True,
        )

        print("\n" + "=" * 50)
        print(f"PREDICTION RESULT — {response.tipping_element.upper()}")
        print("=" * 50)
        print(f"Model Architecture : {response.model_name}")
        print(f"Tipping Probability: {response.tipping_probability * 100:.2f}%")
        print(f"Alarm Triggered    : {response.alert.alarm_triggered}")
        print(f"Alert Severity     : {response.alert.alert_level}")
        if response.alert.estimated_lead_time_steps is not None:
            print(f"Estimated Lead Time: {response.alert.estimated_lead_time_steps} time steps")
        if response.uncertainty:
            print(f"95% Confidence     : [{response.uncertainty['lower_95']:.4f}, {response.uncertainty['upper_95']:.4f}]")
        print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
