"""
Production-ready Flask API for climatological solar generation prediction.

Endpoints
---------
- POST /api/v1/predict-generation
- GET  /api/v1/health
- GET  /api/v1/model-info

The API wraps the core prediction and lifetime functions defined in
`solar_climatology_service.py` and serves JSON responses suitable for a frontend.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, request
from flask_cors import CORS

from solar_climatology_service import (
    FEATURE_COLUMNS,
    DRY_MONTHS,
    get_model_paths,
    load_model_artifacts,
    predict_lifetime_generation,
    predict_solar_generation,
    validate_coordinates,
)


app = Flask(__name__)
CORS(app)  # Enable CORS for all domains by default

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("solar_climatology_api")


def _month_name(month: int) -> str:
    """Return English month name for 1–12."""
    return [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ][month - 1]


def _load_metadata() -> Dict[str, Any]:
    """Load model metadata JSON written by the notebook."""
    paths = get_model_paths()
    if not paths.metadata_path.exists():
        raise FileNotFoundError(
            f"Metadata file '{paths.metadata_path}' not found. "
            "Run the climatological notebook to save model artifacts."
        )
    return json.loads(paths.metadata_path.read_text())


@app.before_request
def log_request() -> None:
    """Simple request logging for observability."""
    logger.info(
        "Request: %s %s from %s", request.method, request.path, request.remote_addr
    )


@app.route("/api/v1/health", methods=["GET"])
def health() -> Any:
    """
    Health check endpoint.

    Returns basic status plus last trained timestamp from model metadata.
    """
    try:
        _, _, metadata = load_model_artifacts()
        status = {
            "status": "ok",
            "model_type": metadata.get("model_type"),
            "last_trained_at": metadata.get("created_at_utc"),
            "validation_mape": metadata.get("validation_mape"),
        }
        return jsonify(status)
    except FileNotFoundError as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/v1/model-info", methods=["GET"])
def model_info() -> Any:
    """
    Return model metadata and training configuration.

    Includes:
    - model_type
    - validation_mape
    - training_locations
    - feature_columns
    """
    try:
        _, feature_cols, metadata = load_model_artifacts()
        info = {
            "model_type": metadata.get("model_type"),
            "validation_mape": metadata.get("validation_mape"),
            "training_locations": metadata.get("training_locations"),
            "feature_columns": feature_cols,
        }
        return jsonify(info)
    except FileNotFoundError as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/v1/predict-generation", methods=["POST"])
def api_predict_generation() -> Any:
    """
    Predict typical solar generation and (optionally) lifetime projection.

    Request JSON:
    {
      \"latitude\": float (-26 to 6),
      \"longitude\": float (-18 to 44),
      \"month\": int (1-12, optional),
      \"include_lifetime\": bool (default true)
    }
    """
    try:
        payload: Dict[str, Any] = request.get_json(force=True) or {}

        if "latitude" not in payload or "longitude" not in payload:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Request must include 'latitude' and 'longitude'.",
                    }
                ),
                400,
            )

        latitude = float(payload["latitude"])
        longitude = float(payload["longitude"])
        month_raw: Optional[Any] = payload.get("month")
        include_lifetime = bool(payload.get("include_lifetime", True))

        coord_status = validate_coordinates(latitude, longitude)
        if coord_status.get("status") == "error":
            return jsonify({"status": "error", "message": coord_status["message"]}), 400

        # Month: if provided, use it; otherwise, compute full climatology
        month: Optional[int] = None
        if month_raw is not None:
            month = int(month_raw)
            if not 1 <= month <= 12:
                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": "month must be an integer between 1 and 12.",
                        }
                    ),
                    400,
                )

        # Point prediction(s)
        monthly_generation: List[Dict[str, Any]] = []
        if month is not None:
            daily_kwh = predict_solar_generation(latitude, longitude, month)
            monthly_generation.append(
                {
                    "month": _month_name(month),
                    "month_index": month,
                    "daily_kwh": daily_kwh,
                    "is_dry_season": month in DRY_MONTHS,
                }
            )
            avg_daily_for_annual = daily_kwh
        else:
            # Full climatology across 12 months
            daily_values: List[float] = []
            for m in range(1, 13):
                g = predict_solar_generation(latitude, longitude, m)
                daily_values.append(g)
                monthly_generation.append(
                    {
                        "month": _month_name(m),
                        "month_index": m,
                        "daily_kwh": g,
                        "is_dry_season": m in DRY_MONTHS,
                    }
                )
            avg_daily_for_annual = float(sum(daily_values) / len(daily_values))

        annual_summary = {
            "year_1_generation_kwh": avg_daily_for_annual * 365.0,
            "average_daily_kwh": avg_daily_for_annual,
        }

        lifetime_prediction: Optional[Dict[str, Any]] = None
        if include_lifetime:
            lifetime_prediction = predict_lifetime_generation(latitude, longitude)

        assumptions = lifetime_prediction["assumptions"] if lifetime_prediction else {
            "panel_area_m2": 10.0,
            "panel_efficiency_pct": 20.0,
            "note": "Lifetime metrics disabled for this request.",
        }

        confidence = (
            lifetime_prediction["confidence"] if lifetime_prediction else {}
        )

        response = {
            "status": "success",
            "location": {"latitude": latitude, "longitude": longitude},
            "coordinate_validation": coord_status,
            "monthly_generation": monthly_generation,
            "annual_summary": annual_summary,
            "lifetime_prediction": lifetime_prediction,
            "assumptions": assumptions,
            "confidence": confidence,
            "note": "Predictions represent typical expected generation, not a daily weather forecast.",
        }

        return jsonify(response)

    except Exception as e:  # pragma: no cover
        logger.exception("Error in /api/v1/predict-generation")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    # For local development only – in production, use a WSGI server.
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=False)



