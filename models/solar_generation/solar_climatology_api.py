"""
Flask API for Climatological Solar Generation Prediction
--------------------------------------------------------

This service exposes a single endpoint:

    POST /predict-generation

Request JSON:
{
  "latitude": -1.2921,
  "longitude": 36.8219,
  "month": 6
}

Response JSON:
{
  "predicted_avg_generation_kwh": 5.87,
  "model_type": "XGBoost climatological regression",
  "note": "Prediction represents typical expected generation, not daily weather forecast"
}

WHY THIS IS ML:
- The API loads a trained XGBoost regression model that has learned spatial–seasonal
  patterns from historical NASA POWER data across diverse SSA locations.
- For any new (latitude, longitude, month) input, the model infers a prediction by
  interpolating in feature space; there is no hard-coded lookup table of cities.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import joblib
import numpy as np
from flask import Flask, jsonify, request
import sys
import os

# Ensure this directory is on the Python path so we can import the training module
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))

from climatological_model import DRY_MONTHS, FEATURE_COLUMNS, TrainConfig


app = Flask(__name__)


def load_model() -> Any:
    """
    Load the trained XGBoost climatology model from disk.

    The training script (climatological_model.py) is responsible for creating
    this artifact after achieving MAPE ≤ 15% on a location-based validation set.
    """
    config = TrainConfig()
    model_path: Path = config.model_output_path
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model file '{model_path}' not found. "
            "Run climatological_model.py to train and save the model first."
        )
    return joblib.load(model_path)


model = load_model()


def build_feature_vector(latitude: float, longitude: float, month: int) -> np.ndarray:
    """
    Construct the feature vector expected by the XGBoost model.

    Features:
    - latitude
    - longitude
    - abs_latitude
    - month
    - is_dry_season
    """
    if not 1 <= month <= 12:
        raise ValueError("`month` must be an integer between 1 and 12.")

    abs_latitude = abs(latitude)
    is_dry_season = 1 if month in DRY_MONTHS else 0

    # Preserve explicit ordering expected by the model
    feature_values = {
        "latitude": float(latitude),
        "longitude": float(longitude),
        "abs_latitude": float(abs_latitude),
        "month": int(month),
        "is_dry_season": int(is_dry_season),
    }

    return np.array([[feature_values[col] for col in FEATURE_COLUMNS]], dtype=float)


@app.route("/predict-generation", methods=["POST"])
def predict_generation():
    """
    Predict typical (climatological) solar generation for arbitrary coordinates.

    This is NOT a weather forecast; it estimates expected average daily generation
    for a 10m² system at 20% efficiency, based on learned spatial–seasonal patterns.
    """
    try:
        payload: Dict[str, Any] = request.get_json(force=True) or {}

        latitude = float(payload.get("latitude"))
        longitude = float(payload.get("longitude"))
        month = int(payload.get("month"))

        features = build_feature_vector(latitude, longitude, month)
        prediction = float(model.predict(features)[0])

        return jsonify(
            {
                "predicted_avg_generation_kwh": round(prediction, 3),
                "model_type": "XGBoost climatological regression",
                "note": "Prediction represents typical expected generation, not daily weather forecast",
            }
        )

    except (TypeError, ValueError) as e:
        return jsonify({"error": str(e)}), 400
    except FileNotFoundError as e:
        # Surface model-loading issues clearly
        return jsonify({"error": str(e)}), 500
    except Exception as e:  # pragma: no cover - defensive catch-all
        return jsonify({"error": f"Unexpected server error: {e}"}), 500


if __name__ == "__main__":
    # For local development only – in production, use gunicorn/uwsgi.
    app.run(host="0.0.0.0", port=8000, debug=False)


