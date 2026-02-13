"""
Security-specific tests for the ML-based Energy Consumption API.

Tests cover:
- API Key Authentication
- Rate Limiting (if testable)
- Enhanced Input Validation
- Output Validation
- Error Handling (hiding internal details)
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock
import pytest
import numpy as np
from flask.testing import FlaskClient

# Add src directory to path for imports
BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"
sys.path.insert(0, str(SRC_DIR))


@pytest.fixture
def app_with_auth():
    """Create Flask app instance with authentication enabled for testing."""
    from app_ml import create_app
    return create_app(test_mode=True, disable_auth=False, api_key="test-api-key-123")


@pytest.fixture
def valid_payload():
    """Valid request payload for ML API."""
    return {
        "business_type": "butchery",
        "sqft_m2": 60.0,
        "operating_hours_weekly": 98.0,
        "num_refrigeration_units": 3,
        "location": "Lagos, Nigeria",
        "num_workers": 3,
        "months_per_year": 12
    }


@pytest.fixture
def app_with_mocked_model_auth(app_with_auth):
    """App instance with mocked model components and auth enabled."""
    from unittest.mock import MagicMock
    import numpy as np
    
    mock_model = MagicMock()
    mock_model.predict.return_value = np.array([12000.0])
    mock_scaler = MagicMock()
    mock_scaler.transform.return_value = np.array([[0.5] * 17])
    mock_le_pba = MagicMock()
    mock_le_pba.transform.return_value = np.array([0])
    mock_le_cendiv = MagicMock()
    mock_le_cendiv.transform.return_value = np.array([0])
    mock_le_size = MagicMock()
    mock_le_size.transform.return_value = np.array([0])
    
    app_with_auth.config['best_model'] = mock_model
    app_with_auth.config['scaler'] = mock_scaler
    app_with_auth.config['use_log_target'] = False
    app_with_auth.config['le_pba'] = mock_le_pba
    app_with_auth.config['le_cendiv'] = mock_le_cendiv
    app_with_auth.config['le_size'] = mock_le_size
    app_with_auth.config['feature_columns'] = [f'feature_{i}' for i in range(17)]
    app_with_auth.config['sme_mappings'] = {}
    
    return app_with_auth


# ============================================================================
# SECURITY: API Key Authentication Tests
# ============================================================================

def test_estimate_consumption_missing_api_key(app_with_mocked_model_auth, valid_payload):
    """Test that request without API key is rejected (SECURITY: authentication)."""
    client = app_with_mocked_model_auth.test_client()
    
    resp = client.post("/api/v1/estimate-consumption", json=valid_payload)
    assert resp.status_code == 401
    body = resp.get_json()
    assert body["error"]["code"] == "UNAUTHORIZED"
    assert "API key" in body["error"]["message"]


def test_estimate_consumption_invalid_api_key(app_with_mocked_model_auth, valid_payload):
    """Test that request with invalid API key is rejected (SECURITY: authentication)."""
    client = app_with_mocked_model_auth.test_client()
    
    resp = client.post(
        "/api/v1/estimate-consumption",
        json=valid_payload,
        headers={"X-API-KEY": "wrong-key"}
    )
    assert resp.status_code == 401
    body = resp.get_json()
    assert body["error"]["code"] == "UNAUTHORIZED"


def test_estimate_consumption_valid_api_key(app_with_mocked_model_auth, valid_payload):
    """Test that request with valid API key is accepted (SECURITY: authentication)."""
    client = app_with_mocked_model_auth.test_client()
    
    resp = client.post(
        "/api/v1/estimate-consumption",
        json=valid_payload,
        headers={"X-API-KEY": "test-api-key-123"}
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert "estimated_consumption_kwh_monthly" in body


def test_health_endpoint_no_auth_required(app_with_auth):
    """Test that health endpoint doesn't require authentication."""
    client = app_with_auth.test_client()
    
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body == {"status": "healthy"}


# ============================================================================
# SECURITY: Enhanced Input Validation Tests
# ============================================================================

def test_exceeds_max_sqft_m2(app_with_mocked_model_auth, valid_payload):
    """Test sqft_m2 exceeding maximum allowed value (SECURITY: input validation)."""
    client = app_with_mocked_model_auth.test_client()
    
    payload = {**valid_payload, "sqft_m2": 10001.0}  # Exceeds maximum
    
    resp = client.post(
        "/api/v1/estimate-consumption",
        json=payload,
        headers={"X-API-KEY": "test-api-key-123"}
    )
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["error"]["code"] == "INVALID_FIELD_VALUE"
    assert "exceeds maximum" in body["error"]["message"].lower()


def test_exceeds_max_refrigeration_units(app_with_mocked_model_auth, valid_payload):
    """Test num_refrigeration_units exceeding maximum allowed (SECURITY: input validation)."""
    client = app_with_mocked_model_auth.test_client()
    
    payload = {**valid_payload, "num_refrigeration_units": 501}  # Exceeds maximum
    
    resp = client.post(
        "/api/v1/estimate-consumption",
        json=payload,
        headers={"X-API-KEY": "test-api-key-123"}
    )
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["error"]["code"] == "INVALID_FIELD_VALUE"
    assert "exceeds maximum" in body["error"]["message"].lower()


def test_exceeds_max_workers(app_with_mocked_model_auth, valid_payload):
    """Test num_workers exceeding maximum allowed (SECURITY: input validation)."""
    client = app_with_mocked_model_auth.test_client()
    
    payload = {**valid_payload, "num_workers": 1001}  # Exceeds maximum
    
    resp = client.post(
        "/api/v1/estimate-consumption",
        json=payload,
        headers={"X-API-KEY": "test-api-key-123"}
    )
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["error"]["code"] == "INVALID_FIELD_VALUE"
    assert "exceeds maximum" in body["error"]["message"].lower()


def test_location_too_long(app_with_mocked_model_auth, valid_payload):
    """Test location string exceeding maximum length (SECURITY: input validation)."""
    client = app_with_mocked_model_auth.test_client()
    
    payload = {**valid_payload, "location": "A" * 201}  # Exceeds 200 character limit
    
    resp = client.post(
        "/api/v1/estimate-consumption",
        json=payload,
        headers={"X-API-KEY": "test-api-key-123"}
    )
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["error"]["code"] == "INVALID_FIELD_VALUE"
    assert "exceeds maximum length" in body["error"]["message"].lower()


# ============================================================================
# SECURITY: Output Validation Tests
# ============================================================================

def test_output_validation_positive_values(app_with_mocked_model_auth, valid_payload):
    """Test that output values are always positive (SECURITY: output validation)."""
    client = app_with_mocked_model_auth.test_client()
    
    resp = client.post(
        "/api/v1/estimate-consumption",
        json=valid_payload,
        headers={"X-API-KEY": "test-api-key-123"}
    )
    assert resp.status_code == 200
    body = resp.get_json()
    
    # All energy values must be non-negative
    assert body["estimated_consumption_kwh_monthly"] >= 0
    assert body["breakdown"]["refrigeration"] >= 0
    assert body["breakdown"]["other"] >= 0
    assert body["climate_adjustment_factor"] > 0
    assert 0 <= body["confidence_score"] <= 1


def test_output_validation_realistic_ranges(app_with_mocked_model_auth, valid_payload):
    """Test that output values are within realistic ranges (SECURITY: output validation)."""
    client = app_with_mocked_model_auth.test_client()
    
    resp = client.post(
        "/api/v1/estimate-consumption",
        json=valid_payload,
        headers={"X-API-KEY": "test-api-key-123"}
    )
    assert resp.status_code == 200
    body = resp.get_json()
    
    # Monthly kWh should be reasonable (not exceeding 1,000,000)
    assert body["estimated_consumption_kwh_monthly"] <= 1000000
    # Confidence score must be in [0, 1]
    assert 0 <= body["confidence_score"] <= 1
    # Climate factor should be reasonable (1.0 to 2.0)
    assert 1.0 <= body["climate_adjustment_factor"] <= 2.0


# ============================================================================
# SECURITY: Error Handling Tests
# ============================================================================

def test_error_hides_internal_details(app_with_mocked_model_auth, valid_payload):
    """Test that 500 errors hide internal stack traces (SECURITY: error handling)."""
    # Force an exception in model prediction
    mock_model = MagicMock()
    mock_model.predict.side_effect = Exception("Internal model error")
    
    app_with_mocked_model_auth.config['best_model'] = mock_model
    client = app_with_mocked_model_auth.test_client()
    
    resp = client.post(
        "/api/v1/estimate-consumption",
        json=valid_payload,
        headers={"X-API-KEY": "test-api-key-123"}
    )
    assert resp.status_code == 500
    body = resp.get_json()
    assert body["error"]["code"] == "PREDICTION_ERROR"
    # SECURITY: Should not expose internal error details
    assert body["error"]["message"] == "Internal Server Error"
    assert "Internal model error" not in body["error"]["message"]
    assert "stack trace" not in str(body).lower()





