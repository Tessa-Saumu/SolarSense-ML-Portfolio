"""
Shared pytest fixtures for Energy Consumption ML API tests.

Provides app created with create_app(test_mode=True, api_key="test-key-123")
and injected mock model components: log-space model (log1p(50000)), identity
scaler, label encoders returning [0], use_log_target=True.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest

# Add src directory to path for imports
BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

# Fixed log-space value: expm1(log1p(50000)) = 50000 annual kWh
LOG_PREDICTION_50K = np.log1p(50000)


@pytest.fixture
def mock_model_log():
    """Mock model that returns fixed log-space prediction (log1p(50000))."""
    mock = MagicMock()
    mock.predict.return_value = np.array([LOG_PREDICTION_50K])
    return mock


@pytest.fixture
def mock_scaler_identity():
    """Mock scaler that returns input unchanged."""
    mock = MagicMock()
    mock.transform.side_effect = lambda x: x
    return mock


@pytest.fixture
def mock_label_encoders():
    """Mock label encoders that return [0] for any input."""
    le = MagicMock()
    le.transform.return_value = np.array([0])
    return {"le_pba": le, "le_cendiv": le, "le_size": le}


@pytest.fixture
def robustness_app(mock_model_log, mock_scaler_identity, mock_label_encoders):
    """
    Flask app for robustness tests: test_mode=True, api_key='test-key-123',
    with injected mocks (log-space model, identity scaler, label encoders).
    """
    from app_ml import create_app

    app = create_app(test_mode=True, api_key="test-key-123")
    app.config["best_model"] = mock_model_log
    app.config["scaler"] = mock_scaler_identity
    app.config["use_log_target"] = True
    app.config["feature_columns"] = [f"feature_{i}" for i in range(17)]
    app.config["sme_mappings"] = {}
    app.config["le_pba"] = mock_label_encoders["le_pba"]
    app.config["le_cendiv"] = mock_label_encoders["le_cendiv"]
    app.config["le_size"] = mock_label_encoders["le_size"]
    return app


@pytest.fixture
def robustness_client(robustness_app):
    """Test client for robustness_app. Use auth_headers for protected endpoints."""
    return robustness_app.test_client()


# Header for all protected requests (estimate-consumption)
AUTH_HEADERS = {"X-API-KEY": "test-key-123"}


@pytest.fixture
def auth_headers():
    return AUTH_HEADERS.copy()


@pytest.fixture
def robustness_valid_payload():
    """Minimal valid payload for estimate-consumption."""
    return {
        "business_type": "butchery",
        "sqft_m2": 60.0,
        "operating_hours_weekly": 98.0,
        "num_refrigeration_units": 3,
        "location": "Lagos, Nigeria",
    }


@pytest.fixture
def baseline_payload():
    """Realistic baseline for sensitivity tests: butchery, 60 m², 98h/week, 3 fridges, Lagos, 3 workers."""
    return {
        "business_type": "butchery",
        "sqft_m2": 60.0,
        "operating_hours_weekly": 98.0,
        "num_refrigeration_units": 3,
        "location": "Lagos, Nigeria",
        "num_workers": 3,
        "months_per_year": 12,
    }
