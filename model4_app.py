"""
MODEL 4: AI RECOMMENDATION ENGINE & ORCHESTRATION
Solar Viability Assessment System

Integrates Models 1-3 deployed on Railway:
- Model 1: Energy Consumption Estimation
- Model 2: Solar Generation Prediction  
- Model 3: Financial Viability & ROI Calculation

Owner: Bella
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

# ============================================
# SECURITY: Load environment variables
# ============================================
load_dotenv()

# SECURITY: API Keys from environment (NOT hardcoded!)
API_KEY = os.getenv('API_KEY')
MODELS_API_KEY = os.getenv('MODELS_API_KEY')  # For calling Models 1-3
MODELS_BASE_URL = os.getenv('MODELS_BASE_URL')

if not API_KEY:
    raise ValueError("ERROR: API_KEY not found in .env file!")
if not MODELS_API_KEY:
    raise ValueError("ERROR: MODELS_API_KEY not found in .env file!")

# ============================================
# LOGGING CONFIGURATION
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# FLASK APP SETUP
# ============================================
app = Flask(__name__)

# SECURITY: Enable CORS
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type", "X-API-KEY"]
    }
})

# SECURITY: Rate Limiting - 100 requests per minute
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per minute"],
    storage_uri="memory://"
)

# ============================================
# DATABASE SCHEMA (for future implementation)
# ============================================
# Tables: business, analysis_results, recommendations
# See database_schema.sql for complete schema

# ============================================
# SECURITY: API KEY AUTHENTICATION
# ============================================
def require_api_key(f):
    """
    SECURITY: Decorator to require API key authentication
    Checks X-API-KEY header against environment variable
    """
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # SECURITY: Get API key from request header
        api_key = request.headers.get('X-API-KEY')
        
        # SECURITY: Check if API key is missing
        if not api_key:
            logger.warning(" Request rejected: Missing API key")
            return jsonify({
                'error': 'Unauthorized',
                'message': 'API key is required. Include X-API-KEY header.'
            }), 401
        
        # SECURITY: Validate API key
        if api_key != API_KEY:
            logger.warning(" Request rejected: Invalid API key")
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Invalid API key'
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

# ============================================
# INPUT VALIDATION FUNCTIONS
# ============================================

def validate_business_input(data):
    """
    SECURITY: Validate business input data
    Returns (is_valid, error_message)
    """
    required_fields = [
        'business_name', 'business_type', 'location',
        'latitude', 'longitude', 'equipment_list'
    ]
    
    # Check required fields
    missing = [f for f in required_fields if f not in data]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    
    # SECURITY: Validate business_name (1-200 characters)
    if not isinstance(data['business_name'], str) or not (1 <= len(data['business_name']) <= 200):
        return False, "business_name must be 1-200 characters"
    
    # SECURITY: Validate business_type (allowed types)
    allowed_types = [
        "Restaurant", "Retail", "Office", "Hotel", "Healthcare",
        "Education", "Manufacturing", "Food & Beverage", "Cafe",
        "Gym", "Bakery", "Entertainment", "Workshop"
    ]
    if data['business_type'] not in allowed_types:
        return False, f"business_type must be one of: {', '.join(allowed_types)}"
    
    # SECURITY: Validate latitude (-90 to 90)
    try:
        lat = float(data['latitude'])
        if not (-90 <= lat <= 90):
            return False, "latitude must be between -90 and 90"
    except (ValueError, TypeError):
        return False, "latitude must be a valid number"
    
    # SECURITY: Validate longitude (-180 to 180)
    try:
        lon = float(data['longitude'])
        if not (-180 <= lon <= 180):
            return False, "longitude must be between -180 and 180"
    except (ValueError, TypeError):
        return False, "longitude must be a valid number"
    
    # SECURITY: Validate equipment_list
    if not isinstance(data['equipment_list'], list):
        return False, "equipment_list must be an array"
    
    if len(data['equipment_list']) > 500:
        return False, "equipment_list cannot exceed 500 items"
    
    for item in data['equipment_list']:
        if not isinstance(item, dict):
            return False, "Each equipment item must be an object"
        if 'equipment_type' not in item or 'quantity' not in item:
            return False, "Each equipment must have equipment_type and quantity"
        
        # SECURITY: Validate quantity (0-100 per item)
        try:
            qty = int(item['quantity'])
            if not (0 <= qty <= 100):
                return False, f"Equipment quantity must be 0-100, got {qty}"
        except (ValueError, TypeError):
            return False, "Equipment quantity must be a number"
        
        # SECURITY: Validate hours (0-24)
        if 'hours_per_day' in item:
            try:
                hours = float(item['hours_per_day'])
                if not (0 <= hours <= 24):
                    return False, f"hours_per_day must be 0-24, got {hours}"
            except (ValueError, TypeError):
                return False, "hours_per_day must be a number"
    
    return True, None

def validate_output(result):
    """
    SECURITY: Validate and sanitize output data
    """
    # SECURITY: Ensure viability_score is 0-100
    if 'viability_score' in result:
        score = result['viability_score']
        result['viability_score'] = max(0, min(100, score))
    
    # SECURITY: Ensure ROI is positive
    if 'roi_percentage' in result:
        roi = result['roi_percentage']
        result['roi_percentage'] = max(0, roi)
    
    # SECURITY: Ensure consumption/generation are positive
    for field in ['estimated_consumption_kwh', 'predicted_generation_kwh']:
        if field in result and result[field] < 0:
            result[field] = 0
    
    return result

# ============================================
# MODEL INTEGRATION FUNCTIONS
# ============================================

def call_model1_consumption(equipment_list, business_type):
    """
    Call Model 1: Energy Consumption Estimation
    Endpoint: POST /api/v1/estimate-consumption
    """
    try:
        logger.info(" Calling Model 1: Energy Consumption Estimation")
        
        response = requests.post(
            f"{MODELS_BASE_URL}/estimate-consumption",
            headers={
                "X-API-KEY": MODELS_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "equipment_list": equipment_list,
                "business_type": business_type
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f" Model 1 Success: {data.get('estimated_consumption_kwh', 0)} kWh")
            return data
        else:
            logger.error(f" Model 1 Error: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f" Model 1 Exception: {str(e)}")
        return None

def call_model2_generation(latitude, longitude):
    """
    Call Model 2: Solar Generation Prediction
    Endpoint: POST /api/v1/predict-generation
    """
    try:
        logger.info(" Calling Model 2: Solar Generation Prediction")
        
        response = requests.post(
            f"{MODELS_BASE_URL}/predict-generation",
            headers={
                "X-API-KEY": MODELS_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "latitude": latitude,
                "longitude": longitude
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f" Model 2 Success: {data.get('predicted_generation_kwh', 0)} kWh")
            return data
        else:
            logger.error(f" Model 2 Error: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f" Model 2 Exception: {str(e)}")
        return None

def call_model3_roi(consumption_kwh, generation_kwh, tariff):
    """
    Call Model 3: Financial Viability & ROI Calculation
    Endpoint: POST /api/v1/calculate-roi
    """
    try:
        logger.info(" Calling Model 3: ROI Calculation")
        
        response = requests.post(
            f"{MODELS_BASE_URL}/calculate-roi",
            headers={
                "X-API-KEY": MODELS_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "consumption_kwh": consumption_kwh,
                "generation_kwh": generation_kwh,
                "tariff": tariff
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f" Model 3 Success: ROI {data.get('roi_percentage', 0)}%")
            return data
        else:
            logger.error(f" Model 3 Error: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f" Model 3 Exception: {str(e)}")
        return None

# ============================================
# RECOMMENDATION ENGINE
# ============================================

def generate_recommendation(consumption_data, generation_data, roi_data):
    """
    MODEL 4: Generate final viability recommendation
    Based on outputs from Models 1-3
    """
    logger.info(" MODEL 4: Generating recommendation")
    
    # Extract key metrics
    consumption_kwh = consumption_data.get('estimated_consumption_kwh', 0) if consumption_data else 0
    generation_kwh = generation_data.get('predicted_generation_kwh', 0) if generation_data else 0
    roi_percentage = roi_data.get('roi_percentage', 0) if roi_data else 0
    monthly_savings = roi_data.get('monthly_savings', 0) if roi_data else 0
    
    # Calculate viability score (0-100)
    # Factors: ROI (50%), Generation/Consumption ratio (30%), Absolute savings (20%)
    roi_score = min(100, roi_percentage * 0.5) if roi_percentage > 0 else 0
    
    coverage_ratio = (generation_kwh / consumption_kwh * 100) if consumption_kwh > 0 else 0
    coverage_score = min(30, coverage_ratio * 0.3)
    
    savings_score = min(20, monthly_savings / 1000) if monthly_savings > 0 else 0
    
    viability_score = roi_score + coverage_score + savings_score
    
    # Determine recommendation level
    if viability_score >= 70:
        recommendation = "High"
        status = "HIGHLY VIABLE"
        color = "green"
    elif viability_score >= 50:
        recommendation = "Medium"
        status = "MODERATELY VIABLE"
        color = "yellow"
    else:
        recommendation = "Low"
        status = "NOT VIABLE"
        color = "red"
    
    # Generate explainability text
    reasons = []
    
    if roi_percentage > 15:
        reasons.append(f"Strong ROI of {roi_percentage:.1f}%")
    elif roi_percentage > 5:
        reasons.append(f"Moderate ROI of {roi_percentage:.1f}%")
    else:
        reasons.append(f"Low ROI of {roi_percentage:.1f}%")
    
    if coverage_ratio > 80:
        reasons.append(f"Excellent solar coverage ({coverage_ratio:.0f}% of consumption)")
    elif coverage_ratio > 50:
        reasons.append(f"Good solar coverage ({coverage_ratio:.0f}% of consumption)")
    else:
        reasons.append(f"Limited solar coverage ({coverage_ratio:.0f}% of consumption)")
    
    if monthly_savings > 5000:
        reasons.append(f"Significant monthly savings (${monthly_savings:,.0f})")
    elif monthly_savings > 1000:
        reasons.append(f"Moderate monthly savings (${monthly_savings:,.0f})")
    
    explanation = f"Solar is {status.lower()} because: " + "; ".join(reasons) + "."
    
    logger.info(f" MODEL 4 Recommendation: {recommendation} ({viability_score:.1f}/100)")
    
    return {
        'recommendation': recommendation,
        'viability_score': round(viability_score, 2),
        'status': status,
        'explanation': explanation,
        'confidence': round(min(consumption_data.get('confidence', 0.8), generation_data.get('confidence', 0.8)) * 100, 2) if consumption_data and generation_data else 0
    }

# ============================================
# API ENDPOINTS
# ============================================

@app.route('/', methods=['GET'])
def home():
    """Root endpoint - API information"""
    return jsonify({
        'service': 'Solar Viability Assessment - Model 4',
        'description': 'AI Recommendation Engine & Orchestration',
        'version': '1.0.0',
        'owner': 'Bella',
        'endpoints': {
            'health': 'GET /health',
            'analyze': 'POST /api/v1/analyze',
            'models_status': 'GET /api/v1/models/status'
        },
        'security': 'API key required (X-API-KEY header)',
        'integrated_models': {
            'model_1': 'Energy Consumption Estimation',
            'model_2': 'Solar Generation Prediction',
            'model_3': 'Financial Viability & ROI'
        }
    }), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint - NO AUTHENTICATION REQUIRED"""
    return jsonify({
        'status': 'healthy',
        'service': 'Model 4 Orchestration',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    }), 200

@app.route('/api/v1/analyze', methods=['POST'])
@require_api_key  # SECURITY: API Key required
@limiter.limit("100/minute")  # SECURITY: Rate limiting
def analyze():
    """
    MASTER ENDPOINT: Solar Viability Analysis
    Orchestrates Models 1-3 and returns final recommendation
    
    SECURITY FEATURES:
    - API Key authentication (X-API-KEY header)
    - Rate limiting (100 requests/minute)
    - Input validation (realistic ranges)
    - Output validation (safe data)
    - Error handling (no leaked information)
    """
    try:
        # SECURITY: Get and validate JSON data
        data = request.get_json()
        
        if not data:
            logger.warning(" Request rejected: No JSON data")
            return jsonify({
                'error': 'Bad Request',
                'message': 'Request must include JSON data'
            }), 400
        
        # SECURITY: Validate input
        is_valid, error_msg = validate_business_input(data)
        if not is_valid:
            logger.warning(f" Validation failed: {error_msg}")
            return jsonify({
                'error': 'Bad Request',
                'message': error_msg
            }), 400
        
        logger.info(f" MODEL 4: Starting analysis for {data['business_name']}")
        
        # Extract inputs
        equipment_list = data['equipment_list']
        business_type = data['business_type']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tariff = float(data.get('tariff', 0.15))  # Default $0.15/kWh
        
        # STEP 1: Call Model 1 (Energy Consumption)
        consumption_data = call_model1_consumption(equipment_list, business_type)
        
        # STEP 2: Call Model 2 (Solar Generation)
        generation_data = call_model2_generation(latitude, longitude)
        
        # STEP 3: Call Model 3 (ROI Calculation)
        if consumption_data and generation_data:
            consumption_kwh = consumption_data.get('estimated_consumption_kwh', 0)
            generation_kwh = generation_data.get('predicted_generation_kwh', 0)
            
            roi_data = call_model3_roi(consumption_kwh, generation_kwh, tariff)
        else:
            roi_data = None
        
        # STEP 4: Generate Recommendation (Model 4)
        if consumption_data and generation_data and roi_data:
            recommendation = generate_recommendation(
                consumption_data,
                generation_data,
                roi_data
            )
            
            # Build complete response
            result = {
                'business_name': data['business_name'],
                'business_type': data['business_type'],
                'location': data['location'],
                
                # Model 1 outputs
                'estimated_consumption_kwh': consumption_data.get('estimated_consumption_kwh'),
                
                # Model 2 outputs
                'predicted_generation_kwh': generation_data.get('predicted_generation_kwh'),
                
                # Model 3 outputs
                'roi_percentage': roi_data.get('roi_percentage'),
                'monthly_savings': roi_data.get('monthly_savings'),
                'system_cost': roi_data.get('system_cost'),
                
                # Model 4 outputs (recommendation)
                'recommendation': recommendation['recommendation'],
                'viability_score': recommendation['viability_score'],
                'status': recommendation['status'],
                'explanation': recommendation['explanation'],
                'confidence': recommendation['confidence'],
                
                'analyzed_at': datetime.utcnow().isoformat()
            }
            
            # SECURITY: Validate output
            result = validate_output(result)
            
            logger.info(f" MODEL 4 Complete: {result['recommendation']} viability")
            
            return jsonify(result), 200
            
        else:
            # SECURITY: Graceful error handling - don't expose which model failed
            logger.error(" One or more models failed")
            return jsonify({
                'error': 'Service Unavailable',
                'message': 'Unable to complete analysis. One or more required services are unavailable.',
                'business_name': data['business_name'],
                'status': 'INCOMPLETE'
            }), 503
        
    except ValueError as e:
        # SECURITY: 400 for validation errors
        logger.warning(f" Validation error: {str(e)}")
        return jsonify({
            'error': 'Bad Request',
            'message': str(e)
        }), 400
        
    except Exception as e:
        # SECURITY: 500 for server errors - HIDE DETAILS
        logger.error(f" Server error: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred processing your request. Please contact support.'
        }), 500

@app.route('/api/v1/models/status', methods=['GET'])
@require_api_key
def models_status():
    """
    Check status of integrated models
    Requires API key
    """
    try:
        # Check Model 1-3 health
        health_response = requests.get(
            f"{MODELS_BASE_URL}/health",
            headers={"X-API-KEY": MODELS_API_KEY},
            timeout=10
        )
        
        models_healthy = health_response.status_code == 200
        
        return jsonify({
            'model_4': 'operational',
            'integrated_models': {
                'base_url': MODELS_BASE_URL,
                'status': 'healthy' if models_healthy else 'unavailable',
                'model_1': 'Energy Consumption Estimation',
                'model_2': 'Solar Generation Prediction',
                'model_3': 'Financial Viability & ROI'
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'model_4': 'operational',
            'integrated_models': {
                'status': 'unavailable',
                'error': 'Cannot reach models service'
            }
        }), 200

# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(400)
def bad_request(e):
    return jsonify({'error': 'Bad Request', 'message': str(e)}), 400

@app.errorhandler(401)
def unauthorized(e):
    return jsonify({'error': 'Unauthorized', 'message': 'Invalid or missing API key'}), 401

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not Found', 'message': 'Endpoint not found'}), 404

@app.errorhandler(429)
def rate_limit_exceeded(e):
    return jsonify({'error': 'Too Many Requests', 'message': 'Rate limit exceeded'}), 429

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal error: {str(e)}", exc_info=True)
    return jsonify({'error': 'Internal Server Error', 'message': 'An error occurred'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return jsonify({'error': 'Internal Server Error', 'message': 'An unexpected error occurred'}), 500

# ============================================
# STARTUP
# ============================================

if __name__ == '__main__':
    logger.info(" Starting Model 4: AI Recommendation Engine & Orchestration")
    logger.info(f" API Key authentication: ENABLED")
    logger.info(f" Rate limiting: ENABLED (100/minute)")
    logger.info(f" Input validation: ENABLED")
    logger.info(f" Integrated with Models 1-3 at: {MODELS_BASE_URL}")
    
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=False  # SECURITY: Never debug in production
    )
