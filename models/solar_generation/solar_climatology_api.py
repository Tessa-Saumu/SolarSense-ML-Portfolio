"""
Production-ready Flask API for climatological solar generation prediction.

Security features:
- API key authentication via X-API-KEY header (from .env, not hardcoded).
- Global rate limiting (100 requests per minute) using Flask-Limiter.
- Stricter input validation (numeric ranges, optional business fields).
- Output sanity checks for energy values.
- JSON-only responses with clean 400/401/500 handling (no stack traces in responses).

Endpoints
---------
- POST /api/v1/predict-generation
- GET  /api/v1/health
- GET  /api/v1/model-info
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter              # [SECURITY] rate limiting
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv                # [SECURITY] load API key from .env

from solar_climatology_service import (
    DRY_MONTHS,
    get_model_paths,
    load_model_artifacts,
    predict_lifetime_generation,
    predict_solar_generation,
    validate_coordinates,
)


# ---------------------------------------------------------------------------
# Configuration & setup
# ---------------------------------------------------------------------------

load_dotenv()  # [SECURITY] load environment variables from .env

API_KEY = os.getenv("API_KEY")  # [SECURITY] expected API key (never hardcode)

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains by default

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("solar_climatology_api")

# [SECURITY] Global rate limiter: 100 requests per minute per client
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["100 per minute"],
)


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
            "Metadata file not found. Run the climatological notebook to save model artifacts."
        )
    return json.loads(paths.metadata_path.read_text())


# ---------------------------------------------------------------------------
# Request-level security & validation helpers
# ---------------------------------------------------------------------------

@app.before_request
def security_and_logging() -> Optional[Any]:
    """
    Global request hook for:
    - Logging
    - API key authentication
    """
    logger.info(
        "Request: %s %s from %s", request.method, request.path, request.remote_addr
    )

    # [SECURITY] API key authentication for all API endpoints
    if request.path.startswith("/api/"):
        if not API_KEY:
            # Misconfiguration: API key not set; treat as server error (do not expose details).
            return jsonify({"status": "error", "message": "Internal Server Error"}), 500

        header_key = request.headers.get("X-API-KEY")
        if not header_key or header_key != API_KEY:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Unauthorized",  # [SECURITY] 401 message without details
                    }
                ),
                401,
            )
    return None


def _validate_optional_business_fields(payload: Dict[str, Any]) -> List[str]:
    """
    [SECURITY] Extra input validation for optional fields that may be present.

    - hours_per_day: 0–24
    - equipment_units: 0–500
    - monthly_cost / monthly_consumption_kwh: non-negative
    - business_type, location: simple non-empty string check
    """
    errors: List[str] = []

    # Numeric ranges
    if "hours_per_day" in payload:
        try:
            h = float(payload["hours_per_day"])
            if h < 0 or h > 24:
                errors.append("hours_per_day must be between 0 and 24.")
        except (TypeError, ValueError):
            errors.append("hours_per_day must be numeric.")

    if "equipment_units" in payload:
        try:
            units = float(payload["equipment_units"])
            if units < 0 or units > 500:
                errors.append("equipment_units must be between 0 and 500.")
        except (TypeError, ValueError):
            errors.append("equipment_units must be numeric.")

    for field in ("monthly_cost", "monthly_consumption_kwh"):
        if field in payload:
            try:
                v = float(payload[field])
                if v < 0:
                    errors.append(f"{field} must be non-negative.")
            except (TypeError, ValueError):
                errors.append(f"{field} must be numeric.")

    # Simple format checks for strings
    def _check_str(name: str) -> None:
        v = payload.get(name)
        if v is None:
            return
        if not isinstance(v, str) or not v.strip():
            errors.append(f"{name} must be a non-empty string.")

    _check_str("business_type")
    _check_str("location")

    return errors


def _clamp_positive(value: float) -> float:
    """[SECURITY] Ensure energy outputs are not negative."""
    return float(value) if value > 0 else 0.0


@app.route("/api/v1/health", methods=["GET"])
@limiter.limit("100 per minute")  # [SECURITY] explicit rate limit
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
    except FileNotFoundError:
        # [SECURITY] Do not leak file paths or stack traces
        logger.exception("Metadata not found for /health")
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500
    except Exception:
        logger.exception("Unexpected error in /health")
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500


@app.route("/api/v1/model-info", methods=["GET"])
@limiter.limit("100 per minute")  # [SECURITY] explicit rate limit
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
    except FileNotFoundError:
        logger.exception("Metadata not found for /model-info")
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500
    except Exception:
        logger.exception("Unexpected error in /model-info")
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500


@app.route("/api/v1/predict-generation", methods=["POST"])
@limiter.limit("100 per minute")  # [SECURITY] explicit rate limit
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

        # Basic presence check for core fields
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

        # Coordinate validation (range + edge warnings)
        coord_status = validate_coordinates(latitude, longitude)
        if coord_status.get("status") == "error":
            return jsonify({"status": "error", "message": coord_status["message"]}), 400

        # [SECURITY] Additional business/input validation if fields are present
        extra_errors = _validate_optional_business_fields(payload)
        if extra_errors:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Invalid input.",
                        "details": extra_errors,
                    }
                ),
                400,
            )

        # Month: if provided, use it; otherwise, compute full climatology
        month: Optional[int] = None
        if month_raw is not None:
            try:
                month = int(month_raw)
            except (TypeError, ValueError):
                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": "month must be an integer between 1 and 12.",
                        }
                    ),
                    400,
                )
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
            daily_kwh = _clamp_positive(
                predict_solar_generation(latitude, longitude, month)
            )
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
                g = _clamp_positive(
                    predict_solar_generation(latitude, longitude, m)
                )
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

        # [SECURITY] Output sanity: energy must be non-negative
        avg_daily_for_annual = _clamp_positive(avg_daily_for_annual)

        annual_summary = {
            "year_1_generation_kwh": avg_daily_for_annual * 365.0,
            "average_daily_kwh": avg_daily_for_annual,
        }

        # Lifetime projection (optional)
        lifetime_prediction: Optional[Dict[str, Any]] = None
        if include_lifetime:
            lifetime_prediction = predict_lifetime_generation(latitude, longitude)
            # [SECURITY] Clamp key energy outputs to non-negative
            lifetime_prediction["year_1_generation_kwh"] = _clamp_positive(
                lifetime_prediction.get("year_1_generation_kwh", 0.0)
            )
            lifetime_prediction["lifetime_total_kwh"] = _clamp_positive(
                lifetime_prediction.get("lifetime_total_kwh", 0.0)
            )
            lifetime_prediction["lifetime_average_annual_kwh"] = _clamp_positive(
                lifetime_prediction.get("lifetime_average_annual_kwh", 0.0)
            )

        assumptions = (
            lifetime_prediction["assumptions"]
            if lifetime_prediction
            else {
                "panel_area_m2": 10.0,
                "panel_efficiency_pct": 20.0,
                "note": "Lifetime metrics disabled for this request.",
            }
        )

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
            # NOTE: Payback Period is not included or validated (removed from project).
            "note": "Predictions represent typical expected generation, not a daily weather forecast.",
        }

        return jsonify(response)

    except ValueError:
        # e.g., numeric cast issues not caught above
        logger.exception("Bad input value in /api/v1/predict-generation")
        return jsonify({"status": "error", "message": "Bad input."}), 400
    except Exception:
        # [SECURITY] Hide internal error details; log them instead
        logger.exception("Error in /api/v1/predict-generation")
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500


if __name__ == "__main__":
    # For local development only – in production, use a WSGI server.
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=False)



