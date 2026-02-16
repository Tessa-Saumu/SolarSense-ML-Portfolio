# SolarSense Model 4 - MVP Diesel Replacement Test
# Tests grid-only vs diesel replacement scenarios

import requests
import json

BASE_URL = "http://127.0.0.1:5000"
API_KEY = "QfBmvo3htYQPSJWYYLcChxXvZonTuC2U"

print("=" * 80)
print("🚀 MODEL 4 MVP - DIESEL REPLACEMENT ECONOMICS TEST")
print("=" * 80)
print()

headers = {"X-API-KEY": API_KEY, "Content-Type": "application/json"}

# Test Case 1: Grid-Only (Current Scenario)
print("📋 TEST 1: Grid-Only Scenario (No Diesel)")
print("-" * 80)

test_grid_only = {
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
    "tariff": 0.15,
    "uses_diesel": False  # Grid only
}

try:
    response = requests.post(f"{BASE_URL}/api/v1/analyze", headers=headers, json=test_grid_only, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ SUCCESS - Grid Only Scenario")
        print(f"\n📊 Results:")
        print(f"   Consumption: {result.get('estimated_consumption_kwh', 0):.1f} kWh/month")
        print(f"   Solar System: {result.get('recommended_panel_area_m2', 0):.1f}m²")
        print(f"   Generation: {result.get('predicted_generation_kwh', 0):.1f} kWh/month")
        print(f"   System Cost: ${result.get('system_cost', 0):,.0f}")
        print(f"   Current Energy Cost: ${result.get('current_energy_cost', {}).get('total_monthly', 0):.2f}/month")
        print(f"   Monthly Savings: ${result.get('monthly_savings', 0):.2f}")
        print(f"   ROI: {result.get('roi_percentage', 0):.2f}%")
        print(f"   Scenario: {result.get('energy_scenario', 'unknown')}")
        print(f"   Recommendation: {result.get('recommendation', 'Unknown')}")
        print(f"   Viability Score: {result.get('viability_score', 0):.1f}/100")
    else:
        print(f"❌ ERROR: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ EXCEPTION: {e}")

print()
print("=" * 80)
print()

# Test Case 2: Diesel Replacement (12 hours/day)
print("📋 TEST 2: Diesel Replacement Scenario (12 hours/day)")
print("-" * 80)

test_diesel = {
    "business_name": "Joe's Butchery (with diesel)",
    "business_type": "Bakery",  # Maps to butchery in Model 1
    "location": "Lagos, Nigeria",
    "latitude": 5.5244,
    "longitude": 3.3792,
    "equipment_list": [
        {"equipment_type": "refrigerator", "quantity": 3, "hours_per_day": 24},
        {"equipment_type": "freezer", "quantity": 2, "hours_per_day": 24},
        {"equipment_type": "lights", "quantity": 10, "hours_per_day": 12}
    ],
    "tariff": 0.12,  # Grid tariff (when available)
    "uses_diesel": True,
    "diesel_hours_per_day": 12,  # Generator runs 12 hours/day due to outages
    "diesel_price_per_liter": 1.20  # USD per liter in Nigeria
}

try:
    response = requests.post(f"{BASE_URL}/api/v1/analyze", headers=headers, json=test_diesel, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ SUCCESS - Diesel Replacement Scenario")
        print(f"\n📊 Results:")
        print(f"   Consumption: {result.get('estimated_consumption_kwh', 0):.1f} kWh/month")
        print(f"   Solar System: {result.get('recommended_panel_area_m2', 0):.1f}m²")
        print(f"   Generation: {result.get('predicted_generation_kwh', 0):.1f} kWh/month")
        print(f"   System Cost: ${result.get('system_cost', 0):,.0f}")
        print(f"\n💰 Current Energy Costs:")
        print(f"   Diesel: ${result.get('current_energy_cost', {}).get('diesel_monthly', 0):.2f}/month")
        print(f"   Grid: ${result.get('current_energy_cost', {}).get('grid_monthly', 0):.2f}/month")
        print(f"   TOTAL: ${result.get('current_energy_cost', {}).get('total_monthly', 0):.2f}/month")
        print(f"\n⚡ Diesel Details:")
        diesel = result.get('diesel_details', {})
        print(f"   Hours/day: {diesel.get('hours_per_day', 0)}")
        print(f"   Price/liter: ${diesel.get('price_per_liter', 0):.2f}")
        print(f"   Monthly liters: {diesel.get('monthly_liters', 0):.1f}L")
        print(f"   Effective tariff: ${diesel.get('effective_tariff', 0):.2f}/kWh")
        print(f"   Diesel kWh/month: {diesel.get('diesel_kwh_monthly', 0):.1f}")
        print(f"\n💵 Solar Benefits:")
        print(f"   Monthly Savings: ${result.get('monthly_savings', 0):.2f}")
        print(f"   ROI: {result.get('roi_percentage', 0):.2f}%")
        print(f"   Scenario: {result.get('energy_scenario', 'unknown')}")
        print(f"   Recommendation: {result.get('recommendation', 'Unknown')}")
        print(f"   Viability Score: {result.get('viability_score', 0):.1f}/100")
    else:
        print(f"❌ ERROR: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ EXCEPTION: {e}")

print()
print("=" * 80)
print()

# Test Case 3: Heavy Diesel User (18 hours/day - off-grid-like)
print("📋 TEST 3: Heavy Diesel User (18 hours/day)")
print("-" * 80)

test_heavy_diesel = {
    "business_name": "Rural Cold Storage",
    "business_type": "Retail",
    "location": "Mombasa, Kenya",
    "latitude": -4.0435,
    "longitude": 39.6682,
    "equipment_list": [
        {"equipment_type": "cold_room", "quantity": 1, "hours_per_day": 24},
        {"equipment_type": "refrigerator", "quantity": 4, "hours_per_day": 24},
        {"equipment_type": "lights", "quantity": 8, "hours_per_day": 12}
    ],
    "tariff": 0.18,
    "uses_diesel": True,
    "diesel_hours_per_day": 18,  # Very unreliable grid
    "diesel_price_per_liter": 1.35  # Remote area, higher diesel cost
}

try:
    response = requests.post(f"{BASE_URL}/api/v1/analyze", headers=headers, json=test_heavy_diesel, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ SUCCESS - Heavy Diesel User")
        print(f"\n📊 Results:")
        print(f"   Consumption: {result.get('estimated_consumption_kwh', 0):.1f} kWh/month")
        print(f"   Solar System: {result.get('recommended_panel_area_m2', 0):.1f}m²")
        print(f"   Generation: {result.get('predicted_generation_kwh', 0):.1f} kWh/month")
        print(f"   System Cost: ${result.get('system_cost', 0):,.0f}")
        print(f"\n💰 Current Energy Costs:")
        print(f"   Diesel: ${result.get('current_energy_cost', {}).get('diesel_monthly', 0):.2f}/month")
        print(f"   Grid: ${result.get('current_energy_cost', {}).get('grid_monthly', 0):.2f}/month")
        print(f"   TOTAL: ${result.get('current_energy_cost', {}).get('total_monthly', 0):.2f}/month")
        print(f"\n💵 Solar Benefits:")
        print(f"   Monthly Savings: ${result.get('monthly_savings', 0):.2f}")
        print(f"   ROI: {result.get('roi_percentage', 0):.2f}%")
        print(f"   Recommendation: {result.get('recommendation', 'Unknown')}")
        print(f"   Viability Score: {result.get('viability_score', 0):.1f}/100")
        print(f"\n🎯 Impact:")
        diesel_cost = result.get('current_energy_cost', {}).get('diesel_monthly', 0)
        savings = result.get('monthly_savings', 0)
        if diesel_cost > 0:
            reduction = (savings / diesel_cost) * 100
            print(f"   Diesel cost reduction: {reduction:.0f}%")
    else:
        print(f"❌ ERROR: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ EXCEPTION: {e}")

print()
print("=" * 80)
print("✅ All diesel MVP tests complete!")
print("=" * 80)