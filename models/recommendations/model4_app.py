"""
MODEL 4: AI RECOMMENDATION ENGINE & ORCHESTRATION
ENHANCED VERSION - Supports both equipment list AND business metrics

Integrates Models 1-3 deployed on Railway:
- Model 1: Energy Consumption Estimation
- Model 2: Solar Generation Prediction  
- Model 3: Financial Viability & ROI Calculation

This version:
1. Accepts equipment_list from frontend (better UX)
2. Converts equipment → business metrics for Model 1
3. No Model 1 retraining needed!
4. Backward compatible with business metrics input

Owner: Bella
Updates: Tessa
Implements ALL Security Requirements
"""

from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
from datetime import datetime
import requests
from typing import Dict, List, Optional

# Load environment
load_dotenv()

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Module-level limiter (init_app called inside create_app)
limiter = Limiter(key_func=get_remote_address, default_limits=["100 per minute"], storage_uri="memory://")


def create_app() -> Flask:
    """
    Application factory for Model 4.
    Reads API_KEY, and MODELS_BASE_URL from environment.
    Raises ValueError at startup if required keys are missing.
    """
    global API_KEY, MODELS_BASE_URL

    API_KEY = os.getenv('API_KEY')
    MODELS_BASE_URL = os.getenv('MODELS_BASE_URL')

    if not API_KEY:
        raise ValueError("ERROR: API_KEY must be set in environment!")

    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST"], "allow_headers": ["Content-Type", "X-API-KEY"]}})
    limiter.init_app(app)

    # Register all routes on this app instance
    register_routes(app)

    logger.info("Model 4 app created successfully")
    return app

# ============================================
# EQUIPMENT TO BUSINESS METRICS CONVERTER
# ============================================

# Equipment power consumption estimates (watts)
EQUIPMENT_POWER_ESTIMATES = {
    # Refrigeration
    'refrigerator': 150,
    'freezer': 200,
    'fridge': 150,
    'cold_room': 500,
    'display_cooler': 250,
    'ice_maker': 300,
    
    # Kitchen
    'oven': 2500,
    'stove': 1500,
    'microwave': 1000,
    'grill': 2000,
    'fryer': 2500,
    'espresso_machine': 1500,
    'coffee_maker': 800,
    
    # HVAC
    'air_conditioner': 1500,
    'ac': 1500,
    'fan': 75,
    'heater': 1500,
    
    # Lighting
    'lights': 60,
    'led_lights': 20,
    'fluorescent': 40,
    
    # Office
    'computer': 200,
    'printer': 100,
    'monitor': 50,
    
    # Fitness
    'treadmill': 700,
    
    # Other
    'water_cooler': 500,
    'water_heater': 3000,
    'dishwasher': 1800,
    'washing_machine': 500,
}

def convert_equipment_to_business_metrics(equipment_list):
    """
    Convert equipment list to business metrics for Model 1
    
    Returns:
        dict with sqft_m2, operating_hours_weekly, num_refrigeration_units
    """
    # Count refrigeration units
    refrigeration_keywords = ['refrigerat', 'freezer', 'fridge', 'cold', 'cooler', 'ice']
    num_refrigeration_units = 0
    
    total_power_watts = 0
    total_hours = 0
    equipment_count = 0
    
    for item in equipment_list:
        equipment_type = item.get('equipment_type', '').lower()
        quantity = item.get('quantity', 1)
        hours_per_day = item.get('hours_per_day', 12)  # Default 12 hrs/day
        
        # Count refrigeration
        if any(keyword in equipment_type for keyword in refrigeration_keywords):
            num_refrigeration_units += quantity
        
        # Estimate power consumption
        power = EQUIPMENT_POWER_ESTIMATES.get(equipment_type, 100)  # Default 100W
        total_power_watts += power * quantity
        total_hours += hours_per_day
        equipment_count += 1
    
    # Calculate average operating hours per week
    avg_hours_per_day = total_hours / equipment_count if equipment_count > 0 else 12
    operating_hours_weekly = avg_hours_per_day * 7
    
    # Estimate floor area based on equipment
    # Rule of thumb: 10-20 sqm per major piece of equipment
    estimated_sqft_m2 = max(50, len(equipment_list) * 15)  # Minimum 50 sqm
    
    # Cap at reasonable maximums
    operating_hours_weekly = min(168, operating_hours_weekly)
    num_refrigeration_units = min(500, num_refrigeration_units)
    estimated_sqft_m2 = min(10000, estimated_sqft_m2)
    
    logger.info(f"📊 Equipment conversion:")
    logger.info(f"   {len(equipment_list)} equipment items")
    logger.info(f"   → {num_refrigeration_units} refrigeration units")
    logger.info(f"   → {operating_hours_weekly:.0f} hours/week")
    logger.info(f"   → {estimated_sqft_m2:.0f} sqm estimated")
    
    return {
        'sqft_m2': estimated_sqft_m2,
        'operating_hours_weekly': operating_hours_weekly,
        'num_refrigeration_units': num_refrigeration_units
    }

# ============================================
# AUTHENTICATION
# ============================================

def require_api_key(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if not api_key:
            logger.warning("⚠️ Request rejected: Missing API key")
            return jsonify({'error': 'Unauthorized', 'message': 'API key is required'}), 401
        if api_key != API_KEY:
            logger.warning("⚠️ Request rejected: Invalid API key")
            return jsonify({'error': 'Unauthorized', 'message': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

# ============================================
# VALIDATION
# ============================================

def validate_business_input(data):
    """Validate input - supports BOTH equipment list AND business metrics"""
    
    required_base = ['business_name', 'business_type', 'location', 'latitude', 'longitude']
    
    # Check base required fields
    missing = [f for f in required_base if f not in data]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    
    # Must have EITHER equipment_list OR business metrics
    has_equipment = 'equipment_list' in data and isinstance(data['equipment_list'], list)
    has_metrics = all(k in data for k in ['sqft_m2', 'operating_hours_weekly', 'num_refrigeration_units'])
    
    if not has_equipment and not has_metrics:
        return False, "Must provide either 'equipment_list' OR business metrics (sqft_m2, operating_hours_weekly, num_refrigeration_units)"
    
    # Basic validations
    if not isinstance(data['business_name'], str) or not (1 <= len(data['business_name']) <= 200):
        return False, "business_name must be 1-200 characters"
    
    try:
        lat = float(data['latitude'])
        if not (-90 <= lat <= 90):
            return False, "latitude must be between -90 and 90"
    except (ValueError, TypeError):
        return False, "latitude must be a valid number"
    
    try:
        lon = float(data['longitude'])
        if not (-180 <= lon <= 180):
            return False, "longitude must be between -180 and 180"
    except (ValueError, TypeError):
        return False, "longitude must be a valid number"
    
    # If business metrics provided, validate them
    if has_metrics:
        try:
            sqft = float(data['sqft_m2'])
            if not (0 < sqft <= 10000):
                return False, "sqft_m2 must be between 0 and 10000"
        except (ValueError, TypeError):
            return False, "sqft_m2 must be a valid number"
        
        try:
            hours = float(data['operating_hours_weekly'])
            if not (0 < hours <= 168):
                return False, "operating_hours_weekly must be between 0 and 168"
        except (ValueError, TypeError):
            return False, "operating_hours_weekly must be a valid number"
        
        try:
            units = int(data['num_refrigeration_units'])
            if not (0 <= units <= 500):
                return False, "num_refrigeration_units must be between 0 and 500"
        except (ValueError, TypeError):
            return False, "num_refrigeration_units must be an integer"
    
    # Validate diesel parameters if provided (all optional)
    if 'uses_diesel' in data:
        if not isinstance(data['uses_diesel'], bool):
            return False, "uses_diesel must be true or false"
    
    if 'diesel_hours_per_day' in data:
        try:
            diesel_hours = float(data['diesel_hours_per_day'])
            if not (0 <= diesel_hours <= 24):
                return False, "diesel_hours_per_day must be between 0 and 24"
        except (ValueError, TypeError):
            return False, "diesel_hours_per_day must be a valid number"
    
    if 'diesel_price_per_liter' in data:
        try:
            diesel_price = float(data['diesel_price_per_liter'])
            if not (0 < diesel_price <= 10):
                return False, "diesel_price_per_liter must be between 0 and 10"
        except (ValueError, TypeError):
            return False, "diesel_price_per_liter must be a valid number"
    
    return True, None

# ============================================
# DIESEL ECONOMICS CALCULATION
# ============================================

def calculate_diesel_economics(consumption_kwh_monthly, diesel_params, grid_tariff):
    """
    Calculate diesel baseline costs and effective blended tariff
    
    MVP Implementation: Simple but accurate diesel replacement economics
    
    Args:
        consumption_kwh_monthly: Monthly energy consumption
        diesel_params: Dict with uses_diesel, diesel_hours_per_day, diesel_price_per_liter
        grid_tariff: Grid electricity cost per kWh
    
    Returns:
        Dict with diesel costs, blended tariff, and breakdown
    """
    uses_diesel = diesel_params.get('uses_diesel', False)
    
    if not uses_diesel:
        # Grid-only scenario
        return {
            'uses_diesel': False,
            'scenario': 'grid_only',
            'blended_tariff': grid_tariff,
            'diesel_kwh_monthly': 0,
            'grid_kwh_monthly': consumption_kwh_monthly,
            'diesel_cost_monthly': 0,
            'grid_cost_monthly': consumption_kwh_monthly * grid_tariff,
            'total_current_cost': consumption_kwh_monthly * grid_tariff,
            'diesel_effective_tariff': 0
        }
    
    # Diesel + Grid hybrid scenario
    diesel_hours_per_day = diesel_params.get('diesel_hours_per_day', 12)
    diesel_price_per_liter = diesel_params.get('diesel_price_per_liter', 1.20)
    
    # Calculate diesel vs grid split
    diesel_fraction = diesel_hours_per_day / 24
    diesel_kwh_monthly = consumption_kwh_monthly * diesel_fraction
    grid_kwh_monthly = consumption_kwh_monthly * (1 - diesel_fraction)
    
    # Diesel generator economics
    # Small generators at partial load (typical SME): ~0.40 liters per kWh
    # 0.25 L/kWh only applies at full rated load; partial load is 50-60% less efficient
    liters_per_kwh = 0.40
    diesel_liters_monthly = diesel_kwh_monthly * liters_per_kwh
    
    # Diesel costs (fuel only for MVP - maintenance can be added later)
    diesel_fuel_cost = diesel_liters_monthly * diesel_price_per_liter
    diesel_maintenance_cost = diesel_hours_per_day * 30 * 0.50  # $0.50/hour typical
    diesel_cost_monthly = diesel_fuel_cost + diesel_maintenance_cost
    
    # Grid costs
    grid_cost_monthly = grid_kwh_monthly * grid_tariff
    
    # Total current energy cost
    total_current_cost = diesel_cost_monthly + grid_cost_monthly
    
    # Effective diesel tariff (for comparison)
    diesel_effective_tariff = diesel_cost_monthly / diesel_kwh_monthly if diesel_kwh_monthly > 0 else 0
    
    # Blended tariff (weighted average for ROI calculation)
    blended_tariff = total_current_cost / consumption_kwh_monthly if consumption_kwh_monthly > 0 else grid_tariff
    
    logger.info(f"💰 Diesel Economics:")
    logger.info(f"   Diesel hours/day: {diesel_hours_per_day}")
    logger.info(f"   Diesel fraction: {diesel_fraction*100:.0f}%")
    logger.info(f"   Diesel kWh/month: {diesel_kwh_monthly:.1f}")
    logger.info(f"   Diesel cost: ${diesel_cost_monthly:.2f}/month")
    logger.info(f"   Diesel effective tariff: ${diesel_effective_tariff:.2f}/kWh")
    logger.info(f"   Grid kWh/month: {grid_kwh_monthly:.1f}")
    logger.info(f"   Grid cost: ${grid_cost_monthly:.2f}/month")
    logger.info(f"   Total current cost: ${total_current_cost:.2f}/month")
    logger.info(f"   Blended tariff: ${blended_tariff:.2f}/kWh")
    
    return {
        'uses_diesel': True,
        'scenario': 'diesel_replacement',
        'blended_tariff': blended_tariff,
        'diesel_hours_per_day': diesel_hours_per_day,
        'diesel_price_per_liter': diesel_price_per_liter,
        'diesel_kwh_monthly': diesel_kwh_monthly,
        'grid_kwh_monthly': grid_kwh_monthly,
        'diesel_liters_monthly': diesel_liters_monthly,
        'diesel_fuel_cost': diesel_fuel_cost,
        'diesel_maintenance_cost': diesel_maintenance_cost,
        'diesel_cost_monthly': diesel_cost_monthly,
        'grid_cost_monthly': grid_cost_monthly,
        'total_current_cost': total_current_cost,
        'diesel_effective_tariff': diesel_effective_tariff
    }

# ============================================
# MODEL CALLS
# ============================================

def call_model1_consumption(data):
    """Call Model 1 with business metrics (converted from equipment if needed)"""
    try:
        logger.info("🔄 Calling Model 1: Energy Consumption Estimation")
        
        # If equipment_list provided, convert to metrics
        if 'equipment_list' in data and isinstance(data['equipment_list'], list):
            logger.info("🔧 Converting equipment list to business metrics...")
            metrics = convert_equipment_to_business_metrics(data['equipment_list'])
            sqft_m2 = metrics['sqft_m2']
            operating_hours_weekly = metrics['operating_hours_weekly']
            num_refrigeration_units = metrics['num_refrigeration_units']
        else:
            # Use provided metrics
            sqft_m2 = float(data['sqft_m2'])
            operating_hours_weekly = float(data['operating_hours_weekly'])
            num_refrigeration_units = int(data['num_refrigeration_units'])
        
        # Map business type
        business_type_mapping = {
            "Restaurant": "grocery", "Retail": "grocery", "Office": "grocery",
            "Hotel": "grocery", "Cafe": "grocery", "Gym": "grocery",
            "Bakery": "butchery", "butchery": "butchery", "grocery": "grocery",
            "mini_supermarket": "mini_supermarket"
        }
        mapped_business_type = business_type_mapping.get(data['business_type'], "grocery")
        
        model1_payload = {
            "business_type": mapped_business_type,
            "sqft_m2": sqft_m2,
            "operating_hours_weekly": operating_hours_weekly,
            "num_refrigeration_units": num_refrigeration_units,
            "location": data['location'],
            "num_workers": int(data.get('num_workers', 5)),
            "months_per_year": int(data.get('months_per_year', 12))
        }
        
        logger.info(f"📤 Model 1 Payload: {model1_payload}")
        
        response = requests.post(
            f"{MODELS_BASE_URL}/estimate-consumption",
            headers={"X-API-KEY": API_KEY, "Content-Type": "application/json"},
            json=model1_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ Model 1 Success: {result.get('estimated_consumption_kwh_monthly', 0)} kWh/month")
            return result
        else:
            logger.error(f"❌ Model 1 Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Model 1 Exception: {str(e)}")
        return None

def call_model2_generation(latitude, longitude):
    """Call Model 2: Solar Generation"""
    try:
        logger.info("🔄 Calling Model 2: Solar Generation Prediction")
        
        # Use current month (1-12)
        current_month = datetime.now().month
        
        payload = {
            "latitude": latitude,
            "longitude": longitude,
            "month": current_month,
            "include_lifetime": True
        }
        
        logger.info(f"📤 Model 2 Payload: {payload}")
        
        response = requests.post(
            f"{MODELS_BASE_URL}/predict-generation",
            headers={"X-API-KEY": API_KEY, "Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Model 2 returns generation for 10m² @ 20% efficiency
            # Extract base generation (daily kWh from the API)
            base_daily_kwh = 0
            
            # Check for monthly_generation first (current month)
            if 'monthly_generation' in result and len(result['monthly_generation']) > 0:
                base_daily_kwh = result['monthly_generation'][0].get('daily_kwh', 0)
            # Fallback to annual summary
            elif 'annual_summary' in result:
                base_daily_kwh = result['annual_summary'].get('average_daily_kwh', 0)
            
            # Convert to monthly (30 days) for 10m² system
            base_monthly_kwh = base_daily_kwh * 30
            
            # Store base generation for reference
            result['base_generation_10m2_kwh'] = max(0, base_monthly_kwh)
            result['base_daily_kwh'] = max(0, base_daily_kwh)
            
            # NOTE: System sizing will be done in analyze() function
            # where we have access to consumption data
            result['predicted_generation_kwh'] = max(0, base_monthly_kwh)
            
            logger.info(f"✅ Model 2 Success: {base_monthly_kwh:.2f} kWh/month (10m² base)")
            logger.info(f"📊 Daily generation: {base_daily_kwh:.2f} kWh/day")
            return result
        else:
            logger.error(f"❌ Model 2 Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"❌ Model 2 Exception: {str(e)}")
        return None

def call_model3_roi(consumption_kwh, generation_kwh, tariff, system_cost_usd=6000.0):
    """Call Model 3: ROI"""
    try:
        logger.info("🔄 Calling Model 3: ROI Calculation")
        
        payload = {
            "consumption_kwh": consumption_kwh,
            "generation_kwh": generation_kwh,
            "tariff_per_kwh": tariff,  # Note: tariff_per_kwh not just tariff
            "system_cost_usd": system_cost_usd
        }
        
        logger.info(f"📤 Model 3 Payload: {payload}")
        
        response = requests.post(
            f"{MODELS_BASE_URL}/calculate-roi",
            headers={"X-API-KEY": API_KEY, "Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ Model 3 Success: ROI {result.get('roi_percentage', 0)}%")
            return result
        else:
            logger.error(f"❌ Model 3 Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"❌ Model 3 Exception: {str(e)}")
        return None

def generate_recommendation(consumption_data, generation_data, roi_data):
    """Generate recommendation"""
    logger.info("🤖 MODEL 4: Generating recommendation")
    
    consumption_kwh = consumption_data.get('estimated_consumption_kwh_monthly', 0) if consumption_data else 0
    generation_kwh = generation_data.get('predicted_generation_kwh', 0) if generation_data else 0
    roi_percentage = roi_data.get('roi_percentage', 0) if roi_data else 0
    monthly_savings = roi_data.get('monthly_savings', 0) if roi_data else 0
    
    # Viability score calculation
    # ROI scoring: calibrated for both grid-only (2-5%) and diesel (20-40%) scenarios
    # Uses diminishing returns so both ranges produce meaningful scores
    if roi_percentage <= 0:
        roi_score = 0
    elif roi_percentage <= 5:
        roi_score = roi_percentage * 3          # 0-5% ROI → 0-15 pts (linear, low range)
    elif roi_percentage <= 20:
        roi_score = 15 + (roi_percentage - 5) * 1.5  # 5-20% ROI → 15-37.5 pts
    else:
        roi_score = min(50, 37.5 + (roi_percentage - 20) * 0.625)  # 20%+ ROI → 37.5-50 pts

    coverage_ratio = (generation_kwh / consumption_kwh * 100) if consumption_kwh > 0 else 0
    coverage_score = min(30, coverage_ratio * 0.3)
    savings_score = min(20, monthly_savings / 25) if monthly_savings > 0 else 0
    viability_score = roi_score + coverage_score + savings_score
    
    if viability_score >= 65:
        recommendation, status = "High", "HIGHLY VIABLE"
    elif viability_score >= 40:
        recommendation, status = "Medium", "MODERATELY VIABLE"
    else:
        recommendation, status = "Low", "NOT VIABLE"
    
    reasons = []
    if roi_percentage > 15:
        reasons.append(f"Strong ROI of {roi_percentage:.1f}%")
    elif roi_percentage > 5:
        reasons.append(f"Moderate ROI of {roi_percentage:.1f}%")
    else:
        reasons.append(f"Low ROI of {roi_percentage:.1f}%")
    
    if coverage_ratio > 80:
        reasons.append(f"Excellent solar coverage ({coverage_ratio:.0f}%)")
    elif coverage_ratio > 50:
        reasons.append(f"Good solar coverage ({coverage_ratio:.0f}%)")
    else:
        reasons.append(f"Limited solar coverage ({coverage_ratio:.0f}%)")
    
    if monthly_savings > 500:
        reasons.append(f"Significant savings (${monthly_savings:,.0f}/mo)")
    elif monthly_savings > 100:
        reasons.append(f"Moderate savings (${monthly_savings:,.0f}/mo)")
    
    explanation = f"Solar is {status.lower()} because: " + "; ".join(reasons) + "."
    
    logger.info(f"✨ Recommendation: {recommendation} ({viability_score:.1f}/100)")
    
    return {
        'recommendation': recommendation,
        'viability_score': round(viability_score, 2),
        'status': status,
        'explanation': explanation,
        'confidence': round(consumption_data.get('confidence_score', 0.85) * 100, 2) if consumption_data else 85
    }

# ============================================
# ENDPOINTS
# ============================================


def register_routes(app: Flask) -> None:
    """Register all routes on the given Flask app instance."""

    @app.route('/', methods=['GET'])
    def home():
        return jsonify({
            'service': 'Solar Viability Assessment - Model 4',
            'version': '1.2.0-mvp-diesel',
            'description': 'MVP: Diesel replacement economics + intelligent system sizing',
            'features': {
                'equipment_to_metrics': 'Converts equipment list to business metrics',
                'intelligent_sizing': 'Auto-scales system to 90% consumption coverage',
                'diesel_economics': 'Calculates diesel replacement savings (MVP)',
                'ml_estimation': 'No historical bills required'
            },
            'endpoints': {
                'health': 'GET /health',
                'analyze': 'POST /api/v1/analyze (requires X-API-KEY header)'
            },
            'new_inputs': {
                'uses_diesel': 'boolean (optional, default false)',
                'diesel_hours_per_day': 'number 0-24 (optional, default 12)',
                'diesel_price_per_liter': 'USD per liter (optional, default 1.20)'
            }
    }), 200

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({
            'status': 'healthy',
            'service': 'Model 4 Orchestration (MVP + Diesel)',
            'timestamp': datetime.now().isoformat(),
            'version': '1.2.0-mvp-diesel'
        }), 200

    @app.route('/api/v1/analyze', methods=['POST'])
    @require_api_key
    @limiter.limit("100/minute")
    def analyze():
        """
        ENHANCED: Accepts BOTH equipment_list OR business metrics
        Automatically converts equipment to metrics for Model 1
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Bad Request', 'message': 'No JSON data'}), 400
        
            is_valid, error_msg = validate_business_input(data)
            if not is_valid:
                return jsonify({'error': 'Bad Request', 'message': error_msg}), 400
        
            logger.info(f"🚀 Starting analysis for {data['business_name']}")
        
            latitude = float(data['latitude'])
            longitude = float(data['longitude'])
            tariff = float(data.get('tariff', 0.15))
        
            # Extract diesel parameters
            diesel_params = {
                'uses_diesel': data.get('uses_diesel', False),
                'diesel_hours_per_day': data.get('diesel_hours_per_day', 12),
                'diesel_price_per_liter': data.get('diesel_price_per_liter', 1.20)
            }
        
            # Call models
            consumption_data = call_model1_consumption(data)
            generation_data = call_model2_generation(latitude, longitude)
        
            # Intelligent System Sizing based on consumption
            if consumption_data and generation_data:
                consumption_kwh = consumption_data.get('estimated_consumption_kwh_monthly', 0)
                base_generation_kwh = generation_data.get('base_generation_10m2_kwh', 0)
                base_daily_kwh = generation_data.get('base_daily_kwh', 0)
            
                if base_generation_kwh > 0 and consumption_kwh > 0:
                    # Calculate optimal system size to cover 80-100% of consumption
                    # Target 90% coverage for good viability
                    target_coverage = 0.90
                    required_generation = consumption_kwh * target_coverage
                
                    # Calculate scaling factor (how many times bigger than 10m²)
                    scaling_factor = required_generation / base_generation_kwh
                
                    # Constrain scaling factor: max 50m² (~$20,000) - realistic SME upper bound
                    scaling_factor = max(1.0, min(5.0, scaling_factor))
                
                    # Scale up the generation
                    scaled_generation_kwh = base_generation_kwh * scaling_factor
                    scaled_daily_kwh = base_daily_kwh * scaling_factor
                    recommended_panel_area = 10.0 * scaling_factor
                
                    # Calculate scaled system cost ($600/m² is typical for African markets)
                    base_system_cost = 6000  # for 10m²
                    scaled_system_cost = base_system_cost * scaling_factor
                
                    # Update generation_data with scaled values
                    generation_data['predicted_generation_kwh'] = scaled_generation_kwh
                    generation_data['scaled_daily_kwh'] = scaled_daily_kwh
                    generation_data['recommended_panel_area_m2'] = recommended_panel_area
                    generation_data['scaling_factor'] = scaling_factor
                    generation_data['system_cost_usd'] = scaled_system_cost
                
                    logger.info(f"🔧 Intelligent System Sizing:")
                    logger.info(f"   Consumption: {consumption_kwh:.2f} kWh/month")
                    logger.info(f"   Base (10m²): {base_generation_kwh:.2f} kWh/month")
                    logger.info(f"   Recommended: {recommended_panel_area:.1f}m² panels")
                    logger.info(f"   Scaled generation: {scaled_generation_kwh:.2f} kWh/month")
                    logger.info(f"   Coverage: {(scaled_generation_kwh/consumption_kwh*100):.1f}%")
                    logger.info(f"   System cost: ${scaled_system_cost:,.0f}")
            
                # Calculate diesel economics and blended tariff
                diesel_economics = calculate_diesel_economics(consumption_kwh, diesel_params, tariff)
                blended_tariff = diesel_economics['blended_tariff']
            
                generation_kwh = generation_data.get('predicted_generation_kwh', 0)
                system_cost = generation_data.get('system_cost_usd', 6000)
                roi_data = call_model3_roi(consumption_kwh, generation_kwh, blended_tariff, system_cost)
            
                # Add diesel economics to roi_data for output
                if roi_data:
                    roi_data['diesel_economics'] = diesel_economics
            else:
                roi_data = None
        
            if consumption_data and generation_data and roi_data:
                recommendation = generate_recommendation(consumption_data, generation_data, roi_data)
            
                result = {
                    'business_name': data['business_name'],
                    'business_type': data['business_type'],
                    'location': data['location'],
                    'estimated_consumption_kwh': consumption_data.get('estimated_consumption_kwh_monthly'),
                    'predicted_generation_kwh': generation_data.get('predicted_generation_kwh'),
                    'recommended_panel_area_m2': generation_data.get('recommended_panel_area_m2', 10.0),
                    'roi_percentage': roi_data.get('roi_percentage'),
                    'monthly_savings': roi_data.get('monthly_savings_usd'),
                    'system_cost': generation_data.get('system_cost_usd', 6000),
                    'recommendation': recommendation['recommendation'],
                    'viability_score': recommendation['viability_score'],
                    'status': recommendation['status'],
                    'explanation': recommendation['explanation'],
                    'confidence': recommendation['confidence'],
                    'analyzed_at': datetime.now().isoformat(),
                
                    # Diesel economics breakdown (MVP feature)
                    'energy_scenario': roi_data.get('diesel_economics', {}).get('scenario', 'grid_only'),
                    'current_energy_cost': {
                        'total_monthly': roi_data.get('diesel_economics', {}).get('total_current_cost', 0),
                        'diesel_monthly': roi_data.get('diesel_economics', {}).get('diesel_cost_monthly', 0),
                        'grid_monthly': roi_data.get('diesel_economics', {}).get('grid_cost_monthly', 0)
                    }
                }
            
                # Add diesel details if applicable
                if roi_data.get('diesel_economics', {}).get('uses_diesel'):
                    result['diesel_details'] = {
                        'hours_per_day': roi_data['diesel_economics'].get('diesel_hours_per_day'),
                        'price_per_liter': roi_data['diesel_economics'].get('diesel_price_per_liter'),
                        'monthly_liters': roi_data['diesel_economics'].get('diesel_liters_monthly'),
                        'effective_tariff': roi_data['diesel_economics'].get('diesel_effective_tariff'),
                        'diesel_kwh_monthly': roi_data['diesel_economics'].get('diesel_kwh_monthly')
                    }
            
                logger.info(f"✅ Complete: {result['recommendation']} viability")
                return jsonify(result), 200
            else:
                logger.error("❌ One or more models failed")
                return jsonify({
                    'error': 'Service Unavailable',
                    'message': 'Unable to complete analysis',
                    'business_name': data['business_name'],
                    'status': 'INCOMPLETE'
                }), 503
        
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}", exc_info=True)
            return jsonify({'error': 'Internal Server Error', 'message': 'An error occurred'}), 500

    # Error handlers — registered here so they bind to the correct app instance
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'error': 'Bad Request', 'message': str(e)}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({'error': 'Unauthorized', 'message': 'Invalid or missing API key'}), 401

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return jsonify({'error': 'Too Many Requests', 'message': 'Rate limit exceeded'}), 429

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({'error': 'Internal Server Error', 'message': 'An error occurred'}), 500



# Module-level app for standalone use and gunicorn
# When imported by api/main.py, create_app() is called there instead.
API_KEY = None
MODELS_BASE_URL = None

if __name__ == '__main__':
    app = create_app()
    logger.info("🚀 Model 4: MVP + Diesel Replacement Economics")
    logger.info(f"✅ Equipment list → Business metrics conversion")
    logger.info(f"✅ Intelligent system sizing (90% coverage target)")
    logger.info(f"✅ Diesel replacement economics (NEW - MVP feature)")
    logger.info(f"🔗 Integrated with Models 1-3 at: {MODELS_BASE_URL}")
    logger.info(f"📖 Version: 1.2.0-mvp-diesel")
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=False)