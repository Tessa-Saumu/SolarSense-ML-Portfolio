import math
import pytest
from solar_scenario.core import calculate, validate, ScenarioValidationError, VERSION

@pytest.fixture
def evidence():
    return {"contract_version":VERSION,"reference_system":{"panel_area_m2":10,"efficiency":0.2},"monthly_reference_generation_kwh_day":[10]*12,"model_sha256":"synthetic arithmetic test"}

def test_dimensional_identity(evidence):
    result=calculate({"panel_area_m2":10,"self_consumption_fraction":1,"annual_maintenance_kes":0},evidence)
    assert result["consumption"]["annual_kwh"]==25920
    assert result["solar"]["annual_generation_kwh"]==3650
    assert result["comparison"]["annual_avoided_grid_cost_kes"]==91250
    assert result["comparison"]["grid_only_annual_cost_kes"]==648000
    assert result["comparison"]["pv_annual_grid_cost_kes"]==556750

@pytest.mark.parametrize("payload",[{"country":"Uganda"},{"city":"Mombasa"},{"business_type":"factory"},{"business_type":[]},{"latitude":-1},{"efficiency":0.9},{"hours_per_day":25},{"panel_area_m2":-1},{"tariff_kes_per_kwh":float("nan")},{"average_load_kw":float("inf")},{"average_load_kw":True},{"tariff_kes_per_kwh":"25"},[],{"consumption_mode":"AI"}])
def test_invalid_inputs(payload):
    with pytest.raises(ScenarioValidationError): validate(payload)

def test_monthly_cap_and_no_export(evidence):
    result=calculate({"consumption_mode":"measured","monthly_consumption_kwh":100,"panel_area_m2":10000},evidence)
    assert result["solar"]["annual_offset_kwh"]==1200
    assert result["solar"]["coverage_percent"]==100
    assert result["comparison"]["pv_annual_grid_cost_kes"]==0

@pytest.mark.parametrize("payload",[{"panel_area_m2":0},{"self_consumption_fraction":0},{"consumption_mode":"measured","monthly_consumption_kwh":0}])
def test_zero_offset(payload,evidence):
    result=calculate(payload,evidence)
    assert result["solar"]["annual_offset_kwh"]==0
    assert result["comparison"]["simple_payback_years"] is None

def test_zero_tariff_no_savings(evidence):
    result=calculate({"tariff_kes_per_kwh":0},evidence)
    assert result["comparison"]["annual_avoided_grid_cost_kes"]==0
    assert result["comparison"]["net_annual_saving_kes"]==-3000
    assert result["comparison"]["simple_payback_years"] is None

def test_scaling(evidence):
    small=calculate({"panel_area_m2":10,"efficiency":0.1},evidence)
    large=calculate({"panel_area_m2":20,"efficiency":0.2},evidence)
    assert large["solar"]["annual_generation_kwh"]==small["solar"]["annual_generation_kwh"]*4

def test_business_profile_and_override():
    assert validate({"business_type":"grocery"})["hours_per_day"]==16
    assert validate({"business_type":"grocery","hours_per_day":10})["hours_per_day"]==10

def test_api_invalid_json():
    from flask import Flask
    from solar_scenario.api import blueprint
    app=Flask(__name__);app.register_blueprint(blueprint)
    client=app.test_client()
    assert client.post("/api/v1/scenario",data="{",content_type="application/json").status_code==400
    assert client.post("/api/v1/scenario",json={"country":"Nigeria"}).status_code==400
    assert client.post("/api/v1/scenario",data="test").status_code==400

def test_actual_served_artifact_and_static_export():
    import json
    from pathlib import Path
    from solar_scenario.core import load_evidence
    e=load_evidence()
    assert "Nairobi_Kenya" in e["evaluation"]["held_out_locations"]
    export=json.loads((Path(__file__).resolve().parents[1]/"web-demo/data/scenario-evidence.json").read_text())
    assert export["model_sha256"]==e["model_sha256"]
    assert export["solar_profiles"]==e["solar_profiles"]
    for vector in export["parity_vectors"]:
        assert vector["result"]==calculate(vector["input"],e)
    baseline=calculate({},e)
    xgb=calculate({"solar_profile":"xgboost"},e)
    assert baseline["solar"]["selected_profile"]=="baseline"
    assert xgb["solar"]["selected_profile"]=="xgboost"
    assert baseline["solar"]["annual_generation_kwh"]!=xgb["solar"]["annual_generation_kwh"]


def test_evaluation_metadata_mismatch_is_rejected(tmp_path, monkeypatch):
    import shutil
    import json
    from pathlib import Path
    import solar_scenario.core as core
    original = Path(core.__file__).resolve().parents[1]
    folder = tmp_path / "models/solar_generation/models"
    folder.mkdir(parents=True)
    (tmp_path / "evidence").mkdir()
    shutil.copy2(original / "models/solar_generation/models/flagship_solar_metadata.json", folder)
    shutil.copy2(original / "evidence/solar_evaluation.json", tmp_path / "evidence")
    data = json.loads((folder / "flagship_solar_metadata.json").read_text(encoding="utf-8"))
    data["baseline_monthly_kwh_day"]["1"] += 1
    (folder / "flagship_solar_metadata.json").write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(core, "__file__", str(tmp_path / "solar_scenario/core.py"))
    with pytest.raises(RuntimeError, match="evaluated release receipt"):
        core.load_evidence()
