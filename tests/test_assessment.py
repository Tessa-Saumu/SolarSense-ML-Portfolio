"""Verify actual model inference, honest provenance and minimal-input API behavior."""
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from flask import Flask
from sklearn.metrics import mean_absolute_percentage_error
from solar_scenario.assessment import assess, load_assessment_evidence, predict_annual
from solar_scenario.core import ScenarioValidationError
from solar_scenario.api import blueprint

ROOT=Path(__file__).resolve().parents[1]

@pytest.fixture(scope="module")
def evidence():
    return load_assessment_evidence()

def test_frozen_holdout_predictions_and_no_target_features(evidence):
    receipt=evidence["consumption_evaluation"]
    assert set(receipt["train_row_indices"]).isdisjoint(receipt["test_row_indices"])
    assert receipt["training_rows"]==247 and receipt["test_rows"]==62
    assert evidence["consumption_model"]["feature_names"]==["floor_area_m2","operating_hours_weekly","refrigeration_units","food_service"]
    p=ROOT/"models/energy_consumption/models/consumption_observable_v1.json"
    assert hashlib.sha256(p.read_bytes()).hexdigest()==receipt["model_sha256"]
    raw=pd.read_csv(ROOT/"models/energy_consumption/models/cbecs2018_final_public.csv",usecols=["PBA","SQFT","WKHRS","RFGCOMPN","ELCNS"])
    holdout=pd.read_csv(ROOT/"evidence/consumption_holdout_predictions.csv")
    assert set(raw.loc[holdout.source_row_index,"PBA"])=={6,15}
    assert holdout.source_row_index.tolist()==receipt["test_row_indices"]
    predictions=[]
    for row_index in receipt["test_row_indices"]:
        r=raw.loc[row_index]
        units=r.RFGCOMPN if pd.notna(r.RFGCOMPN) else evidence["consumption_model"]["imputation_medians"][2]
        predictions.append(predict_annual([r.SQFT/10.764,r.WKHRS,units,int(r.PBA==15)],evidence["consumption_model"]))
    np.testing.assert_allclose(predictions,holdout.predicted_annual_kwh,rtol=1e-12)
    mape=100*mean_absolute_percentage_error(holdout.actual_annual_kwh,predictions)
    assert mape==pytest.approx(receipt["model"]["mape_percent"])
    assert receipt["model"]["mape_percent"]>receipt["area_intensity_baseline"]["mape_percent"]

def test_assessment_requires_no_user_solar_consumption_or_prices(evidence):
    result=assess({"business_type":"grocery","floor_area_m2":100,"operating_hours_weekly":84,"refrigeration_units":3},evidence)
    assert result["consumption"]["monthly_kwh"]>0
    assert result["system"]["capacity_kw"]>0
    assert result["system"]["panel_area_m2"]<=result["system"]["assumed_available_roof_m2"]
    assert result["solar"]["annual_offset_kwh"]<=result["consumption"]["annual_kwh"]
    assert "confidence" not in json.dumps(result)

def test_equipment_crosscheck_does_not_masquerade_as_learned_features(evidence):
    payload={"refrigeration_units":1,"equipment":[{"type":"freezer","quantity":1,"hours_per_day":12}]}
    result=assess(payload,evidence)
    assert result["consumption"]["equipment_monthly_kwh"]==pytest.approx(300*12*365/12/1000)
    payload["equipment"][0]["hours_per_day"]=24
    second=assess(payload,evidence)
    assert second["consumption"]["equipment_monthly_kwh"]==pytest.approx(2*result["consumption"]["equipment_monthly_kwh"])
    assert second["consumption"]["monthly_kwh"]==result["consumption"]["monthly_kwh"]

@pytest.mark.parametrize("payload",[{"floor_area_m2":float("nan")},{"country":"Ghana"},{"power_source":[]},{"refrigeration_units":1.5},{"assumptions":{"made_up":5}},{"equipment":[{"type":[],"quantity":1,"hours_per_day":2}]}])
def test_bad_inputs(payload):
    with pytest.raises(ScenarioValidationError):assess(payload)

def test_out_of_range_and_unvalidated_warehouse_are_qualified(evidence):
    result=assess({"floor_area_m2":10,"business_type":"cold_storage"},evidence)
    assert result["consumption"]["warnings"]
    assert result["recommendation"]["out_of_training_range"]
    assert result["recommendation"]["verdict"]=="needs_site_assessment"

def test_api_returns_model_assessment_and_rejects_wrong_inputs():
    app=Flask(__name__);app.register_blueprint(blueprint)
    client=app.test_client()
    assert client.get("/api/v1/assessment/evidence").status_code==200
    response=client.post("/api/v1/assessment",json={"business_type":"butchery","floor_area_m2":120,"operating_hours_weekly":84,"refrigeration_units":4})
    assert response.status_code==200
    assert len(response.json["consumption"]["model_sha256"])==64
    assert client.post("/api/v1/assessment",json={"city":"London"}).status_code==400
    assert client.post("/api/v1/assessment",data="{bad",content_type="application/json").status_code==400
