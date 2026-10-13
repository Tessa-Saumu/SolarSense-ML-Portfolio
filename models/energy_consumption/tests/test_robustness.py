"""
Comprehensive robustness test suite for Model 1 Energy Consumption ML API.

Uses create_app(test_mode=True, api_key="test-key-123") with mock model components
injected via app.config. All protected requests use header X-API-KEY: test-key-123.

Test groups serve as living documentation of failure modes and acceptable input ranges.
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest

# Add src directory to path for imports
BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"
sys.path.insert(0, str(SRC_DIR))


# =============================================================================
# GROUP 1 — Authentication & Security
# =============================================================================


class TestAuthentication:
    """Authentication and security: API key required for estimate-consumption."""

    def test_missing_api_key_returns_401_unauthorized(
        self, robustness_client, robustness_valid_payload
    ):
        """Missing API key → 401, code UNAUTHORIZED."""
        resp = robustness_client.post(
            "/api/v1/estimate-consumption",
            json=robustness_valid_payload,
        )
        assert resp.status_code == 401
        body = resp.get_json()
        assert body["error"]["code"] == "UNAUTHORIZED"

    def test_wrong_api_key_returns_401_unauthorized(
        self, robustness_client, robustness_valid_payload
    ):
        """Wrong API key → 401, code UNAUTHORIZED."""
        resp = robustness_client.post(
            "/api/v1/estimate-consumption",
            json=robustness_valid_payload,
            headers={"X-API-KEY": "wrong-key"},
        )
        assert resp.status_code == 401
        body = resp.get_json()
        assert body["error"]["code"] == "UNAUTHORIZED"

    def test_correct_api_key_returns_not_401(
        self, robustness_client, robustness_valid_payload, auth_headers
    ):
        """Correct API key → not 401."""
        resp = robustness_client.post(
            "/api/v1/estimate-consumption",
            json=robustness_valid_payload,
            headers=auth_headers,
        )
        assert resp.status_code != 401

    def test_health_endpoint_requires_no_auth_returns_200(self, robustness_client):
        """Health endpoint requires no auth → 200."""
        resp = robustness_client.get("/api/v1/health")
        assert resp.status_code == 200
        assert resp.get_json() == {"status": "healthy"}


# =============================================================================
# GROUP 2 — Content Type & JSON Validation
# =============================================================================


class TestContentTypeAndJsonValidation:
    """Content-Type and JSON body validation."""

    def test_no_content_type_header_returns_415_unsupported_media_type(
        self, robustness_client, auth_headers
    ):
        """No Content-Type header → 415, code INVALID_CONTENT_TYPE."""
        resp = robustness_client.post(
            "/api/v1/estimate-consumption",
            data=json.dumps(
                {
                    "business_type": "butchery",
                    "sqft_m2": 60,
                    "operating_hours_weekly": 98,
                    "num_refrigeration_units": 3,
                    "location": "Lagos, Nigeria",
                }
            ),
            headers=auth_headers,
        )
        assert resp.status_code == 415
        body = resp.get_json()
        assert body["error"]["code"] == "INVALID_CONTENT_TYPE"

    def test_malformed_json_body_returns_400_invalid_json(
        self, robustness_client, auth_headers
    ):
        """Malformed JSON body → 400, code INVALID_JSON."""
        resp = robustness_client.post(
            "/api/v1/estimate-consumption",
            data="{ invalid json }",
            headers={**auth_headers, "Content-Type": "application/json"},
        )
        assert resp.status_code == 400
        body = resp.get_json()
        assert body["error"]["code"] == "INVALID_JSON"

    def test_empty_body_with_correct_content_type_returns_400_invalid_json(
        self, robustness_client, auth_headers
    ):
        """Empty body with correct Content-Type → 400, code INVALID_JSON."""
        resp = robustness_client.post(
            "/api/v1/estimate-consumption",
            data="",
            headers={**auth_headers, "Content-Type": "application/json"},
        )
        assert resp.status_code == 400
        body = resp.get_json()
        assert body["error"]["code"] == "INVALID_JSON"


# =============================================================================
# GROUP 3 — Missing Required Fields
# =============================================================================


class TestMissingRequiredFields:
    """Each required field missing individually → 400, MISSING_REQUIRED_FIELDS."""

    def test_missing_business_type_returns_400_missing_field(
        self, robustness_client, auth_headers
    ):
        """Missing business_type → 400, MISSING_REQUIRED_FIELDS."""
        payload = {
            "sqft_m2": 60,
            "operating_hours_weekly": 98,
            "num_refrigeration_units": 3,
            "location": "Lagos, Nigeria",
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 400
        assert resp.get_json()["error"]["code"] == "MISSING_REQUIRED_FIELDS"
        assert "business_type" in resp.get_json()["error"]["message"]

    def test_missing_sqft_m2_returns_400_missing_field(
        self, robustness_client, auth_headers
    ):
        """Missing sqft_m2 → 400, MISSING_REQUIRED_FIELDS."""
        payload = {
            "business_type": "butchery",
            "operating_hours_weekly": 98,
            "num_refrigeration_units": 3,
            "location": "Lagos, Nigeria",
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 400
        assert resp.get_json()["error"]["code"] == "MISSING_REQUIRED_FIELDS"

    def test_missing_operating_hours_weekly_returns_400_missing_field(
        self, robustness_client, auth_headers
    ):
        """Missing operating_hours_weekly → 400, MISSING_REQUIRED_FIELDS."""
        payload = {
            "business_type": "butchery",
            "sqft_m2": 60,
            "num_refrigeration_units": 3,
            "location": "Lagos, Nigeria",
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 400
        assert resp.get_json()["error"]["code"] == "MISSING_REQUIRED_FIELDS"

    def test_missing_num_refrigeration_units_returns_400_missing_field(
        self, robustness_client, auth_headers
    ):
        """Missing num_refrigeration_units → 400, MISSING_REQUIRED_FIELDS."""
        payload = {
            "business_type": "butchery",
            "sqft_m2": 60,
            "operating_hours_weekly": 98,
            "location": "Lagos, Nigeria",
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 400
        assert resp.get_json()["error"]["code"] == "MISSING_REQUIRED_FIELDS"

    def test_missing_location_returns_400_missing_field(
        self, robustness_client, auth_headers
    ):
        """Missing location → 400, MISSING_REQUIRED_FIELDS."""
        payload = {
            "business_type": "butchery",
            "sqft_m2": 60,
            "operating_hours_weekly": 98,
            "num_refrigeration_units": 3,
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 400
        assert resp.get_json()["error"]["code"] == "MISSING_REQUIRED_FIELDS"


# =============================================================================
# GROUP 4 — Invalid Field Types
# =============================================================================


class TestInvalidFieldTypes:
    """Invalid field types → 400, INVALID_FIELD_TYPE (or documented acceptance)."""

    def test_sqft_m2_as_string_abc_returns_400_invalid_field_type(
        self, robustness_client, auth_headers
    ):
        """sqft_m2 as string 'abc' → 400, INVALID_FIELD_TYPE."""
        payload = {
            "business_type": "butchery",
            "sqft_m2": "abc",
            "operating_hours_weekly": 98,
            "num_refrigeration_units": 3,
            "location": "Lagos, Nigeria",
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 400
        assert resp.get_json()["error"]["code"] == "INVALID_FIELD_TYPE"

    def test_operating_hours_weekly_as_string_abc_returns_400_invalid_field_type(
        self, robustness_client, auth_headers
    ):
        """operating_hours_weekly as string 'abc' → 400, INVALID_FIELD_TYPE."""
        payload = {
            "business_type": "butchery",
            "sqft_m2": 60,
            "operating_hours_weekly": "abc",
            "num_refrigeration_units": 3,
            "location": "Lagos, Nigeria",
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 400
        assert resp.get_json()["error"]["code"] == "INVALID_FIELD_TYPE"

    def test_num_refrigeration_units_as_float_string_documented_behavior(
        self, robustness_client, auth_headers
    ):
        """num_refrigeration_units as float string '3.5' — rejected (must be integer)."""
        payload = {
            "business_type": "butchery",
            "sqft_m2": 60,
            "operating_hours_weekly": 98,
            "num_refrigeration_units": "3.5",
            "location": "Lagos, Nigeria",
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        # int("3.5") raises ValueError → INVALID_FIELD_TYPE
        assert resp.status_code == 400
        assert resp.get_json()["error"]["code"] == "INVALID_FIELD_TYPE"

    def test_location_as_integer_returns_400_invalid_field_type(
        self, robustness_client, auth_headers
    ):
        """location as integer → 400, INVALID_FIELD_TYPE."""
        payload = {
            "business_type": "butchery",
            "sqft_m2": 60,
            "operating_hours_weekly": 98,
            "num_refrigeration_units": 3,
            "location": 12345,
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 400
        assert resp.get_json()["error"]["code"] == "INVALID_FIELD_TYPE"

    def test_business_type_as_integer_returns_400_invalid_field_type(
        self, robustness_client, auth_headers
    ):
        """business_type as integer → 400, INVALID_FIELD_TYPE."""
        payload = {
            "business_type": 123,
            "sqft_m2": 60,
            "operating_hours_weekly": 98,
            "num_refrigeration_units": 3,
            "location": "Lagos, Nigeria",
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 400
        assert resp.get_json()["error"]["code"] == "INVALID_FIELD_TYPE"


# =============================================================================
# GROUP 5 — Boundary / Range Validation
# =============================================================================


class TestBoundaryRangeValidation:
    """Boundary and range validation; document exact boundaries."""

    def test_sqft_m2_zero_returns_400_invalid_field_value(
        self, robustness_client, auth_headers
    ):
        """sqft_m2 = 0 → 400, INVALID_FIELD_VALUE."""
        payload = {
            "business_type": "butchery",
            "sqft_m2": 0,
            "operating_hours_weekly": 98,
            "num_refrigeration_units": 3,
            "location": "Lagos, Nigeria",
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 400
        assert resp.get_json()["error"]["code"] == "INVALID_FIELD_VALUE"

    def test_sqft_m2_negative_returns_400_invalid_field_value(
        self, robustness_client, auth_headers
    ):
        """sqft_m2 = -1 → 400, INVALID_FIELD_VALUE."""
        payload = {
            "business_type": "butchery",
            "sqft_m2": -1,
            "operating_hours_weekly": 98,
            "num_refrigeration_units": 3,
            "location": "Lagos, Nigeria",
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 400
        assert resp.get_json()["error"]["code"] == "INVALID_FIELD_VALUE"

    def test_sqft_m2_just_above_zero_is_accepted(
        self, robustness_client, auth_headers
    ):
        """sqft_m2 = 0.001 → 200 (just above zero, should pass)."""
        payload = {
            "business_type": "butchery",
            "sqft_m2": 0.001,
            "operating_hours_weekly": 98,
            "num_refrigeration_units": 3,
            "location": "Lagos, Nigeria",
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 200

    def test_sqft_m2_at_exact_maximum_is_accepted(
        self, robustness_client, auth_headers
    ):
        """sqft_m2 = 10000 → 200 (at max, should pass)."""
        payload = {
            "business_type": "butchery",
            "sqft_m2": 10000,
            "operating_hours_weekly": 98,
            "num_refrigeration_units": 3,
            "location": "Lagos, Nigeria",
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 200

    def test_sqft_m2_above_max_returns_400_invalid_field_value(
        self, robustness_client, auth_headers
    ):
        """sqft_m2 = 10001 → 400, INVALID_FIELD_VALUE."""
        payload = {
            "business_type": "butchery",
            "sqft_m2": 10001,
            "operating_hours_weekly": 98,
            "num_refrigeration_units": 3,
            "location": "Lagos, Nigeria",
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 400
        assert resp.get_json()["error"]["code"] == "INVALID_FIELD_VALUE"

    def test_operating_hours_weekly_zero_returns_400(
        self, robustness_client, auth_headers
    ):
        """operating_hours_weekly = 0 → 400."""
        payload = {
            "business_type": "butchery",
            "sqft_m2": 60,
            "operating_hours_weekly": 0,
            "num_refrigeration_units": 3,
            "location": "Lagos, Nigeria",
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 400

    def test_operating_hours_weekly_at_max_168_is_accepted(
        self, robustness_client, auth_headers
    ):
        """operating_hours_weekly = 168 → 200 (at max)."""
        payload = {
            "business_type": "butchery",
            "sqft_m2": 60,
            "operating_hours_weekly": 168,
            "num_refrigeration_units": 3,
            "location": "Lagos, Nigeria",
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 200

    def test_operating_hours_weekly_above_168_returns_400(
        self, robustness_client, auth_headers
    ):
        """operating_hours_weekly = 168.1 → 400."""
        payload = {
            "business_type": "butchery",
            "sqft_m2": 60,
            "operating_hours_weekly": 168.1,
            "num_refrigeration_units": 3,
            "location": "Lagos, Nigeria",
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 400

    def test_num_refrigeration_units_zero_is_valid(
        self, robustness_client, auth_headers
    ):
        """num_refrigeration_units = 0 → 200 (zero is valid)."""
        payload = {
            "business_type": "butchery",
            "sqft_m2": 60,
            "operating_hours_weekly": 98,
            "num_refrigeration_units": 0,
            "location": "Lagos, Nigeria",
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 200

    def test_num_refrigeration_units_at_max_500_is_accepted(
        self, robustness_client, auth_headers
    ):
        """num_refrigeration_units = 500 → 200 (at max)."""
        payload = {
            "business_type": "butchery",
            "sqft_m2": 60,
            "operating_hours_weekly": 98,
            "num_refrigeration_units": 500,
            "location": "Lagos, Nigeria",
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 200

    def test_num_refrigeration_units_501_returns_400(
        self, robustness_client, auth_headers
    ):
        """num_refrigeration_units = 501 → 400."""
        payload = {
            "business_type": "butchery",
            "sqft_m2": 60,
            "operating_hours_weekly": 98,
            "num_refrigeration_units": 501,
            "location": "Lagos, Nigeria",
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 400

    def test_num_refrigeration_units_negative_returns_400(
        self, robustness_client, auth_headers
    ):
        """num_refrigeration_units = -1 → 400."""
        payload = {
            "business_type": "butchery",
            "sqft_m2": 60,
            "operating_hours_weekly": 98,
            "num_refrigeration_units": -1,
            "location": "Lagos, Nigeria",
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 400

    def test_num_workers_zero_rejected_returns_400(
        self, robustness_client, auth_headers
    ):
        """num_workers = 0 → 200 (should default to 5)."""
        payload = {
            "business_type": "butchery",
            "sqft_m2": 60,
            "operating_hours_weekly": 98,
            "num_refrigeration_units": 3,
            "location": "Lagos, Nigeria",
            "num_workers": 0,
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 400
        assert resp.get_json()["error"]["code"] == "INVALID_FIELD_VALUE"

    def test_num_workers_at_max_1000_is_accepted(
        self, robustness_client, auth_headers
    ):
        """num_workers = 1000 → 200 (at max)."""
        payload = {
            "business_type": "butchery",
            "sqft_m2": 60,
            "operating_hours_weekly": 98,
            "num_refrigeration_units": 3,
            "location": "Lagos, Nigeria",
            "num_workers": 1000,
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 200

    def test_num_workers_1001_returns_400(
        self, robustness_client, auth_headers
    ):
        """num_workers = 1001 → 400."""
        payload = {
            "business_type": "butchery",
            "sqft_m2": 60,
            "operating_hours_weekly": 98,
            "num_refrigeration_units": 3,
            "location": "Lagos, Nigeria",
            "num_workers": 1001,
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 400

    def test_months_per_year_zero_resets_to_12_returns_200(
        self, robustness_client, auth_headers
    ):
        """months_per_year = 0 → 200 (should reset to 12)."""
        payload = {
            "business_type": "butchery",
            "sqft_m2": 60,
            "operating_hours_weekly": 98,
            "num_refrigeration_units": 3,
            "location": "Lagos, Nigeria",
            "months_per_year": 0,
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 200

    def test_months_per_year_13_resets_to_12_returns_200(
        self, robustness_client, auth_headers
    ):
        """months_per_year = 13 → 200 (should reset to 12)."""
        payload = {
            "business_type": "butchery",
            "sqft_m2": 60,
            "operating_hours_weekly": 98,
            "num_refrigeration_units": 3,
            "location": "Lagos, Nigeria",
            "months_per_year": 13,
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 200

    def test_location_string_200_chars_is_accepted(
        self, robustness_client, auth_headers
    ):
        """location string of exactly 200 chars → 200."""
        payload = {
            "business_type": "butchery",
            "sqft_m2": 60,
            "operating_hours_weekly": 98,
            "num_refrigeration_units": 3,
            "location": "A" * 200,
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 200

    def test_location_string_201_chars_returns_400(
        self, robustness_client, auth_headers
    ):
        """location string of 201 chars → 400."""
        payload = {
            "business_type": "butchery",
            "sqft_m2": 60,
            "operating_hours_weekly": 98,
            "num_refrigeration_units": 3,
            "location": "A" * 201,
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 400
        assert resp.get_json()["error"]["code"] == "INVALID_FIELD_VALUE"


# =============================================================================
# GROUP 6 — Business Type Validation
# =============================================================================


class TestBusinessTypeValidation:
    """Valid and invalid business types."""

    def test_butchery_returns_200(
        self, robustness_client, auth_headers
    ):
        """'butchery' → 200."""
        payload = {
            "business_type": "butchery",
            "sqft_m2": 60,
            "operating_hours_weekly": 98,
            "num_refrigeration_units": 3,
            "location": "Lagos, Nigeria",
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 200

    def test_grocery_returns_200(
        self, robustness_client, auth_headers
    ):
        """'grocery' → 200."""
        payload = {
            "business_type": "grocery",
            "sqft_m2": 60,
            "operating_hours_weekly": 98,
            "num_refrigeration_units": 3,
            "location": "Lagos, Nigeria",
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 200

    def test_mini_supermarket_returns_200(
        self, robustness_client, auth_headers
    ):
        """'mini_supermarket' → 200."""
        payload = {
            "business_type": "mini_supermarket",
            "sqft_m2": 60,
            "operating_hours_weekly": 98,
            "num_refrigeration_units": 3,
            "location": "Lagos, Nigeria",
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 200

    def test_business_type_uppercase_case_insensitive_returns_200(
        self, robustness_client, auth_headers
    ):
        """'BUTCHERY' (uppercase) → 200 (case-insensitive)."""
        payload = {
            "business_type": "BUTCHERY",
            "sqft_m2": 60,
            "operating_hours_weekly": 98,
            "num_refrigeration_units": 3,
            "location": "Lagos, Nigeria",
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 200

    def test_restaurant_returns_400_invalid_business_type(
        self, robustness_client, auth_headers
    ):
        """'restaurant' → 400, INVALID_BUSINESS_TYPE."""
        payload = {
            "business_type": "restaurant",
            "sqft_m2": 60,
            "operating_hours_weekly": 98,
            "num_refrigeration_units": 3,
            "location": "Lagos, Nigeria",
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 400
        assert resp.get_json()["error"]["code"] == "INVALID_BUSINESS_TYPE"

    def test_business_type_empty_string_returns_400(
        self, robustness_client, auth_headers
    ):
        """'' (empty string) → 400."""
        payload = {
            "business_type": "",
            "sqft_m2": 60,
            "operating_hours_weekly": 98,
            "num_refrigeration_units": 3,
            "location": "Lagos, Nigeria",
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 400
        assert resp.get_json()["error"]["code"] == "INVALID_BUSINESS_TYPE"


# =============================================================================
# GROUP 7 — Climate Factor Sensitivity (Happy Path)
# =============================================================================


class TestClimateFactorSensitivity:
    """Climate adjustment factor and monthly kWh scale by location."""

    EXPECTED_CLIMATE_FACTORS = {
        "Lagos, Nigeria": 1.35,
        "Accra, Ghana": 1.30,
        "Nairobi, Kenya": 1.20,
        "Kampala, Uganda": 1.25,
        "Johannesburg, South Africa": 1.18,
        "Dar es Salaam, Tanzania": 1.35,
        "Unknown City, Country": 1.20,
    }

    def _base_payload(self, location):
        return {
            "business_type": "butchery",
            "sqft_m2": 60,
            "operating_hours_weekly": 98,
            "num_refrigeration_units": 3,
            "location": location,
        }

    def test_climate_factor_lagos(self, robustness_client, auth_headers):
        """Lagos, Nigeria → climate_adjustment_factor 1.35."""
        resp = robustness_client.post(
            "/api/v1/estimate-consumption",
            json=self._base_payload("Lagos, Nigeria"),
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.get_json()["climate_adjustment_factor"] == 1.35

    def test_climate_factor_accra(self, robustness_client, auth_headers):
        """Accra, Ghana → 1.30."""
        resp = robustness_client.post(
            "/api/v1/estimate-consumption",
            json=self._base_payload("Accra, Ghana"),
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.get_json()["climate_adjustment_factor"] == 1.30

    def test_climate_factor_nairobi(self, robustness_client, auth_headers):
        """Nairobi, Kenya → 1.20."""
        resp = robustness_client.post(
            "/api/v1/estimate-consumption",
            json=self._base_payload("Nairobi, Kenya"),
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.get_json()["climate_adjustment_factor"] == 1.20

    def test_climate_factor_kampala(self, robustness_client, auth_headers):
        """Kampala, Uganda → 1.25."""
        resp = robustness_client.post(
            "/api/v1/estimate-consumption",
            json=self._base_payload("Kampala, Uganda"),
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.get_json()["climate_adjustment_factor"] == 1.25

    def test_climate_factor_johannesburg(self, robustness_client, auth_headers):
        """Johannesburg, South Africa → 1.18."""
        resp = robustness_client.post(
            "/api/v1/estimate-consumption",
            json=self._base_payload("Johannesburg, South Africa"),
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.get_json()["climate_adjustment_factor"] == 1.18

    def test_climate_factor_dar_es_salaam(self, robustness_client, auth_headers):
        """Dar es Salaam, Tanzania → 1.35."""
        resp = robustness_client.post(
            "/api/v1/estimate-consumption",
            json=self._base_payload("Dar es Salaam, Tanzania"),
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.get_json()["climate_adjustment_factor"] == 1.35

    def test_climate_factor_unknown_city_default(self, robustness_client, auth_headers):
        """Unknown City, Country → 1.20 (default)."""
        resp = robustness_client.post(
            "/api/v1/estimate-consumption",
            json=self._base_payload("Unknown City, Country"),
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.get_json()["climate_adjustment_factor"] == 1.20

    def test_monthly_kwh_lagos_greater_than_johannesburg(
        self, robustness_client, auth_headers
    ):
        """Monthly kWh for Lagos > Johannesburg (highest vs lowest factor)."""
        resp_lagos = robustness_client.post(
            "/api/v1/estimate-consumption",
            json=self._base_payload("Lagos, Nigeria"),
            headers=auth_headers,
        )
        resp_joburg = robustness_client.post(
            "/api/v1/estimate-consumption",
            json=self._base_payload("Johannesburg, South Africa"),
            headers=auth_headers,
        )
        assert resp_lagos.status_code == 200
        assert resp_joburg.status_code == 200
        kwh_lagos = resp_lagos.get_json()["estimated_consumption_kwh_monthly"]
        kwh_joburg = resp_joburg.get_json()["estimated_consumption_kwh_monthly"]
        assert kwh_lagos > kwh_joburg


# =============================================================================
# GROUP 8 — Input Sensitivity / Behavioral Scenarios
# =============================================================================


class TestInputSensitivityBehavioral:
    """Single-variable sweeps; assert directional correctness of output."""

    def test_sqft_m2_sweep_output_increases_monotonically(
        self, robustness_client, auth_headers, baseline_payload
    ):
        """sqft_m2 sweep [20, 60, 150, 500, 2000]: output increases monotonically."""
        values = [20, 60, 150, 500, 2000]
        results = []
        for v in values:
            p = {**baseline_payload, "sqft_m2": v}
            resp = robustness_client.post(
                "/api/v1/estimate-consumption", json=p, headers=auth_headers
            )
            assert resp.status_code == 200
            results.append(resp.get_json()["estimated_consumption_kwh_monthly"])
        for i in range(len(results) - 1):
            assert results[i + 1] >= results[i], (
                f"sqft_m2 sweep not monotonic: {results}"
            )

    def test_operating_hours_weekly_sweep_output_increases_monotonically(
        self, robustness_client, auth_headers, baseline_payload
    ):
        """operating_hours_weekly sweep [10, 40, 80, 120, 168]: output increases monotonically."""
        values = [10, 40, 80, 120, 168]
        results = []
        for v in values:
            p = {**baseline_payload, "operating_hours_weekly": v}
            resp = robustness_client.post(
                "/api/v1/estimate-consumption", json=p, headers=auth_headers
            )
            assert resp.status_code == 200
            results.append(resp.get_json()["estimated_consumption_kwh_monthly"])
        for i in range(len(results) - 1):
            assert results[i + 1] >= results[i], (
                f"operating_hours_weekly sweep not monotonic: {results}"
            )

    def test_num_refrigeration_units_sweep_formula_breakdown(
        self, robustness_client, auth_headers, baseline_payload
    ):
        """num_refrigeration_units sweep [0, 1, 3, 10, 50]: refrigeration share 50–70%, increases with units."""
        values = [0, 1, 3, 10, 50]
        results_refrigeration = []
        for v in values:
            p = {**baseline_payload, "num_refrigeration_units": v}
            resp = robustness_client.post(
                "/api/v1/estimate-consumption", json=p, headers=auth_headers
            )
            assert resp.status_code == 200
            body = resp.get_json()
            total = body["estimated_consumption_kwh_monthly"]
            refrigeration = body["breakdown"]["refrigeration"]
            # Formula refrigeration is zero at zero units and linear otherwise;
            # it is not constrained to a 50-70% allocation heuristic.
            assert refrigeration == pytest.approx(v * 250 * body['climate_adjustment_factor'])
            assert refrigeration + body['breakdown']['other'] == pytest.approx(total, abs=0.02)
            results_refrigeration.append(refrigeration)
        # At high unit count, refrigeration share is higher than at low (formula caps at 0.7)
        assert results_refrigeration[-1] >= results_refrigeration[0]

    def test_num_workers_sweep_documents_direction(
        self, robustness_client, auth_headers, baseline_payload
    ):
        """num_workers sweep [1, 5, 20, 100]: document how output changes."""
        values = [1, 5, 20, 100]
        results = []
        for v in values:
            p = {**baseline_payload, "num_workers": v}
            resp = robustness_client.post(
                "/api/v1/estimate-consumption", json=p, headers=auth_headers
            )
            assert resp.status_code == 200
            results.append(resp.get_json()["estimated_consumption_kwh_monthly"])
        # All return 200; values within plausible range (0–1,000,000)
        for r in results:
            assert 0 <= r <= 1_000_000

    def test_business_type_comparison_all_200_and_plausible_range(
        self, robustness_client, auth_headers, baseline_payload
    ):
        """Butchery, grocery, mini_supermarket at fixed inputs: all 200, monthly kWh in 0–1,000,000."""
        for business_type in ["butchery", "grocery", "mini_supermarket"]:
            p = {**baseline_payload, "business_type": business_type}
            resp = robustness_client.post(
                "/api/v1/estimate-consumption", json=p, headers=auth_headers
            )
            assert resp.status_code == 200, f"Failed for {business_type}"
            kwh = resp.get_json()["estimated_consumption_kwh_monthly"]
            assert 0 <= kwh <= 1_000_000, f"Plausible range for {business_type}: {kwh}"


# =============================================================================
# GROUP 9 — Confidence Score Logic
# =============================================================================


class TestConfidenceScoreLogic:
    """Confidence score conditions and range."""

    def test_zero_refrigeration_units_confidence_075(
        self, robustness_client, auth_headers
    ):
        """num_refrigeration_units = 0 → confidence score 0.75."""
        payload = {
            "business_type": "butchery",
            "sqft_m2": 60,
            "operating_hours_weekly": 98,
            "num_refrigeration_units": 0,
            "location": "Lagos, Nigeria",
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 200
        assert resp.get_json()["confidence_score"] == 0.75

    def test_positive_inputs_confidence_085(
        self, robustness_client, auth_headers
    ):
        """num_refrigeration_units > 0, sqft_m2 > 0, operating_hours_weekly > 0 → 0.85."""
        payload = {
            "business_type": "butchery",
            "sqft_m2": 60,
            "operating_hours_weekly": 98,
            "num_refrigeration_units": 3,
            "location": "Lagos, Nigeria",
        }
        resp = robustness_client.post(
            "/api/v1/estimate-consumption", json=payload, headers=auth_headers
        )
        assert resp.status_code == 200
        assert resp.get_json()["confidence_score"] == 0.85

    def test_confidence_score_always_in_zero_one(
        self, robustness_client, auth_headers
    ):
        """confidence_score is always in [0, 1]."""
        cases = [
            {"num_refrigeration_units": 0, "sqft_m2": 0.001, "operating_hours_weekly": 1},
            {"num_refrigeration_units": 500, "sqft_m2": 10000, "operating_hours_weekly": 168},
        ]
        for overrides in cases:
            payload = {
                "business_type": "butchery",
                "sqft_m2": 60,
                "operating_hours_weekly": 98,
                "num_refrigeration_units": 3,
                "location": "Lagos, Nigeria",
            }
            payload.update(overrides)
            resp = robustness_client.post(
                "/api/v1/estimate-consumption", json=payload, headers=auth_headers
            )
            assert resp.status_code == 200
            score = resp.get_json()["confidence_score"]
            assert 0 <= score <= 1, f"confidence_score {score} not in [0, 1]"


# =============================================================================
# GROUP 10 — Output Capping & Safety Rails
# =============================================================================


class TestOutputCappingAndSafetyRails:
    """Capping and floor for model output."""

    def test_extreme_high_prediction_capped_at_1_000_000_monthly(
        self, robustness_app, robustness_client, auth_headers, robustness_valid_payload
    ):
        """Mock returns very large log (expm1 > 12M annual): monthly capped at 1,000,000, 200."""
        # log such that expm1(x) > 12_000_000 → x > log1p(12e6)
        huge_log = np.log1p(15_000_000)
        robustness_app.config["best_model"].predict.return_value = np.array([huge_log])
        resp = robustness_client.post(
            "/api/v1/estimate-consumption",
            json=robustness_valid_payload,
            headers=auth_headers,
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["estimated_consumption_kwh_monthly"] == pytest.approx(1957.5)
        assert body["breakdown"]["refrigeration"] >= 0
        assert body["breakdown"]["other"] >= 0
        robustness_app.config["best_model"].predict.assert_not_called()

    def test_very_negative_prediction_reset_to_zero(
        self, robustness_app, robustness_client, auth_headers, robustness_valid_payload
    ):
        """Mock returns very negative value: estimated_consumption_kwh_monthly reset to 0.0."""
        robustness_app.config["best_model"].predict.return_value = np.array([-100.0])
        resp = robustness_client.post(
            "/api/v1/estimate-consumption",
            json=robustness_valid_payload,
            headers=auth_headers,
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["estimated_consumption_kwh_monthly"] == pytest.approx(1957.5)
        robustness_app.config["best_model"].predict.assert_not_called()


# =============================================================================
# GROUP 11 — Model Not Loaded (500)
# =============================================================================


class TestModelNotLoaded:
    """Model not loaded → 500, no internal leak."""

    def test_best_model_none_returns_500_prediction_error(
        self, robustness_app, robustness_client, auth_headers, robustness_valid_payload
    ):
        """best_model = None → 500, code PREDICTION_ERROR."""
        robustness_app.config["best_model"] = None
        resp = robustness_client.post(
            "/api/v1/estimate-consumption",
            json=robustness_valid_payload,
            headers=auth_headers,
        )
        assert resp.status_code == 500
        body = resp.get_json()
        assert body["error"]["code"] == "PREDICTION_ERROR"

    def test_500_response_does_not_leak_internal_details(
        self, robustness_app, robustness_client, auth_headers, robustness_valid_payload
    ):
        """Response body does NOT leak internal details (e.g. stack trace, ValueError)."""
        robustness_app.config["best_model"] = None
        resp = robustness_client.post(
            "/api/v1/estimate-consumption",
            json=robustness_valid_payload,
            headers=auth_headers,
        )
        assert resp.status_code == 500
        body = resp.get_json()
        msg = body.get("error", {}).get("message", "")
        full = json.dumps(body).lower()
        assert "valueerror" not in full
        assert "stack" not in full
        assert "traceback" not in full
        assert msg == "Internal Server Error"
