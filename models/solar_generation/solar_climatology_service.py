"""
Core services for the climatological solar generation model.

This module provides:
- Model persistence utilities (save/load artifacts)
- Coordinate validation
- Point prediction for typical daily solar generation
- Lifetime generation projection with degradation and confidence bands

All functions are designed to be used both from the notebook and the Flask API.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np

# Months considered climatological "dry season" in many SSA regions
DRY_MONTHS = {12, 1, 2, 6, 7, 8}

# Feature order expected by the XGBoost model
FEATURE_COLUMNS: List[str] = [
    "latitude",
    "longitude",
    "abs_latitude",
    "month",
    "is_dry_season",
]


@dataclass
class ModelPaths:
    """Container for all model-related artifact paths."""

    model_dir: Path
    model_path: Path
    feature_cols_path: Path
    metadata_path: Path


def get_model_paths() -> ModelPaths:
    """
    Resolve model artifact paths using MODEL_DIR env var (default: 'models/').
    """
    base_dir = Path(os.getenv("MODEL_DIR", "models")).resolve()
    return ModelPaths(
        model_dir=base_dir,
        model_path=base_dir / "xgboost_climatological_model.pkl",
        feature_cols_path=base_dir / "feature_columns.pkl",
        metadata_path=base_dir / "xgboost_climatological_metadata.json",
    )


def save_model_artifacts(
    model: Any,
    feature_columns: List[str],
    mape: float,
    training_locations: List[str],
) -> None:
    """
    Persist trained model, feature list, and basic metadata to disk.

    This should be called from the notebook *after* training is complete.
    """
    paths = get_model_paths()
    paths.model_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, paths.model_path)
    joblib.dump(feature_columns, paths.feature_cols_path)

    metadata = {
        "model_type": "XGBoost climatological regression",
        "created_at_utc": datetime.utcnow().isoformat() + "Z",
        "validation_mape": mape,
        "training_locations": sorted(training_locations),
        "feature_columns": feature_columns,
    }
    paths.metadata_path.write_text(json.dumps(metadata, indent=2))


def load_model_artifacts() -> Tuple[Any, List[str], Dict[str, Any]]:
    """
    Load model, feature column list, and metadata.

    Raises:
        FileNotFoundError if any critical artifact is missing.
    """
    paths = get_model_paths()

    missing = [
        p for p in [paths.model_path, paths.feature_cols_path, paths.metadata_path] if not p.exists()
    ]
    if missing:
        raise FileNotFoundError(
            "Missing model artifacts: "
            + ", ".join(str(p) for p in missing)
            + ". Run the climatological notebook to train and save the model first."
        )

    model = joblib.load(paths.model_path)
    feature_cols: List[str] = joblib.load(paths.feature_cols_path)
    metadata: Dict[str, Any] = json.loads(paths.metadata_path.read_text())
    return model, feature_cols, metadata


def validate_coordinates(latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Validate whether coordinates fall roughly within the model's SSA coverage.

    Rules:
    - Error if latitude not in [-26, 6] or longitude not in [-18, 44]
    - Warning if near edge: latitude < -20 or latitude > 2
    - Otherwise status = 'valid'
    """
    lat = float(latitude)
    lon = float(longitude)

    result: Dict[str, Any] = {
        "status": "valid",
        "warnings": [],
    }

    if lat < -26 or lat > 6 or lon < -18 or lon > 44:
        result["status"] = "error"
        result["message"] = (
            "Coordinates are outside the model's calibrated Sub-Saharan Africa coverage "
            "(lat: -26 to 6, lon: -18 to 44)."
        )
        return result

    if lat < -20 or lat > 2:
        result["warnings"].append(
            "Latitude is near the edge of the training coverage; predictions may have higher uncertainty."
        )

    return result


def _build_feature_vector(
    latitude: float, longitude: float, month: int, feature_columns: Optional[List[str]] = None
) -> np.ndarray:
    """
    Internal helper to construct feature vector in the correct order.
    """
    if not 1 <= int(month) <= 12:
        raise ValueError("`month` must be an integer between 1 and 12.")

    abs_latitude = abs(float(latitude))
    is_dry_season = 1 if int(month) in DRY_MONTHS else 0

    feature_values = {
        "latitude": float(latitude),
        "longitude": float(longitude),
        "abs_latitude": float(abs_latitude),
        "month": int(month),
        "is_dry_season": int(is_dry_season),
    }

    cols = feature_columns or FEATURE_COLUMNS
    return np.array([[feature_values[col] for col in cols]], dtype=float)


def predict_solar_generation(
    latitude: float,
    longitude: float,
    month: Optional[int],
) -> float:
    """
    Predict typical daily solar generation (kWh/day) for a 10m², 20% efficiency system.

    Args:
        latitude: Decimal degrees
        longitude: Decimal degrees
        month: Month index (1–12). If None, predictions are averaged over all 12 months.

    Returns:
        Predicted typical daily generation in kWh.
    """
    model, feature_cols, _ = load_model_artifacts()

    if month is None:
        # Average over climatological year if month not specified
        preds: List[float] = []
        for m in range(1, 13):
            X = _build_feature_vector(latitude, longitude, m, feature_cols)
            # NOTE: model target is generation, not GHI; derive GHI only if needed.
            gen_kwh = float(model.predict(X)[0])
            preds.append(gen_kwh)
        return float(np.mean(preds))

    X = _build_feature_vector(latitude, longitude, int(month), feature_cols)
    gen_kwh = float(model.predict(X)[0])

    # If you want the implied GHI, you could compute:
    # predicted_ghi = gen_kwh / (10.0 * 0.2)
    # but the core output here is generation_kwh.
    return gen_kwh


def predict_lifetime_generation(
    latitude: float,
    longitude: float,
    lifetime_years: int = 25,
    base_degradation_rate: float = 0.007,
) -> Dict[str, Any]:
    """
    Project lifetime generation with degradation and confidence intervals.

    Args:
        latitude: Decimal degrees
        longitude: Decimal degrees
        lifetime_years: Panel lifetime in years (default 25)
        base_degradation_rate: Annual efficiency loss (e.g. 0.007 = 0.7%)

    Returns:
        Structured JSON-like dict with year 1, lifetime totals, yearly breakdown,
        and confidence intervals varying over time.
    """
    # Month-by-month typical generation
    monthly_gens: List[Tuple[int, float, bool]] = []
    for m in range(1, 13):
        gen_kwh = predict_solar_generation(latitude, longitude, m)
        monthly_gens.append((m, gen_kwh, m in DRY_MONTHS))

    # Average daily generation across the climatological year
    avg_daily_kwh = float(np.mean([g for _, g, _ in monthly_gens]))
    year_1_generation_kwh = avg_daily_kwh * 365.0

    yearly_breakdown: List[Dict[str, Any]] = []
    total_kwh = 0.0

    for year in range(1, lifetime_years + 1):
        efficiency = (1.0 - base_degradation_rate) ** (year - 1)
        year_gen = year_1_generation_kwh * efficiency
        total_kwh += year_gen

        # Confidence band widening over time
        if year <= 5:
            band = 0.10
        elif year <= 15:
            band = 0.15
        else:
            band = 0.20

        yearly_breakdown.append(
            {
                "year": year,
                "generation_kwh": year_gen,
                "efficiency_pct": efficiency * 100.0,
                "confidence_low_kwh": year_gen * (1.0 - band),
                "confidence_high_kwh": year_gen * (1.0 + band),
                "confidence_band_pct": band * 100.0,
            }
        )

    lifetime_total_kwh = total_kwh
    lifetime_average_annual_kwh = lifetime_total_kwh / float(lifetime_years)

    assumptions = {
        "panel_area_m2": 10.0,
        "panel_efficiency_pct": 20.0,
        "lifetime_years": lifetime_years,
        "annual_degradation_pct": base_degradation_rate * 100.0,
        "dry_months": sorted(DRY_MONTHS),
    }

    # Top-level confidence summary for convenience
    confidence = {
        "year_1_band_pct": 10.0,
        "years_1_5_band_pct": 10.0,
        "years_6_15_band_pct": 15.0,
        "years_16_25_band_pct": 20.0,
    }

    return {
        "year_1_generation_kwh": year_1_generation_kwh,
        "lifetime_total_kwh": lifetime_total_kwh,
        "lifetime_average_annual_kwh": lifetime_average_annual_kwh,
        "yearly_breakdown": yearly_breakdown,
        "assumptions": assumptions,
        "confidence": confidence,
        "monthly_generation_climatology": [
            {
                "month": m,
                "daily_kwh": g,
                "is_dry_season": is_dry,
            }
            for (m, g, is_dry) in monthly_gens
        ],
    }


