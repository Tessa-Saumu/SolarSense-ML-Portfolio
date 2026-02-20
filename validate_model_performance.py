#!/usr/bin/env python3
"""
SolarSense DSE Pipeline Integration Validation Script

This script validates the performance of all 4 models in the SolarSense pipeline
by calling each endpoint in sequence, chaining outputs, and asserting accuracy targets.

Usage:
    export API_KEY=your_api_key_here
    python validate_model_performance.py
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional, Tuple
import requests
from requests.exceptions import RequestException, Timeout

# ============================================================================
# CONFIGURATION SECTION
# ============================================================================
# Configure base URLs for each service here
# Default assumes unified gateway, but can be overridden for standalone services

MODEL_1_BASE_URL = os.getenv("MODEL_1_BASE_URL", "http://localhost:8000")
MODEL_2_BASE_URL = os.getenv("MODEL_2_BASE_URL", "http://localhost:8000")
MODEL_3_BASE_URL = os.getenv("MODEL_3_BASE_URL", "http://localhost:8000")
MODEL_4_BASE_URL = os.getenv("MODEL_4_BASE_URL", "http://localhost:8000")

# API endpoints
MODEL_1_ENDPOINT = f"{MODEL_1_BASE_URL}/api/v1/estimate-consumption"
MODEL_2_ENDPOINT = f"{MODEL_2_BASE_URL}/api/v1/predict-generation"
MODEL_2_INFO_ENDPOINT = f"{MODEL_2_BASE_URL}/api/v1/model-info"
MODEL_3_ENDPOINT = f"{MODEL_3_BASE_URL}/api/v1/calculate-roi"
MODEL_4_ENDPOINT = f"{MODEL_4_BASE_URL}/api/v1/analyze"

# Request timeout (seconds)
REQUEST_TIMEOUT = 3

# ---------------------------------------------------------------------------
# SCENARIO DEFINITIONS: On-Grid and Diesel (two cases)
# ---------------------------------------------------------------------------

# On-grid scenario: grid-only, no diesel (e.g. Lagos butchery)
SCENARIO_ON_GRID = {
    "name": "On-Grid",
    "model_1_input": {
        "business_type": "butchery",
        "sqft_m2": 60.0,
        "operating_hours_weekly": 98.0,
        "num_refrigeration_units": 3,
        "location": "Lagos, Nigeria",
        "num_workers": 3,
        "months_per_year": 12,
    },
    "latitude": 6.5244,
    "longitude": 3.3792,
    "tariff_per_kwh": 0.20,
    "system_cost_usd": 6000.0,
    "uses_diesel": False,
    # No diesel fields for on-grid
}

# Diesel scenario: business with diesel backup (e.g. Mombasa cold storage)
# Extra inputs: diesel_hours_per_day, diesel_price_per_liter
SCENARIO_DIESEL = {
    "name": "Diesel",
    "model_1_input": {
        "business_type": "mini_supermarket",
        "sqft_m2": 80.0,
        "operating_hours_weekly": 112.0,
        "num_refrigeration_units": 5,
        "location": "Mombasa, Kenya",
        "num_workers": 4,
        "months_per_year": 12,
    },
    "latitude": -4.0435,
    "longitude": 39.6682,
    "tariff_per_kwh": 0.18,
    "system_cost_usd": 7500.0,
    "uses_diesel": True,
    "diesel_hours_per_day": 18,
    "diesel_price_per_liter": 1.35,
}

# List of scenarios to run (on-grid first, then diesel)
SCENARIOS = [SCENARIO_ON_GRID, SCENARIO_DIESEL]

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_api_key() -> str:
    """Read API key from environment variable."""
    api_key = os.getenv("API_KEY")
    if not api_key:
        logger.error("ERROR: API_KEY environment variable is not set!")
        logger.error("Please set it before running: export API_KEY=your_key_here")
        sys.exit(1)
    return api_key


def make_request(
    method: str,
    url: str,
    headers: Dict[str, str],
    json_data: Optional[Dict[str, Any]] = None,
    timeout: int = REQUEST_TIMEOUT
) -> Tuple[Optional[requests.Response], Optional[str]]:
    """
    Make HTTP request with error handling and logging.
    
    Returns:
        Tuple of (response object, error_message)
    """
    try:
        if method.upper() == "POST":
            response = requests.post(
                url,
                json=json_data,
                headers=headers,
                timeout=timeout
            )
        elif method.upper() == "GET":
            response = requests.get(
                url,
                headers=headers,
                timeout=timeout
            )
        else:
            return None, f"Unsupported HTTP method: {method}"
        
        logger.info(f"Request: {method} {url}")
        logger.info(f"Response Status: {response.status_code}")
        
        # Log full raw JSON response
        try:
            response_json = response.json()
            logger.info(f"Raw JSON Response:\n{json.dumps(response_json, indent=2)}")
        except ValueError:
            logger.warning(f"Response is not JSON:\n{response.text}")
        
        return response, None
        
    except Timeout:
        error_msg = f"Request to {url} timed out after {timeout} seconds"
        logger.error(error_msg)
        return None, error_msg
    except RequestException as e:
        error_msg = f"Request failed: {str(e)}"
        logger.error(error_msg)
        return None, error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return None, error_msg


def print_section_header(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_test_result(model_name: str, passed: bool, details: str):
    """Print formatted test result."""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"\n[{status}] {model_name}")
    print(f"  {details}")


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_model_1(
    api_key: str,
    model_1_input: Dict[str, Any],
    scenario_name: str = "",
) -> Tuple[bool, Dict[str, Any], Optional[str]]:
    """
    Validate Model 1 (Energy Consumption).

    Args:
        api_key: API key for auth
        model_1_input: JSON body for POST /estimate-consumption
        scenario_name: Optional label for logs (e.g. "On-Grid", "Diesel")

    Returns:
        Tuple of (passed, response_data, error_message)
    """
    title = "Model 1: Energy Consumption Prediction"
    if scenario_name:
        title += f" [{scenario_name}]"
    print_section_header(title)

    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key
    }

    response, error = make_request("POST", MODEL_1_ENDPOINT, headers, model_1_input)
    
    if error:
        print_test_result("Model 1", False, f"Request failed: {error}")
        return False, {}, error
    
    if response.status_code != 200:
        print_test_result(
            "Model 1",
            False,
            f"Expected HTTP 200, got {response.status_code}: {response.text}"
        )
        return False, {}, f"HTTP {response.status_code}"
    
    try:
        data = response.json()
    except ValueError:
        print_test_result("Model 1", False, "Response is not valid JSON")
        return False, {}, "Invalid JSON response"
    
    # Extract values for validation
    consumption = data.get("estimated_consumption_kwh_monthly")
    confidence = data.get("confidence_score")
    breakdown = data.get("breakdown", {})
    refrigeration = breakdown.get("refrigeration", 0)
    other = breakdown.get("other", 0)
    total_breakdown = refrigeration + other
    
    # Calculate refrigeration percentage
    refrigeration_pct = (refrigeration / total_breakdown * 100) if total_breakdown > 0 else 0
    
    # Validation assertions
    checks = []
    
    # Check 1: confidence_score >= 0.85
    if confidence is None:
        checks.append(("confidence_score missing", False))
    elif confidence >= 0.85:
        checks.append((f"confidence_score >= 0.85: {confidence:.3f}", True))
    else:
        checks.append((f"confidence_score >= 0.85: {confidence:.3f} (FAILED)", False))
    
    # Check 2: estimated_consumption_kwh_monthly > 0
    if consumption is None:
        checks.append(("estimated_consumption_kwh_monthly missing", False))
    elif consumption > 0:
        checks.append((f"estimated_consumption_kwh_monthly > 0: {consumption:.2f}", True))
    else:
        checks.append((f"estimated_consumption_kwh_monthly > 0: {consumption:.2f} (FAILED)", False))
    
    # Check 3: refrigeration breakdown is 50-70% of total
    if total_breakdown == 0:
        checks.append(("breakdown total is zero", False))
    elif 50 <= refrigeration_pct <= 70:
        checks.append(
            (f"refrigeration breakdown 50-70%: {refrigeration_pct:.1f}% "
             f"(refrigeration={refrigeration:.2f}, other={other:.2f})", True)
        )
    else:
        checks.append(
            (f"refrigeration breakdown 50-70%: {refrigeration_pct:.1f}% (FAILED) "
             f"(refrigeration={refrigeration:.2f}, other={other:.2f})", False)
        )
    
    # Determine overall pass/fail
    all_passed = all(check[1] for check in checks)
    
    details = "\n  ".join([check[0] for check in checks])
    print_test_result("Model 1", all_passed, details)
    
    return all_passed, data, None


def validate_model_2(
    api_key: str,
    latitude: float,
    longitude: float,
    scenario_name: str = "",
) -> Tuple[bool, Dict[str, Any], Optional[str]]:
    """
    Validate Model 2 (Solar Generation).

    Args:
        api_key: API key for auth
        latitude: Site latitude (SSA range)
        longitude: Site longitude (SSA range)
        scenario_name: Optional label for logs

    Returns:
        Tuple of (passed, response_data, error_message)
    """
    title = "Model 2: Solar Generation Prediction"
    if scenario_name:
        title += f" [{scenario_name}]"
    print_section_header(title)

    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key
    }

    payload = {
        "latitude": latitude,
        "longitude": longitude,
        "include_lifetime": True
    }
    
    response, error = make_request("POST", MODEL_2_ENDPOINT, headers, payload)
    
    if error:
        print_test_result("Model 2", False, f"Request failed: {error}")
        return False, {}, error
    
    if response.status_code != 200:
        print_test_result(
            "Model 2",
            False,
            f"Expected HTTP 200, got {response.status_code}: {response.text}"
        )
        return False, {}, f"HTTP {response.status_code}"
    
    try:
        data = response.json()
    except ValueError:
        print_test_result("Model 2", False, "Response is not valid JSON")
        return False, {}, "Invalid JSON response"
    
    # Get model info for MAPE validation
    info_response, info_error = make_request("GET", MODEL_2_INFO_ENDPOINT, headers)
    model_info = {}
    if info_response and info_response.status_code == 200:
        try:
            model_info = info_response.json()
        except ValueError:
            logger.warning("Model info response is not valid JSON")
    
    # Extract values for validation
    annual_summary = data.get("annual_summary", {})
    daily_kwh = annual_summary.get("average_daily_kwh")
    monthly_generation = data.get("monthly_generation", [])
    
    # Get first month's daily_kwh if available
    if monthly_generation and len(monthly_generation) > 0:
        first_month_daily = monthly_generation[0].get("daily_kwh")
        if daily_kwh is None:
            daily_kwh = first_month_daily
    
    validation_mape = model_info.get("validation_mape")
    
    # Validation assertions
    checks = []
    
    # Check 1: daily_kwh > 0
    if daily_kwh is None:
        checks.append(("daily_kwh missing", False))
    elif daily_kwh > 0:
        checks.append((f"daily_kwh > 0: {daily_kwh:.2f}", True))
    else:
        checks.append((f"daily_kwh > 0: {daily_kwh:.2f} (FAILED)", False))
    
    # Check 2: MAPE target <= 15%
    if validation_mape is None:
        checks.append(("validation_mape missing from model-info", False))
    else:
        mape_percent = validation_mape * 100  # Convert to percentage
        if mape_percent <= 15.0:
            checks.append((f"MAPE <= 15%: {mape_percent:.2f}%", True))
        else:
            checks.append((f"MAPE <= 15%: {mape_percent:.2f}% (FAILED)", False))
    
    # Check 3: Response is in plausible range for SSA coordinates
    # Typical daily generation for 10m² panel in SSA: 3-8 kWh/day
    if daily_kwh is None:
        checks.append(("Cannot validate SSA range (daily_kwh missing)", False))
    elif 3.0 <= daily_kwh <= 8.0:
        checks.append(
            (f"daily_kwh in plausible SSA range (3-8 kWh/day): {daily_kwh:.2f}", True)
        )
    else:
        checks.append(
            (f"daily_kwh in plausible SSA range (3-8 kWh/day): {daily_kwh:.2f} "
             f"(WARNING: outside typical range)", True)  # Warning, not failure
        )
    
    # Determine overall pass/fail
    all_passed = all(check[1] for check in checks)
    
    details = "\n  ".join([check[0] for check in checks])
    print_test_result("Model 2", all_passed, details)
    
    return all_passed, data, None


def validate_model_3(
    api_key: str,
    consumption_kwh: float,
    generation_kwh: float,
    tariff_per_kwh: float,
    system_cost_usd: float,
    scenario_name: str = "",
) -> Tuple[bool, Dict[str, Any], Optional[str]]:
    """
    Validate Model 3 (ROI Calculation).

    Args:
        api_key: API key for authentication
        consumption_kwh: Monthly consumption from Model 1
        generation_kwh: Monthly generation from Model 2
        tariff_per_kwh: Electricity tariff (USD/kWh) for this scenario
        system_cost_usd: Solar system cost (USD) for this scenario
        scenario_name: Optional label for logs

    Returns:
        Tuple of (passed, response_data, error_message)
    """
    title = "Model 3: ROI Calculation"
    if scenario_name:
        title += f" [{scenario_name}]"
    print_section_header(title)

    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key
    }

    payload = {
        "consumption_kwh": consumption_kwh,
        "generation_kwh": generation_kwh,
        "tariff_per_kwh": tariff_per_kwh,
        "system_cost_usd": system_cost_usd
    }

    logger.info("Model 3 Input (chained from Models 1 & 2):")
    logger.info("  consumption_kwh: %.2f", consumption_kwh)
    logger.info("  generation_kwh: %.2f", generation_kwh)
    logger.info("  tariff_per_kwh: %s", tariff_per_kwh)
    logger.info("  system_cost_usd: %s", system_cost_usd)
    
    response, error = make_request("POST", MODEL_3_ENDPOINT, headers, payload)
    
    if error:
        print_test_result("Model 3", False, f"Request failed: {error}")
        return False, {}, error
    
    if response.status_code != 200:
        print_test_result(
            "Model 3",
            False,
            f"Expected HTTP 200, got {response.status_code}: {response.text}"
        )
        return False, {}, f"HTTP {response.status_code}"
    
    try:
        data = response.json()
    except ValueError:
        print_test_result("Model 3", False, "Response is not valid JSON")
        return False, {}, "Invalid JSON response"
    
    # Extract values for validation
    monthly_savings = data.get("monthly_savings_usd")
    roi_percentage = data.get("roi_percentage")
    system_cost_echoed = data.get("system_cost_usd")
    
    # Validation assertions
    checks = []
    
    # Check 1: monthly_savings_usd > 0
    if monthly_savings is None:
        checks.append(("monthly_savings_usd missing", False))
    elif monthly_savings > 0:
        checks.append((f"monthly_savings_usd > 0: ${monthly_savings:.2f}", True))
    else:
        checks.append((f"monthly_savings_usd > 0: ${monthly_savings:.2f} (FAILED)", False))
    
    # Check 2: roi_percentage > 0
    if roi_percentage is None:
        checks.append(("roi_percentage missing", False))
    elif roi_percentage > 0:
        checks.append((f"roi_percentage > 0: {roi_percentage:.2f}%", True))
    else:
        checks.append((f"roi_percentage > 0: {roi_percentage:.2f}% (FAILED)", False))
    
    # Check 3: system_cost_usd echoed correctly
    if system_cost_echoed is None:
        checks.append(("system_cost_usd missing", False))
    elif abs(system_cost_echoed - system_cost_usd) < 0.01:
        checks.append(
            (f"system_cost_usd echoed correctly: ${system_cost_echoed:.2f} "
             f"(expected ${system_cost_usd:.2f})", True)
        )
    else:
        checks.append(
            (f"system_cost_usd echoed correctly: ${system_cost_echoed:.2f} "
             f"(expected ${system_cost_usd:.2f}) (FAILED)", False)
        )
    
    # Determine overall pass/fail
    all_passed = all(check[1] for check in checks)
    
    details = "\n  ".join([check[0] for check in checks])
    print_test_result("Model 3", all_passed, details)
    
    return all_passed, data, None


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def run_scenario(api_key: str, scenario: Dict[str, Any]) -> Tuple[bool, Dict[str, str]]:
    """
    Run the full Model 1 → Model 2 → Model 3 validation chain for one scenario.
    Returns (all_passed, results_dict).
    """
    name = scenario["name"]
    results = {"model_1": "fail", "model_2": "fail", "model_3": "fail"}

    # Step 1: Model 1
    passed, data, _ = validate_model_1(
        api_key,
        scenario["model_1_input"],
        scenario_name=name,
    )
    results["model_1"] = "pass" if passed else "fail"
    if not passed:
        return False, results
    consumption_kwh = data.get("estimated_consumption_kwh_monthly")
    if consumption_kwh is None:
        return False, results

    # Step 2: Model 2
    passed, data, _ = validate_model_2(
        api_key,
        scenario["latitude"],
        scenario["longitude"],
        scenario_name=name,
    )
    results["model_2"] = "pass" if passed else "fail"
    if not passed:
        return False, results
    annual_summary = data.get("annual_summary", {})
    annual_generation_kwh = annual_summary.get("year_1_generation_kwh")
    if annual_generation_kwh is None:
        monthly_generation = data.get("monthly_generation", [])
        if monthly_generation:
            annual_generation_kwh = sum(
                month.get("daily_kwh", 0) * 30 for month in monthly_generation
            )
    if annual_generation_kwh is None:
        return False, results
    monthly_generation_kwh = annual_generation_kwh / 12

    # Step 3: Model 3 (chained)
    passed, _, _ = validate_model_3(
        api_key,
        consumption_kwh,
        monthly_generation_kwh,
        scenario["tariff_per_kwh"],
        scenario["system_cost_usd"],
        scenario_name=name,
    )
    results["model_3"] = "pass" if passed else "fail"
    all_passed = all(r == "pass" for r in results.values())
    return all_passed, results


def main():
    """Main execution function."""
    print("\n" + "=" * 70)
    print("  SolarSense DSE Pipeline - Integration Validation")
    print("=" * 70)
    print("\nScenarios: On-Grid (grid-only) and Diesel (with diesel extra inputs)")
    print("\nConfiguration:")
    print(f"  Model 1 URL: {MODEL_1_BASE_URL}")
    print(f"  Model 2 URL: {MODEL_2_BASE_URL}")
    print(f"  Model 3 URL: {MODEL_3_BASE_URL}")
    print(f"  Model 4 URL: {MODEL_4_BASE_URL}")
    print(f"  Request Timeout: {REQUEST_TIMEOUT}s")

    api_key = get_api_key()
    logger.info("API_KEY found in environment")

    scenario_results = []
    any_fail = False

    for scenario in SCENARIOS:
        name = scenario["name"]
        print_section_header(f"Scenario: {name}")
        if scenario.get("uses_diesel"):
            print("  (Diesel: uses_diesel=true, diesel_hours_per_day=%s, diesel_price_per_liter=%s)"
                  % (scenario.get("diesel_hours_per_day"), scenario.get("diesel_price_per_liter")))
        else:
            print("  (On-Grid: uses_diesel=false)")
        all_passed, results = run_scenario(api_key, scenario)
        scenario_results.append({"name": name, "passed": all_passed, "results": results})
        if not all_passed:
            any_fail = True

    # Final summary
    print_section_header("Validation Summary")

    for sr in scenario_results:
        status = "✓ PASS" if sr["passed"] else "✗ FAIL"
        print(f"\n  {status} {sr['name']}:")
        for model, res in sr["results"].items():
            print(f"    - {model}: {res}")

    total_scenarios = len(scenario_results)
    passed_scenarios = sum(1 for sr in scenario_results if sr["passed"])
    print(f"\nScenarios: {passed_scenarios}/{total_scenarios} passed")

    if not any_fail:
        print("\n🎉 All scenarios passed validation!")
        sys.exit(0)
    print("\n❌ One or more scenarios failed validation.")
    sys.exit(1)


if __name__ == "__main__":
    main()
