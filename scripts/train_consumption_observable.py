"""Fit a small, leakage-free consumption prototype from retained CBECS records.

No target-dependent predictors, target trimming or holdout-driven tuning. The old
artifact stays untouched: it needs ELCNS/SQFT, which is unavailable at inference.
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
FEATURES = ["floor_area_m2", "operating_hours_weekly", "refrigeration_units", "food_service"]


def metrics(y, p):
    return {"mae_annual_kwh": float(mean_absolute_error(y, p)), "rmse_annual_kwh": float(np.sqrt(mean_squared_error(y, p))), "mape_percent": float(mean_absolute_percentage_error(y, p)*100), "r2": float(r2_score(y, p))}


def train():
    path = ROOT / "models/energy_consumption/models/cbecs2018_final_public.csv"
    data = pd.read_csv(path, usecols=["PBA", "SQFT", "WKHRS", "RFGCOMPN", "ELCNS"])
    # Official EIA 2018 questionnaire: PBA 6 food sales; PBA 15 food service.
    cohort = data[data.PBA.isin([6, 15]) & data.ELCNS.notna() & (data.ELCNS > 0) & (data.SQFT > 0) & (data.WKHRS > 0)].copy()
    x = pd.DataFrame({"floor_area_m2": cohort.SQFT/10.764, "operating_hours_weekly": cohort.WKHRS, "refrigeration_units": cohort.RFGCOMPN, "food_service": (cohort.PBA == 15).astype(int)})
    y = cohort.ELCNS
    train_ids, test_ids = train_test_split(cohort.index.to_numpy(), test_size=.2, random_state=42, stratify=cohort.PBA)
    imputer = SimpleImputer(strategy="median")
    xt = imputer.fit_transform(x.loc[train_ids])
    xv = imputer.transform(x.loc[test_ids])
    model = GradientBoostingRegressor(n_estimators=200, learning_rate=.1, max_depth=3, random_state=42)
    model.fit(xt, np.log1p(y.loc[train_ids]))
    predicted = np.expm1(model.predict(xv))
    intensity = float(np.median(y.loc[train_ids].to_numpy()/x.loc[train_ids, "floor_area_m2"].to_numpy()))
    area_baseline = xv[:, 0]*intensity
    constant = float(np.median(y.loc[train_ids]))
    trees = []
    for estimator in model.estimators_[:, 0]:
        t = estimator.tree_
        trees.append({"children_left": t.children_left.tolist(), "children_right": t.children_right.tolist(), "feature": t.feature.tolist(), "threshold": t.threshold.tolist(), "value": t.value[:, 0, 0].tolist()})
    artifact = {"version": "consumption-observable-v1", "feature_names": FEATURES, "imputation_medians": imputer.statistics_.tolist(), "init_log": float(model.init_.constant_[0, 0]), "learning_rate": float(model.learning_rate), "trees": trees, "target": "annual electricity consumption kWh; log1p fit, expm1 inference", "training_ranges": {c: {"min": float(x.loc[train_ids,c].min()), "max": float(x.loc[train_ids,c].max())} for c in FEATURES}, "area_baseline_annual_kwh_per_m2": intensity}
    from solar_scenario.assessment import predict_annual
    exported_prediction = np.asarray([predict_annual(row, artifact) for row in xv])
    np.testing.assert_allclose(exported_prediction, predicted, rtol=1e-12, atol=1e-7)
    destination = ROOT/"models/energy_consumption/models/consumption_observable_v1.json"
    destination.write_text(json.dumps(artifact, separators=(",", ":"))+"\n", encoding="utf-8")
    receipt = {"version": artifact["version"], "source": "Retained CBECS 2018 US public-use CSV", "dataset_sha256_lf": hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest(), "official_pba_source": "https://www.eia.gov/consumption/commercial/data/2018/pdf/eia871aij_2018.pdf", "cohort": "PBA 6 food sales and PBA 15 food service; positive available target, floor area and hours; no target-based outlier removal", "rows": len(cohort), "training_rows": len(train_ids), "test_rows": len(test_ids), "train_row_indices": train_ids.tolist(), "test_row_indices": test_ids.tolist(), "features": FEATURES, "missing_refrigeration_rows": int(x.refrigeration_units.isna().sum()), "missing_predictor_handling": "Training-only median imputation; no imputation of target", "parameters": {"n_estimators":200,"learning_rate":.1,"max_depth":3,"random_state":42}, "split": "80/20 fixed seed 42, stratified by PBA, no hyperparameter search", "model": metrics(y.loc[test_ids], predicted), "area_intensity_baseline": metrics(y.loc[test_ids], area_baseline), "training_median_baseline": metrics(y.loc[test_ids], np.full(len(test_ids), constant)), "model_sha256": hashlib.sha256(destination.read_bytes()).hexdigest(), "limitations": ["US building-level random holdout is not validation in African SMEs.", "Food sales/service proxy categories do not distinguish every shop or appliance subtype.", "Most refrigeration counts are missing and imputed from training records.", "Small African shops can be outside training floor-area range; tree models do not reliably extrapolate.", "No climate factor applied: unvalidated transfer adjustments would not make this model locally calibrated.", "Old model metrics were compromised by target leakage and incorrect PBA descriptions; they are not current accuracy claims."]}
    out = ROOT/"evidence/consumption_evaluation.json"
    out.write_text(json.dumps(receipt, indent=2)+"\n", encoding="utf-8")
    pd.DataFrame({"source_row_index": test_ids, "actual_annual_kwh": y.loc[test_ids].to_numpy(), "predicted_annual_kwh": predicted, "area_baseline_annual_kwh": area_baseline}).to_csv(ROOT/"evidence/consumption_holdout_predictions.csv", index=False)
    print(json.dumps({k:receipt[k] for k in ["rows","training_rows","test_rows","model","area_intensity_baseline","training_median_baseline","model_sha256"]},indent=2))


if __name__ == "__main__":
    train()
