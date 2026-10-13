"""Evaluation tests check independent predictions and train/test separation."""
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import xgboost as xgb

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("solar_evaluation", ROOT / "scripts/evaluate_solar.py")
evaluation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluation)
ARTIFACTS = ROOT / "models/solar_generation/models"


def test_fixed_city_split_and_missing_target_records():
    raw, good, monthly = evaluation.prepare()
    train = monthly.loc[monthly.split.eq("train")]
    test = monthly.loc[monthly.split.eq("test")]
    assert len(raw) == 29200 and len(good) == 29100
    assert len(train) == 180 and len(test) == 60
    assert set(train.location_name).isdisjoint(test.location_name)
    assert "Nairobi_Kenya" in set(test.location_name)
    assert monthly.groupby("location_name").size().eq(12).all()
    np.testing.assert_allclose(monthly.target_kwh_day, monthly.ghi_kwh_m2 * 2)


def test_saved_model_predictions_and_baseline_independently_recompute():
    _, _, monthly = evaluation.prepare()
    test = monthly.loc[monthly.split.eq("test")]
    train = monthly.loc[monthly.split.eq("train")]
    metadata = json.loads((ARTIFACTS / "flagship_solar_metadata.json").read_text())
    artifact = ARTIFACTS / "flagship_solar_xgb.json"
    assert evaluation.sha256(artifact) == metadata["model_sha256"]
    assert evaluation.sha256(evaluation.SOURCE) == metadata["dataset_sha256"]
    model = xgb.Booster()
    model.load_model(artifact)
    prediction = model.predict(xgb.DMatrix(test[evaluation.FEATURES]))
    baseline = test.month.map(train.groupby("month").target_kwh_day.mean())
    for key, value in evaluation.metrics(test.target_kwh_day, prediction).items():
        assert value == pytest.approx(metadata["evaluation"]["model"][key], abs=1e-10)
    for key, value in evaluation.metrics(test.target_kwh_day, baseline).items():
        assert value == pytest.approx(metadata["evaluation"]["baseline"][key], abs=1e-10)
    saved = pd.read_csv(ROOT / "evidence/solar_holdout_predictions.csv")
    np.testing.assert_allclose(prediction, saved.model_kwh_day, rtol=1e-8)


def test_retraining_isolated_is_deterministic_and_does_not_replace_serving_model(tmp_path):
    serving_hash = evaluation.sha256(ARTIFACTS / "flagship_solar_xgb.json")
    result = evaluation.evaluate(tmp_path / "models", tmp_path / "evidence")
    assert result["model_sha256"] == serving_hash
    assert evaluation.sha256(ARTIFACTS / "flagship_solar_xgb.json") == serving_hash
    assert result["evaluation"]["model"]["mape_percent"] == pytest.approx(11.2055781674)
    assert result["per_city"]["Nairobi_Kenya"]["model"]["mape_percent"] > result["per_city"]["Nairobi_Kenya"]["baseline"]["mape_percent"]
