from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Global limiter instance; app is attached in create_app / module init.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per minute"],
)

app = Flask(__name__)

# Security: limit maximum request size to 100 KB
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
    energy_offset_kwh = min(consumption_kwh, generation_kwh)

    monthly_savings_usd = energy_offset_kwh * tariff_per_kwh
    annual_savings_usd = monthly_savings_usd * 12

    # Safe division: guard against zero or near‑zero annual savings
    if annual_savings_usd <= 0:
        roi_percentage = 0.0
    else:
        roi_percentage = (annual_savings_usd / system_cost_usd) * 100

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

    try:
        value = float(data[field_name])
    except (TypeError, ValueError):
        return None, ({"error": f"{field_name} must be a number"}, 400)

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

    try:
        result = calculate_roi(
            system_cost_usd=system_cost_usd,
            consumption_kwh=consumption_kwh,
            generation_kwh=generation_kwh,
            tariff_per_kwh=tariff_per_kwh,
        )
    except Exception:
        # Generic 500 for unexpected server errors (no stack trace leakage)
        return jsonify({"error": "Internal server error"}), 500

    return jsonify(result), 200


@app.route("/")
def home():
    return jsonify({"message": "Model 3 ROI API running"}), 200


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
    app.run(host="0.0.0.0", port=5000, debug=False)
