"""Minimal-input exploratory assessment using a real consumption tree ensemble."""
from __future__ import annotations
import calendar
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from .core import load_evidence, ScenarioValidationError

ROOT = Path(__file__).resolve().parents[1]
VERSION = "solarsense-assessment-v1"
BUSINESSES = {"frozen_food_retail", "butchery", "cold_storage", "mini_mart", "mini_supermarket", "grocery", "bakery", "restaurant", "cafe"}
DEFAULTS = {"business_name": "My food business", "business_type": "grocery", "country": "Kenya", "city": "Nairobi", "floor_area_m2": 100, "operating_hours_weekly": 84, "refrigeration_units": 3, "power_source": "grid", "equipment": []}
ASSUMPTIONS = {"grid_tariff_kes_per_kwh": 25, "diesel_cost_kes_per_kwh": 55, "hybrid_diesel_fraction": .4, "installed_cost_kes_per_kw": 100000, "annual_maintenance_fraction": .01, "panel_efficiency": .2, "panel_kw": .4, "usable_roof_fraction": .6, "target_solar_fraction": .8, "self_consumption_fraction": .8, "performance_ratio": .85}
EQUIPMENT_WATTS = {"freezer": 300, "fridge": 200, "cold_room": 6000, "display_cooler": 350, "ice_machine": 500, "lighting": 60}
LIMITATIONS = ["Exploratory prototype, not a site survey, installation design or investment recommendation.", "Consumption is a real gradient-boosted model trained on US 2018 buildings, not locally validated African shops; its 63.05% holdout MAPE is worse than the area-intensity baseline's 59.03%.", "Solar is an irradiance-derived monthly climatology, not measured panel output. Weather, shading, roof orientation, grid outages, battery dispatch and export sales are not simulated.", "Prices, roof availability and operating losses are editable demonstration assumptions, not verified tariffs or installer quotations. Savings and payback are conditional estimates.", "The consumption model uses floor area, weekly hours, refrigeration-unit count and a broad food-sales/service indicator. Appliance subtypes and appliance-specific hours do not have separately learned effects."]
LIMITATIONS.append("The equipment crosscheck uses illustrative average watts, not measured appliance ratings or learned duty cycles. It does not replace or validate the consumption-model output.")


def load_assessment_evidence():
    p = ROOT/"models/energy_consumption/models/consumption_observable_v1.json"
    model = json.loads(p.read_text(encoding="utf-8"))
    receipt = json.loads((ROOT/"evidence/consumption_evaluation.json").read_text(encoding="utf-8"))
    digest = hashlib.sha256(p.read_bytes()).hexdigest()
    if digest != receipt["model_sha256"]:
        raise RuntimeError("Consumption artifact differs from evaluation receipt.")
    solar = load_evidence()
    return {"version": VERSION, "defaults": DEFAULTS, "assumptions": ASSUMPTIONS, "equipment_watts": EQUIPMENT_WATTS, "limitations": LIMITATIONS, "consumption_model": model, "consumption_evaluation": receipt, "consumption_model_sha256": digest, "solar_profiles": solar["solar_profiles"], "solar_evaluation": solar["evaluation"], "solar_model_sha256": solar["model_sha256"], "solar_reference_system": solar["reference_system"], "business_types": sorted(BUSINESSES)}


def predict_annual(features, model):
    # sklearn decision trees compare float32 input values against float64 thresholds.
    values = np.asarray(features, dtype=np.float32)
    score = model["init_log"]
    for tree in model["trees"]:
        node = 0
        while tree["children_left"][node] != -1:
            node = tree["children_left"][node] if values[tree["feature"][node]] <= tree["threshold"][node] else tree["children_right"][node]
        score += model["learning_rate"]*tree["value"][node]
    result = math.expm1(score)
    if not math.isfinite(result) or result <= 0:
        raise RuntimeError("Consumption model produced invalid output.")
    return result


def validate_assessment(payload):
    if not isinstance(payload, dict):
        raise ScenarioValidationError("Provide a JSON object.")
    unknown = set(payload)-set(DEFAULTS)-{"assumptions"}
    if unknown:
        raise ScenarioValidationError("Unknown fields: "+", ".join(sorted(unknown)))
    data = {**DEFAULTS, **payload}
    if not isinstance(data["business_type"], str) or data["business_type"] not in BUSINESSES:
        raise ScenarioValidationError("Unsupported business type.")
    for field in ("business_name", "city", "country"):
        if not isinstance(data[field], str) or not 1 <= len(data[field].strip()) <= 200:
            raise ScenarioValidationError(field+" must be a nonempty string up to 200 characters.")
    if data["country"] != "Kenya" or data["city"] != "Nairobi":
        raise ScenarioValidationError("This runnable prototype supports Nairobi, Kenya only.")
    if not isinstance(data["power_source"],str) or data["power_source"] not in {"grid", "hybrid", "diesel"}:
        raise ScenarioValidationError("power_source must be grid, hybrid or diesel.")
    for key, low, high in [("floor_area_m2", 1, 10000), ("operating_hours_weekly", 1, 168), ("refrigeration_units", 0, 500)]:
        v = data[key]
        if isinstance(v, bool) or not isinstance(v,(float,int)) or not math.isfinite(v) or not low <= v <= high or (key == "refrigeration_units" and int(v) != v):
            raise ScenarioValidationError(f"{key} must be a number between {low} and {high}. Refrigeration units must be whole units.")
    if not isinstance(data["equipment"], list) or len(data["equipment"]) > 20:
        raise ScenarioValidationError("equipment must be a list of at most 20 entries.")
    for item in data["equipment"]:
        if not isinstance(item,dict) or set(item)-{"type","quantity","hours_per_day"} or not isinstance(item.get("type"),str) or item.get("type") not in {"freezer","fridge","cold_room","display_cooler","ice_machine","lighting"}:
            raise ScenarioValidationError("Unsupported equipment entry.")
        for key, maximum in [("quantity",500),("hours_per_day",24)]:
            v=item.get(key)
            if isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v) or not 0 <= v <= maximum or (key=="quantity" and int(v)!=v):
                raise ScenarioValidationError("Invalid equipment quantity or daily hours.")
    if data["equipment"]:
        units = sum(i["quantity"] for i in data["equipment"] if i["type"] != "lighting")
        if units != data["refrigeration_units"]:
            raise ScenarioValidationError("refrigeration_units must match the non-lighting equipment count.")
    override = data.pop("assumptions", {})
    if not isinstance(override,dict) or set(override)-set(ASSUMPTIONS):
        raise ScenarioValidationError("Unknown assessment assumptions.")
    assumptions = {**ASSUMPTIONS, **override}
    fractions={"hybrid_diesel_fraction","annual_maintenance_fraction","panel_efficiency","usable_roof_fraction","target_solar_fraction","self_consumption_fraction","performance_ratio"}
    for key,value in assumptions.items():
        low = 0 if key in {"grid_tariff_kes_per_kwh","diesel_cost_kes_per_kwh","annual_maintenance_fraction","hybrid_diesel_fraction"} else .000001
        high = 1 if key in fractions else 1000000
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not low <= value <= high:
            raise ScenarioValidationError(f"Invalid assumption {key}.")
    return data, assumptions


def assess(payload, evidence=None):
    data, assumptions = validate_assessment(payload)
    evidence = evidence or load_assessment_evidence()
    if evidence["version"] != VERSION:
        raise RuntimeError("Assessment evidence version mismatch.")
    features = [data["floor_area_m2"], data["operating_hours_weekly"], data["refrigeration_units"], int(data["business_type"] in {"restaurant","cafe"})]
    model = evidence["consumption_model"]
    annual = predict_annual(features, model)
    warnings = []
    for key,value in zip(model["feature_names"],features):
        bounds = model["training_ranges"][key]
        if not bounds["min"] <= value <= bounds["max"]:
            warnings.append(f"{key} is outside the US training range ({bounds['min']:.2f}–{bounds['max']:.2f}); extrapolation is unreliable.")
    if data["business_type"] == "cold_storage":
        warnings.append("Cold storage is mapped to food sales for this prototype; dedicated refrigerated warehouses were not in this repaired training cohort.")
    monthly = annual/12
    equipment_kwh = sum(evidence["equipment_watts"][i["type"]]*i["quantity"]*i["hours_per_day"]*365/12/1000 for i in data["equipment"])
    reference_kw = evidence["solar_reference_system"]["panel_area_m2"]*evidence["solar_reference_system"]["efficiency"]
    profile = evidence["solar_profiles"]["baseline"]  # Better Nairobi holdout result; retained openly.
    specific = sum(day*calendar.monthrange(2025,m)[1] for m,day in enumerate(profile,1))/reference_kw*assumptions["performance_ratio"]
    roof = data["floor_area_m2"]*assumptions["usable_roof_fraction"]
    target_kw = annual*assumptions["target_solar_fraction"]/(specific*assumptions["self_consumption_fraction"])
    max_roof_kw = roof*assumptions["panel_efficiency"]
    panel_count = max(0, math.floor(min(target_kw,max_roof_kw)/assumptions["panel_kw"]+1e-12))
    capacity = panel_count*assumptions["panel_kw"]
    area = capacity/assumptions["panel_efficiency"]
    months=[]
    for month,daily in enumerate(profile,1):
        days=calendar.monthrange(2025,month)[1]
        generation=daily/reference_kw*capacity*days*assumptions["performance_ratio"]
        months.append({"month":month,"generation_kwh":generation,"consumption_kwh":monthly,"offset_kwh":min(monthly,generation*assumptions["self_consumption_fraction"])})
    generation=sum(m["generation_kwh"] for m in months)
    offset=sum(m["offset_kwh"] for m in months)
    diesel_fraction = {"grid":0,"diesel":1,"hybrid":assumptions["hybrid_diesel_fraction"]}[data["power_source"]]
    rate=assumptions["grid_tariff_kes_per_kwh"]*(1-diesel_fraction)+assumptions["diesel_cost_kes_per_kwh"]*diesel_fraction
    capex=capacity*assumptions["installed_cost_kes_per_kw"]
    maintenance=capex*assumptions["annual_maintenance_fraction"]
    gross=offset*rate
    net=gross-maintenance
    payback=capex/net if net>0 and capex>0 else None
    roof_limited=max_roof_kw<target_kw
    verdict="promising_under_assumptions" if payback is not None and payback<=10 and not warnings else "needs_site_assessment"
    return {"version":VERSION,"input":data,"consumption":{"method":"leakage-free gradient-boosted tree model; US food-building transfer prototype","annual_kwh":annual,"monthly_kwh":monthly,"equipment_monthly_kwh":equipment_kwh,"area_baseline_monthly_kwh":data["floor_area_m2"]*model["area_baseline_annual_kwh_per_m2"]/12,"model_sha256":evidence["consumption_model_sha256"],"model_features":dict(zip(model["feature_names"],features)),"warnings":warnings},"system":{"capacity_kw":capacity,"panel_count":panel_count,"panel_area_m2":area,"assumed_available_roof_m2":roof,"roof_limited":roof_limited},"solar":{"method":"training-city monthly baseline; better than XGBoost on Nairobi holdout","model_sha256":evidence["solar_model_sha256"],"annual_generation_kwh":generation,"annual_offset_kwh":offset,"coverage_percent":offset/annual*100,"monthly":months},"economics":{"currency":"KES","blended_cost_kes_per_kwh":rate,"estimated_installation_cost_kes":capex,"annual_without_solar_cost_kes":annual*rate,"annual_with_solar_cost_kes":(annual-offset)*rate+maintenance,"gross_annual_saving_kes":gross,"annual_maintenance_kes":maintenance,"net_annual_saving_kes":net,"simple_payback_years":payback},"recommendation":{"verdict":verdict,"summary":"Conditional screening only: verify actual bills, usable roof and an installer quote before any decision.","roof_limited":roof_limited,"out_of_training_range":bool(warnings)},"assumptions":assumptions,"limitations":evidence["limitations"]}
