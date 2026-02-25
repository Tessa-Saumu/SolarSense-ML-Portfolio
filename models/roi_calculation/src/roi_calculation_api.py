import os  # [SECURITY] Used to read API key from environment

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv  # [SECURITY] Load .env for API key and config

# [SECURITY] Load environment variables from .env file
load_dotenv()

# [SECURITY] Read API key from environment (not hardcoded)
API_KEY = os.getenv("API_KEY")

# Global limiter instance; app is attached in create_app / module init.
# [SECURITY] Rate limiting: 100 requests per minute per IP
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per minute"],
)

app = Flask(__name__)

# [SECURITY] Limit maximum request size to 100 KB
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024  # 100 KB

# Enable CORS for integration with frontends (can be restricted further if needed)
CORS(app)

# Attach limiter to the application
limiter.init_app(app)


def calculate_roi(system_cost_usd: float,
                  consumption_kwh: float,
                  generation_kwh: float,
                  tariff_per_kwh: float) -> dict:
    """
    Pure ROI calculation function.

    - Uses energy offset between consumption and generation.
    - Computes monthly and annual savings.
    - Returns ROI percentage and monthly savings.
    - No payback period calculation (explicitly descoped).
    """

    # Energy offset should not exceed either consumption or generation
    energy_offset_kwh = generation_kwh if generation_kwh <= consumption_kwh else consumption_kwh

    monthly_savings_usd = energy_offset_kwh * tariff_per_kwh
    annual_savings_usd = monthly_savings_usd * 12

    # Safe division: guard against zero or near‑zero annual savings
    if annual_savings_usd <= 0:
        roi_percentage = 0.0
    else:
        raw_roi = (annual_savings_usd / system_cost_usd) * 100

        # [SECURITY] Output realism: clamp ROI between 0 and 100%
        roi_percentage = max(0.0, min(raw_roi, 100.0))

    # [SECURITY] Ensure outputs are realistic / non-negative
    monthly_savings_usd = max(0.0, monthly_savings_usd)
    system_cost_usd = max(0.0, system_cost_usd)

    return {
        "monthly_savings_usd": round(monthly_savings_usd, 2),
        "roi_percentage": round(roi_percentage, 2),
        "system_cost_usd": round(system_cost_usd, 2),
    }


def _validate_float_field(data: dict,
                          field_name: str,
                          display_name: str,
                          min_value: float = 0.0,
                          strictly_positive: bool = True,
                          max_value: float | None = None):
    """Helper to validate numeric input fields with range checks."""
    if field_name not in data:
        return None, ({"error": f"Missing field: {field_name}"}, 400)

    _raw = data[field_name]
    if not isinstance(_raw, (int, float)) or isinstance(_raw, bool):
        return None, ({"error": f"{field_name} must be a number"}, 400)
    value = float(_raw)

    if strictly_positive:
        if value <= min_value:
            return None, ({
                "error":
                f"{field_name} must be greater than {min_value}"
            }, 400)
    else:
        if value < min_value:
            return None, ({
                "error":
                f"{field_name} must be greater than or equal to {min_value}"
            }, 400)

    if max_value is not None and value > max_value:
        return None, ({
            "error":
            f"{field_name} must be less than or equal to {max_value}"
        }, 400)

    return value, None


ALLOWED_BUSINESS_TYPE_CHARS = set(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 _-&/"
)


def _validate_optional_hours(data: dict, field_name: str):
    """
    [SECURITY] Validate optional hour-like fields (0–24).
    """
    if field_name not in data:
        return None, None
    _raw = data[field_name]
    if not isinstance(_raw, (int, float)) or isinstance(_raw, bool):
        return None, ({"error": f"{field_name} must be a number"}, 400)
    value = float(_raw)

    if value < 0 or value > 24:
        return None, ({
            "error":
            f"{field_name} must be between 0 and 24 hours"
        }, 400)
    return value, None


def _validate_optional_units(data: dict, field_name: str, max_units: int = 500):
    """
    [SECURITY] Validate optional 'units of equipment' style fields.
    Reject obviously wrong data (e.g., >500 units).
    """
    if field_name not in data:
        return None, None
    _raw = data[field_name]
    if not isinstance(_raw, int) or isinstance(_raw, bool):
        return None, ({"error": f"{field_name} must be an integer"}, 400)
    value = int(_raw)

    if value < 0 or value > max_units:
        return None, ({
            "error":
            f"{field_name} must be between 0 and {max_units}"
        }, 400)
    return value, None


def _validate_optional_string(data: dict, field_name: str, max_len: int = 64):
    """
    [SECURITY] Validate optional string fields such as business_type or location.
    Checks basic format and allowed characters.
    """
    if field_name not in data:
        return None, None

    value = data[field_name]

    if not isinstance(value, str):
        return None, ({"error": f"{field_name} must be a string"}, 400)

    value_stripped = value.strip()
    if not value_stripped:
        return None, ({"error": f"{field_name} cannot be empty"}, 400)

    if len(value_stripped) > max_len:
        return None, ({
            "error":
            f"{field_name} must be at most {max_len} characters"
        }, 400)

    if field_name == "business_type":
        # Restrict to a safe character set
        if not all(ch in ALLOWED_BUSINESS_TYPE_CHARS for ch in value_stripped):
            return None, ({
                "error":
                f"{field_name} contains invalid characters"
            }, 400)

    # For location we keep it simple: non-empty string with a reasonable max length.
    return value_stripped, None


@app.before_request
def require_api_key():
    """
    [SECURITY] Enforce API key authentication on the ROI API endpoints.

    - Requires header: X-API-KEY
    - Compares against API_KEY loaded from environment.
    """
    # Only protect the versioned API endpoints; allow "/" health check without key
    path = request.path or ""
    if path.startswith("/api/"):
        if not API_KEY:
            # Misconfiguration on the server – treat as 500 for callers
            return jsonify({"error": "Internal server error"}), 500

        header_key = request.headers.get("X-API-KEY")
        if not header_key or header_key != API_KEY:
            # [SECURITY] 401 Unauthorized for missing/invalid API key
            return jsonify({"error": "Unauthorized"}), 401


@app.route("/api/v1/calculate-roi", methods=["POST"])
@limiter.limit("100 per minute")
def roi_endpoint():
    """Model 3 ROI calculation endpoint."""
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400

    # Align field names with alignment_doc specification
    consumption_kwh, err = _validate_float_field(
        data,
        "consumption_kwh",
        "consumption_kwh",
        min_value=0.0,
        strictly_positive=True,
        max_value=100000.0,
    )
    if err:
        return jsonify(err[0]), err[1]

    generation_kwh, err = _validate_float_field(
        data,
        "generation_kwh",
        "generation_kwh",
        min_value=0.0,
        strictly_positive=True,
        max_value=100000.0,
    )
    if err:
        return jsonify(err[0]), err[1]

    tariff_per_kwh, err = _validate_float_field(
        data,
        "tariff_per_kwh",
        "tariff_per_kwh",
        min_value=0.0,
        strictly_positive=True,
        max_value=100.0,
    )
    if err:
        return jsonify(err[0]), err[1]

    system_cost_usd, err = _validate_float_field(
        data,
        "system_cost_usd",
        "system_cost_usd",
        min_value=0.0,
        strictly_positive=True,
        max_value=1_000_000.0,
    )
    if err:
        return jsonify(err[0]), err[1]

    # [SECURITY] Additional optional input validation (if these fields are provided)
    operating_hours, err = _validate_optional_hours(data, "operating_hours")
    if err:
        return jsonify(err[0]), err[1]

    equipment_units, err = _validate_optional_units(data, "equipment_units")
    if err:
        return jsonify(err[0]), err[1]

    business_type, err = _validate_optional_string(data, "business_type")
    if err:
        return jsonify(err[0]), err[1]

    location, err = _validate_optional_string(data, "location", max_len=128)
    if err:
        return jsonify(err[0]), err[1]

    try:
        result = calculate_roi(
            system_cost_usd=system_cost_usd,
            consumption_kwh=consumption_kwh,
            generation_kwh=generation_kwh,
            tariff_per_kwh=tariff_per_kwh,
        )
    except Exception:
        # [SECURITY] Generic 500 for unexpected server errors (no stack trace leakage)
        return jsonify({"error": "Internal server error"}), 500

    return jsonify(result), 200


@app.route("/api/v1/health")
def health():
    return jsonify({"status": "ok", "service": "roi-calculation"}), 200


@app.errorhandler(413)
def request_entity_too_large(e):
    return jsonify({"error": "Request payload too large"}), 413


@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"error": "Rate limit exceeded"}), 429


@app.errorhandler(500)
def internal_server_error(e):
    # Generic 500 handler to avoid exposing stack traces
    return jsonify({"error": "Internal server error"}), 500


def create_app(config_overrides: dict | None = None) -> Flask:
    """
    Application factory used for testing and deployment.

    This returns the module-level Flask app with optional config overrides.
    """

    if config_overrides:
        app.config.update(config_overrides)

    return app

if __name__ == "__main__":
    # Debug disabled by default for security; enable only during local development.
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
