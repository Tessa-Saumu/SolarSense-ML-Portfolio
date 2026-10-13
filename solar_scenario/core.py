"""Bounded, transparent Nairobi scenario arithmetic. No consumption ML claims."""
from __future__ import annotations
import calendar
import hashlib
import json
import math
from pathlib import Path
import numpy as np
import xgboost as xgb

VERSION = "solarsense-scenario-v1"
LOCATION = {"country": "Kenya", "city": "Nairobi", "latitude": -1.2921, "longitude": 36.8219}
PROFILES = {"bakery": {"average_load_kw": 6, "hours_per_day": 12}, "grocery": {"average_load_kw": 3, "hours_per_day": 16}, "butchery": {"average_load_kw": 4, "hours_per_day": 18}}
DEFAULTS = {"country": "Kenya", "city": "Nairobi", "business_type": "bakery", "consumption_mode": "formula", "solar_profile": "baseline", "days_per_month": 30, "average_load_kw": 6, "hours_per_day": 12, "monthly_consumption_kwh": 2160, "panel_area_m2": 30, "efficiency": 0.2, "tariff_kes_per_kwh": 25, "self_consumption_fraction": 0.8, "installed_cost_kes": 300000, "annual_maintenance_kes": 3000}
LIMITS = {"days_per_month": (1,31), "average_load_kw": (0,1000), "hours_per_day": (0,24), "monthly_consumption_kwh": (0,1000000), "panel_area_m2": (0,10000), "efficiency": (0.01,0.4), "tariff_kes_per_kwh": (0,1000), "self_consumption_fraction": (0,1), "installed_cost_kes": (0,100000000), "annual_maintenance_kes": (0,10000000)}
ASSUMPTIONS = ["Tariff default KES 25/kWh is a fictional demo assumption created 2026-10-13, not a verified Kenyan tariff. Enter your own variable electricity rate; fixed charges and tax are excluded.", "Business load, operating hours, installation cost and maintenance defaults are fictional examples, not observed SME measurements.", "Formula consumption is average load in kW × operating hours/day × representative days/month; measured mode uses your supplied monthly kWh. Annual consumption assumes twelve identical months.", "Self-consumption fraction is a user assumption. Usable solar is capped against consumption each month; export revenue is zero.", "Panel-area and efficiency changes scale the model reference target linearly, not a separately learned model."]
LIMITATIONS = ["Nairobi XGBoost MAPE is 12.5268%, worse than the training-city monthly baseline at 8.4342%; default baseline is a transparent comparison-driven choice, not an independent new validation result.", "Nairobi only; no automatic geography inference. No verified local installation output or customer savings evidence.", "Solar target is derived from bundled irradiance with fixed panel area and efficiency, not measured installation generation. Baseline and held-out metrics describe that derived target only.", "Climatological monthly estimates omit shading, roof orientation, inverter losses, batteries, degradation and weather extremes.", "Simple payback omits financing, discounting, replacement costs and tax; this is scenario arithmetic, not financial advice or validated ROI."]

class ScenarioValidationError(ValueError):
    """Actionable input failure at the scenario boundary."""

def validate(payload):
    if not isinstance(payload, dict):
        raise ScenarioValidationError("Provide a JSON object.")
    unknown = set(payload) - set(DEFAULTS)
    if unknown:
        raise ScenarioValidationError("Unknown fields: " + ", ".join(sorted(unknown)))
    data = dict(DEFAULTS)
    if not isinstance(payload.get("business_type", "bakery"), str) or payload.get("business_type", "bakery") not in PROFILES:
        raise ScenarioValidationError("business_type must be bakery, grocery or butchery.")
    data.update(PROFILES[payload.get("business_type", "bakery")])
    data.update(payload)
    if data["country"] != "Kenya" or data["city"] != "Nairobi":
        raise ScenarioValidationError("Only Nairobi, Kenya is supported; coordinates are fixed explicitly.")
    if data["consumption_mode"] not in ("formula", "measured"):
        raise ScenarioValidationError("consumption_mode must be formula or measured.")
    if data["solar_profile"] not in ("baseline", "xgboost"):
        raise ScenarioValidationError("solar_profile must be baseline or xgboost.")
    for key, (low, high) in LIMITS.items():
        value = data[key]
        if isinstance(value, bool) or not isinstance(value, (int,float)) or not math.isfinite(value) or not low <= value <= high:
            raise ScenarioValidationError(f"{key} must be a finite number between {low} and {high}.")
    return data

def load_evidence():
    directory = Path(__file__).resolve().parents[1] / "models/solar_generation/models"
    model_path = directory / "flagship_solar_xgb.json"
    metadata_path = directory / "flagship_solar_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    release = json.loads((Path(__file__).resolve().parents[1] / "evidence/solar_evaluation.json").read_text(encoding="utf-8"))
    if metadata != release:
        raise RuntimeError("Solar metadata differs from the evaluated release receipt.")
    digest = hashlib.sha256(model_path.read_bytes()).hexdigest()
    if digest != metadata["model_sha256"]:
        raise RuntimeError("Evaluated solar artifact checksum mismatch.")
    cols = metadata["feature_columns"]
    model = xgb.Booster(); model.load_model(str(model_path))
    rows = []
    for month in range(1,13):
        features = {"latitude": LOCATION["latitude"], "longitude": LOCATION["longitude"], "abs_latitude": abs(LOCATION["latitude"]), "month": month, "is_dry_season": int(month in {12,1,2,6,7,8})}
        rows.append([features[c] for c in cols])
    predictions = model.predict(xgb.DMatrix(np.array(rows, dtype=float), feature_names=cols)).tolist()
    if any(not math.isfinite(p) or p < 0 for p in predictions):
        raise RuntimeError("Solar artifact produced invalid generation.")
    return {"contract_version": VERSION, "location": LOCATION, "reference_system": {"panel_area_m2": metadata["reference_panel_area_m2"], "efficiency": metadata["reference_efficiency"]}, "monthly_reference_generation_kwh_day": predictions, "solar_profiles": {"xgboost": predictions, "baseline": [metadata["baseline_monthly_kwh_day"][str(m)] for m in range(1,13)]}, "model_sha256": digest, "metadata_sha256": hashlib.sha256(metadata_path.read_bytes()).hexdigest(), "evaluation": metadata, "business_profiles": PROFILES, "defaults": DEFAULTS, "assumptions": ASSUMPTIONS, "limitations": LIMITATIONS, "input_limits": LIMITS}

def calculate(payload, evidence=None):
    data = validate(payload)
    evidence = evidence or load_evidence()
    if evidence["contract_version"] != VERSION:
        raise RuntimeError("Scenario evidence contract mismatch.")
    consumption = data["monthly_consumption_kwh"] if data["consumption_mode"] == "measured" else data["average_load_kw"] * data["hours_per_day"] * data["days_per_month"]
    annual_consumption = consumption * 12
    reference = evidence["reference_system"]
    factor = data["panel_area_m2"] / reference["panel_area_m2"] * data["efficiency"] / reference["efficiency"]
    profiles=evidence.get("solar_profiles", {"baseline": evidence["monthly_reference_generation_kwh_day"], "xgboost": evidence["monthly_reference_generation_kwh_day"]})
    months=[]
    for month, daily in enumerate(profiles[data["solar_profile"]],1):
        days=calendar.monthrange(2025,month)[1]
        generation=daily*factor*days
        months.append({"month":month,"days":days,"reference_kwh_day":daily,"generation_kwh":generation,"offset_kwh":min(consumption,generation*data["self_consumption_fraction"])})
    offset=sum(m["offset_kwh"] for m in months)
    avoided=offset*data["tariff_kes_per_kwh"]
    net=avoided-data["annual_maintenance_kes"]
    grid=annual_consumption*data["tariff_kes_per_kwh"]
    pv_grid=(annual_consumption-offset)*data["tariff_kes_per_kwh"]
    return {"contract_version":VERSION,"input":data,"location":LOCATION,"consumption":{"method":data["consumption_mode"],"monthly_kwh":consumption,"annual_kwh":annual_consumption},"solar":{"method":"training-city monthly mean baseline" if data["solar_profile"]=="baseline" else "held-out evaluated XGBoost artifact, derived solar target", "selected_profile":data["solar_profile"], "reference_profiles_kwh_day":profiles, "model_sha256":evidence["model_sha256"],"monthly":months,"annual_generation_kwh":sum(m["generation_kwh"] for m in months),"annual_offset_kwh":offset,"coverage_percent":offset/annual_consumption*100 if annual_consumption else 0},"comparison":{"grid_only_annual_cost_kes":grid,"pv_annual_grid_cost_kes":pv_grid,"pv_annual_operating_cost_kes":pv_grid+data["annual_maintenance_kes"],"annual_avoided_grid_cost_kes":avoided,"net_annual_saving_kes":net,"simple_payback_years":data["installed_cost_kes"]/net if net>0 else None},"sensitivity":[{"tariff_kes_per_kwh":data["tariff_kes_per_kwh"]*mult,"annual_avoided_grid_cost_kes":offset*data["tariff_kes_per_kwh"]*mult,"net_annual_saving_kes":offset*data["tariff_kes_per_kwh"]*mult-data["annual_maintenance_kes"]} for mult in (0.8,1,1.2)],"assumptions":ASSUMPTIONS,"limitations":LIMITATIONS}
