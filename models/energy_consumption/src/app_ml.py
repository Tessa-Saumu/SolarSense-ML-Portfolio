
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import numpy as np
import joblib
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
import logging

# SECURITY: Load environment variables from .env file
load_dotenv()

# SECURITY: Configure logging (hide sensitive details in production)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Climate zones
CLIMATE_ZONES = {
    'lagos': 1.35, 'accra': 1.30, 'nairobi': 1.20, 'kampala': 1.25,
    'johannesburg': 1.18, 'dar es salaam': 1.35, 'kinshasa': 1.35, 'abidjan': 1.30
}

def get_climate_factor(location: str) -> float:
    """Get climate adjustment factor from location string."""
    location_lower = location.lower()
    for city, factor in CLIMATE_ZONES.items():
        if city in location_lower:
            return factor
    return 1.20  # default


def create_app(
    model_path: Optional[Path] = None,
    scaler_path: Optional[Path] = None,
    feature_cols_path: Optional[Path] = None,
    mappings_path: Optional[Path] = None,
    test_mode: bool = False,
    api_key: Optional[str] = None,
    disable_auth: bool = False
) -> Flask:
    """
    Factory function to create Flask app with optional model paths for testing.
    
    Args:
        model_path: Optional path to model file (for testing)
        scaler_path: Optional path to scaler file (for testing)
        feature_cols_path: Optional path to feature columns file (for testing)
        mappings_path: Optional path to mappings file (for testing)
        test_mode: If True, allows loading to fail (for testing error scenarios)
        api_key: Optional API key (for testing). If None, loads from env var.
        disable_auth: If True, disables API key authentication (for testing)
    
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    CORS(app)
    
    # SECURITY: API Key Authentication
    # Load API key from environment variable or use provided key
    if api_key is None:
        app.config['API_KEY'] = os.getenv('API_KEY')
    else:
        app.config['API_KEY'] = api_key
    
    app.config['DISABLE_AUTH'] = disable_auth  # For testing
    
    # SECURITY: Rate Limiting - 100 requests per minute
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["100 per minute"],
        storage_uri="memory://"  # In-memory storage for simplicity
    )
    app.config['limiter'] = limiter
    
    # Determine paths
    if model_path is None:
        BASE_DIR = Path(__file__).resolve().parent
        MODELS_DIR = BASE_DIR.parent / "models"
        MODEL_PATH = MODELS_DIR / "energy_consumption_model_v1.joblib"
        SCALER_PATH = MODELS_DIR / "energy_scaler_v1.joblib"
        FEATURE_COLS_PATH = MODELS_DIR / "feature_columns_v1.joblib"
        MAPPINGS_PATH = MODELS_DIR / "sme_mappings_v1.joblib"
    else:
        MODEL_PATH = model_path
        SCALER_PATH = scaler_path
        FEATURE_COLS_PATH = feature_cols_path
        MAPPINGS_PATH = mappings_path
    
    # Load model and dependencies (only if not in test mode or paths exist)
    if test_mode and not MODEL_PATH.exists():
        # In test mode, we'll mock these later
        app.config['TEST_MODE'] = True
        best_model = None
        scaler = None
        feature_columns = None
        sme_mappings = None
        use_log_target = False
        le_pba = None
        le_cendiv = None
        le_size = None
    else:
        app.config['TEST_MODE'] = False
        model_data = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        feature_columns = joblib.load(FEATURE_COLS_PATH)
        sme_mappings = joblib.load(MAPPINGS_PATH)
        
        best_model = model_data['best_model']
        use_log_target = model_data.get('use_log_target', False)
        le_pba = sme_mappings['le_pba']
        le_cendiv = sme_mappings['le_cendiv']
        le_size = sme_mappings['le_size']
    
    # Store in app config for access in routes
    app.config['best_model'] = best_model
    app.config['scaler'] = scaler
    app.config['feature_columns'] = feature_columns
    app.config['sme_mappings'] = sme_mappings
    app.config['use_log_target'] = use_log_target
    app.config['le_pba'] = le_pba
    app.config['le_cendiv'] = le_cendiv
    app.config['le_size'] = le_size

    # SECURITY: API Key Authentication Decorator
    def require_api_key(f):
        """Decorator to require API key authentication."""
        from functools import wraps
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Skip auth in test mode if disabled
            if app.config.get('DISABLE_AUTH', False):
                return f(*args, **kwargs)
            
            api_key_header = request.headers.get('X-API-KEY')
            expected_key = app.config.get('API_KEY')
            
            if not expected_key:
                logger.error("API_KEY not configured in environment")
                return jsonify({
                    'error': {
                        'code': 'AUTH_ERROR',
                        'message': 'Server configuration error',
                        'status': 500
                    }
                }), 500
            
            if not api_key_header or api_key_header != expected_key:
                logger.warning(f"Unauthorized access attempt from {get_remote_address()}")
                return jsonify({
                    'error': {
                        'code': 'UNAUTHORIZED',
                        'message': 'Invalid or missing API key',
                        'status': 401
                    }
                }), 401
            
            return f(*args, **kwargs)
        return decorated_function

    @app.route('/api/v1/estimate-consumption', methods=['POST'])
    @limiter.limit("100 per minute")  # SECURITY: Rate limiting
    @require_api_key  # SECURITY: API key authentication
    def estimate_consumption():
        """Estimate energy consumption for African SME."""
        try:
            data = request.get_json()
            
            # Check for empty or None request body
            if data is None:
                return jsonify({
                    'error': {
                        'code': 'INVALID_JSON',
                        'message': 'Request body must be valid JSON',
                        'status': 400
                    }
                }), 400

            # Input validation
            required_fields = ['business_type', 'sqft_m2', 'operating_hours_weekly', 
                              'num_refrigeration_units', 'location']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'error': {
                            'code': 'MISSING_FIELD',
                            'message': f'Missing required field: {field}',
                            'status': 400
                        }
                    }), 400

            # Extract and validate inputs
            business_type = data['business_type']
            if not isinstance(business_type, str):
                return jsonify({
                    'error': {
                        'code': 'INVALID_FIELD_TYPE',
                        'message': 'business_type must be a string',
                        'status': 400
                    }
                }), 400
            business_type = business_type.lower()

            # SECURITY: Enhanced input validation with realistic ranges
            # Validate sqft_m2: must be positive and realistic (1 m² to 10,000 m²)
            try:
                sqft_m2 = float(data['sqft_m2'])
                if sqft_m2 <= 0:
                    return jsonify({
                        'error': {
                            'code': 'INVALID_FIELD_VALUE',
                            'message': 'sqft_m2 must be greater than 0',
                            'status': 400
                        }
                    }), 400
                if sqft_m2 > 10000:  # SECURITY: Reject unrealistically large values
                    return jsonify({
                        'error': {
                            'code': 'INVALID_FIELD_VALUE',
                            'message': 'sqft_m2 exceeds maximum allowed value (10,000 m²)',
                            'status': 400
                        }
                    }), 400
            except (ValueError, TypeError):
                return jsonify({
                    'error': {
                        'code': 'INVALID_FIELD_TYPE',
                        'message': 'sqft_m2 must be a number',
                        'status': 400
                    }
                }), 400

            # SECURITY: Validate operating_hours_weekly: 0-168 (hours in a week)
            try:
                operating_hours_weekly = float(data['operating_hours_weekly'])
                if operating_hours_weekly <= 0 or operating_hours_weekly > 168:
                    return jsonify({
                        'error': {
                            'code': 'INVALID_FIELD_VALUE',
                            'message': 'operating_hours_weekly must be between 0 and 168',
                            'status': 400
                        }
                    }), 400
            except (ValueError, TypeError):
                return jsonify({
                    'error': {
                        'code': 'INVALID_FIELD_TYPE',
                        'message': 'operating_hours_weekly must be a number',
                        'status': 400
                    }
                }), 400

            # SECURITY: Validate num_refrigeration_units: non-negative and realistic (max 500)
            try:
                num_refrigeration_units = int(data['num_refrigeration_units'])
                if num_refrigeration_units < 0:
                    return jsonify({
                        'error': {
                            'code': 'INVALID_FIELD_VALUE',
                            'message': 'num_refrigeration_units must be non-negative',
                            'status': 400
                        }
                    }), 400
                if num_refrigeration_units > 500:  # SECURITY: Reject obviously wrong data
                    return jsonify({
                        'error': {
                            'code': 'INVALID_FIELD_VALUE',
                            'message': 'num_refrigeration_units exceeds maximum allowed value (500)',
                            'status': 400
                        }
                    }), 400
            except (ValueError, TypeError):
                return jsonify({
                    'error': {
                        'code': 'INVALID_FIELD_TYPE',
                        'message': 'num_refrigeration_units must be an integer',
                        'status': 400
                    }
                }), 400

            location = data['location']
            if not isinstance(location, str):
                return jsonify({
                    'error': {
                        'code': 'INVALID_FIELD_TYPE',
                        'message': 'location must be a string',
                        'status': 400
                    }
                }), 400

            # SECURITY: Validate optional fields with realistic ranges
            try:
                num_workers = int(data.get('num_workers', 5))
                if num_workers <= 0:
                    num_workers = 5  # Default fallback
                if num_workers > 1000:  # SECURITY: Reject unrealistically large values
                    return jsonify({
                        'error': {
                            'code': 'INVALID_FIELD_VALUE',
                            'message': 'num_workers exceeds maximum allowed value (1000)',
                            'status': 400
                        }
                    }), 400
            except (ValueError, TypeError):
                num_workers = 5

            try:
                months_per_year = int(data.get('months_per_year', 12))
                if months_per_year <= 0 or months_per_year > 12:
                    months_per_year = 12  # Default fallback
            except (ValueError, TypeError):
                months_per_year = 12

            # SECURITY: Validate business_type matches expected format
            valid_business_types = ['butchery', 'grocery', 'mini_supermarket']
            if business_type not in valid_business_types:
                return jsonify({
                    'error': {
                        'code': 'INVALID_BUSINESS_TYPE',
                        'message': f'Invalid business_type. Must be one of: {valid_business_types}',
                        'status': 400
                    }
                }), 400
            
            # SECURITY: Validate location format (must be non-empty string, reasonable length)
            if len(location) > 200:  # Prevent extremely long location strings
                return jsonify({
                    'error': {
                        'code': 'INVALID_FIELD_VALUE',
                        'message': 'location string exceeds maximum length (200 characters)',
                        'status': 400
                    }
                }), 400

            # Get model components from app config
            best_model = app.config['best_model']
            scaler = app.config['scaler']
            use_log_target = app.config['use_log_target']
            le_pba = app.config['le_pba']
            le_cendiv = app.config['le_cendiv']
            le_size = app.config['le_size']

            if best_model is None or scaler is None:
                raise ValueError("Model not loaded")

            # Map business type to PBA
            pba_code = 11  # Food Sales

            # Get climate factor
            climate_factor = get_climate_factor(location)

            # Create features
            sqft = sqft_m2 * 10.764  # Convert m2 to sqft
            sqft_per_worker = sqft / max(num_workers, 1)
            wkhrs_per_week_normalized = operating_hours_weekly / 168
            annual_operating_hours = operating_hours_weekly * months_per_year * (52/12)
            refrigeration_density = (num_refrigeration_units / max(sqft, 1)) * 1000
            is_high_refrigeration = 1 if num_refrigeration_units > 3 else 0
            is_extended_hours = 1 if operating_hours_weekly > 60 else 0

            # Size category
            if sqft < 2000:
                size_category = 'small'
            elif sqft < 10000:
                size_category = 'medium'
            else:
                size_category = 'large'

            # Encode categoricals
            pba_encoded = le_pba.transform([str(pba_code)])[0]
            cendiv_encoded = le_cendiv.transform(['5'])[0]  # Default
            size_category_encoded = le_size.transform([size_category])[0]

            # Build feature vector
            feature_vector = np.array([[
                sqft, operating_hours_weekly, num_refrigeration_units, 1,  # NFLOOR=1
                num_workers, months_per_year, 5,  # YRCONC=5
                0,  # kwh_per_sqft (will be predicted)
                sqft_per_worker, wkhrs_per_week_normalized, annual_operating_hours,
                refrigeration_density, is_high_refrigeration, is_extended_hours,
                pba_encoded, cendiv_encoded, size_category_encoded
            ]])

            # Scale and predict
            feature_vector_scaled = scaler.transform(feature_vector)

            if use_log_target:
                log_prediction = best_model.predict(feature_vector_scaled)[0]
                base_prediction = np.expm1(log_prediction)
            else:
                base_prediction = best_model.predict(feature_vector_scaled)[0]

            # Apply climate adjustment
            adjusted_prediction = base_prediction * climate_factor
            monthly_kwh = adjusted_prediction / 12

            # Breakdown
            refrigeration_share = min(0.70, max(0.50, num_refrigeration_units / max(num_workers * 2, 1)))
            refrigeration_kwh = monthly_kwh * refrigeration_share
            other_kwh = monthly_kwh * (1 - refrigeration_share)

            # Confidence score (based on data completeness)
            confidence_score = 0.75
            if all([sqft_m2 > 0, operating_hours_weekly > 0, num_refrigeration_units > 0]):
                confidence_score = 0.85

            # SECURITY: Output validation - ensure all numbers are realistic and positive
            # Validate monthly_kwh is positive and reasonable (max 1,000,000 kWh/month)
            if monthly_kwh < 0:
                monthly_kwh = 0.0
            if monthly_kwh > 1000000:  # Unrealistically high value
                monthly_kwh = 1000000.0
                logger.warning(f"Monthly kWh capped at 1,000,000 for input: {data}")
            
            # Ensure breakdown values are non-negative
            refrigeration_kwh = max(0.0, refrigeration_kwh)
            other_kwh = max(0.0, other_kwh)
            
            # Ensure confidence_score is in valid range [0, 1]
            confidence_score = max(0.0, min(1.0, confidence_score))

            # SECURITY: Ensure response is strictly JSON with validated values
            response = {
                'estimated_consumption_kwh_monthly': round(monthly_kwh, 2),
                'confidence_score': round(confidence_score, 2),
                'breakdown': {
                    'refrigeration': round(refrigeration_kwh, 2),
                    'other': round(other_kwh, 2)
                },
                'climate_adjustment_factor': round(climate_factor, 2),
                'equipment_summary': {
                    'total_refrigeration_units': num_refrigeration_units,
                    'total_other_equipment': 0  # Not tracked in this version
                }
            }
            
            return jsonify(response), 200

        except ValueError as e:
            # SECURITY: Hide internal error details in production
            logger.error(f"ValueError in estimate_consumption: {str(e)}", exc_info=True)
            return jsonify({
                'error': {
                    'code': 'PREDICTION_ERROR',
                    'message': 'Internal Server Error',
                    'status': 500
                }
            }), 500
        except Exception as e:
            # SECURITY: Hide stack traces and model details - return generic error
            logger.error(f"Unexpected error in estimate_consumption: {str(e)}", exc_info=True)
            return jsonify({
                'error': {
                    'code': 'PREDICTION_ERROR',
                    'message': 'Internal Server Error',
                    'status': 500
                }
            }), 500

    @app.route('/api/v1/health', methods=['GET'])
    def health():
        """Health check endpoint (no authentication required)."""
        # SECURITY: Health endpoint doesn't require auth but still returns JSON
        return jsonify({'status': 'healthy'}), 200

    return app


# Create app instance for direct execution (only when not imported as module)
# SECURITY: Prevent loading models during test imports
if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('MODEL1_PORT', 8001))
    app.run(host='0.0.0.0', port=port, debug=True)
else:
    # For imports (like in tests), create a lazy app instance that won't load models
    app = None
