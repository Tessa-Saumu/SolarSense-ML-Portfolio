"""
MODEL 4 COMPREHENSIVE TEST SUITE
Tests all functionality of the AI Recommendation Engine

Run with: python test.py
"""

import requests
import json
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = os.getenv('BASE_URL')
API_KEY = os.getenv('API_KEY')

# Test results tracking
test_results = []

def print_header(title):
    """Print a formatted test section header"""
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70)

def print_test(test_name, passed, message=""):
    """Print test result and track it"""
    status = " PASS" if passed else " FAIL"
    print(f"{status}: {test_name}")
    if message:
        print(f"     {message}")
    
    test_results.append({
        'test': test_name,
        'passed': passed,
        'message': message
    })

# ============================================
# TEST 1: HEALTH CHECK (No Auth)
# ============================================

def test_health_check():
    print_header("TEST 1: Health Check Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_test(
                "Health endpoint accessible",
                True,
                f"Status: {data.get('status')}, Service: {data.get('service')}"
            )
            return True
        else:
            print_test(
                "Health endpoint accessible",
                False,
                f"Got status code: {response.status_code}"
            )
            return False
            
    except Exception as e:
        print_test("Health endpoint accessible", False, str(e))
        return False

# ============================================
# TEST 2: ROOT ENDPOINT (No Auth)
# ============================================

def test_root_endpoint():
    print_header("TEST 2: Root Endpoint (API Info)")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            has_required_fields = all(key in data for key in ['service', 'version', 'endpoints'])
            
            print_test(
                "Root endpoint returns API info",
                has_required_fields,
                f"Service: {data.get('service')}, Version: {data.get('version')}"
            )
            return has_required_fields
        else:
            print_test("Root endpoint returns API info", False, f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_test("Root endpoint returns API info", False, str(e))
        return False

# ============================================
# TEST 3: AUTHENTICATION (Security)
# ============================================

def test_authentication():
    print_header("TEST 3: API Key Authentication")
    
    test_data = {
        "business_name": "Test Cafe",
        "business_type": "Cafe",
        "location": "Nairobi, Kenya",
        "latitude": -1.2921,
        "longitude": 36.8219,
        "equipment_list": [
            {"equipment_type": "refrigerator", "quantity": 2, "hours_per_day": 24}
        ]
    }
    
    # Test 3a: No API Key (should fail)
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/analyze",
            json=test_data,
            timeout=10
        )
        
        print_test(
            "Reject request without API key",
            response.status_code == 401,
            f"Status: {response.status_code}"
        )
        
    except Exception as e:
        print_test("Reject request without API key", False, str(e))
    
    # Test 3b: Wrong API Key (should fail)
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/analyze",
            headers={"X-API-KEY": "wrong_key_12345"},
            json=test_data,
            timeout=10
        )
        
        print_test(
            "Reject request with wrong API key",
            response.status_code == 401,
            f"Status: {response.status_code}"
        )
        
    except Exception as e:
        print_test("Reject request with wrong API key", False, str(e))

# ============================================
# TEST 4: INPUT VALIDATION
# ============================================

def test_input_validation():
    print_header("TEST 4: Input Validation")
    
    headers = {"X-API-KEY": API_KEY, "Content-Type": "application/json"}
    
    # Test 4a: Missing required fields
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/analyze",
            headers=headers,
            json={"business_name": "Test"},
            timeout=10
        )
        
        print_test(
            "Reject missing required fields",
            response.status_code == 400,
            f"Status: {response.status_code}"
        )
        
    except Exception as e:
        print_test("Reject missing required fields", False, str(e))
    
    # Test 4b: Invalid latitude
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/analyze",
            headers=headers,
            json={
                "business_name": "Test",
                "business_type": "Cafe",
                "location": "Test",
                "latitude": 999,  # Invalid
                "longitude": 0,
                "equipment_list": []
            },
            timeout=10
        )
        
        print_test(
            "Reject invalid latitude (>90)",
            response.status_code == 400,
            f"Status: {response.status_code}"
        )
        
    except Exception as e:
        print_test("Reject invalid latitude", False, str(e))
    
    # Test 4c: Too many equipment items
    try:
        large_equipment_list = [
            {"equipment_type": "light", "quantity": 1, "hours_per_day": 10}
            for _ in range(600)  # Exceeds limit
        ]
        
        response = requests.post(
            f"{BASE_URL}/api/v1/analyze",
            headers=headers,
            json={
                "business_name": "Test",
                "business_type": "Cafe",
                "location": "Test",
                "latitude": -1.29,
                "longitude": 36.82,
                "equipment_list": large_equipment_list
            },
            timeout=10
        )
        
        print_test(
            "Reject too many equipment items (>500)",
            response.status_code == 400,
            f"Status: {response.status_code}"
        )
        
    except Exception as e:
        print_test("Reject too many equipment items", False, str(e))
    
    # Test 4d: Invalid hours_per_day
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/analyze",
            headers=headers,
            json={
                "business_name": "Test",
                "business_type": "Cafe",
                "location": "Test",
                "latitude": -1.29,
                "longitude": 36.82,
                "equipment_list": [
                    {"equipment_type": "light", "quantity": 5, "hours_per_day": 30}  # >24
                ]
            },
            timeout=10
        )
        
        print_test(
            "Reject invalid hours_per_day (>24)",
            response.status_code == 400,
            f"Status: {response.status_code}"
        )
        
    except Exception as e:
        print_test("Reject invalid hours_per_day", False, str(e))

# ============================================
# TEST 5: VALID ANALYSIS REQUEST
# ============================================

def test_valid_analysis():
    print_header("TEST 5: Valid Analysis Request")
    
    headers = {"X-API-KEY": API_KEY, "Content-Type": "application/json"}
    
    test_data = {
        "business_name": "Joe's Coffee Shop",
        "business_type": "Cafe",
        "location": "Nairobi, Kenya",
        "latitude": -1.2921,
        "longitude": 36.8219,
        "equipment_list": [
            {"equipment_type": "refrigerator", "quantity": 2, "hours_per_day": 24},
            {"equipment_type": "espresso_machine", "quantity": 1, "hours_per_day": 10},
            {"equipment_type": "lights", "quantity": 15, "hours_per_day": 12},
            {"equipment_type": "air_conditioner", "quantity": 2, "hours_per_day": 8}
        ],
        "tariff": 0.15
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/analyze",
            headers=headers,
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required output fields
            required_fields = [
                'business_name', 'recommendation', 'viability_score',
                'status', 'explanation', 'estimated_consumption_kwh',
                'predicted_generation_kwh', 'roi_percentage'
            ]
            
            all_fields_present = all(field in data for field in required_fields)
            
            print_test(
                "Valid request returns 200 OK",
                True,
                f"Business: {data.get('business_name')}"
            )
            
            print_test(
                "Response has all required fields",
                all_fields_present,
                f"Fields present: {len([f for f in required_fields if f in data])}/{len(required_fields)}"
            )
            
            # Check recommendation values
            rec = data.get('recommendation')
            valid_recommendation = rec in ['High', 'Medium', 'Low']
            
            print_test(
                "Recommendation is valid (High/Medium/Low)",
                valid_recommendation,
                f"Got: {rec}"
            )
            
            # Check viability score range
            score = data.get('viability_score', -1)
            valid_score = 0 <= score <= 100
            
            print_test(
                "Viability score in valid range (0-100)",
                valid_score,
                f"Score: {score}"
            )
            
            # Check positive energy values
            consumption = data.get('estimated_consumption_kwh', -1)
            generation = data.get('predicted_generation_kwh', -1)
            
            print_test(
                "Energy values are positive",
                consumption >= 0 and generation >= 0,
                f"Consumption: {consumption} kWh, Generation: {generation} kWh"
            )
            
            # Print full result
            print("\n FULL ANALYSIS RESULT:")
            print(f"   Business: {data.get('business_name')}")
            print(f"   Recommendation: {data.get('recommendation')}")
            print(f"   Viability Score: {data.get('viability_score')}/100")
            print(f"   Status: {data.get('status')}")
            print(f"   Consumption: {data.get('estimated_consumption_kwh')} kWh")
            print(f"   Generation: {data.get('predicted_generation_kwh')} kWh")
            print(f"   ROI: {data.get('roi_percentage')}%")
            print(f"   Monthly Savings: ${data.get('monthly_savings')}")
            print(f"   Explanation: {data.get('explanation')}")
            
            return True
            
        elif response.status_code == 503:
            print_test(
                "Valid request processes",
                False,
                "Models 1-3 unavailable (503). This is OK if models are down."
            )
            return False
        else:
            print_test(
                "Valid request processes",
                False,
                f"Got unexpected status: {response.status_code}"
            )
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_test("Valid request processes", False, str(e))
        return False

# ============================================
# TEST 6: MODELS STATUS CHECK
# ============================================

def test_models_status():
    print_header("TEST 6: Models Status Endpoint")
    
    headers = {"X-API-KEY": API_KEY}
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/models/status",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print_test(
                "Models status endpoint accessible",
                True,
                f"Model 4: {data.get('model_4')}, Integrated: {data.get('integrated_models', {}).get('status')}"
            )
            
            print("\n📡 MODELS STATUS:")
            print(f"   Model 4: {data.get('model_4')}")
            print(f"   Integrated Models: {data.get('integrated_models', {}).get('status')}")
            print(f"   Base URL: {data.get('integrated_models', {}).get('base_url')}")
            
            return True
        else:
            print_test(
                "Models status endpoint accessible",
                False,
                f"Status: {response.status_code}"
            )
            return False
            
    except Exception as e:
        print_test("Models status endpoint accessible", False, str(e))
        return False

# ============================================
# TEST 7: ERROR HANDLING
# ============================================

def test_error_handling():
    print_header("TEST 7: Error Handling")
    
    headers = {"X-API-KEY": API_KEY, "Content-Type": "application/json"}
    
    # Test 7a: Invalid JSON
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/analyze",
            headers=headers,
            data="not valid json",
            timeout=10
        )
        
        print_test(
            "Handle invalid JSON gracefully",
            response.status_code in [400, 500],
            f"Status: {response.status_code}"
        )
        
    except Exception as e:
        print_test("Handle invalid JSON gracefully", False, str(e))
    
    # Test 7b: 404 for non-existent endpoint
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/nonexistent",
            headers=headers,
            timeout=10
        )
        
        print_test(
            "Return 404 for non-existent endpoint",
            response.status_code == 404,
            f"Status: {response.status_code}"
        )
        
    except Exception as e:
        print_test("Return 404 for non-existent endpoint", False, str(e))

# ============================================
# RUN ALL TESTS
# ============================================

def run_all_tests():
    print("\n" + "="*70)
    print(" MODEL 4: AI RECOMMENDATION ENGINE - TEST SUITE")
    print(" Solar Viability Assessment System")
    print(f" Testing against: {BASE_URL}")
    print(f" Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Run all test suites
    test_health_check()
    test_root_endpoint()
    test_authentication()
    test_input_validation()
    test_valid_analysis()
    test_models_status()
    test_error_handling()
    
    # Print summary
    print_header("TEST SUMMARY")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for t in test_results if t['passed'])
    failed_tests = total_tests - passed_tests
    
    print(f"\n   Total Tests:  {total_tests}")
    print(f"    Passed:    {passed_tests}")
    print(f"    Failed:    {failed_tests}")
    print(f"   Success Rate: {(passed_tests/total_tests*100):.1f}%")
    
    if failed_tests > 0:
        print("\n   Failed Tests:")
        for test in test_results:
            if not test['passed']:
                print(f"   • {test['test']}")
                if test['message']:
                    print(f"     {test['message']}")
    
    print("\n" + "="*70)
    
    if passed_tests == total_tests:
        print("  ALL TESTS PASSED! Model 4 is working correctly!")
    elif passed_tests / total_tests >= 0.8:
        print("   MOST TESTS PASSED - Some issues to fix")
    else:
        print("  MANY TESTS FAILED - Check configuration and fix issues")
    
    print("="*70 + "\n")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
