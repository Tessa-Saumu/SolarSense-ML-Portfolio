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
from werkzeug.exceptions import BadRequest, UnsupportedMediaType

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
    
    # Load model and dependencies
    #
    # SECURITY/TESTABILITY: When `test_mode=True`, we ALWAYS skip loading model files
    # and expect tests to inject mocks into `app.config`. This avoids filesystem and
    # dependency issues during CI/test collection.
    if test_mode:
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

        # region agent log
        # Debug instrumentation for model loading path (hypothesis H1: env/version mismatch)
        try:
            import json as _json, time as _time
            _log_path = "c:\\Users\\ingex\\OneDrive\\Documents\\Git Projects\\SolarSense AI ML Microservice\\Model-1-branch\\.cursor\\debug.log"
            with open(_log_path, "a", encoding="utf-8") as _f:
                _f.write(
                    _json.dumps(
                        {
                            "id": f"log_{int(_time.time() * 1000)}",
                            "timestamp": int(_time.time() * 1000),
                            "location": "models/energy_consumption/src/app_ml.py:create_app",
                            "message": "about_to_load_energy_model",
                            "runId": "run1",
                            "hypothesisId": "H1",
                            "data": {
                                "MODEL_PATH": str(MODEL_PATH),
                                "SCALER_PATH": str(SCALER_PATH),
                                "FEATURE_COLS_PATH": str(FEATURE_COLS_PATH),
                                "MAPPINGS_PATH": str(MAPPINGS_PATH),
                            },
                        }
                    )
                    + "\n"
                )
        except Exception:
            # Logging must never break app startup
            pass
        # endregion

        try:
            model_data = joblib.load(MODEL_PATH)
        except Exception as e:
            # region agent log
            # Capture details about the environment and error during model load
            try:
                import json as _json, time as _time, joblib as _joblib, sys as _sys
                try:
                    import sklearn as _sklearn  # type: ignore
                    _sk_version = getattr(_sklearn, "__version__", None)
                except Exception:
                    _sk_version = None
                _log_path = "c:\\Users\\ingex\\OneDrive\\Documents\\Git Projects\\SolarSense AI ML Microservice\\Model-1-branch\\.cursor\\debug.log"
                with open(_log_path, "a", encoding="utf-8") as _f:
                    _f.write(
                        _json.dumps(
                            {
                                "id": f"log_{int(_time.time() * 1000)}",
                                "timestamp": int(_time.time() * 1000),
                                "location": "models/energy_consumption/src/app_ml.py:create_app",
                                "message": "energy_model_load_failed",
                                "runId": "run1",
                                "hypothesisId": "H1",
                                "data": {
                                    "error": repr(e),
                                    "sklearn_version": _sk_version,
                                    "joblib_version": getattr(_joblib, "__version__", None),
                                    "python_version": _sys.version,
                                },
                            }
                        )
                        + "\n"
                    )
            except Exception:
                pass
            # endregion
            # Re-raise so the calling code still sees the failure
            raise

        scaler = joblib.load(SCALER_PATH)
        feature_columns = joblib.load(FEATURE_COLS_PATH)
        sme_mappings = joblib.load(MAPPINGS_PATH)

        best_model = model_data['best_model']
        use_log_target = model_data.get('use_log_target', False)

        le_pba = sme_mappings['le_pba']
        le_cendiv = sme_mappings['le_cendiv']
        le_size = sme_mappings['le_size']

    # Store components in app config
    app.config['best_model'] = best_model
    app.config['scaler'] = scaler
    app.config['use_log_target'] = use_log_target
    app.config['le_pba'] = le_pba
    app.config['le_cendiv'] = le_cendiv
    app.config['le_size'] = le_size

    def authenticate_request():
        """SECURITY: Validate API key from request headers."""
        if app.config.get('DISABLE_AUTH'):  # Skip auth in testing
            return True
        
        api_key = request.headers.get('X-API-KEY')
        expected_key = app.config.get('API_KEY')
        
        if not expected_key:
            # If no API_KEY is set in environment, allow all requests (development mode)
            logger.warning("No API_KEY configured - authentication disabled")
            return True
        
        if not api_key:
            logger.warning("Request rejected: Missing API key")
            return False
        
        if api_key != expected_key:
            logger.warning("Request rejected: Invalid API key")
            return False
        
        return True

    @app.route('/api/v1/estimate-consumption', methods=['POST'])
    def estimate_consumption():
        """
        Estimate energy consumption for a food retail SME.
        
        SECURITY: Requires X-API-KEY header for authentication.
        SECURITY: Strict input validation on all numeric fields.
        SECURITY: Rate limited to 100 requests per minute.
        
        Expected JSON body:
        {
            "business_type": "butchery" | "grocery" | "mini_supermarket",
            "sqft_m2": float (>0, ≤10000),
            "operating_hours_weekly": float (>0, ≤168),
            "num_refrigeration_units": int (≥0, ≤500),
            "location": str (≤200 chars),
            "num_workers": int (optional, ≥1, ≤1000, default=5),
            "months_per_year": int (optional, 1-12, default=12)
        }
        
        Returns:
        {
            "estimated_consumption_kwh_monthly": float,
            "confidence_score": float,
            "breakdown": {
                "refrigeration": float,
                "other": float
            },
            "climate_adjustment_factor": float
        }
        """
        # SECURITY: Authenticate request
        if not authenticate_request():
            return jsonify({
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Invalid or missing API key',
                    'status': 401
                }
            }), 401

        # SECURITY: Validate Content-Type
        if not request.is_json:
            return jsonify({
                'error': {
                    'code': 'INVALID_CONTENT_TYPE',
                    'message': 'Content-Type must be application/json',
                    'status': 415
                }
            }), 415

        try:
            data = request.get_json()
            
            # SECURITY: Strict field extraction with type validation
            required_fields = ['business_type', 'sqft_m2', 'operating_hours_weekly', 
                             'num_refrigeration_units', 'location']
            
            missing_fields = [f for f in required_fields if f not in data]
            if missing_fields:
                return jsonify({
                    'error': {
                        'code': 'MISSING_REQUIRED_FIELDS',
                        'message': f'Missing required fields: {", ".join(missing_fields)}',
                        'status': 400
                    }
                }), 400

            business_type = str(data['business_type']).strip().lower()
            location = str(data['location']).strip()

            # SECURITY: Validate numeric types before conversion
            try:
                sqft_m2 = float(data['sqft_m2'])
                operating_hours_weekly = float(data['operating_hours_weekly'])
                num_refrigeration_units = int(data['num_refrigeration_units'])
            except (ValueError, TypeError) as e:
                return jsonify({
                    'error': {
                        'code': 'INVALID_FIELD_TYPE',
                        'message': f'Invalid numeric field type: {str(e)}',
                        'status': 400
                    }
                }), 400

            # SECURITY: Range validation on numeric inputs
            if sqft_m2 <= 0 or sqft_m2 > 10000:
                return jsonify({
                    'error': {
                        'code': 'INVALID_FIELD_VALUE',
                        'message': 'sqft_m2 must be between 0 and 10000',
                        'status': 400
                    }
                }), 400

            if operating_hours_weekly <= 0 or operating_hours_weekly > 168:
                return jsonify({
                    'error': {
                        'code': 'INVALID_FIELD_VALUE',
                        'message': 'operating_hours_weekly must be between 0 and 168',
                        'status': 400
                    }
                }), 400

            if num_refrigeration_units < 0 or num_refrigeration_units > 500:
                return jsonify({
                    'error': {
                        'code': 'INVALID_FIELD_VALUE',
                        'message': 'num_refrigeration_units must be between 0 and 500',
                        'status': 400
                    }
                }), 400

            # Optional parameters with strict type checking
            num_workers = 5  # Default
            if 'num_workers' in data:
                _raw_workers = data['num_workers']
                if not isinstance(_raw_workers, int) or isinstance(_raw_workers, bool):
                    return jsonify({
                        'error': {
                            'code': 'INVALID_FIELD_TYPE',
                            'message': 'num_workers must be an integer',
                            'status': 400
                        }
                    }), 400
                num_workers = int(_raw_workers)
                if num_workers <= 0:
                    return jsonify({
                        'error': {
                            'code': 'INVALID_FIELD_VALUE',
                            'message': 'num_workers must be greater than 0',
                            'status': 400
                        }
                    }), 400
                if num_workers > 1000:
                    return jsonify({
                        'error': {
                            'code': 'INVALID_FIELD_VALUE',
                            'message': 'num_workers must not exceed 1000',
                            'status': 400
                        }
                    }), 400

            months_per_year = 12  # Default
            if 'months_per_year' in data:
                _raw_months = data['months_per_year']
                if not isinstance(_raw_months, int) or isinstance(_raw_months, bool):
                    return jsonify({
                        'error': {
                            'code': 'INVALID_FIELD_TYPE',
                            'message': 'months_per_year must be an integer',
                            'status': 400
                        }
                    }), 400
                months_per_year = int(_raw_months)
                if months_per_year <= 0 or months_per_year > 12:
                    months_per_year = 12  # Default fallback

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
            
            # ========================================================================
            # BASE LOAD: Direct formula calibrated for African SMEs
            # CBECS model is trained on large US commercial buildings and cannot
            # reliably extrapolate to sub-500sqm African shops. We use a direct
            # formula instead: base lighting/HVAC/misc load from floor area and hours.
            #
            # Calibration basis:
            #   - African SME base load (non-refrigeration): ~3-5 kWh/sqm/month
            #   - Operating hours scale linearly (84 hrs/wk = full business hours)
            #   - Reference: 84 hrs/wk standard business hours baseline
            # ========================================================================
            HOURS_REFERENCE = 84.0          # hrs/week = standard 12hrs/day 7 days
            BASE_KWH_PER_SQM_MONTH = 10.0    # lighting + fans + misc for African SME

            hours_factor = operating_hours_weekly / HOURS_REFERENCE
            base_monthly_kwh = sqft_m2 * BASE_KWH_PER_SQM_MONTH * hours_factor
            base_annual_kwh = base_monthly_kwh * 12

            # ========================================================================
            # REFRIGERATION ADJUSTMENT: Marginal delta above CBECS baseline
            # The CBECS model (Food Sales pba=11) already includes a baseline
            # refrigeration load for a typical food business (~5 units average).
            # We only add/subtract the DELTA vs that baseline.
            # Climate factor applied ONCE to the combined total only.
            # African SME realistic marginal load: ~120 kWh/month per unit
            # ========================================================================
            CBECS_BASELINE_UNITS = 0        # CBECS Food Sales average refrigeration units
            UNIT_MARGINAL_KWH_MONTHLY = 250  # kWh/month per unit above/below baseline

            unit_delta = num_refrigeration_units - CBECS_BASELINE_UNITS
            refrigeration_adjustment_annual = unit_delta * UNIT_MARGINAL_KWH_MONTHLY * 12

            # Apply climate factor ONCE to the combined total
            total_annual_kwh = (base_annual_kwh + refrigeration_adjustment_annual) * climate_factor
            monthly_kwh = total_annual_kwh / 12

            # Breakdown for response
            refrigeration_kwh = max(0.0, (refrigeration_adjustment_annual * climate_factor) / 12)
            other_kwh = (base_annual_kwh * climate_factor) / 12

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

            # Log the calculation for debugging
            logger.info(f"Consumption calculation:")
            logger.info(f"  Base annual (model): {base_annual_kwh:,.0f} kWh")
            logger.info(f"  Refrigeration adjustment annual: {refrigeration_adjustment_annual:,.0f} kWh")
            logger.info(f"  Climate factor: {climate_factor}")
            logger.info(f"  Total monthly: {monthly_kwh:,.2f} kWh")
            logger.info(f"  Breakdown - Refrigeration: {refrigeration_kwh:,.2f} kWh, Other: {other_kwh:,.2f} kWh")

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
                    'estimated_cold_rooms': 0,
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

    @app.route("/")
    def home():
        return jsonify({"message": "ENERGY CONSUMPTION API running"}), 200

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