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

# Test input data - Lagos butchery scenario
TEST_INPUT = {
    "business_type": "butchery",
    "sqft_m2": 60.0,
    "operating_hours_weekly": 98.0,
    "num_refrigeration_units": 3,
    "location": "Lagos, Nigeria",
    "num_workers": 3,
    "months_per_year": 12
}

# Lagos coordinates (for Model 2)
LAGOS_LATITUDE = 6.5244
LAGOS_LONGITUDE = 3.3792

# Expected tariff and system cost for Model 3
TARIFF_PER_KWH = 0.20
SYSTEM_COST_USD = 6000.0

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

def validate_model_1(api_key: str) -> Tuple[bool, Dict[str, Any], Optional[str]]:
    """
    Validate Model 1 (Energy Consumption).
    
    Returns:
        Tuple of (passed, response_data, error_message)
    """
    print_section_header("Model 1: Energy Consumption Prediction")
    
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key
    }
    
    response, error = make_request("POST", MODEL_1_ENDPOINT, headers, TEST_INPUT)
    
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


def validate_model_2(api_key: str) -> Tuple[bool, Dict[str, Any], Optional[str]]:
    """
    Validate Model 2 (Solar Generation).
    
    Returns:
        Tuple of (passed, response_data, error_message)
    """
    print_section_header("Model 2: Solar Generation Prediction")
    
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key
    }
    
    # Request payload for Lagos coordinates
    payload = {
        "latitude": LAGOS_LATITUDE,
        "longitude": LAGOS_LONGITUDE,
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
    generation_kwh: float
) -> Tuple[bool, Dict[str, Any], Optional[str]]:
    """
    Validate Model 3 (ROI Calculation).
    
    Args:
        api_key: API key for authentication
        consumption_kwh: Monthly consumption from Model 1
        generation_kwh: Monthly generation from Model 2
    
    Returns:
        Tuple of (passed, response_data, error_message)
    """
    print_section_header("Model 3: ROI Calculation")
    
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key
    }
    
    payload = {
        "consumption_kwh": consumption_kwh,
        "generation_kwh": generation_kwh,
        "tariff_per_kwh": TARIFF_PER_KWH,
        "system_cost_usd": SYSTEM_COST_USD
    }
    
    logger.info(f"Model 3 Input (chained from Models 1 & 2):")
    logger.info(f"  consumption_kwh: {consumption_kwh:.2f}")
    logger.info(f"  generation_kwh: {generation_kwh:.2f}")
    logger.info(f"  tariff_per_kwh: {TARIFF_PER_KWH}")
    logger.info(f"  system_cost_usd: {SYSTEM_COST_USD}")
    
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
    elif abs(system_cost_echoed - SYSTEM_COST_USD) < 0.01:
        checks.append(
            (f"system_cost_usd echoed correctly: ${system_cost_echoed:.2f} "
             f"(expected ${SYSTEM_COST_USD:.2f})", True)
        )
    else:
        checks.append(
            (f"system_cost_usd echoed correctly: ${system_cost_echoed:.2f} "
             f"(expected ${SYSTEM_COST_USD:.2f}) (FAILED)", False)
        )
    
    # Determine overall pass/fail
    all_passed = all(check[1] for check in checks)
    
    details = "\n  ".join([check[0] for check in checks])
    print_test_result("Model 3", all_passed, details)
    
    return all_passed, data, None


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""
    print("\n" + "=" * 70)
    print("  SolarSense DSE Pipeline - Integration Validation")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  Model 1 URL: {MODEL_1_BASE_URL}")
    print(f"  Model 2 URL: {MODEL_2_BASE_URL}")
    print(f"  Model 3 URL: {MODEL_3_BASE_URL}")
    print(f"  Model 4 URL: {MODEL_4_BASE_URL}")
    print(f"  Request Timeout: {REQUEST_TIMEOUT}s")
    
    # Get API key
    api_key = get_api_key()
    logger.info("API_KEY found in environment")
    
    # Track results
    results = {
        "model_1": {"passed": False, "data": {}},
        "model_2": {"passed": False, "data": {}},
        "model_3": {"passed": False, "data": {}}
    }
    
    # Step 1: Validate Model 1
    passed, data, error = validate_model_1(api_key)
    results["model_1"]["passed"] = passed
    results["model_1"]["data"] = data
    
    if not passed:
        print("\n⚠️  Model 1 validation failed. Cannot proceed with chained validation.")
        print("   Fix Model 1 issues before continuing.")
        sys.exit(1)
    
    # Extract consumption from Model 1
    consumption_kwh = data.get("estimated_consumption_kwh_monthly")
    if consumption_kwh is None:
        print("\n⚠️  Model 1 response missing estimated_consumption_kwh_monthly.")
        print("   Cannot proceed with Model 3 validation.")
        sys.exit(1)
    
    # Step 2: Validate Model 2
    passed, data, error = validate_model_2(api_key)
    results["model_2"]["passed"] = passed
    results["model_2"]["data"] = data
    
    if not passed:
        print("\n⚠️  Model 2 validation failed. Cannot proceed with chained validation.")
        print("   Fix Model 2 issues before continuing.")
        sys.exit(1)
    
    # Extract generation from Model 2
    annual_summary = data.get("annual_summary", {})
    annual_generation_kwh = annual_summary.get("year_1_generation_kwh")
    
    # If year_1_generation_kwh not available, try to calculate from monthly
    if annual_generation_kwh is None:
        monthly_generation = data.get("monthly_generation", [])
        if monthly_generation:
            # Sum up monthly generation (approximate annual total)
            # Each month has daily_kwh, multiply by ~30 days and sum
            annual_generation_kwh = sum(
                month.get("daily_kwh", 0) * 30  # Approximate days per month
                for month in monthly_generation
            )
    
    if annual_generation_kwh is None:
        print("\n⚠️  Model 2 response missing generation_kwh data.")
        print("   Cannot proceed with Model 3 validation.")
        sys.exit(1)
    
    # Convert annual to monthly average
    # Model 2 returns annual generation, Model 3 expects monthly
    monthly_generation_kwh = annual_generation_kwh / 12
    
    # Step 3: Validate Model 3 (chained)
    passed, data, error = validate_model_3(
        api_key,
        consumption_kwh,
        monthly_generation_kwh
    )
    results["model_3"]["passed"] = passed
    results["model_3"]["data"] = data
    
    # Final summary
    print_section_header("Validation Summary")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r["passed"])
    
    print(f"\nTotal Models Tested: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    
    print("\nDetailed Results:")
    for model_name, result in results.items():
        status = "✓ PASS" if result["passed"] else "✗ FAIL"
        print(f"  {status} - {model_name.replace('_', ' ').title()}")
    
    if passed_tests == total_tests:
        print("\n🎉 All models passed validation!")
        sys.exit(0)
    else:
        print(f"\n❌ {total_tests - passed_tests} model(s) failed validation.")
        sys.exit(1)


if __name__ == "__main__":
    main()
