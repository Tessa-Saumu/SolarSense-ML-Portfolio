"""
Comprehensive test suite for the ML-based Energy Consumption API (app_ml.py).

Tests cover:
- All endpoints (health, estimate-consumption)
- Successful predictions
- Input validation (missing fields, invalid types, invalid values)
- Error handling (malformed JSON, model failures)
- Edge cases (large values, boundary conditions)
- Response schema validation
"""

import json
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
def app():
    """Create Flask app instance for testing with auth disabled."""
    from app_ml import create_app
    # SECURITY: Disable auth and rate limiting for testing
    return create_app(test_mode=True, disable_auth=True, api_key="test-key")


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def mock_model_components():
    """Create mock model components for testing."""
    # Mock model
    mock_model = MagicMock()
    mock_model.predict.return_value = np.array([12000.0])  # Annual kWh prediction
    
    # Mock scaler
    mock_scaler = MagicMock()
    mock_scaler.transform.return_value = np.array([[0.5] * 17])  # 17 features
    
    # Mock label encoders
    # Avoid importing sklearn in tests; keep mocks lightweight and deterministic
    mock_le_pba = MagicMock()
    mock_le_pba.transform.return_value = np.array([0])
    
    mock_le_cendiv = MagicMock()
    mock_le_cendiv.transform.return_value = np.array([0])
    
    mock_le_size = MagicMock()
    mock_le_size.transform.return_value = np.array([0])
    
    return {
        'model': mock_model,
        'scaler': mock_scaler,
        'le_pba': mock_le_pba,
        'le_cendiv': mock_le_cendiv,
        'le_size': mock_le_size,
        'use_log_target': False
    }


@pytest.fixture
def valid_payload():
    """Valid request payload for ML API."""
    return {
        "business_type": "butchery",
        "sqft_m2": 60.0,
        "operating_hours_weekly": 98.0,  # 14 hours/day * 7 days
        "num_refrigeration_units": 3,
        "location": "Lagos, Nigeria",
        "num_workers": 3,
        "months_per_year": 12
    }


@pytest.fixture
def app_with_auth():
    """Create Flask app instance with authentication enabled for testing."""
    from app_ml import create_app
    return create_app(test_mode=True, disable_auth=False, api_key="test-api-key-123")


@pytest.fixture
def client_with_auth(app_with_auth):
    """Create test client with auth headers."""
    client = app_with_auth.test_client()
    # Add API key header to all requests
    client.environ_base['HTTP_X_API_KEY'] = 'test-api-key-123'
    return client


@pytest.fixture
def app_with_mocked_model(app, mock_model_components):
    """App instance with mocked model components."""
    app.config['best_model'] = mock_model_components['model']
    app.config['scaler'] = mock_model_components['scaler']
    app.config['use_log_target'] = mock_model_components['use_log_target']
    app.config['le_pba'] = mock_model_components['le_pba']
    app.config['le_cendiv'] = mock_model_components['le_cendiv']
    app.config['le_size'] = mock_model_components['le_size']
    app.config['feature_columns'] = [f'feature_{i}' for i in range(17)]
    app.config['sme_mappings'] = {}
    return app


# ============================================================================
# Health Endpoint Tests
# ============================================================================

def test_health_endpoint(client):
    """Test health check endpoint returns 200 with correct response."""
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body == {"status": "healthy"}


def test_health_endpoint_method_not_allowed(client):
    """Test health endpoint rejects POST requests."""
    resp = client.post("/api/v1/health")
    assert resp.status_code == 405  # Method Not Allowed


# ============================================================================
# Successful Prediction Tests
# ============================================================================

def test_estimate_consumption_success(client, app_with_mocked_model, valid_payload):
    """Test successful prediction with valid payload."""
    client = app_with_mocked_model.test_client()
    
    resp = client.post("/api/v1/estimate-consumption", json=valid_payload)
    
    assert resp.status_code == 200
    body = resp.get_json()
    
    # Verify response schema
    assert "estimated_consumption_kwh_monthly" in body
    assert "confidence_score" in body
    assert "breakdown" in body
    assert "climate_adjustment_factor" in body
    assert "equipment_summary" in body
    
    # Verify types
    assert isinstance(body["estimated_consumption_kwh_monthly"], (int, float))
    assert isinstance(body["confidence_score"], (int, float))
    assert isinstance(body["breakdown"], dict)
    assert isinstance(body["climate_adjustment_factor"], (int, float))
    assert isinstance(body["equipment_summary"], dict)
    
    # Verify breakdown structure
    assert "refrigeration" in body["breakdown"]
    assert "other" in body["breakdown"]
    
    # Verify equipment summary
    assert "total_refrigeration_units" in body["equipment_summary"]
    assert body["equipment_summary"]["total_refrigeration_units"] == 3
    
    # Verify logical consistency
    total = body["estimated_consumption_kwh_monthly"]
    refrigeration = body["breakdown"]["refrigeration"]
    other = body["breakdown"]["other"]
    
    assert total > 0
    assert refrigeration >= 0
    assert other >= 0
    assert abs((refrigeration + other) - total) < 0.01  # Allow floating point error
    
    # Refrigeration should be 50-70% of total for food retail
    if total > 0:
        refrigeration_share = refrigeration / total
        assert 0.5 <= refrigeration_share <= 0.7


def test_estimate_consumption_all_business_types(client, app_with_mocked_model):
    """Test all valid business types."""
    base_payload = {
        "sqft_m2": 100.0,
        "operating_hours_weekly": 84.0,
        "num_refrigeration_units": 5,
        "location": "Nairobi, Kenya"
    }
    
    for business_type in ["butchery", "grocery", "mini_supermarket"]:
        payload = {**base_payload, "business_type": business_type}
        resp = client.post("/api/v1/estimate-consumption", json=payload)
        assert resp.status_code == 200, f"Failed for business_type: {business_type}"


def test_estimate_consumption_all_climate_zones(client, app_with_mocked_model):
    """Test all supported climate zones."""
    base_payload = {
        "business_type": "grocery",
        "sqft_m2": 100.0,
        "operating_hours_weekly": 84.0,
        "num_refrigeration_units": 5
    }
    
    climate_cities = [
        "Lagos, Nigeria",  # 1.35
        "Accra, Ghana",  # 1.30
        "Nairobi, Kenya",  # 1.20
        "Kampala, Uganda",  # 1.25
        "Johannesburg, South Africa",  # 1.18
        "Dar es Salaam, Tanzania",  # 1.35
        "Unknown City, Country"  # 1.20 default
    ]
    
    for location in climate_cities:
        payload = {**base_payload, "location": location}
        resp = client.post("/api/v1/estimate-consumption", json=payload)
        assert resp.status_code == 200, f"Failed for location: {location}"
        body = resp.get_json()
        assert "climate_adjustment_factor" in body
        assert 1.18 <= body["climate_adjustment_factor"] <= 1.35


def test_estimate_consumption_optional_fields_defaults(client, app_with_mocked_model):
    """Test that optional fields use correct defaults."""
    payload = {
        "business_type": "butchery",
        "sqft_m2": 60.0,
        "operating_hours_weekly": 98.0,
        "num_refrigeration_units": 3,
        "location": "Lagos, Nigeria"
        # num_workers and months_per_year omitted
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["estimated_consumption_kwh_monthly"] > 0


# ============================================================================
# Input Validation Tests - Missing Fields
# ============================================================================

def test_estimate_consumption_missing_business_type(client, app_with_mocked_model):
    """Test missing business_type field."""
    payload = {
        "sqft_m2": 60.0,
        "operating_hours_weekly": 98.0,
        "num_refrigeration_units": 3,
        "location": "Lagos, Nigeria"
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 400
    body = resp.get_json()
    assert "error" in body
    assert body["error"]["code"] == "MISSING_FIELD"
    assert "business_type" in body["error"]["message"]


def test_estimate_consumption_missing_sqft_m2(client, app_with_mocked_model):
    """Test missing sqft_m2 field."""
    payload = {
        "business_type": "butchery",
        "operating_hours_weekly": 98.0,
        "num_refrigeration_units": 3,
        "location": "Lagos, Nigeria"
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["error"]["code"] == "MISSING_FIELD"
    assert "sqft_m2" in body["error"]["message"]


def test_estimate_consumption_missing_operating_hours(client, app_with_mocked_model):
    """Test missing operating_hours_weekly field."""
    payload = {
        "business_type": "butchery",
        "sqft_m2": 60.0,
        "num_refrigeration_units": 3,
        "location": "Lagos, Nigeria"
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 400
    assert resp.get_json()["error"]["code"] == "MISSING_FIELD"


def test_estimate_consumption_missing_refrigeration_units(client, app_with_mocked_model):
    """Test missing num_refrigeration_units field."""
    payload = {
        "business_type": "butchery",
        "sqft_m2": 60.0,
        "operating_hours_weekly": 98.0,
        "location": "Lagos, Nigeria"
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 400
    assert resp.get_json()["error"]["code"] == "MISSING_FIELD"


def test_estimate_consumption_missing_location(client, app_with_mocked_model):
    """Test missing location field."""
    payload = {
        "business_type": "butchery",
        "sqft_m2": 60.0,
        "operating_hours_weekly": 98.0,
        "num_refrigeration_units": 3
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 400
    assert resp.get_json()["error"]["code"] == "MISSING_FIELD"


# ============================================================================
# Input Validation Tests - Invalid Business Type
# ============================================================================

def test_estimate_consumption_invalid_business_type(client, app_with_mocked_model):
    """Test invalid business_type value."""
    payload = {
        "business_type": "invalid_type",
        "sqft_m2": 60.0,
        "operating_hours_weekly": 98.0,
        "num_refrigeration_units": 3,
        "location": "Lagos, Nigeria"
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["error"]["code"] == "INVALID_BUSINESS_TYPE"


def test_estimate_consumption_business_type_case_insensitive(client, app_with_mocked_model):
    """Test business_type is case-insensitive."""
    for case in ["BUTCHERY", "Butchery", "bUtChErY", "butchery"]:
        payload = {
            "business_type": case,
            "sqft_m2": 60.0,
            "operating_hours_weekly": 98.0,
            "num_refrigeration_units": 3,
            "location": "Lagos, Nigeria"
        }
        resp = client.post("/api/v1/estimate-consumption", json=payload)
        assert resp.status_code == 200, f"Failed for case: {case}"


# ============================================================================
# Input Validation Tests - Invalid Numeric Values
# ============================================================================

def test_estimate_consumption_negative_sqft_m2(client, app_with_mocked_model):
    """Test negative sqft_m2 value."""
    payload = {
        "business_type": "butchery",
        "sqft_m2": -10.0,
        "operating_hours_weekly": 98.0,
        "num_refrigeration_units": 3,
        "location": "Lagos, Nigeria"
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["error"]["code"] == "INVALID_FIELD_VALUE"


def test_estimate_consumption_zero_sqft_m2(client, app_with_mocked_model):
    """Test zero sqft_m2 value."""
    payload = {
        "business_type": "butchery",
        "sqft_m2": 0.0,
        "operating_hours_weekly": 98.0,
        "num_refrigeration_units": 3,
        "location": "Lagos, Nigeria"
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 400
    assert resp.get_json()["error"]["code"] == "INVALID_FIELD_VALUE"


def test_estimate_consumption_negative_operating_hours(client, app_with_mocked_model):
    """Test negative operating_hours_weekly value."""
    payload = {
        "business_type": "butchery",
        "sqft_m2": 60.0,
        "operating_hours_weekly": -10.0,
        "num_refrigeration_units": 3,
        "location": "Lagos, Nigeria"
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 400
    assert resp.get_json()["error"]["code"] == "INVALID_FIELD_VALUE"


def test_estimate_consumption_excessive_operating_hours(client, app_with_mocked_model):
    """Test operating_hours_weekly > 168 (hours in a week)."""
    payload = {
        "business_type": "butchery",
        "sqft_m2": 60.0,
        "operating_hours_weekly": 200.0,
        "num_refrigeration_units": 3,
        "location": "Lagos, Nigeria"
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 400
    assert resp.get_json()["error"]["code"] == "INVALID_FIELD_VALUE"


def test_estimate_consumption_negative_refrigeration_units(client, app_with_mocked_model):
    """Test negative num_refrigeration_units value."""
    payload = {
        "business_type": "butchery",
        "sqft_m2": 60.0,
        "operating_hours_weekly": 98.0,
        "num_refrigeration_units": -1,
        "location": "Lagos, Nigeria"
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 400
    assert resp.get_json()["error"]["code"] == "INVALID_FIELD_VALUE"


def test_estimate_consumption_zero_refrigeration_units(client, app_with_mocked_model):
    """Test zero num_refrigeration_units (should be allowed but may affect confidence)."""
    payload = {
        "business_type": "butchery",
        "sqft_m2": 60.0,
        "operating_hours_weekly": 98.0,
        "num_refrigeration_units": 0,
        "location": "Lagos, Nigeria"
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    # Zero refrigeration units should be allowed (validation doesn't require > 0)
    assert resp.status_code == 200


# ============================================================================
# Input Validation Tests - Invalid Types
# ============================================================================

def test_estimate_consumption_non_numeric_sqft_m2(client, app_with_mocked_model):
    """Test non-numeric sqft_m2 value."""
    payload = {
        "business_type": "butchery",
        "sqft_m2": "not_a_number",
        "operating_hours_weekly": 98.0,
        "num_refrigeration_units": 3,
        "location": "Lagos, Nigeria"
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["error"]["code"] == "INVALID_FIELD_TYPE"


def test_estimate_consumption_non_numeric_operating_hours(client, app_with_mocked_model):
    """Test non-numeric operating_hours_weekly value."""
    payload = {
        "business_type": "butchery",
        "sqft_m2": 60.0,
        "operating_hours_weekly": "not_a_number",
        "num_refrigeration_units": 3,
        "location": "Lagos, Nigeria"
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 400
    assert resp.get_json()["error"]["code"] == "INVALID_FIELD_TYPE"


def test_estimate_consumption_non_integer_refrigeration_units(client, app_with_mocked_model):
    """Test non-integer num_refrigeration_units value."""
    payload = {
        "business_type": "butchery",
        "sqft_m2": 60.0,
        "operating_hours_weekly": 98.0,
        "num_refrigeration_units": "three",
        "location": "Lagos, Nigeria"
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 400
    assert resp.get_json()["error"]["code"] == "INVALID_FIELD_TYPE"


def test_estimate_consumption_non_string_business_type(client, app_with_mocked_model):
    """Test non-string business_type value."""
    payload = {
        "business_type": 123,
        "sqft_m2": 60.0,
        "operating_hours_weekly": 98.0,
        "num_refrigeration_units": 3,
        "location": "Lagos, Nigeria"
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 400
    assert resp.get_json()["error"]["code"] == "INVALID_FIELD_TYPE"


def test_estimate_consumption_non_string_location(client, app_with_mocked_model):
    """Test non-string location value."""
    payload = {
        "business_type": "butchery",
        "sqft_m2": 60.0,
        "operating_hours_weekly": 98.0,
        "num_refrigeration_units": 3,
        "location": 12345
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 400
    assert resp.get_json()["error"]["code"] == "INVALID_FIELD_TYPE"


# ============================================================================
# Malformed Request Tests
# ============================================================================

def test_estimate_consumption_empty_body(client, app_with_mocked_model):
    """Test empty request body."""
    resp = client.post(
        "/api/v1/estimate-consumption",
        data="",
        content_type="application/json"
    )
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["error"]["code"] == "INVALID_JSON"


def test_estimate_consumption_malformed_json(client, app_with_mocked_model):
    """Test malformed JSON in request body."""
    resp = client.post(
        "/api/v1/estimate-consumption",
        data="{invalid json}",
        content_type="application/json"
    )
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["error"]["code"] == "INVALID_JSON"


def test_estimate_consumption_not_json(client, app_with_mocked_model):
    """Test request with non-JSON content type."""
    resp = client.post(
        "/api/v1/estimate-consumption",
        data="not json",
        content_type="text/plain"
    )
    assert resp.status_code == 415
    body = resp.get_json()
    assert body["error"]["code"] == "UNSUPPORTED_MEDIA_TYPE"


def test_estimate_consumption_null_body(client, app_with_mocked_model):
    """Test null JSON body."""
    resp = client.post(
        "/api/v1/estimate-consumption",
        json=None,
        content_type="application/json"
    )
    assert resp.status_code == 400
    assert resp.get_json()["error"]["code"] == "INVALID_JSON"


# ============================================================================
# Unexpected Fields Tests
# ============================================================================

def test_estimate_consumption_extra_fields_ignored(client, app_with_mocked_model):
    """Test that extra fields in payload are ignored (should still work)."""
    payload = {
        "business_type": "butchery",
        "sqft_m2": 60.0,
        "operating_hours_weekly": 98.0,
        "num_refrigeration_units": 3,
        "location": "Lagos, Nigeria",
        "unexpected_field": "should be ignored",
        "another_field": 12345
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 200
    # Extra fields should not cause errors


# ============================================================================
# Edge Cases and Stress Tests
# ============================================================================

def test_estimate_consumption_very_large_sqft(client, app_with_mocked_model):
    """Test very large sqft_m2 value (stress test - at max allowed)."""
    payload = {
        "business_type": "mini_supermarket",
        "sqft_m2": 10000.0,  # Maximum allowed
        "operating_hours_weekly": 168.0,  # 24/7
        "num_refrigeration_units": 50,
        "location": "Lagos, Nigeria"
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["estimated_consumption_kwh_monthly"] > 0


def test_estimate_consumption_exceeds_max_sqft(client, app_with_mocked_model):
    """Test sqft_m2 exceeding maximum allowed value (SECURITY: input validation)."""
    payload = {
        "business_type": "mini_supermarket",
        "sqft_m2": 10001.0,  # Exceeds maximum
        "operating_hours_weekly": 168.0,
        "num_refrigeration_units": 50,
        "location": "Lagos, Nigeria"
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["error"]["code"] == "INVALID_FIELD_VALUE"
    assert "exceeds maximum" in body["error"]["message"].lower()


def test_estimate_consumption_very_small_sqft(client, app_with_mocked_model):
    """Test very small sqft_m2 value (edge case)."""
    payload = {
        "business_type": "butchery",
        "sqft_m2": 1.0,  # Very small space
        "operating_hours_weekly": 40.0,
        "num_refrigeration_units": 1,
        "location": "Nairobi, Kenya"
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["estimated_consumption_kwh_monthly"] > 0


def test_estimate_consumption_max_operating_hours(client, app_with_mocked_model):
    """Test maximum valid operating_hours_weekly (168 = 24/7)."""
    payload = {
        "business_type": "grocery",
        "sqft_m2": 100.0,
        "operating_hours_weekly": 168.0,  # Maximum
        "num_refrigeration_units": 5,
        "location": "Lagos, Nigeria"
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 200


def test_estimate_consumption_min_operating_hours(client, app_with_mocked_model):
    """Test minimum valid operating_hours_weekly (just above 0)."""
    payload = {
        "business_type": "butchery",
        "sqft_m2": 60.0,
        "operating_hours_weekly": 0.1,  # Very small
        "num_refrigeration_units": 1,
        "location": "Nairobi, Kenya"
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 200


def test_estimate_consumption_large_refrigeration_units(client, app_with_mocked_model):
    """Test large number of refrigeration units (at max allowed)."""
    payload = {
        "business_type": "mini_supermarket",
        "sqft_m2": 500.0,
        "operating_hours_weekly": 120.0,
        "num_refrigeration_units": 500,  # Maximum allowed
        "location": "Lagos, Nigeria"
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 200
    body = resp.get_json()
    # With many refrigeration units, refrigeration share should be high
    total = body["estimated_consumption_kwh_monthly"]
    refrigeration = body["breakdown"]["refrigeration"]
    if total > 0:
        assert refrigeration / total >= 0.5


def test_estimate_consumption_exceeds_max_refrigeration_units(client, app_with_mocked_model):
    """Test num_refrigeration_units exceeding maximum allowed (SECURITY: input validation)."""
    payload = {
        "business_type": "mini_supermarket",
        "sqft_m2": 500.0,
        "operating_hours_weekly": 120.0,
        "num_refrigeration_units": 501,  # Exceeds maximum
        "location": "Lagos, Nigeria"
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["error"]["code"] == "INVALID_FIELD_VALUE"
    assert "exceeds maximum" in body["error"]["message"].lower()


def test_estimate_consumption_exceeds_max_workers(client, app_with_mocked_model):
    """Test num_workers exceeding maximum allowed (SECURITY: input validation)."""
    payload = {
        "business_type": "mini_supermarket",
        "sqft_m2": 500.0,
        "operating_hours_weekly": 120.0,
        "num_refrigeration_units": 10,
        "location": "Lagos, Nigeria",
        "num_workers": 1001  # Exceeds maximum
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["error"]["code"] == "INVALID_FIELD_VALUE"
    assert "exceeds maximum" in body["error"]["message"].lower()


def test_estimate_consumption_location_too_long(client, app_with_mocked_model):
    """Test location string exceeding maximum length (SECURITY: input validation)."""
    payload = {
        "business_type": "butchery",
        "sqft_m2": 60.0,
        "operating_hours_weekly": 98.0,
        "num_refrigeration_units": 3,
        "location": "A" * 201  # Exceeds 200 character limit
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["error"]["code"] == "INVALID_FIELD_VALUE"
    assert "exceeds maximum length" in body["error"]["message"].lower()


def test_estimate_consumption_boundary_size_categories(client, app_with_mocked_model):
    """Test boundary values for size categories (small/medium/large)."""
    base_payload = {
        "business_type": "grocery",
        "operating_hours_weekly": 84.0,
        "num_refrigeration_units": 5,
        "location": "Nairobi, Kenya"
    }
    
    # Small: < 2000 sqft
    payload_small = {**base_payload, "sqft_m2": 185.0}  # ~1990 sqft
    resp = client.post("/api/v1/estimate-consumption", json=payload_small)
    assert resp.status_code == 200
    
    # Medium: 2000-10000 sqft
    payload_medium = {**base_payload, "sqft_m2": 930.0}  # ~10000 sqft
    resp = client.post("/api/v1/estimate-consumption", json=payload_medium)
    assert resp.status_code == 200
    
    # Large: > 10000 sqft
    payload_large = {**base_payload, "sqft_m2": 1000.0}  # ~10764 sqft
    resp = client.post("/api/v1/estimate-consumption", json=payload_large)
    assert resp.status_code == 200


# ============================================================================
# Model Failure Tests
# ============================================================================

def test_estimate_consumption_model_not_loaded(client, app):
    """Test behavior when model is not loaded (None)."""
    app.config['best_model'] = None
    app.config['scaler'] = None
    
    payload = {
        "business_type": "butchery",
        "sqft_m2": 60.0,
        "operating_hours_weekly": 98.0,
        "num_refrigeration_units": 3,
        "location": "Lagos, Nigeria"
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 500
    body = resp.get_json()
    assert body["error"]["code"] == "PREDICTION_ERROR"


def test_estimate_consumption_model_prediction_exception(client, app_with_mocked_model, mock_model_components):
    """Test when model.predict() raises an exception."""
    mock_model_components['model'].predict.side_effect = Exception("Model prediction failed")
    
    app_with_mocked_model.config['best_model'] = mock_model_components['model']
    client = app_with_mocked_model.test_client()
    
    payload = {
        "business_type": "butchery",
        "sqft_m2": 60.0,
        "operating_hours_weekly": 98.0,
        "num_refrigeration_units": 3,
        "location": "Lagos, Nigeria"
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 500
    body = resp.get_json()
    assert body["error"]["code"] == "PREDICTION_ERROR"


def test_estimate_consumption_scaler_transform_exception(client, app_with_mocked_model, mock_model_components):
    """Test when scaler.transform() raises an exception."""
    mock_model_components['scaler'].transform.side_effect = Exception("Scaler transform failed")
    
    app_with_mocked_model.config['scaler'] = mock_model_components['scaler']
    client = app_with_mocked_model.test_client()
    
    payload = {
        "business_type": "butchery",
        "sqft_m2": 60.0,
        "operating_hours_weekly": 98.0,
        "num_refrigeration_units": 3,
        "location": "Lagos, Nigeria"
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 500
    assert resp.get_json()["error"]["code"] == "PREDICTION_ERROR"


def test_estimate_consumption_encoder_transform_exception(client, app_with_mocked_model, mock_model_components):
    """Test when label encoder raises an exception."""
    mock_model_components['le_pba'].transform.side_effect = Exception("Encoder failed")
    
    app_with_mocked_model.config['le_pba'] = mock_model_components['le_pba']
    client = app_with_mocked_model.test_client()
    
    payload = {
        "business_type": "butchery",
        "sqft_m2": 60.0,
        "operating_hours_weekly": 98.0,
        "num_refrigeration_units": 3,
        "location": "Lagos, Nigeria"
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 500
    assert resp.get_json()["error"]["code"] == "PREDICTION_ERROR"


# ============================================================================
# Log-Transformed Target Tests
# ============================================================================

def test_estimate_consumption_log_transformed_target(client, app_with_mocked_model, mock_model_components):
    """Test prediction with log-transformed target model."""
    # Mock log-transformed prediction
    mock_model_components['model'].predict.return_value = np.array([8.0])  # log value
    mock_model_components['use_log_target'] = True
    
    app_with_mocked_model.config['best_model'] = mock_model_components['model']
    app_with_mocked_model.config['use_log_target'] = True
    client = app_with_mocked_model.test_client()
    
    payload = {
        "business_type": "butchery",
        "sqft_m2": 60.0,
        "operating_hours_weekly": 98.0,
        "num_refrigeration_units": 3,
        "location": "Lagos, Nigeria"
    }
    
    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["estimated_consumption_kwh_monthly"] > 0
    # Verify expm1 was applied (8.0 -> ~2980.96 annual, then /12 and climate factor)
    assert body["estimated_consumption_kwh_monthly"] > 200


# ============================================================================
# Response Schema Validation Tests
# ============================================================================

def test_response_schema_completeness(client, app_with_mocked_model, valid_payload):
    """Test that response contains all required fields with correct types."""
    client = app_with_mocked_model.test_client()
    resp = client.post("/api/v1/estimate-consumption", json=valid_payload)
    
    assert resp.status_code == 200
    body = resp.get_json()
    
    # Required top-level fields
    required_fields = [
        "estimated_consumption_kwh_monthly",
        "confidence_score",
        "breakdown",
        "climate_adjustment_factor",
        "equipment_summary"
    ]
    
    for field in required_fields:
        assert field in body, f"Missing required field: {field}"
    
    # Breakdown structure
    assert isinstance(body["breakdown"], dict)
    assert "refrigeration" in body["breakdown"]
    assert "other" in body["breakdown"]
    assert isinstance(body["breakdown"]["refrigeration"], (int, float))
    assert isinstance(body["breakdown"]["other"], (int, float))
    
    # Equipment summary structure
    assert isinstance(body["equipment_summary"], dict)
    assert "total_refrigeration_units" in body["equipment_summary"]
    assert isinstance(body["equipment_summary"]["total_refrigeration_units"], int)
    
    # Numeric fields should be numbers
    assert isinstance(body["estimated_consumption_kwh_monthly"], (int, float))
    assert isinstance(body["confidence_score"], (int, float))
    assert isinstance(body["climate_adjustment_factor"], (int, float))
    
    # Values should be positive
    assert body["estimated_consumption_kwh_monthly"] > 0
    assert 0 <= body["confidence_score"] <= 1
    assert body["climate_adjustment_factor"] > 0


def test_response_confidence_score_range(client, app_with_mocked_model):
    """Test confidence score is always in valid range [0, 1]."""
    test_cases = [
        {"sqft_m2": 60.0, "operating_hours_weekly": 98.0, "num_refrigeration_units": 3},
        {"sqft_m2": 0.1, "operating_hours_weekly": 0.1, "num_refrigeration_units": 0},
        {"sqft_m2": 10000.0, "operating_hours_weekly": 168.0, "num_refrigeration_units": 100}
    ]
    
    for case in test_cases:
        payload = {
            "business_type": "butchery",
            **case,
            "location": "Lagos, Nigeria"
        }
        resp = client.post("/api/v1/estimate-consumption", json=payload)
        assert resp.status_code == 200
        body = resp.get_json()
        assert 0 <= body["confidence_score"] <= 1


# ============================================================================
# Method Not Allowed Tests
# ============================================================================

def test_estimate_consumption_get_not_allowed(client, app_with_mocked_model):
    """Test GET method not allowed on estimate-consumption endpoint."""
    resp = client.get("/api/v1/estimate-consumption")
    assert resp.status_code == 405  # Method Not Allowed


def test_estimate_consumption_put_not_allowed(client, app_with_mocked_model):
    """Test PUT method not allowed on estimate-consumption endpoint."""
    resp = client.put("/api/v1/estimate-consumption", json={})
    assert resp.status_code == 405


def test_estimate_consumption_delete_not_allowed(client, app_with_mocked_model):
    """Test DELETE method not allowed on estimate-consumption endpoint."""
    resp = client.delete("/api/v1/estimate-consumption")
    assert resp.status_code == 405


# ============================================================================
# Deterministic Output Tests (with mocked model)
# ============================================================================

def test_estimate_consumption_deterministic_output(client, app_with_mocked_model, valid_payload):
    """Test that same input produces same output (with mocked model)."""
    client = app_with_mocked_model.test_client()
    
    resp1 = client.post("/api/v1/estimate-consumption", json=valid_payload)
    resp2 = client.post("/api/v1/estimate-consumption", json=valid_payload)
    
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    
    body1 = resp1.get_json()
    body2 = resp2.get_json()
    
    # With mocked model, outputs should be identical
    assert body1["estimated_consumption_kwh_monthly"] == body2["estimated_consumption_kwh_monthly"]
    assert body1["confidence_score"] == body2["confidence_score"]
    assert body1["climate_adjustment_factor"] == body2["climate_adjustment_factor"]


# ============================================================================
# Integration Tests
# ============================================================================

def test_multiple_requests_sequential(client, app_with_mocked_model):
    """Test handling multiple sequential requests."""
    payloads = [
        {
            "business_type": "butchery",
            "sqft_m2": 60.0,
            "operating_hours_weekly": 98.0,
            "num_refrigeration_units": 3,
            "location": "Lagos, Nigeria"
        },
        {
            "business_type": "grocery",
            "sqft_m2": 120.0,
            "operating_hours_weekly": 84.0,
            "num_refrigeration_units": 5,
            "location": "Nairobi, Kenya"
        },
        {
            "business_type": "mini_supermarket",
            "sqft_m2": 200.0,
            "operating_hours_weekly": 112.0,
            "num_refrigeration_units": 8,
            "location": "Accra, Ghana"
        }
    ]
    
    client = app_with_mocked_model.test_client()
    
    for payload in payloads:
        resp = client.post("/api/v1/estimate-consumption", json=payload)
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["estimated_consumption_kwh_monthly"] > 0

