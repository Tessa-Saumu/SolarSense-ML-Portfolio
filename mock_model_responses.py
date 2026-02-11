"""
Mock Model Responses
Use these for testing your orchestration service without real AI models
"""

import random
from typing import Dict, Any
import json


# ============================================
# MODEL 1 MOCK RESPONSES (Solar Analysis)
# ============================================

MODEL1_MOCK_RESPONSES = {
    "high_solar": {
        "solar_irradiance_kwh_m2_day": 5.8,
        "annual_sunshine_hours": 2800,
        "optimal_panel_angle": 15.0,
        "shading_factor": 0.85,
        "solar_potential_score": 8.5,
        "model_confidence": 92.0,
        "location_type": "equatorial_high_sun"
    },
    "medium_solar": {
        "solar_irradiance_kwh_m2_day": 4.2,
        "annual_sunshine_hours": 2200,
        "optimal_panel_angle": 25.0,
        "shading_factor": 0.70,
        "solar_potential_score": 6.5,
        "model_confidence": 85.0,
        "location_type": "moderate_climate"
    },
    "low_solar": {
        "solar_irradiance_kwh_m2_day": 2.8,
        "annual_sunshine_hours": 1600,
        "optimal_panel_angle": 35.0,
        "shading_factor": 0.55,
        "solar_potential_score": 4.2,
        "model_confidence": 78.0,
        "location_type": "cloudy_climate"
    }
}


# ============================================
# MODEL 2 MOCK RESPONSES (Cost Analysis)
# ============================================

MODEL2_MOCK_RESPONSES = {
    "excellent_roi": {
        "system_size_kw": 20.0,
        "installation_cost": 1600000,
        "annual_energy_production_kwh": 31536,
        "annual_savings": 378432,
        "roi_years": 4.2,
        "payback_period_years": 4.2,
        "net_present_value": 2400000,
        "incentives_available": 320000,
        "cost_per_kwh_saved": 8.5
    },
    "good_roi": {
        "system_size_kw": 15.0,
        "installation_cost": 1200000,
        "annual_energy_production_kwh": 23652,
        "annual_savings": 283824,
        "roi_years": 5.8,
        "payback_period_years": 5.8,
        "net_present_value": 1800000,
        "incentives_available": 240000,
        "cost_per_kwh_saved": 9.2
    },
    "marginal_roi": {
        "system_size_kw": 10.0,
        "installation_cost": 800000,
        "annual_energy_production_kwh": 15768,
        "annual_savings": 189216,
        "roi_years": 7.5,
        "payback_period_years": 7.5,
        "net_present_value": 1200000,
        "incentives_available": 160000,
        "cost_per_kwh_saved": 10.8
    },
    "poor_roi": {
        "system_size_kw": 8.0,
        "installation_cost": 640000,
        "annual_energy_production_kwh": 12614,
        "annual_savings": 151368,
        "roi_years": 9.2,
        "payback_period_years": 9.2,
        "net_present_value": 960000,
        "incentives_available": 128000,
        "cost_per_kwh_saved": 12.5
    }
}


# ============================================
# MODEL 3 MOCK RESPONSES (Business Suitability)
# ============================================

MODEL3_MOCK_RESPONSES = {
    "excellent_fit": {
        "business_hours_match_score": 9.0,
        "energy_pattern_compatibility": 8.5,
        "roof_suitability_score": 8.8,
        "maintenance_capacity_score": 7.5,
        "overall_suitability_score": 8.5,
        "risk_factors": [
            "Minor: Roof inspection recommended before installation"
        ],
        "opportunities": [
            "Peak energy use aligns perfectly with solar production",
            "Can achieve near 100% daytime energy offset",
            "Excellent marketing opportunity for green business",
            "Potential for EV charging station integration"
        ]
    },
    "good_fit": {
        "business_hours_match_score": 8.0,
        "energy_pattern_compatibility": 7.5,
        "roof_suitability_score": 7.0,
        "maintenance_capacity_score": 6.5,
        "overall_suitability_score": 7.3,
        "risk_factors": [
            "Moderate: Roof may require structural reinforcement",
            "Some evening energy use won't be offset by solar"
        ],
        "opportunities": [
            "Good daytime energy offset potential",
            "Can reduce grid dependency significantly",
            "Positive brand differentiation"
        ]
    },
    "marginal_fit": {
        "business_hours_match_score": 6.5,
        "energy_pattern_compatibility": 6.0,
        "roof_suitability_score": 5.5,
        "maintenance_capacity_score": 5.0,
        "overall_suitability_score": 5.8,
        "risk_factors": [
            "Significant evening/night operations reduce solar benefit",
            "Roof condition requires assessment",
            "Limited in-house maintenance capacity",
            "May need battery storage for optimal benefit"
        ],
        "opportunities": [
            "Partial daytime energy offset possible",
            "Could improve with battery storage addition",
            "Some environmental branding value"
        ]
    },
    "poor_fit": {
        "business_hours_match_score": 4.0,
        "energy_pattern_compatibility": 4.5,
        "roof_suitability_score": 4.0,
        "maintenance_capacity_score": 3.5,
        "overall_suitability_score": 4.0,
        "risk_factors": [
            "Critical: Primarily night operations - minimal solar benefit",
            "Critical: Roof unsuitable without major work",
            "No in-house technical capacity",
            "High upfront cost vs limited benefit",
            "Better alternatives available (e.g., energy efficiency)"
        ],
        "opportunities": [
            "Consider energy efficiency upgrades first",
            "Explore time-of-use tariff optimization",
            "Reassess if operations shift to daytime"
        ]
    }
}


# ============================================
# COMPLETE SCENARIO RESPONSES
# ============================================

COMPLETE_SCENARIOS = {
    "coffee_shop_nairobi_excellent": {
        "business_input": {
            "business_name": "Sunshine Coffee House",
            "location": "Nairobi, Kenya",
            "latitude": -1.2921,
            "longitude": 36.8219,
            "monthly_energy_usage_kwh": 2800,
            "monthly_energy_cost": 50400,
            "roof_area_sqm": 180,
            "business_type": "Food & Beverage"
        },
        "model1_response": MODEL1_MOCK_RESPONSES["high_solar"],
        "model2_response": MODEL2_MOCK_RESPONSES["excellent_roi"],
        "model3_response": MODEL3_MOCK_RESPONSES["excellent_fit"],
        "expected_viable": True
    },
    
    "restaurant_mombasa_good": {
        "business_input": {
            "business_name": "Coastal Grill Restaurant",
            "location": "Mombasa, Kenya",
            "latitude": -4.0435,
            "longitude": 39.6682,
            "monthly_energy_usage_kwh": 3500,
            "monthly_energy_cost": 63000,
            "roof_area_sqm": 200,
            "business_type": "Restaurant"
        },
        "model1_response": MODEL1_MOCK_RESPONSES["high_solar"],
        "model2_response": MODEL2_MOCK_RESPONSES["good_roi"],
        "model3_response": MODEL3_MOCK_RESPONSES["good_fit"],
        "expected_viable": True
    },
    
    "bakery_kisumu_marginal": {
        "business_input": {
            "business_name": "Night Owl Bakery",
            "location": "Kisumu, Kenya",
            "latitude": -0.0917,
            "longitude": 34.7680,
            "monthly_energy_usage_kwh": 4200,
            "monthly_energy_cost": 75600,
            "roof_area_sqm": 150,
            "business_type": "Bakery"
        },
        "model1_response": MODEL1_MOCK_RESPONSES["medium_solar"],
        "model2_response": MODEL2_MOCK_RESPONSES["marginal_roi"],
        "model3_response": MODEL3_MOCK_RESPONSES["marginal_fit"],
        "expected_viable": False
    },
    
    "nightclub_eldoret_poor": {
        "business_input": {
            "business_name": "Midnight Lounge",
            "location": "Eldoret, Kenya",
            "latitude": 0.5143,
            "longitude": 35.2698,
            "monthly_energy_usage_kwh": 5000,
            "monthly_energy_cost": 90000,
            "roof_area_sqm": 120,
            "business_type": "Entertainment"
        },
        "model1_response": MODEL1_MOCK_RESPONSES["medium_solar"],
        "model2_response": MODEL2_MOCK_RESPONSES["poor_roi"],
        "model3_response": MODEL3_MOCK_RESPONSES["poor_fit"],
        "expected_viable": False
    },
    
    "small_office_nairobi": {
        "business_input": {
            "business_name": "TechStart Office",
            "location": "Nairobi, Kenya",
            "latitude": -1.2921,
            "longitude": 36.8219,
            "monthly_energy_usage_kwh": 1800,
            "monthly_energy_cost": 32400,
            "roof_area_sqm": 100,
            "business_type": "Office"
        },
        "model1_response": MODEL1_MOCK_RESPONSES["high_solar"],
        "model2_response": MODEL2_MOCK_RESPONSES["good_roi"],
        "model3_response": MODEL3_MOCK_RESPONSES["excellent_fit"],
        "expected_viable": True
    }
}


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_random_scenario() -> Dict[str, Any]:
    """Returns a random complete scenario for testing"""
    scenario_name = random.choice(list(COMPLETE_SCENARIOS.keys()))
    return {
        "scenario_name": scenario_name,
        **COMPLETE_SCENARIOS[scenario_name]
    }


def get_scenario_by_name(name: str) -> Dict[str, Any]:
    """Returns a specific scenario by name"""
    if name not in COMPLETE_SCENARIOS:
        raise ValueError(f"Scenario '{name}' not found. Available: {list(COMPLETE_SCENARIOS.keys())}")
    return {
        "scenario_name": name,
        **COMPLETE_SCENARIOS[name]
    }


def print_scenario(scenario: Dict[str, Any]) -> None:
    """Pretty print a scenario for testing"""
    print("\n" + "="*70)
    print(f"SCENARIO: {scenario['scenario_name']}")
    print("="*70)
    
    print("\n📋 BUSINESS INPUT:")
    for key, value in scenario['business_input'].items():
        print(f"  {key}: {value}")
    
    print("\n🌞 MODEL 1 (Solar Analysis):")
    for key, value in scenario['model1_response'].items():
        print(f"  {key}: {value}")
    
    print("\n💰 MODEL 2 (Cost Analysis):")
    for key, value in scenario['model2_response'].items():
        print(f"  {key}: {value}")
    
    print("\n🏢 MODEL 3 (Business Suitability):")
    for key, value in scenario['model3_response'].items():
        if isinstance(value, list):
            print(f"  {key}:")
            for item in value:
                print(f"    • {item}")
        else:
            print(f"  {key}: {value}")
    
    print(f"\n✅ EXPECTED VIABLE: {scenario['expected_viable']}")
    print("="*70 + "\n")


def export_scenarios_json(filename: str = "test_scenarios.json") -> None:
    """Export all scenarios to a JSON file"""
    with open(filename, 'w') as f:
        json.dump(COMPLETE_SCENARIOS, f, indent=2)
    print(f"✅ Exported {len(COMPLETE_SCENARIOS)} scenarios to {filename}")


# ============================================
# TESTING HELPERS
# ============================================

class MockModelAPI:
    """
    Mock API class that simulates real model responses
    Use this in your tests instead of real API calls
    """
    
    @staticmethod
    def get_solar_analysis(latitude: float, longitude: float) -> Dict:
        """Mock Model 1 API response"""
        # Simple logic: closer to equator = better solar
        if abs(latitude) < 10:
            return MODEL1_MOCK_RESPONSES["high_solar"]
        elif abs(latitude) < 30:
            return MODEL1_MOCK_RESPONSES["medium_solar"]
        else:
            return MODEL1_MOCK_RESPONSES["low_solar"]
    
    @staticmethod
    def get_cost_analysis(
        system_size_kw: float,
        energy_usage_kwh: float
    ) -> Dict:
        """Mock Model 2 API response"""
        # Simple logic: larger system + higher usage = better ROI
        score = (system_size_kw / 20) * (energy_usage_kwh / 3000)
        
        if score > 0.8:
            return MODEL2_MOCK_RESPONSES["excellent_roi"]
        elif score > 0.6:
            return MODEL2_MOCK_RESPONSES["good_roi"]
        elif score > 0.4:
            return MODEL2_MOCK_RESPONSES["marginal_roi"]
        else:
            return MODEL2_MOCK_RESPONSES["poor_roi"]
    
    @staticmethod
    def get_business_suitability(business_type: str) -> Dict:
        """Mock Model 3 API response"""
        # Simple logic based on business type
        daytime_businesses = ["Food & Beverage", "Office", "Retail", "Cafe"]
        mixed_businesses = ["Restaurant", "Hotel", "Gym"]
        night_businesses = ["Entertainment", "Nightclub", "Bar"]
        
        if business_type in daytime_businesses:
            return MODEL3_MOCK_RESPONSES["excellent_fit"]
        elif business_type in mixed_businesses:
            return MODEL3_MOCK_RESPONSES["good_fit"]
        elif business_type in night_businesses:
            return MODEL3_MOCK_RESPONSES["poor_fit"]
        else:
            return MODEL3_MOCK_RESPONSES["marginal_fit"]


# ============================================
# EXAMPLE USAGE
# ============================================

if __name__ == "__main__":
    print("\n🧪 MOCK MODEL RESPONSE EXAMPLES\n")
    
    # Show all scenarios
    print("Available test scenarios:")
    for i, name in enumerate(COMPLETE_SCENARIOS.keys(), 1):
        print(f"{i}. {name}")
    
    print("\n" + "-"*70)
    
    # Show one detailed scenario
    scenario = get_scenario_by_name("coffee_shop_nairobi_excellent")
    print_scenario(scenario)
    
    # Test mock API
    print("\n🔧 MOCK API TEST:")
    mock_api = MockModelAPI()
    
    solar = mock_api.get_solar_analysis(-1.2921, 36.8219)
    print(f"Solar score for Nairobi: {solar['solar_potential_score']}/10")
    
    cost = mock_api.get_cost_analysis(20, 2800)
    print(f"ROI for 20kW system: {cost['roi_years']} years")
    
    suitability = mock_api.get_business_suitability("Food & Beverage")
    print(f"Suitability for cafe: {suitability['overall_suitability_score']}/10")
    
    # Export to JSON
    print("\n📤 Exporting scenarios...")
    export_scenarios_json()
