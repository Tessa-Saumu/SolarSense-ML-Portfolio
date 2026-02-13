"""
Pytest configuration and shared fixtures for solar_climatology_api tests.

This file ensures proper path setup for imports when running tests
from the project root and provides reusable fixtures.
"""

import sys
from pathlib import Path
from typing import Any, Dict, Generator
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask
from flask.testing import FlaskClient

# Ensure the models/solar_generation directory is in the Python path
# This allows imports to work when running from project root
_test_dir = Path(__file__).parent
_module_dir = _test_dir.parent
if str(_module_dir) not in sys.path:
    sys.path.insert(0, str(_module_dir))

from solar_climatology_api import create_app


@pytest.fixture
def test_api_key() -> str:
    """Test API key for authentication."""
    return "test_api_key_12345"


@pytest.fixture
def app(test_api_key: str) -> Flask:
    """
    Create and configure a Flask app instance for testing.
    
    Uses the factory pattern with test-specific configuration:
    - Custom API key for testing
    - Testing mode enabled (reduces logging noise)
    """
    config = {
        "api_key": test_api_key,
        "testing": True,
    }
    app = create_app(config)
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create a test client for the Flask app."""
    return app.test_client()


@pytest.fixture
def valid_payload() -> Dict[str, Any]:
    """Valid sample payload for predict-generation endpoint."""
    return {
        "latitude": -1.2921,  # Nairobi
        "longitude": 36.8219,
        "include_lifetime": True,
    }


@pytest.fixture
def valid_payload_single_month() -> Dict[str, Any]:
    """Valid payload with a specific month."""
    return {
        "latitude": -4.0435,  # Mombasa
        "longitude": 39.6682,
        "month": 6,
        "include_lifetime": False,
    }


@pytest.fixture
def mock_model_artifacts() -> Generator[Dict[str, Any], None, None]:
    """
    Mock model artifacts (model, feature_cols, metadata).
    
    This fixture patches load_model_artifacts to return predictable test data.
    """
    mock_model = MagicMock()
    mock_model.predict.return_value = [5.5]  # Mock prediction value
    
    mock_feature_cols = [
        "latitude",
        "longitude",
        "abs_latitude",
        "month",
        "is_dry_season",
    ]
    
    mock_metadata = {
        "model_type": "XGBoost climatological regression",
        "created_at_utc": "2026-02-10T19:18:41Z",
        "validation_mape": 0.0746,
        "training_locations": ["Nairobi", "Mombasa", "Kampala"],
        "feature_columns": mock_feature_cols,
    }
    
    with patch("solar_climatology_api.load_model_artifacts") as mock_load:
        mock_load.return_value = (mock_model, mock_feature_cols, mock_metadata)
        yield {
            "model": mock_model,
            "feature_cols": mock_feature_cols,
            "metadata": mock_metadata,
        }


@pytest.fixture
def mock_predict_solar_generation() -> Generator[MagicMock, None, None]:
    """Mock predict_solar_generation function."""
    with patch("solar_climatology_api.predict_solar_generation") as mock_predict:
        mock_predict.return_value = 5.5  # Mock daily kWh
        yield mock_predict


@pytest.fixture
def mock_predict_lifetime_generation() -> Generator[Dict[str, Any], None, None]:
    """Mock predict_lifetime_generation function."""
    mock_lifetime = {
        "year_1_generation_kwh": 2007.5,
        "lifetime_total_kwh": 45000.0,
        "lifetime_average_annual_kwh": 1800.0,
        "yearly_breakdown": [
            {
                "year": 1,
                "generation_kwh": 2007.5,
                "efficiency_pct": 100.0,
                "confidence_low_kwh": 1806.75,
                "confidence_high_kwh": 2208.25,
                "confidence_band_pct": 10.0,
            }
        ],
        "assumptions": {
            "panel_area_m2": 10.0,
            "panel_efficiency_pct": 20.0,
            "lifetime_years": 25,
            "annual_degradation_pct": 0.7,
            "dry_months": [1, 2, 6, 7, 8, 12],
        },
        "confidence": {
            "year_1_band_pct": 10.0,
            "years_1_5_band_pct": 10.0,
            "years_6_15_band_pct": 15.0,
            "years_16_25_band_pct": 20.0,
        },
        "monthly_generation_climatology": [
            {"month": 1, "daily_kwh": 5.5, "is_dry_season": True}
        ],
    }
    
    with patch("solar_climatology_api.predict_lifetime_generation") as mock_lifetime_func:
        mock_lifetime_func.return_value = mock_lifetime
        yield mock_lifetime


@pytest.fixture
def mock_validate_coordinates() -> Generator[MagicMock, None, None]:
    """Mock validate_coordinates function."""
    with patch("solar_climatology_api.validate_coordinates") as mock_validate:
        mock_validate.return_value = {"status": "valid", "warnings": []}
        yield mock_validate


