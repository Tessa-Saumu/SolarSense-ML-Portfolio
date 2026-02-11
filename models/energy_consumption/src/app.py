import os
import logging
from functools import wraps

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter                      # NEW: rate limiting
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv                         # NEW: load .env

from validation import validate_request
from estimator import estimate_consumption

# =====================================================
# LOAD ENVIRONMENT VARIABLES
# =====================================================
load_dotenv()  # NEW: loads variables from .env file

API_KEY = os.getenv("MODEL1_API_KEY")
PORT = int(os.getenv("MODEL1_PORT", 8001))

if not API_KEY:
    raise RuntimeError("MODEL1_API_KEY not set in environment")

# =====================================================
# APP SETUP
# =====================================================
app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)

# =====================================================
# RATE LIMITING (100 requests per minute)
# =====================================================
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["100 per minute"]   # NEW
)

# =====================================================
# API KEY AUTHENTICATION DECORATOR
# =====================================================
def require_api_key(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        key = request.headers.get("X-API-KEY")
        if not key or key != API_KEY:
            return jsonify({
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Invalid or missing API key",
                    "status": 401
                }
            }), 401
        return func(*args, **kwargs)
    return wrapper

# =====================================================
# ADDITIONAL INPUT RANGE VALIDATION
# =====================================================
def validate_ranges(data):
    equipment = data.get("equipment", [])

    for item in equipment:
        qty = item.get("quantity")
        hours = item.get("daily_operating_hours")

        if qty is None or hours is None:
            raise ValueError("Equipment quantity and hours are required")

        if qty < 0 or qty > 500:
            raise ValueError("Equipment quantity must be between 0 and 500")

        if hours < 0 or hours > 24:
            raise ValueError("daily_operating_hours must be between 0 and 24")

# =====================================================
# OUTPUT VALIDATION
# =====================================================
def validate_output(result):
    kwh = result.get("estimated_kwh")
    confidence = result.get("confidence_score")

    if kwh is None or kwh <= 0:
        raise ValueError("Invalid output: estimated_kwh must be positive")

    if confidence < 0 or confidence > 1:
        raise ValueError("Invalid output: confidence_score must be between 0 and 1")

# =====================================================
# HEALTH ENDPOINT
# =====================================================
@app.route("/api/v1/health")
def health():
    return jsonify({"status": "ok"})

# =====================================================
# MAIN ESTIMATION ENDPOINT (SECURED)
# =====================================================
@app.route("/api/v1/estimate-consumption", methods=["POST"])
@require_api_key                     # NEW: API key protection
@limiter.limit("100 per minute")     # NEW: per-endpoint limit
def estimate():
    try:
        data = request.get_json()

        if not data:
            raise ValueError("Request body must be JSON")

        # Existing validation
        validate_request(data)

        # NEW: numeric/range validation
        validate_ranges(data)

        # Run model
        result = estimate_consumption(data)

        # NEW: output sanity check
        validate_output(result)

        logging.info(
            f"ESTIMATION_SUCCESS business={data.get('business_type')} "
            f"location={data.get('location')} "
            f"kwh={result['estimated_kwh']} "
            f"confidence={result['confidence_score']}"
        )

        return jsonify(result), 200

    except ValueError as e:
        logging.error(f"VALIDATION_ERROR {str(e)}")
        return jsonify({
            "error": {
                "code": "INVALID_INPUT",
                "message": str(e),
                "status": 400
            }
        }), 400

    except Exception:
        logging.exception("SERVER_ERROR")
        return jsonify({
            "error": {
                "code": "SERVER_ERROR",
                "message": "Internal Server Error",
                "status": 500
            }
        }), 500

# =====================================================
# START SERVER
# =====================================================
if __name__ == "__main__":
    app.run(port=PORT)
