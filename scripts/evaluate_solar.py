"""Reproduce the fixed city holdout and save the exact evaluated solar model.

No network calls or hyperparameter search. Targets are irradiance-derived
theoretical output, not electricity measured from solar installations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
import xgboost
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "models/solar_generation/models/solar_data_20cities_4yr.csv"
FEATURES = ["latitude", "longitude", "abs_latitude", "month", "is_dry_season"]
# Declared before fitting: four legacy-script cities plus the demo's Nairobi.
HELD_OUT = ["Abidjan_Ivory_Coast", "Cape_Town_SA", "Johannesburg_SA", "Lusaka_Zambia", "Nairobi_Kenya"]
PARAMETERS = dict(n_estimators=400, max_depth=4, learning_rate=0.05,
                  subsample=0.9, colsample_bytree=0.9,
                  objective="reg:squarederror", random_state=42, n_jobs=1,
                  tree_method="hist")


def sha256(path: Path) -> str:
    data = path.read_bytes()
    if path.suffix.lower() == ".csv":
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def prepare(source: Path = SOURCE):
    raw = pd.read_csv(source)
    raw.columns = raw.columns.str.strip()
    for col in ["location_name", "country", "data_quality"]:
        raw[col] = raw[col].str.strip()
    raw["date"] = pd.to_datetime(raw["date"], errors="raise")
    if raw.duplicated(["location_name", "date"]).any():
        raise ValueError("Duplicate city/date records")
    # The inherited quality flag marks 100 missing-GHI rows as good.
    # Drop missing target inputs explicitly, without imputing holdout labels.
    good = raw.loc[raw.data_quality.eq("good") & raw.ghi_kwh_m2.notna()].copy()
    if not np.isfinite(good[["latitude", "longitude", "ghi_kwh_m2"]]).all().all() or (good.ghi_kwh_m2 <= 0).any():
        raise ValueError("Expected finite coordinates and positive irradiance")
    good["month"] = good.date.dt.month
    monthly = good.groupby(["location_name", "country", "latitude", "longitude", "month"], as_index=False).ghi_kwh_m2.mean()
    monthly["abs_latitude"] = monthly.latitude.abs()
    monthly["is_dry_season"] = monthly.month.isin({12, 1, 2, 6, 7, 8}).astype(int)
    monthly["target_kwh_day"] = monthly.ghi_kwh_m2 * 10.0 * 0.2
    monthly["split"] = np.where(monthly.location_name.isin(HELD_OUT), "test", "train")
    if set(HELD_OUT) - set(monthly.location_name):
        raise ValueError("Fixed holdout city is absent")
    return raw, good, monthly


def metrics(truth, prediction):
    return dict(mae_kwh_day=float(mean_absolute_error(truth, prediction)),
                rmse_kwh_day=float(np.sqrt(mean_squared_error(truth, prediction))),
                mape_percent=float(np.mean(np.abs((truth - prediction) / truth)) * 100),
                r2=float(r2_score(truth, prediction)))


def evaluate(output_dir: Path, evidence_dir: Path, source: Path = SOURCE):
    raw, good, monthly = prepare(source)
    train = monthly.loc[monthly.split.eq("train")]
    test = monthly.loc[monthly.split.eq("test")].copy()
    model = XGBRegressor(**PARAMETERS)
    model.fit(train[FEATURES], train.target_kwh_day)
    test["model_kwh_day"] = model.predict(test[FEATURES])
    # Month-only climatology uses training cities exclusively.
    climatology = train.groupby("month").target_kwh_day.mean()
    test["baseline_kwh_day"] = test.month.map(climatology)
    result = {"model": metrics(test.target_kwh_day, test.model_kwh_day),
              "baseline": metrics(test.target_kwh_day, test.baseline_kwh_day)}
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    artifact = output_dir / "flagship_solar_xgb.json"
    model.save_model(artifact)
    monthly.to_csv(evidence_dir / "solar_monthly_split.csv", index=False, float_format="%.10g")
    test.to_csv(evidence_dir / "solar_holdout_predictions.csv", index=False, float_format="%.10g")
    per_city = {city: {"model": metrics(group.target_kwh_day, group.model_kwh_day),
                       "baseline": metrics(group.target_kwh_day, group.baseline_kwh_day)}
                for city, group in test.groupby("location_name")}
    metadata = dict(model_type="XGBoost fixed-city holdout regression", feature_columns=FEATURES,
                    reference_panel_area_m2=10.0, reference_efficiency=0.2,
                    target="Monthly mean GHI * 10 m² * 0.20; theoretical kWh/day, not observed PV output",
                    model_sha256=sha256(artifact), dataset_sha256=sha256(source),
                    dataset_hash_scope="SHA-256 with CSV CRLF normalized to LF; content unchanged across Git checkouts",
                    dataset_path=source.relative_to(ROOT).as_posix() if source.is_relative_to(ROOT) else source.name,
                    raw_rows=len(raw), usable_rows=len(good), missing_ghi_rows=int(raw.ghi_kwh_m2.isna().sum()), monthly_rows=len(monthly),
                    date_start=str(raw.date.min().date()), date_end=str(raw.date.max().date()),
                    training_locations=sorted(train.location_name.unique()), held_out_locations=HELD_OUT,
                    training_rows=len(train), test_rows=len(test), parameters=PARAMETERS,
                    versions={"xgboost": xgboost.__version__, "sklearn": sklearn.__version__, "pandas": pd.__version__, "numpy": np.__version__},
                    validation_mape=result["model"]["mape_percent"] / 100,
                    evaluation=result, per_city=per_city,
                    baseline_monthly_kwh_day={str(int(month)): float(value) for month, value in climatology.items()},
                    training_coordinate_bounds={c: [float(train[c].min()), float(train[c].max())] for c in ["latitude", "longitude"]},
                    target_bounds_kwh_day=[float(monthly.target_kwh_day.min()), float(monthly.target_kwh_day.max())],
                    provenance="Inherited NASA POWER-labelled bundled CSV; original upstream API receipt/raw responses not independently verified. Whitespace normalized; no new data fetched.",
                    qualification="No future-year holdout, no observed installation data; five cities were predeclared, no tuning or all-city refit. Nairobi is held out.")
    (output_dir / "flagship_solar_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    (evidence_dir / "solar_evaluation.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "models/solar_generation/models")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "evidence")
    args = parser.parse_args()
    print(json.dumps(evaluate(args.output_dir, args.evidence_dir)["evaluation"], indent=2))
