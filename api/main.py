import os
import sys
from pathlib import Path

from flask import Flask, jsonify
from flask_cors import CORS

# Ensure repo root is on sys.path so model packages can be imported reliably
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


# Import the four model app factories
from models.energy_consumption.src.app_ml import create_app as create_energy_app  # noqa: E402
from models.solar_generation.src.solar_climatology_api import (  # noqa: E402
    create_app as create_solar_app,
)
from models.roi_calculation.src.roi_calculation_api import (  # noqa: E402
    create_app as create_roi_app,
)
from models.recommendations.model4_app import (  # noqa: E402
    create_app as create_recommendations_app,
)


class MultiModelDispatcher:
    """
    WSGI dispatcher that routes requests to the appropriate model app
    based on the request path, preserving all existing endpoint paths
    and per-model business / security logic.
    """

    def __init__(self, main_app, energy_app, solar_app, roi_app, recommendations_app):
        self.main_app = main_app
        self.energy_app = energy_app
        self.solar_app = solar_app
        self.roi_app = roi_app
        self.recommendations_app = recommendations_app

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "") or ""

        # Gateway routes (handled by main_app) - check these first
        if path == "/" or path == "/api/v1/health":
            return self.main_app(environ, start_response)

        # Model 1 — Energy Consumption
        if path.startswith("/api/v1/estimate-consumption"):
            return self.energy_app(environ, start_response)

        # Model 2 — Solar Generation
        if path.startswith("/api/v1/predict-generation") or path.startswith(
            "/api/v1/model-info"
        ):
            return self.solar_app(environ, start_response)

        # Model 3 — ROI Calculation
        if path.startswith("/api/v1/calculate-roi"):
            return self.roi_app(environ, start_response)

        # Model 4 — AI Recommendation Engine & Orchestration
        if path.startswith("/api/v1/analyze"):
            return self.recommendations_app(environ, start_response)

        # Fall back to the gateway app (for any other routes)
        return self.main_app(environ, start_response)


def create_app() -> Flask:
    """
    Gateway application factory that wires together all four model APIs.

    - Does NOT modify or duplicate per-model logic.
    - Preserves all existing endpoint paths.
    - Models 1-3 share the same API_KEY from environment variable.
    - Model 4 uses API_KEY + MODELS_BASE_URL from environment.
    """
    app = Flask(__name__)
    CORS(app)

    shared_api_key = os.getenv("API_KEY")

    energy_app = create_energy_app(api_key=shared_api_key) if shared_api_key else create_energy_app()
    solar_app = create_solar_app(config={"api_key": shared_api_key}) if shared_api_key else create_solar_app()
    roi_app = create_roi_app()
    recommendations_app = create_recommendations_app()

    @app.route("/", methods=["GET"])
    def root():
        return jsonify({"message": "SolarSense API running", "status": "ok"}), 200

    @app.route("/api/v1/health", methods=["GET"])
    def gateway_health():
        return jsonify({"status": "ok", "service": "gateway"}), 200

    app.wsgi_app = MultiModelDispatcher(
        app,
        energy_app,
        solar_app,
        roi_app,
        recommendations_app,
    )

    return app


# Default app object for gunicorn: `api.main:app`
app = create_app()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=False)