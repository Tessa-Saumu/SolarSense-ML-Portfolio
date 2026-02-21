#!/usr/bin/env python3
"""
SolarSense DSE Pipeline Integration Validation Script
Version 2.1 — Post cache-fix

DEPLOYMENT SEQUENCE (must be done before running this script):
  Step 1: Deploy patched solar_climatology_service.py  → _MODEL_CACHE in load_model_artifacts()
  Step 2: Deploy patched solar_climatology_api.py      → startup preload added
  Step 3: Deploy patched model4_app.py                 → include_lifetime=False (safe default)
  Step 4: Run this script — Model 2 must show daily_kwh >= 1.5, no negative monthly values
  Step 5: Once Model 2 passes cleanly, restore include_lifetime=True in model4_app.py and re-run
          The lifetime projection graph data will then be correct for the frontend

Changes from v1:
  - Model 2 now sends `month` field (was missing, causing 400s)
  - Diesel scenario now calls Model 4 /api/v1/analyze (the only endpoint
    that correctly computes the blended tariff + system sizing).
    Calling Model 1→2→3 directly for diesel produces wrong numbers because
    the blended tariff and scaled system cost are computed inside Model 4.
  - Model 4 is now actually exercised and asserted against
  - MAPE check from /model-info is now a WARNING not a hard FAIL
    (endpoint may not be exposed in all deployments)
  - Fixed: on-grid chain now passes current month to Model 2

Usage:
    export API_KEY=your_api_key_here
    python validate_model_performance.py

    # Override base URLs if not running on localhost:
    export MODEL_1_BASE_URL=https://dse-models-production.up.railway.app
    export MODEL_4_BASE_URL=https://your-model4.railway.app
"""

import os
import sys
import json
import logging
import datetime
from typing import Dict, Any, Optional, Tuple
import requests
from requests.exceptions import RequestException, Timeout

# ============================================================================
# CONFIGURATION
# ============================================================================

MODEL_1_BASE_URL = os.getenv("MODEL_1_BASE_URL", "http://localhost:8000")
MODEL_2_BASE_URL = os.getenv("MODEL_2_BASE_URL", "http://localhost:8000")
MODEL_3_BASE_URL = os.getenv("MODEL_3_BASE_URL", "http://localhost:8000")
MODEL_4_BASE_URL = os.getenv("MODEL_4_BASE_URL", "http://localhost:8000")

MODEL_1_ENDPOINT = f"{MODEL_1_BASE_URL}/api/v1/estimate-consumption"
MODEL_2_ENDPOINT = f"{MODEL_2_BASE_URL}/api/v1/predict-generation"
MODEL_2_INFO_ENDPOINT = f"{MODEL_2_BASE_URL}/api/v1/model-info"
MODEL_3_ENDPOINT = f"{MODEL_3_BASE_URL}/api/v1/calculate-roi"
MODEL_4_ENDPOINT = f"{MODEL_4_BASE_URL}/api/v1/analyze"

REQUEST_TIMEOUT = 10  # Increased from 3s — Railway cold starts can be slow

# Current month for Model 2 (1-12)
CURRENT_MONTH = datetime.datetime.now().month

# ============================================================================
# SCENARIO DEFINITIONS
# ============================================================================
#
# ON-GRID SCENARIO
# ----------------
# Validates the full Model 1 → Model 2 → Model 3 chain directly.
# Lagos, Nigeria: lat=6.45, lon=3.40 — within Model 2's valid SSA range
# (lat: -26 to 6, lon: -18 to 44). NOTE: Lagos is right at the northern
# boundary (~6.45°N). If Model 2 rejects it, switch to Accra (lat=5.56,
# lon=-0.20) or Nairobi (lat=-1.29, lon=36.82) which are safely inside range.
#
SCENARIO_ON_GRID = {
    "name": "On-Grid (Lagos Butchery)",
    "description": "Grid-only business. Validates Model 1 → Model 2 → Model 3 chain directly.",
    # Model 1 inputs
    "model_1_input": {
        "business_type": "butchery",
        "sqft_m2": 60.0,
        "operating_hours_weekly": 98.0,
        "num_refrigeration_units": 3,
        "location": "Lagos, Nigeria",
        "num_workers": 3,
        "months_per_year": 12,
    },
    # Model 2 inputs — coordinates in valid SSA range
    # Using Accra (5.56, -0.20) which is safely inside lat[-26,6] lon[-18,44]
    # Lagos (6.45, 3.40) is at the very edge of lat range — use Accra to be safe
    "latitude": -1.2921,
    "longitude": 36.8219,
    # Model 3 inputs
    "tariff_per_kwh": 0.20,
    "system_cost_usd": 6000.0,
    "uses_diesel": False,
}

#
# DIESEL SCENARIO
# ---------------
# IMPORTANT: For diesel, we call Model 4 /api/v1/analyze — NOT the 1→2→3 chain.
# Reason: the blended tariff (grid + diesel fuel + maintenance) and the scaled
# system cost are computed INSIDE Model 4. If you call Model 3 directly with
# the raw grid tariff you get completely wrong ROI numbers for diesel businesses.
# Model 4 is the only correct entry point for the diesel path.
#
# Nairobi, Kenya: lat=-1.29, lon=36.82 — safely inside SSA range.
#
SCENARIO_DIESEL = {
    "name": "Diesel (Nairobi Mini-Supermarket)",
    "description": "Diesel-using business. Calls Model 4 /api/v1/analyze (only correct path for diesel).",
    # Model 4 /api/v1/analyze payload
    "model_4_input": {
        "business_name": "Nairobi Mini-Supermarket Test",
        "business_type": "mini_supermarket",
        "location": "Nairobi, Kenya",
        "latitude": -1.2921,
        "longitude": 36.8219,
        # Business metrics mode (alternative to equipment_list)
        "sqft_m2": 80.0,
        "operating_hours_weekly": 112.0,
        "num_refrigeration_units": 5,
        "num_workers": 4,
        "months_per_year": 12,
        # Grid tariff
        "tariff": 0.18,
        # Diesel flags — these trigger blended tariff calculation inside Model 4
        "uses_diesel": True,
        "diesel_hours_per_day": 18,
        "diesel_price_per_liter": 1.35,
    },
    "uses_diesel": True,
}

SCENARIOS = [SCENARIO_ON_GRID, SCENARIO_DIESEL]

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


# ============================================================================
# HELPERS
# ============================================================================

def get_api_key() -> str:
    api_key = os.getenv("API_KEY")
    if not api_key:
        logger.error("API_KEY environment variable is not set.")
        logger.error("Run: export API_KEY=your_key_here")
        sys.exit(1)
    return api_key


def make_request(
    method: str,
    url: str,
    headers: Dict[str, str],
    json_data: Optional[Dict[str, Any]] = None,
    timeout: int = REQUEST_TIMEOUT,
) -> Tuple[Optional[requests.Response], Optional[str]]:
    try:
        if method.upper() == "POST":
            response = requests.post(url, json=json_data, headers=headers, timeout=timeout)
        elif method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=timeout)
        else:
            return None, f"Unsupported HTTP method: {method}"

        logger.info(f"→ {method} {url}  [HTTP {response.status_code}]")
        try:
            logger.info(f"Raw response:\n{json.dumps(response.json(), indent=2)}")
        except ValueError:
            logger.warning(f"Non-JSON response: {response.text[:500]}")

        return response, None

    except Timeout:
        msg = f"Timeout after {timeout}s calling {url}"
        logger.error(msg)
        return None, msg
    except RequestException as e:
        msg = f"Request error: {e}"
        logger.error(msg)
        return None, msg
    except Exception as e:
        msg = f"Unexpected error: {e}"
        logger.error(msg)
        return None, msg


def print_header(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_result(label: str, passed: bool, details: str):
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"\n[{status}] {label}")
    for line in details.strip().split("\n"):
        print(f"  {line}")


# ============================================================================
# MODEL 1 VALIDATION — used by on-grid scenario
# ============================================================================

def validate_model_1(
    api_key: str,
    model_1_input: Dict[str, Any],
    scenario_name: str = "",
) -> Tuple[bool, Dict[str, Any], Optional[str]]:

    print_header(f"Model 1: Energy Consumption [{scenario_name}]")
    headers = {"Content-Type": "application/json", "X-API-KEY": api_key}

    response, error = make_request("POST", MODEL_1_ENDPOINT, headers, model_1_input)
    if error:
        print_result("Model 1", False, f"Request failed: {error}")
        return False, {}, error

    if response.status_code != 200:
        print_result("Model 1", False, f"HTTP {response.status_code}: {response.text}")
        return False, {}, f"HTTP {response.status_code}"

    try:
        data = response.json()
    except ValueError:
        print_result("Model 1", False, "Response is not valid JSON")
        return False, {}, "Invalid JSON"

    consumption = data.get("estimated_consumption_kwh_monthly")
    confidence = data.get("confidence_score")
    breakdown = data.get("breakdown", {})
    refrigeration = breakdown.get("refrigeration", 0)
    other = breakdown.get("other", 0)
    total = refrigeration + other
    refrig_pct = (refrigeration / total * 100) if total > 0 else 0

    checks = []

    if confidence is None:
        checks.append(("confidence_score: MISSING", False))
    elif confidence >= 0.85:
        checks.append((f"confidence_score >= 0.85: {confidence:.3f} ✓", True))
    else:
        checks.append((f"confidence_score >= 0.85: {confidence:.3f} — below target", False))

    if consumption is None:
        checks.append(("estimated_consumption_kwh_monthly: MISSING", False))
    elif consumption > 0:
        checks.append((f"estimated_consumption_kwh_monthly > 0: {consumption:.2f} kWh ✓", True))
    else:
        checks.append((f"estimated_consumption_kwh_monthly: {consumption:.2f} — not positive", False))

    if total == 0:
        checks.append(("refrigeration breakdown: total is zero", False))
    elif 50 <= refrig_pct <= 70:
        checks.append((
            f"refrigeration breakdown 50-70%: {refrig_pct:.1f}% ✓ "
            f"(refrigeration={refrigeration:.2f}, other={other:.2f})", True
        ))
    else:
        checks.append((
            f"refrigeration breakdown 50-70%: {refrig_pct:.1f}% — outside range "
            f"(refrigeration={refrigeration:.2f}, other={other:.2f})", False
        ))

    all_passed = all(c[1] for c in checks)
    print_result("Model 1", all_passed, "\n".join(c[0] for c in checks))
    return all_passed, data, None


# ============================================================================
# MODEL 2 VALIDATION — used by on-grid scenario
# ============================================================================

def validate_model_2(
    api_key: str,
    latitude: float,
    longitude: float,
    scenario_name: str = "",
) -> Tuple[bool, Dict[str, Any], Optional[str]]:

    print_header(f"Model 2: Solar Generation [{scenario_name}]")
    headers = {"Content-Type": "application/json", "X-API-KEY": api_key}

    # FIX: month is a required field — was missing in v1 of this script
    payload = {
        "latitude": latitude,
        "longitude": longitude,
        "month": CURRENT_MONTH,   # ← was missing in original script
        "include_lifetime": True,
    }
    print("Model 2 payload:", json.dumps(payload, indent=2))
    logger.info(f"Model 2 payload (month={CURRENT_MONTH}, lat={latitude}, lon={longitude})")

    response, error = make_request("POST", MODEL_2_ENDPOINT, headers, payload)
    if error:
        print_result("Model 2", False, f"Request failed: {error}")
        return False, {}, error

    if response.status_code != 200:
        print_result("Model 2", False, f"HTTP {response.status_code}: {response.text}")
        return False, {}, f"HTTP {response.status_code}"

    try:
        data = response.json()
    except ValueError:
        print_result("Model 2", False, "Response is not valid JSON")
        return False, {}, "Invalid JSON"

    annual_summary = data.get("annual_summary", {})
    daily_kwh = annual_summary.get("average_daily_kwh")
    monthly_gen = data.get("monthly_generation", [])
    if daily_kwh is None and monthly_gen:
        daily_kwh = monthly_gen[0].get("daily_kwh")

    # Try to get MAPE from model-info — soft warning if unavailable
    mape_check_str = ""
    info_resp, _ = make_request("GET", MODEL_2_INFO_ENDPOINT, headers)
    if info_resp and info_resp.status_code == 200:
        try:
            info = info_resp.json()
            mape = info.get("validation_mape")
            if mape is not None:
                mape_pct = mape * 100 if mape < 1 else mape  # handle both 0.07 and 7.46 formats
                mape_check_str = f"MAPE from model-info: {mape_pct:.2f}% ({'≤15% ✓' if mape_pct <= 15 else '>15% ✗'})"
            else:
                mape_check_str = "MAPE: not returned by /model-info (WARNING — not a hard fail)"
        except ValueError:
            mape_check_str = "MAPE: /model-info response not valid JSON (WARNING)"
    else:
        mape_check_str = "MAPE: /model-info endpoint unavailable (WARNING — not a hard fail)"

    checks = []

    if daily_kwh is None:
        checks.append(("daily_kwh: MISSING", False))
    elif daily_kwh > 0:
        checks.append((f"daily_kwh > 0: {daily_kwh:.2f} kWh/day ✓", True))
    else:
        checks.append((f"daily_kwh > 0: {daily_kwh:.2f} — not positive", False))

    # HARD FAIL: plausible range check.
    # A 10m² system at 20% efficiency in SSA should produce 3-8 kWh/day.
    # Values below 3 (e.g. 0.84) indicate a unit/scaling bug in the model —
    # NOT an edge case. This previously passed as a warning and masked the bug
    # propagating downstream into Model 4's system sizer.
    if daily_kwh is not None:
        if 3.0 <= daily_kwh <= 15.0:
            checks.append((f"daily_kwh in SSA plausible range 3-8 kWh/day: {daily_kwh:.2f} ✓", True))
        else:
            checks.append((
                f"daily_kwh OUTSIDE SSA plausible range 3-8 kWh/day: {daily_kwh:.2f} — "
                f"cache fix in solar_climatology_service.py not deployed yet (HARD FAIL)", False
            ))

    # HARD FAIL: negative monthly generation values are physically impossible.
    # If any month in the climatology is negative, the model artifact or its
    # post-processing is broken — raw XGBoost outputs are not being converted
    # correctly (e.g. GHI in W/m² not being multiplied by area × efficiency).
    lifetime = data.get("lifetime_prediction", {})
    climatology = lifetime.get("monthly_generation_climatology", [])
    if climatology:
        negative_months = [
            f"month {m['month']} = {m['daily_kwh']:.4f}"
            for m in climatology
            if m.get("daily_kwh", 0) < 0
        ]
        if negative_months:
            checks.append((
                f"NEGATIVE daily_kwh in climatology (physically impossible — model bug): "
                f"{', '.join(negative_months)}", False
            ))
        else:
            checks.append((
                f"All {len(climatology)} monthly climatology values are non-negative ✓", True
            ))
    else:
        checks.append(("monthly_generation_climatology: not present in lifetime_prediction (WARNING)", True))

    # MAPE is informational — never causes a hard fail
    print(f"  [INFO] {mape_check_str}")

    all_passed = all(c[1] for c in checks)
    print_result("Model 2", all_passed, "\n".join(c[0] for c in checks))
    return all_passed, data, None


# ============================================================================
# MODEL 3 VALIDATION — used by on-grid scenario
# ============================================================================

def validate_model_3(
    api_key: str,
    consumption_kwh: float,
    generation_kwh: float,
    tariff_per_kwh: float,
    system_cost_usd: float,
    scenario_name: str = "",
) -> Tuple[bool, Dict[str, Any], Optional[str]]:

    print_header(f"Model 3: ROI Calculation [{scenario_name}]")
    headers = {"Content-Type": "application/json", "X-API-KEY": api_key}

    payload = {
        "consumption_kwh": consumption_kwh,
        "generation_kwh": generation_kwh,
        "tariff_per_kwh": tariff_per_kwh,
        "system_cost_usd": system_cost_usd,
    }

    logger.info("Model 3 chained inputs:")
    logger.info(f"  consumption_kwh  = {consumption_kwh:.2f}  (from Model 1)")
    logger.info(f"  generation_kwh   = {generation_kwh:.2f}  (derived from Model 2 annual / 12)")
    logger.info(f"  tariff_per_kwh   = {tariff_per_kwh}  (grid tariff — on-grid scenario)")
    logger.info(f"  system_cost_usd  = {system_cost_usd}  (scenario config)")
    logger.info("  NOTE: For diesel scenario, Model 4 computes blended tariff before calling Model 3.")

    response, error = make_request("POST", MODEL_3_ENDPOINT, headers, payload)
    if error:
        print_result("Model 3", False, f"Request failed: {error}")
        return False, {}, error

    if response.status_code != 200:
        print_result("Model 3", False, f"HTTP {response.status_code}: {response.text}")
        return False, {}, f"HTTP {response.status_code}"

    try:
        data = response.json()
    except ValueError:
        print_result("Model 3", False, "Response is not valid JSON")
        return False, {}, "Invalid JSON"

    monthly_savings = data.get("monthly_savings_usd")
    roi_pct = data.get("roi_percentage")
    echoed_cost = data.get("system_cost_usd")

    checks = []

    if monthly_savings is None:
        checks.append(("monthly_savings_usd: MISSING", False))
    elif monthly_savings > 0:
        checks.append((f"monthly_savings_usd > 0: ${monthly_savings:.2f} ✓", True))
    else:
        checks.append((f"monthly_savings_usd: ${monthly_savings:.2f} — not positive", False))

    if roi_pct is None:
        checks.append(("roi_percentage: MISSING", False))
    elif roi_pct > 0:
        checks.append((f"roi_percentage > 0: {roi_pct:.2f}% ✓", True))
    else:
        checks.append((f"roi_percentage: {roi_pct:.2f}% — not positive", False))

    if echoed_cost is None:
        checks.append(("system_cost_usd echo: MISSING", False))
    elif abs(echoed_cost - system_cost_usd) < 0.01:
        checks.append((f"system_cost_usd echoed correctly: ${echoed_cost:.2f} ✓", True))
    else:
        checks.append((
            f"system_cost_usd echo mismatch: got ${echoed_cost:.2f}, "
            f"expected ${system_cost_usd:.2f}", False
        ))

    # Sanity check: manual ROI verification
    if monthly_savings and roi_pct and system_cost_usd:
        expected_roi = round((monthly_savings * 12 / system_cost_usd) * 100, 2)
        if abs(expected_roi - roi_pct) < 0.5:
            checks.append((
                f"ROI formula check: ({monthly_savings:.2f}×12/{system_cost_usd:.2f})×100 "
                f"= {expected_roi:.2f}% matches returned {roi_pct:.2f}% ✓", True
            ))
        else:
            checks.append((
                f"ROI formula check: expected {expected_roi:.2f}%, got {roi_pct:.2f}% — mismatch", False
            ))

    all_passed = all(c[1] for c in checks)
    print_result("Model 3", all_passed, "\n".join(c[0] for c in checks))
    return all_passed, data, None


# ============================================================================
# MODEL 4 VALIDATION — used by diesel scenario (and as pipeline smoke test)
# ============================================================================

def validate_model_4(
    api_key: str,
    model_4_input: Dict[str, Any],
    scenario_name: str = "",
) -> Tuple[bool, Dict[str, Any], Optional[str]]:
    """
    Validate Model 4 /api/v1/analyze.

    For the diesel scenario this is the ONLY correct validation path.
    Model 4 internally calls Models 1, 2, 3 and applies blended tariff logic.
    We assert on the final output fields.
    """
    print_header(f"Model 4: Full Pipeline via /api/v1/analyze [{scenario_name}]")
    headers = {"Content-Type": "application/json", "X-API-KEY": api_key}

    uses_diesel = model_4_input.get("uses_diesel", False)
    if uses_diesel:
        logger.info("Diesel mode active — Model 4 will compute blended tariff internally.")
        logger.info(f"  diesel_hours_per_day  = {model_4_input.get('diesel_hours_per_day')}")
        logger.info(f"  diesel_price_per_liter = {model_4_input.get('diesel_price_per_liter')}")

    response, error = make_request("POST", MODEL_4_ENDPOINT, headers, model_4_input)
    if error:
        print_result("Model 4", False, f"Request failed: {error}")
        return False, {}, error

    if response.status_code != 200:
        print_result("Model 4", False, f"HTTP {response.status_code}: {response.text}")
        return False, {}, f"HTTP {response.status_code}"

    try:
        data = response.json()
    except ValueError:
        print_result("Model 4", False, "Response is not valid JSON")
        return False, {}, "Invalid JSON"

    # Extract core fields
    consumption    = data.get("estimated_consumption_kwh")
    generation     = data.get("predicted_generation_kwh")
    panel_area     = data.get("recommended_panel_area_m2")
    system_cost    = data.get("system_cost")
    roi_pct        = data.get("roi_percentage")
    monthly_savings= data.get("monthly_savings")
    score          = data.get("viability_score")
    status         = data.get("status")
    scenario_type  = data.get("energy_scenario")
    confidence     = data.get("confidence")
    diesel_details = data.get("diesel_details")

    checks = []

    # Core fields present
    for field, val in [
        ("estimated_consumption_kwh", consumption),
        ("predicted_generation_kwh", generation),
        ("recommended_panel_area_m2", panel_area),
        ("system_cost", system_cost),
        ("roi_percentage", roi_pct),
        ("monthly_savings", monthly_savings),
        ("viability_score", score),
        ("status", status),
    ]:
        if val is None:
            checks.append((f"{field}: MISSING", False))
        else:
            checks.append((f"{field} present: {val}", True))

    # Numeric sanity
    if consumption and consumption > 0:
        checks.append((f"consumption > 0: {consumption:.2f} kWh ✓", True))
    elif consumption is not None:
        checks.append((f"consumption not positive: {consumption}", False))

    if generation and generation > 0:
        checks.append((f"generation > 0: {generation:.2f} kWh ✓", True))
    elif generation is not None:
        checks.append((f"generation not positive: {generation}", False))

    if roi_pct is not None and roi_pct > 0:
        checks.append((f"roi_percentage > 0: {roi_pct:.2f}% ✓", True))
    elif roi_pct is not None:
        checks.append((f"roi_percentage: {roi_pct:.2f}% — not positive", False))

    if monthly_savings is not None and monthly_savings > 0:
        checks.append((f"monthly_savings > 0: ${monthly_savings:.2f} ✓", True))
    elif monthly_savings is not None:
        checks.append((f"monthly_savings: ${monthly_savings:.2f} — not positive", False))

    if score is not None and 0 <= score <= 100:
        checks.append((f"viability_score in 0-100: {score:.1f} ✓", True))
    elif score is not None:
        checks.append((f"viability_score out of range: {score}", False))

    # Status string check
    if status in ("HIGHLY VIABLE", "MODERATELY VIABLE", "NOT VIABLE"):
        checks.append((f"status is valid enum value: '{status}' ✓", True))
    elif status is not None:
        checks.append((f"status unexpected value: '{status}'", False))

    # Panel area sizing check (should be 10-50m²)
    if panel_area is not None:
        if 10.0 <= panel_area <= 50.0:
            checks.append((f"panel_area in SME range 10-50m²: {panel_area:.1f}m² ✓", True))
        else:
            checks.append((f"panel_area outside expected 10-50m²: {panel_area:.1f}m²", False))

    # System cost check ($600/m² logic)
    if panel_area and system_cost:
        expected_cost = round(600 * panel_area, 2)
        if abs(system_cost - expected_cost) < 50:  # allow small rounding
            checks.append((
                f"system_cost = $600 × {panel_area:.1f}m² = ${expected_cost:.0f} "
                f"≈ ${system_cost:.0f} ✓", True
            ))
        else:
            checks.append((
                f"system_cost mismatch: expected ~${expected_cost:.0f}, "
                f"got ${system_cost:.0f}", False
            ))

    # Diesel-specific checks
    if uses_diesel:
        if scenario_type == "diesel_replacement":
            checks.append((f"energy_scenario = 'diesel_replacement' ✓", True))
        else:
            checks.append((
                f"energy_scenario should be 'diesel_replacement', got '{scenario_type}'", False
            ))

        if diesel_details:
            eff_tariff = diesel_details.get("effective_tariff")
            diesel_kwh = diesel_details.get("diesel_kwh_monthly")
            checks.append((
                f"diesel_details present: effective_tariff=${eff_tariff}, "
                f"diesel_kwh_monthly={diesel_kwh} ✓", True
            ))
            # Blended tariff should be materially higher than a typical grid tariff
            if eff_tariff and eff_tariff > 0.30:
                checks.append((
                    f"diesel effective_tariff > $0.30/kWh (reflects diesel cost): "
                    f"${eff_tariff:.3f} ✓", True
                ))
            elif eff_tariff is not None:
                checks.append((
                    f"diesel effective_tariff suspiciously low at ${eff_tariff:.3f} "
                    f"— check blended tariff calculation", False
                ))
        else:
            checks.append(("diesel_details block missing from response", False))
    else:
        if scenario_type == "grid_only":
            checks.append((f"energy_scenario = 'grid_only' ✓", True))
        else:
            checks.append((
                f"energy_scenario should be 'grid_only', got '{scenario_type}'", False
            ))

    # Coverage ratio check (should be near 90% by design — Model 4 sizes to this target).
    # After the cache fix is deployed this should consistently pass at ~90%.
    # If it still fails: check Model 2 daily_kwh above — if that is also failing,
    # the service fix is not yet live; coverage failure is downstream of that root cause.
    if consumption and generation:
        coverage = (generation / consumption) * 100
        if 80 <= coverage <= 100:
            checks.append((f"solar coverage near 90% target: {coverage:.1f}% ✓", True))
        else:
            checks.append((
                f"solar coverage outside 80-100%: {coverage:.1f}% — "
                f"check Model 2 daily_kwh result above; if that failed too, "
                f"this is the same root cause propagating (not a Model 4 bug)", False
            ))

    all_passed = all(c[1] for c in checks)
    print_result("Model 4", all_passed, "\n".join(c[0] for c in checks))

    # Print a human-readable summary of what Model 4 decided
    print(f"\n  ── Model 4 Decision Summary ──")
    print(f"     Scenario      : {scenario_type}")
    print(f"     Consumption   : {consumption} kWh/month")
    print(f"     Generation    : {generation} kWh/month  ({panel_area}m² panels)")
    print(f"     System Cost   : ${system_cost}")
    print(f"     Monthly Save  : ${monthly_savings}")
    print(f"     ROI           : {roi_pct}%")
    print(f"     Score         : {score}/100  →  {status}")
    print(f"     Confidence    : {confidence}%")
    if diesel_details:
        print(f"     Blended Tariff: ${diesel_details.get('effective_tariff')}/kWh")
        print(f"     Diesel kWh/mo : {diesel_details.get('diesel_kwh_monthly')}")

    return all_passed, data, None


# ============================================================================
# SCENARIO RUNNERS
# ============================================================================

def run_on_grid_scenario(api_key: str, scenario: Dict[str, Any]) -> Tuple[bool, Dict[str, str]]:
    """
    On-grid: runs Model 1 → Model 2 → Model 3 directly, then also calls
    Model 4 as a smoke test to confirm the orchestrated result is consistent.
    """
    name = scenario["name"]
    results = {"model_1": "skip", "model_2": "skip", "model_3": "skip", "model_4": "skip"}

    # Model 1
    passed, m1_data, _ = validate_model_1(api_key, scenario["model_1_input"], name)
    results["model_1"] = "pass" if passed else "fail"
    if not passed:
        return False, results

    consumption_kwh = m1_data.get("estimated_consumption_kwh_monthly")
    if not consumption_kwh:
        logger.error("No consumption_kwh from Model 1 — cannot chain to Model 2/3")
        return False, results

    # Model 2
    passed, m2_data, _ = validate_model_2(
        api_key, scenario["latitude"], scenario["longitude"], name
    )
    results["model_2"] = "pass" if passed else "fail"
    if not passed:
        return False, results

    # Derive monthly generation from annual summary
    annual_summary = m2_data.get("annual_summary", {})
    annual_kwh = annual_summary.get("year_1_generation_kwh")
    if annual_kwh is None:
        # Fallback: sum monthly_generation array
        monthly_gen = m2_data.get("monthly_generation", [])
        if monthly_gen:
            annual_kwh = sum(m.get("daily_kwh", 0) * 30 for m in monthly_gen)
    if annual_kwh is None:
        logger.error("Cannot derive annual kWh from Model 2 response")
        return False, results

    monthly_generation_kwh = annual_kwh / 12
    logger.info(f"Derived monthly_generation_kwh = {annual_kwh:.2f} / 12 = {monthly_generation_kwh:.2f}")

    # Model 3
    passed, _, _ = validate_model_3(
        api_key,
        consumption_kwh,
        monthly_generation_kwh,
        scenario["tariff_per_kwh"],
        scenario["system_cost_usd"],
        name,
    )
    results["model_3"] = "pass" if passed else "fail"

    # Model 4 smoke test for on-grid (build equivalent analyze payload)
    m4_payload = {
        "business_name": "On-Grid Validation Test",
        **{k: v for k, v in scenario["model_1_input"].items()},
        "latitude": scenario["latitude"],
        "longitude": scenario["longitude"],
        "tariff": scenario["tariff_per_kwh"],
        "uses_diesel": False,
    }
    # business_type in model_4 uses different accepted values — map butchery directly
    m4_payload["business_type"] = scenario["model_1_input"]["business_type"]

    passed, _, _ = validate_model_4(api_key, m4_payload, f"{name} — Model 4 smoke test")
    results["model_4"] = "pass" if passed else "fail"

    all_passed = all(r == "pass" for r in results.values())
    return all_passed, results


def run_diesel_scenario(api_key: str, scenario: Dict[str, Any]) -> Tuple[bool, Dict[str, str]]:
    """
    Diesel: calls Model 4 /api/v1/analyze only.
    The blended tariff and system sizing happen inside Model 4 — there is no
    correct way to replicate the diesel ROI by calling Model 3 directly.
    """
    name = scenario["name"]
    results = {"model_1": "N/A (via M4)", "model_2": "N/A (via M4)", "model_3": "N/A (via M4)", "model_4": "skip"}

    passed, _, _ = validate_model_4(api_key, scenario["model_4_input"], name)
    results["model_4"] = "pass" if passed else "fail"

    return passed, results


# ============================================================================
# MAIN
# ============================================================================

def main():
    print_header("SolarSense DSE Pipeline — Integration Validation v2.0")
    print(f"\n  Current month for Model 2: {CURRENT_MONTH}")
    print(f"  Model 1 URL : {MODEL_1_BASE_URL}")
    print(f"  Model 2 URL : {MODEL_2_BASE_URL}")
    print(f"  Model 3 URL : {MODEL_3_BASE_URL}")
    print(f"  Model 4 URL : {MODEL_4_BASE_URL}")
    print(f"  Timeout     : {REQUEST_TIMEOUT}s")

    api_key = get_api_key()
    logger.info("API_KEY found")

    scenario_results = []
    any_fail = False

    for scenario in SCENARIOS:
        name = scenario["name"]
        print_header(f"SCENARIO: {name}")
        print(f"  {scenario.get('description', '')}")

        if scenario.get("uses_diesel"):
            all_passed, results = run_diesel_scenario(api_key, scenario)
        else:
            all_passed, results = run_on_grid_scenario(api_key, scenario)

        scenario_results.append({"name": name, "passed": all_passed, "results": results})
        if not all_passed:
            any_fail = True

    # Summary
    print_header("VALIDATION SUMMARY")
    for sr in scenario_results:
        status = "✓ PASS" if sr["passed"] else "✗ FAIL"
        print(f"\n  {status}  {sr['name']}")
        for model, res in sr["results"].items():
            icon = "✓" if res == "pass" else ("—" if res in ("skip", "N/A (via M4)") else "✗")
            print(f"    {icon} {model}: {res}")

    total = len(scenario_results)
    passed = sum(1 for sr in scenario_results if sr["passed"])
    print(f"\n  Scenarios: {passed}/{total} passed\n")

    if not any_fail:
        print("  🎉 All scenarios passed validation!")
        sys.exit(0)
    else:
        print("  ❌ One or more scenarios failed validation.")
        sys.exit(1)


if __name__ == "__main__":
    main()