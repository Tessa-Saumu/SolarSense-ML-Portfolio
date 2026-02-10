"""
Climatological Solar Generation Model (XGBoost)
------------------------------------------------

This module implements an end-to-end training pipeline that:
- Loads historical daily GHI data (from NASA POWER API, pre-exported to CSV)
- Aggregates to monthly climatological patterns per city
- Engineers spatial–seasonal features (latitude, longitude, month, dry season)
- Trains an XGBoost regression model to predict typical solar generation
- Evaluates generalisation to unseen locations using a location-based split
- Saves the trained model artifact for use in the Flask API

WHY THIS IS ML (not a rule-based lookup):
- The model learns a non-linear mapping between (lat, lon, month, dry-season)
  and typical generation, instead of using hard-coded rules or city lookups.
- At inference, you can pass ANY coordinates (even outside training cities);
  the tree ensemble interpolates patterns learned from diverse SSA locations.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_percentage_error
import joblib


# Months considered climatological "dry season" in many SSA regions
DRY_MONTHS = {12, 1, 2, 6, 7, 8}

# Features expected by the model
FEATURE_COLUMNS = ["latitude", "longitude", "abs_latitude", "month", "is_dry_season"]


@dataclass
class TrainConfig:
    data_csv_path: Path = Path("solar_data_merged.csv")
    model_output_path: Path = Path("xgboost_climatology_model.pkl")
    random_state: int = 42
    # Hold out these locations entirely for validation to test spatial generalisation.
    # If any are missing in the dataset, a fallback heuristic will be used.
    validation_locations: Tuple[str, ...] = (
        "Johannesburg_SA",
        "Kigali_Rwanda",
    )


def build_monthly_dataset(config: TrainConfig) -> pd.DataFrame:
    """
    Load daily NASA-derived data and aggregate to monthly climatological patterns.

    - Input: solar_data_merged.csv (daily GHI + metadata for multiple SSA cities)
    - Output: one row per (city, month) with average GHI and engineered features.
    """
    csv_path = config.data_csv_path
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Expected merged solar data CSV at '{csv_path}', "
            "but it was not found. Run the NASA POWER pipeline + cleaning first."
        )

    df = pd.read_csv(csv_path)

    required_cols = {
        "location_name",
        "country",
        "latitude",
        "longitude",
        "date",
        "ghi_kwh_m2",
        "data_quality",
    }
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing required columns: {missing}")

    # Use only good-quality NASA POWER records
    df = df[df["data_quality"] == "good"].copy()

    # Ensure date → month is correctly parsed (ignore any float month column already present)
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.month

    # Aggregate to monthly mean GHI per city (climatology-style)
    monthly = (
        df.groupby(
            ["location_name", "country", "latitude", "longitude", "month"],
            as_index=False,
        )["ghi_kwh_m2"]
        .mean()
        .rename(columns={"ghi_kwh_m2": "avg_ghi_kwh_m2"})
    )

    # Spatial + seasonal features
    monthly["abs_latitude"] = monthly["latitude"].abs()
    monthly["is_dry_season"] = monthly["month"].isin(DRY_MONTHS).astype(int)

    # Target variable: typical monthly daily generation for a 10m², 20% efficiency system
    # NOTE: This is climatological expected output, not a one-day forecast.
    monthly["target_avg_generation_kwh"] = monthly["avg_ghi_kwh_m2"] * 10.0 * 0.2

    return monthly


def make_location_split(
    monthly: pd.DataFrame, config: TrainConfig
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split data by LOCATION, not by random rows.

    This ensures we test whether the model can generalise to completely unseen
    coordinates, which is the core requirement of the DSE brief.
    """
    all_locations: List[str] = sorted(monthly["location_name"].unique())

    # Use configured validation locations if they exist; otherwise fall back to
    # a simple deterministic split (last 2 cities as validation).
    val_locs = [loc for loc in config.validation_locations if loc in all_locations]
    if not val_locs:
        # Fallback: hold out last 2 alphabetically
        val_locs = all_locations[-2:]

    train_mask = ~monthly["location_name"].isin(val_locs)
    val_mask = monthly["location_name"].isin(val_locs)

    train_df = monthly[train_mask].reset_index(drop=True)
    val_df = monthly[val_mask].reset_index(drop=True)

    print(f"Training locations ({train_df['location_name'].nunique()}):")
    print(sorted(train_df["location_name"].unique()))
    print(f"\nValidation locations ({val_df['location_name'].nunique()}):")
    print(sorted(val_df["location_name"].unique()))

    return train_df, val_df


def train_xgboost_model(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    config: TrainConfig,
) -> Tuple[XGBRegressor, float]:
    """
    Train XGBoost regression on spatial–seasonal features and evaluate MAPE.

    Because this is ML:
    - The model learns tree-based decision rules directly from data.
    - There is no hard-coded 'if latitude > X then Y' logic; everything is inferred.
    """
    for col in FEATURE_COLUMNS + ["target_avg_generation_kwh"]:
        if col not in train_df.columns:
            raise ValueError(f"Missing required column for training: '{col}'")

    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df["target_avg_generation_kwh"]

    X_val = val_df[FEATURE_COLUMNS]
    y_val = val_df["target_avg_generation_kwh"]

    model = XGBRegressor(
        n_estimators=400,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="reg:squarederror",
        random_state=config.random_state,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    y_val_pred = model.predict(X_val)
    mape = float(mean_absolute_percentage_error(y_val, y_val_pred))

    print(f"\nValidation MAPE (location-based split): {mape * 100:.2f}%")

    # Hard requirement from the DSE brief
    assert mape <= 0.15, (
        f"Validation MAPE {mape * 100:.2f}% exceeds 15% threshold. "
        "Investigate data quality, feature engineering, or model capacity."
    )

    return model, mape


def save_model(model: XGBRegressor, config: TrainConfig) -> None:
    """Persist the trained model to disk as a pickle artifact."""
    output_path = config.model_output_path
    joblib.dump(model, output_path)
    print(f"\n✓ Saved climatological XGBoost model to: {output_path}")


def main() -> None:
    """
    Run the full climatological training pipeline end-to-end.

    Steps:
    1. Load NASA-derived daily data from CSV (output of upstream pipeline).
    2. Aggregate to monthly climatology per city and engineer features.
    3. Split by location into train/validation sets.
    4. Train XGBoost regression and compute location-level MAPE.
    5. Assert MAPE ≤ 15% and save the model artifact for the Flask API.
    """
    config = TrainConfig()
    print("=" * 70)
    print("Climatological Solar Generation Model - Training Pipeline")
    print("=" * 70)

    monthly = build_monthly_dataset(config)
    print(f"\nBuilt monthly climatology dataset with {len(monthly)} rows")
    print(
        f"Unique locations: {monthly['location_name'].nunique()} | "
        f"Months: {sorted(monthly['month'].unique())}"
    )

    train_df, val_df = make_location_split(monthly, config)

    model, mape = train_xgboost_model(train_df, val_df, config)

    save_model(model, config)

    print("\nTraining complete.")
    print(f"Final location-based validation MAPE: {mape * 100:.2f}%")
    print("\nNOTE: This model predicts typical climatological generation,")
    print("      not short-horizon weather forecasts.")


if __name__ == "__main__":
    main()



