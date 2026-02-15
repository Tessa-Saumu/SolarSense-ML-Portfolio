import logging
import os

from flask import Flask, request, jsonify
from flask_cors import CORS

from config import (
    ALLOWED_BUSINESS_TYPES,
    EQUIPMENT_POWER_WATTS,
    CLIMATE_ZONES,
    DEFAULT_CLIMATE_FACTOR,
    DAYS_PER_MONTH,
)
from estimator import estimate_energy_consumption
from validation import validate_request_payload, ValidationError


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    # Basic structured logging for observability
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("energy_consumption_api")

    @app.route("/api/v1/estimate-consumption", methods=["POST"])
    def estimate_consumption():
        try:
            payload = request.get_json(force=True, silent=False)
        except Exception:
            return (
                jsonify(
                    {
                        "error": {
                            "code": "INVALID_JSON",
                            "message": "Request body must be valid JSON",
                            "status": 400,
                        }
                    }
                ),
                400,
            )

        try:
            validated = validate_request_payload(payload)
        except ValidationError as ve:
            logger.warning(
                "validation_error",
                extra={
                    "code": ve.code,
                    "message": ve.message,
                },
            )
            return (
                jsonify(
                    {
                        "error": {
                            "code": ve.code,
                            "message": ve.message,
                            "status": 400,
                        }
                    }
                ),
                400,
            )

        result = estimate_energy_consumption(
            business_type=validated["business_type"],
            operating_hours=validated["operating_hours"],
            equipment=validated["equipment"],
            location=validated["location"],
        )

        logger.info(
            "estimate_consumption",
            extra={
                "business_type": validated["business_type"],
                "location": validated["location"],
                "estimated_kwh_monthly": result["estimated_consumption_kwh_monthly"],
                "confidence_score": result["confidence_score"],
            },
        )

        return jsonify(result), 200

    @app.route("/api/v1/health", methods=["GET"])
    def health():
        return jsonify({"status": "healthy"}), 200

    @app.route("/health", methods=["GET"])
    def legacy_health():
        # Simple non-versioned health check for convenience
        return jsonify({"status": "healthy"}), 200

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("MODEL1_PORT", "8001"))
    app.run(host="0.0.0.0", port=port, debug=True)


