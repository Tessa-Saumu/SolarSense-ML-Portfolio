"""
COMPREHENSIVE TEST SUITE FOR MODEL 4 ORCHESTRATION API
Tests against 10 realistic African SME solar viability profiles

Requirements:
- Validates Model 4 outputs against realistic expected values
- Converts all currencies to/from USD correctly
- Generates detailed comparison reports
- Logs all API interactions
- Identifies weak points and bugs

Owner: Bella
Date: February 2026
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Tuple
from dotenv import load_dotenv
import logging

# Load environment
load_dotenv()

# Configure logging
log_file = 'test_results/api_logs.txt'
os.makedirs('test_results', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================
# CONFIGURATION
# ============================================

MODEL_4_BASE_URL = os.getenv("MODEL_4_BASE_URL", "http://localhost:8000")
MODEL_4_ENDPOINT = f"{MODEL_4_BASE_URL}/api/v1/analyze"
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise ValueError("API_KEY not found in environment variables!")

# Exchange rates (matching corrected profiles)
USD_EXCHANGE_RATES = {
    "Nigeria": 1550,    # ₦1550 = $1
    "Ghana": 12.5,      # GHS 12.5 = $1
    "Kenya": 140,       # KES 140 = $1
    "South Africa": 18.5,  # R 18.5 = $1
    "Ethiopia": 56,     # ETB 56 = $1
    "Uganda": 3700,     # UGX 3700 = $1
    "Rwanda": 1300,     # RWF 1300 = $1
    "Tanzania": 2350,   # TZS 2350 = $1
}

# City coordinates (city centers)
CITY_COORDINATES = {
    "Lagos, Nigeria": (6.5244, 3.3792),
    "Accra, Ghana": (5.6037, -0.1870),
    "Nairobi, Kenya": (-1.2921, 36.8219),
    "Johannesburg, South Africa": (-26.2041, 28.0473),
    "Addis Ababa, Ethiopia": (9.0320, 38.7469),
    "Kampala, Uganda": (0.3476, 32.5825),
    "Kigali, Rwanda": (-1.9536, 30.0606),
    "Dar es Salaam, Tanzania": (-6.7924, 39.2083),
    "Cape Town, South Africa": (-33.9249, 18.4241),
    "Mombasa, Kenya": (-4.0435, 39.6682)
}

# Profile name to city mapping
PROFILE_TO_CITY = {
    "Lagos Fresh Cuts Butchery": "Lagos, Nigeria",
    "Accra Daily Grocery": "Accra, Ghana",
    "Nairobi Bread Haven Bakery": "Nairobi, Kenya",
    "Johannesburg ChillMart Supermarket": "Johannesburg, South Africa",
    "Addis Ice Foods Frozen Retail": "Addis Ababa, Ethiopia",
    "Kampala Farm Cold Storage": "Kampala, Uganda",
    "Kigali Quick Freeze Butchery": "Kigali, Rwanda",
    "Dar Fresh Mart Grocery": "Dar es Salaam, Tanzania",
    "Cape Meat Locker Cold Storage": "Cape Town, South Africa",
    "Nairobi Frosty Mini Mart": "Nairobi, Kenya"
}

# Tolerance thresholds
TOLERANCE = {
    'consumption_kwh': 0.15,      # ±15%
    'system_cost': 0.20,          # ±20%
    'roi_percentage': 0.20,       # ±20%
    'monthly_savings': 0.20,      # ±20%
    'payback_years': 0.25         # ±25%
}

# ============================================
# HELPER FUNCTIONS
# ============================================

def parse_equipment_from_profile(equipment_str: str) -> List[Dict]:
    """
    Parse equipment string like:
    "4 freezers (24h), 2 refrigerators (24h), 20 lighting (12h)"
    
    Returns list of equipment dicts for API
    """
    equipment_list = []
    
    # Split by commas
    items = equipment_str.split(',')
    
    for item in items:
        item = item.strip()
        
        # Extract quantity, type, and hours
        # Pattern: "4 freezers (24h)" or "1 cold room (24h)"
        parts = item.split('(')
        if len(parts) != 2:
            continue
            
        # Get quantity and equipment type
        qty_and_type = parts[0].strip().split(' ', 1)
        if len(qty_and_type) != 2:
            continue
            
        try:
            quantity = int(qty_and_type[0])
        except ValueError:
            continue
            
        equipment_type = qty_and_type[1].strip().rstrip('s')  # Remove plural 's'
        
        # Get hours
        hours_str = parts[1].strip().rstrip('h)')
        try:
            hours_per_day = float(hours_str)
        except ValueError:
            hours_per_day = 12  # Default
        
        # Normalize equipment type names
        type_mapping = {
            'freezer': 'freezer',
            'refrigerator': 'refrigerator',
            'lighting': 'lights',
            'light': 'lights',
            'cold room': 'cold_room',
            'display cooler': 'display_cooler',
            'ice machine': 'ice_maker',
        }
        
        normalized_type = type_mapping.get(equipment_type.lower(), equipment_type.lower())
        
        equipment_list.append({
            'equipment_type': normalized_type,
            'quantity': quantity,
            'hours_per_day': hours_per_day
        })
    
    return equipment_list


def extract_location_name(profile_name: str) -> str:
    """
    Extract standardized location from profile name
    """
    # Direct mapping from profile name
    if profile_name in PROFILE_TO_CITY:
        return PROFILE_TO_CITY[profile_name]
    
    # Fallback: try to match by city name in profile
    for profile_key, city_key in PROFILE_TO_CITY.items():
        if any(word in profile_name for word in profile_key.split()):
            return city_key
    
    raise ValueError(f"Could not resolve location for profile: {profile_name}")


def parse_energy_scenario(scenario_str: str, profile_data: Dict) -> Dict:
    """
    Parse energy scenario string to extract diesel parameters
    Returns dict with uses_diesel, diesel_hours_per_day, diesel_price_per_liter
    """
    if "diesel" not in scenario_str.lower():
        return {
            'uses_diesel': False,
            'diesel_hours_per_day': 0,
            'diesel_price_per_liter': 0
        }
    
    # Extract hours per day
    # Pattern: "8h/day" or "8 h/day"
    import re
    hours_match = re.search(r'(\d+)\s*h/day', scenario_str)
    diesel_hours = float(hours_match.group(1)) if hours_match else 12
    
    # Extract price per liter
    # Pattern: "₦1,400/L" or "KES 210/L"
    price_match = re.search(r'[\₦\w]+\s*([\d,]+)/l', scenario_str, re.IGNORECASE)
    
    if price_match:
        price_local = float(price_match.group(1).replace(',', ''))
        country = profile_data.get('country')
        
        # Convert to USD
        exchange_rate = USD_EXCHANGE_RATES.get(country, 1)
        diesel_price_usd = price_local / exchange_rate
    else:
        diesel_price_usd = 1.20  # Default
    
    return {
        'uses_diesel': True,
        'diesel_hours_per_day': diesel_hours,
        'diesel_price_per_liter': diesel_price_usd
    }


def convert_to_usd(amount: float, country: str) -> float:
    """Convert local currency to USD"""
    rate = USD_EXCHANGE_RATES.get(country, 1)
    return amount / rate


def convert_from_usd(amount_usd: float, country: str) -> float:
    """Convert USD to local currency"""
    rate = USD_EXCHANGE_RATES.get(country, 1)
    return amount_usd * rate


def calculate_deviation(actual, expected) -> float:
    """Calculate percentage deviation"""
    if expected == 0:
        return 0 if actual == 0 else 100
    return ((actual - expected) / expected) * 100


def assess_severity(deviation_pct: float, tolerance: float) -> str:
    """Assess deviation severity"""
    abs_dev = abs(deviation_pct)
    if abs_dev <= tolerance * 100:
        return "PASS"
    elif abs_dev <= tolerance * 150:
        return "MEDIUM"
    else:
        return "HIGH"


# ============================================
# API INTERACTION
# ============================================

def call_model4_api(request_payload: Dict) -> Tuple[Dict, int, str]:
    """
    Call Model 4 API and return response
    Returns: (response_json, status_code, error_message)
    """
    headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': API_KEY
    }
    
    try:
        logger.info(f"\n{'='*80}")
        logger.info(f"📤 REQUEST TO MODEL 4 API")
        logger.info(f"{'='*80}")
        logger.info(f"Endpoint: {MODEL_4_ENDPOINT}")
        logger.info(f"Payload:\n{json.dumps(request_payload, indent=2)}")
        
        response = requests.post(
            MODEL_4_ENDPOINT,
            json=request_payload,
            headers=headers,
            timeout=30
        )
        
        logger.info(f"\n📥 RESPONSE FROM MODEL 4 API")
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response:\n{json.dumps(response.json(), indent=2)}")
        
        return response.json(), response.status_code, None
        
    except requests.exceptions.RequestException as e:
        error_msg = f"API Request Failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {}, 0, error_msg


# ============================================
# TEST EXECUTION
# ============================================

def run_single_test(profile: Dict) -> Dict:
    """
    Run test for a single profile
    Returns detailed comparison results
    """
    logger.info(f"\n\n{'#'*100}")
    logger.info(f"🧪 TESTING PROFILE: {profile['name']}")
    logger.info(f"{'#'*100}")
    
    # Extract profile data
    country = profile['country']
    outputs = profile['outputs']
    
    # Build API request
    location_key = extract_location_name(profile['name'])
    latitude, longitude = CITY_COORDINATES[location_key]
    
    equipment_list = parse_equipment_from_profile(profile['equipment'])
    diesel_params = parse_energy_scenario(profile['energy_scenario'], profile)
    
    request_payload = {
        'business_name': profile['name'],
        'business_type': profile['business_type'],
        'location': location_key,
        'latitude': latitude,
        'longitude': longitude,
        'equipment_list': equipment_list,
        **diesel_params  # Unpack diesel parameters
    }
    
    # Call API
    response, status_code, error = call_model4_api(request_payload)
    
    if error or status_code != 200:
        return {
            'profile_name': profile['name'],
            'status': 'FAILED',
            'error': error or response.get('error', 'Unknown error'),
            'status_code': status_code
        }
    
    # Compare results
    expected = {
        'consumption_kwh': outputs['2_monthly_usage_kwh'],
        'system_cost_local': outputs['5_system_cost'],
        'system_cost_usd': convert_to_usd(outputs['5_system_cost'], country),
        'payback_years': outputs['10_payback_years'],
        'annual_savings_local': outputs['9_annual_savings'],
        'monthly_savings_local': outputs['9_annual_savings'] / 12,
        'monthly_savings_usd': convert_to_usd(outputs['9_annual_savings'] / 12, country),
    }
    
    actual = {
        'consumption_kwh': response.get('estimated_consumption_kwh', 0),
        'system_cost_usd': response.get('system_cost', 0),
        'system_cost_local': convert_from_usd(response.get('system_cost', 0), country),
        'payback_years': (response.get('system_cost', 0) / 
                         (response.get('monthly_savings', 0) * 12)) if response.get('monthly_savings', 0) > 0 else 999,
        'monthly_savings_usd': response.get('monthly_savings', 0),
        'monthly_savings_local': convert_from_usd(response.get('monthly_savings', 0), country),
    }
    
    # Calculate deviations
    deviations = {
        'consumption_kwh': calculate_deviation(actual['consumption_kwh'], expected['consumption_kwh']),
        'system_cost': calculate_deviation(actual['system_cost_usd'], expected['system_cost_usd']),
        'monthly_savings': calculate_deviation(actual['monthly_savings_usd'], expected['monthly_savings_usd']),
        'payback_years': calculate_deviation(actual['payback_years'], expected['payback_years']),
    }
    
    # Assess severity
    assessment = {
        'consumption_kwh': assess_severity(deviations['consumption_kwh'], TOLERANCE['consumption_kwh']),
        'system_cost': assess_severity(deviations['system_cost'], TOLERANCE['system_cost']),
        'monthly_savings': assess_severity(deviations['monthly_savings'], TOLERANCE['monthly_savings']),
        'payback_years': assess_severity(deviations['payback_years'], TOLERANCE['payback_years']),
    }
    
    # Overall status
    severities = list(assessment.values())
    if all(s == "PASS" for s in severities):
        overall_status = "PASS"
    elif any(s == "HIGH" for s in severities):
        overall_status = "FAIL"
    else:
        overall_status = "WARNING"
    
    return {
        'profile_name': profile['name'],
        'country': country,
        'status': overall_status,
        'status_code': status_code,
        'request': request_payload,
        'expected': expected,
        'actual': actual,
        'deviations': deviations,
        'assessment': assessment,
        'api_response': response
    }


def run_all_tests() -> Dict:
    """
    Run all profile tests
    Returns aggregated results
    """
    # Load profiles
    with open('FINAL_SME_PROFILES.json', 'r', encoding="utf-8") as f:
        profiles = json.load(f)
    
    logger.info(f"\n{'='*100}")
    logger.info(f"🚀 STARTING COMPREHENSIVE TEST SUITE")
    logger.info(f"{'='*100}")
    logger.info(f"Total Profiles: {len(profiles)}")
    logger.info(f"API Endpoint: {MODEL_4_ENDPOINT}")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    
    results = []
    
    for i, profile in enumerate(profiles, 1):
        logger.info(f"\n>>> Test {i}/{len(profiles)}")
        result = run_single_test(profile)
        results.append(result)
    
    # Aggregate statistics
    passed = sum(1 for r in results if r['status'] == 'PASS')
    warnings = sum(1 for r in results if r['status'] == 'WARNING')
    failed = sum(1 for r in results if r['status'] == 'FAIL')
    errors = sum(1 for r in results if r['status'] == 'FAILED')
    
    summary = {
        'total_tests': len(results),
        'passed': passed,
        'warnings': warnings,
        'failed': failed,
        'errors': errors,
        'timestamp': datetime.now().isoformat(),
        'results': results
    }
    
    logger.info(f"\n{'='*100}")
    logger.info(f"📊 TEST SUITE COMPLETE")
    logger.info(f"{'='*100}")
    logger.info(f"Total: {len(results)} | Passed: {passed} | Warnings: {warnings} | Failed: {failed} | Errors: {errors}")
    
    return summary


# ============================================
# REPORT GENERATION
# ============================================

def generate_json_report(summary: Dict):
    """Generate detailed JSON report"""
    filename = 'test_results/detailed_results.json'
    with open(filename, 'w', encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    logger.info(f"✅ JSON report saved: {filename}")


def generate_markdown_summary(summary: Dict):
    """Generate executive summary in Markdown"""
    filename = 'test_results/summary.md'
    
    with open(filename, 'w', encoding="utf-8") as f:
        f.write("# MODEL 4 TEST SUITE - EXECUTIVE SUMMARY\n\n")
        f.write(f"**Test Date:** {summary['timestamp']}\n\n")
        f.write(f"**API Endpoint:** {MODEL_4_ENDPOINT}\n\n")
        
        f.write("## 📊 Overall Results\n\n")
        f.write(f"- **Total Tests:** {summary['total_tests']}\n")
        f.write(f"- **✅ Passed:** {summary['passed']}\n")
        f.write(f"- **⚠️  Warnings:** {summary['warnings']}\n")
        f.write(f"- **❌ Failed:** {summary['failed']}\n")
        f.write(f"- **🔥 Errors:** {summary['errors']}\n\n")
        
        # Pass rate
        pass_rate = (summary['passed'] / summary['total_tests'] * 100) if summary['total_tests'] > 0 else 0
        f.write(f"**Pass Rate:** {pass_rate:.1f}%\n\n")
        
        # Summary table
        f.write("## 📋 Test Results Summary\n\n")
        f.write("| Profile | Country | Status | Issues |\n")
        f.write("|---------|---------|--------|--------|\n")
        
        for result in summary['results']:
            if result['status'] == 'FAILED':
                issues = f"API Error: {result.get('error', 'Unknown')}"
            else:
                # Collect high severity issues
                high_issues = [k for k, v in result.get('assessment', {}).items() if v == 'HIGH']
                issues = ', '.join(high_issues) if high_issues else 'None'
            
            status_emoji = {
                'PASS': '✅',
                'WARNING': '⚠️',
                'FAIL': '❌',
                'FAILED': '🔥'
            }.get(result['status'], '❓')
            
            f.write(f"| {result['profile_name'][:30]} | {result.get('country', 'N/A')} | {status_emoji} {result['status']} | {issues} |\n")
        
        f.write("\n## 🎯 Tolerance Thresholds\n\n")
        f.write(f"- **Consumption:** ±{TOLERANCE['consumption_kwh']*100:.0f}%\n")
        f.write(f"- **System Cost:** ±{TOLERANCE['system_cost']*100:.0f}%\n")
        f.write(f"- **Monthly Savings:** ±{TOLERANCE['monthly_savings']*100:.0f}%\n")
        f.write(f"- **Payback Period:** ±{TOLERANCE['payback_years']*100:.0f}%\n\n")
        
        f.write("## 🔍 Key Findings\n\n")
        
        # Analyze common issues
        if summary['failed'] > 0 or summary['warnings'] > 0:
            f.write("### Issues Identified:\n\n")
            
            # Collect all high/medium severity issues
            issue_counts = {}
            for result in summary['results']:
                if result['status'] in ['FAIL', 'WARNING']:
                    for metric, severity in result.get('assessment', {}).items():
                        if severity in ['HIGH', 'MEDIUM']:
                            issue_counts[metric] = issue_counts.get(metric, 0) + 1
            
            for metric, count in sorted(issue_counts.items(), key=lambda x: -x[1]):
                f.write(f"- **{metric}**: {count} profiles affected\n")
        else:
            f.write("✅ All tests passed within tolerance thresholds!\n")
        
        f.write("\n---\n\n")
        f.write("*For detailed profile-by-profile comparison, see `detailed_comparison.md`*\n")
    
    logger.info(f"✅ Summary report saved: {filename}")


def generate_detailed_comparison(summary: Dict):
    """Generate detailed profile-by-profile comparison"""
    filename = 'test_results/detailed_comparison.md'
    
    with open(filename, 'w', encoding="utf-8") as f:
        f.write("# MODEL 4 TEST SUITE - DETAILED COMPARISON\n\n")
        f.write(f"**Test Date:** {summary['timestamp']}\n\n")
        
        for i, result in enumerate(summary['results'], 1):
            f.write(f"\n## {i}. {result['profile_name']}\n\n")
            
            if result['status'] == 'FAILED':
                f.write(f"**Status:** 🔥 API ERROR\n\n")
                f.write(f"**Error:** {result.get('error', 'Unknown')}\n")
                f.write(f"**Status Code:** {result.get('status_code', 'N/A')}\n\n")
                continue
            
            # Status
            status_emoji = {
                'PASS': '✅',
                'WARNING': '⚠️',
                'FAIL': '❌'
            }.get(result['status'], '❓')
            
            f.write(f"**Status:** {status_emoji} {result['status']}\n\n")
            f.write(f"**Country:** {result['country']}\n\n")
            
            # Input summary
            f.write("### 📥 Input\n\n")
            req = result['request']
            f.write(f"- **Business Type:** {req['business_type']}\n")
            f.write(f"- **Location:** {req['location']}\n")
            f.write(f"- **Coordinates:** ({req['latitude']}, {req['longitude']})\n")
            f.write(f"- **Uses Diesel:** {req.get('uses_diesel', False)}\n")
            if req.get('uses_diesel'):
                f.write(f"  - Hours/day: {req.get('diesel_hours_per_day', 0)}\n")
                f.write(f"  - Price/liter: ${req.get('diesel_price_per_liter', 0):.2f}\n")
            f.write(f"- **Equipment:** {len(req['equipment_list'])} items\n\n")
            
            # Comparison table
            f.write("### 📊 Comparison\n\n")
            f.write("| Metric | Expected | Actual | Deviation | Status |\n")
            f.write("|--------|----------|--------|-----------|--------|\n")
            
            exp = result['expected']
            act = result['actual']
            dev = result['deviations']
            assess = result['assessment']
            
            # Get currency symbol
            currency_symbols = {
                "Nigeria": "₦", "Ghana": "GHS", "Kenya": "KES", 
                "South Africa": "R", "Ethiopia": "ETB", "Uganda": "UGX",
                "Rwanda": "RWF", "Tanzania": "TZS"
            }
            symbol = currency_symbols.get(result['country'], "$")
            
            metrics = [
                ('Consumption (kWh/mo)', f"{exp['consumption_kwh']:.1f}", 
                 f"{act['consumption_kwh']:.1f}", 'consumption_kwh'),
                ('System Cost (USD)', f"${exp['system_cost_usd']:,.0f}", 
                 f"${act['system_cost_usd']:,.0f}", 'system_cost'),
                (f'System Cost ({symbol})', f"{symbol}{exp['system_cost_local']:,.0f}", 
                 f"{symbol}{act['system_cost_local']:,.0f}", 'system_cost'),
                ('Monthly Savings (USD)', f"${exp['monthly_savings_usd']:.2f}", 
                 f"${act['monthly_savings_usd']:.2f}", 'monthly_savings'),
                (f'Monthly Savings ({symbol})', f"{symbol}{exp['monthly_savings_local']:,.0f}", 
                 f"{symbol}{act['monthly_savings_local']:,.0f}", 'monthly_savings'),
                ('Payback (years)', f"{exp['payback_years']:.1f}", 
                 f"{act['payback_years']:.1f}", 'payback_years'),
            ]
            
            for label, exp_val, act_val, key in metrics:
                deviation = dev.get(key, 0)
                status = assess.get(key, 'PASS')
                status_symbol = {'PASS': '✅', 'MEDIUM': '⚠️', 'HIGH': '❌'}[status]
                f.write(f"| {label} | {exp_val} | {act_val} | {deviation:+.1f}% | {status_symbol} |\n")
            
            f.write("\n")
            
            # API response excerpt
            f.write("### 🔍 API Response (Key Fields)\n\n")
            api_resp = result['api_response']
            f.write(f"- **Viability Score:** {api_resp.get('viability_score', 'N/A')}\n")
            f.write(f"- **Recommendation:** {api_resp.get('recommendation', 'N/A')}\n")
            f.write(f"- **Status:** {api_resp.get('status', 'N/A')}\n")
            f.write(f"- **ROI %:** {api_resp.get('roi_percentage', 'N/A')}\n")
            f.write(f"- **Energy Scenario:** {api_resp.get('energy_scenario', 'N/A')}\n\n")
            
            f.write("---\n")
    
    logger.info(f"✅ Detailed comparison saved: {filename}")


# ============================================
# MAIN EXECUTION
# ============================================

def main():
    """Main test execution"""
    print("\n" + "="*100)
    print("🧪 MODEL 4 COMPREHENSIVE TEST SUITE")
    print("="*100)
    print(f"Testing against 10 realistic African SME profiles")
    print(f"API Endpoint: {MODEL_4_ENDPOINT}")
    print(f"Results will be saved to: test_results/")
    print("="*100 + "\n")
    
    try:
        # Run tests
        summary = run_all_tests()
        
        # Generate reports
        print("\n📝 Generating reports...")
        generate_json_report(summary)
        generate_markdown_summary(summary)
        generate_detailed_comparison(summary)
        
        print("\n✅ Test suite complete!")
        print(f"\nResults Summary:")
        print(f"  ✅ Passed: {summary['passed']}")
        print(f"  ⚠️  Warnings: {summary['warnings']}")
        print(f"  ❌ Failed: {summary['failed']}")
        print(f"  🔥 Errors: {summary['errors']}")
        print(f"\n📂 Reports saved to test_results/")
        
        # Exit code
        if summary['failed'] > 0 or summary['errors'] > 0:
            exit(1)
        else:
            exit(0)
            
    except Exception as e:
        logger.error(f"❌ Test suite failed: {str(e)}", exc_info=True)
        exit(1)


if __name__ == "__main__":
    main()