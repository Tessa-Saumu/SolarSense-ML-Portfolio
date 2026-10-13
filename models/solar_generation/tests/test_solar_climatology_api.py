"""
Comprehensive test suite for solar_climatology_api Flask application.

This test suite covers:
- All endpoints (health, model-info, predict-generation)
- Successful responses (200-level)
- Client errors (400-level)
- Server errors (500-level via mocking)
- Malformed JSON
- Empty request bodies
- Missing required fields
- Invalid data types
- Invalid numeric ranges
- Unexpected extra fields
- Large but valid inputs (edge cases)
- Response schema validation
- Status code verification
- Logical consistency checks
"""

import json
from typing import Any, Dict
from unittest.mock import patch

import pytest
from flask.testing import FlaskClient


class TestHealthEndpoint:
    """Tests for GET /api/v1/health endpoint."""

    def test_health_success(
        self, client: FlaskClient, test_api_key: str, mock_model_artifacts: Dict[str, Any]
    ):
        """Test successful health check response."""
        response = client.get(
            "/api/v1/health",
            headers={"X-API-KEY": test_api_key},
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "ok"
        assert "model_type" in data
        assert "last_trained_at" in data
        assert "validation_mape" in data
        assert data["model_type"] == "XGBoost climatological regression"

    def test_health_missing_api_key(self, client: FlaskClient):
        """Test health endpoint without API key returns 401."""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 401
        data = response.get_json()
        assert data["status"] == "error"
        assert data["message"] == "Unauthorized"

    def test_health_invalid_api_key(self, client: FlaskClient, test_api_key: str):
        """Test health endpoint with invalid API key returns 401."""
        response = client.get(
            "/api/v1/health",
            headers={"X-API-KEY": "wrong_key"},
        )
        
        assert response.status_code == 401
        data = response.get_json()
        assert data["status"] == "error"
        assert data["message"] == "Unauthorized"

    def test_health_file_not_found_error(
        self, client: FlaskClient, test_api_key: str
    ):
        """Test health endpoint when model artifacts are missing (500 error)."""
        with patch("solar_climatology_api.load_model_artifacts") as mock_load:
            mock_load.side_effect = FileNotFoundError("Model not found")
            
            response = client.get(
                "/api/v1/health",
                headers={"X-API-KEY": test_api_key},
            )
            
            assert response.status_code == 500
            data = response.get_json()
            assert data["status"] == "error"
            assert data["message"] == "Internal Server Error"

    def test_health_unexpected_error(
        self, client: FlaskClient, test_api_key: str
    ):
        """Test health endpoint with unexpected exception (500 error)."""
        with patch("solar_climatology_api.load_model_artifacts") as mock_load:
            mock_load.side_effect = Exception("Unexpected error")
            
            response = client.get(
                "/api/v1/health",
                headers={"X-API-KEY": test_api_key},
            )
            
            assert response.status_code == 500
            data = response.get_json()
            assert data["status"] == "error"
            assert data["message"] == "Internal Server Error"


class TestModelInfoEndpoint:
    """Tests for GET /api/v1/model-info endpoint."""

    def test_model_info_success(
        self, client: FlaskClient, test_api_key: str, mock_model_artifacts: Dict[str, Any]
    ):
        """Test successful model-info response."""
        response = client.get(
            "/api/v1/model-info",
            headers={"X-API-KEY": test_api_key},
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert "model_type" in data
        assert "validation_mape" in data
        assert "training_locations" in data
        assert "feature_columns" in data
        assert isinstance(data["feature_columns"], list)
        assert len(data["feature_columns"]) > 0

    def test_model_info_missing_api_key(self, client: FlaskClient):
        """Test model-info endpoint without API key returns 401."""
        response = client.get("/api/v1/model-info")
        
        assert response.status_code == 401
        data = response.get_json()
        assert data["status"] == "error"
        assert data["message"] == "Unauthorized"

    def test_model_info_invalid_api_key(self, client: FlaskClient, test_api_key: str):
        """Test model-info endpoint with invalid API key returns 401."""
        response = client.get(
            "/api/v1/model-info",
            headers={"X-API-KEY": "wrong_key"},
        )
        
        assert response.status_code == 401
        data = response.get_json()
        assert data["status"] == "error"
        assert data["message"] == "Unauthorized"

    def test_model_info_file_not_found_error(
        self, client: FlaskClient, test_api_key: str
    ):
        """Test model-info endpoint when model artifacts are missing (500 error)."""
        with patch("solar_climatology_api.load_model_artifacts") as mock_load:
            mock_load.side_effect = FileNotFoundError("Model not found")
            
            response = client.get(
                "/api/v1/model-info",
                headers={"X-API-KEY": test_api_key},
            )
            
            assert response.status_code == 500
            data = response.get_json()
            assert data["status"] == "error"
            assert data["message"] == "Internal Server Error"

    def test_model_info_unexpected_error(
        self, client: FlaskClient, test_api_key: str
    ):
        """Test model-info endpoint with unexpected exception (500 error)."""
        with patch("solar_climatology_api.load_model_artifacts") as mock_load:
            mock_load.side_effect = Exception("Unexpected error")
            
            response = client.get(
                "/api/v1/model-info",
                headers={"X-API-KEY": test_api_key},
            )
            
            assert response.status_code == 500
            data = response.get_json()
            assert data["status"] == "error"
            assert data["message"] == "Internal Server Error"


class TestPredictGenerationEndpoint:
    """Tests for POST /api/v1/predict-generation endpoint."""

    def test_predict_success_full_climatology(
        self,
        client: FlaskClient,
        test_api_key: str,
        valid_payload: Dict[str, Any],
        mock_predict_solar_generation: Any,
        mock_predict_lifetime_generation: Dict[str, Any],
        mock_validate_coordinates: Any,
    ):
        """Test successful prediction with full climatology (all 12 months)."""
        response = client.post(
            "/api/v1/predict-generation",
            json=valid_payload,
            headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "location" in data
        assert "monthly_generation" in data
        assert "annual_summary" in data
        assert "lifetime_prediction" in data
        assert "assumptions" in data
        assert "confidence" in data
        assert len(data["monthly_generation"]) == 12
        assert data["location"]["latitude"] == valid_payload["latitude"]
        assert data["location"]["longitude"] == valid_payload["longitude"]
        assert data["annual_summary"]["average_daily_kwh"] >= 0
        assert data["annual_summary"]["year_1_generation_kwh"] >= 0

    def test_predict_success_single_month(
        self,
        client: FlaskClient,
        test_api_key: str,
        valid_payload_single_month: Dict[str, Any],
        mock_predict_solar_generation: Any,
        mock_predict_lifetime_generation: Dict[str, Any],
        mock_validate_coordinates: Any,
    ):
        """Test successful prediction for a single month."""
        response = client.post(
            "/api/v1/predict-generation",
            json=valid_payload_single_month,
            headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert len(data["monthly_generation"]) == 1
        assert data["monthly_generation"][0]["month_index"] == 6
        assert "daily_kwh" in data["monthly_generation"][0]
        assert "is_dry_season" in data["monthly_generation"][0]

    def test_predict_success_without_lifetime(
        self,
        client: FlaskClient,
        test_api_key: str,
        mock_predict_solar_generation: Any,
        mock_validate_coordinates: Any,
    ):
        """Test successful prediction with include_lifetime=False."""
        payload = {
            "latitude": -1.2921,
            "longitude": 36.8219,
            "include_lifetime": False,
        }
        
        response = client.post(
            "/api/v1/predict-generation",
            json=payload,
            headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["lifetime_prediction"] is None
        assert "assumptions" in data
        assert data["assumptions"]["note"] == "Lifetime metrics disabled for this request."

    def test_predict_missing_api_key(self, client: FlaskClient):
        """Test predict endpoint without API key returns 401."""
        response = client.post(
            "/api/v1/predict-generation",
            json={"latitude": -1.2921, "longitude": 36.8219},
        )
        
        assert response.status_code == 401
        data = response.get_json()
        assert data["status"] == "error"
        assert data["message"] == "Unauthorized"

    def test_predict_invalid_api_key(self, client: FlaskClient):
        """Test predict endpoint with invalid API key returns 401."""
        response = client.post(
            "/api/v1/predict-generation",
            json={"latitude": -1.2921, "longitude": 36.8219},
            headers={"X-API-KEY": "wrong_key"},
        )
        
        assert response.status_code == 401
        data = response.get_json()
        assert data["status"] == "error"
        assert data["message"] == "Unauthorized"

    def test_predict_missing_latitude(self, client: FlaskClient, test_api_key: str):
        """Test predict endpoint with missing latitude returns 400."""
        response = client.post(
            "/api/v1/predict-generation",
            json={"longitude": 36.8219},
            headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        assert "latitude" in data["message"].lower()

    def test_predict_missing_longitude(self, client: FlaskClient, test_api_key: str):
        """Test predict endpoint with missing longitude returns 400."""
        response = client.post(
            "/api/v1/predict-generation",
            json={"latitude": -1.2921},
            headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        assert "longitude" in data["message"].lower()

    def test_predict_missing_both_coordinates(self, client: FlaskClient, test_api_key: str):
        """Test predict endpoint with missing both coordinates returns 400."""
        response = client.post(
            "/api/v1/predict-generation",
            json={},
            headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        assert "latitude" in data["message"].lower() or "longitude" in data["message"].lower()

    def test_predict_empty_body(self, client: FlaskClient, test_api_key: str):
        """Test predict endpoint with empty request body returns 400."""
        response = client.post(
            "/api/v1/predict-generation",
            data="",
            headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
        )
        
        assert response.status_code == 400

    def test_predict_malformed_json(self, client: FlaskClient, test_api_key: str):
        """Test predict endpoint with malformed JSON returns 400."""
        response = client.post(
            "/api/v1/predict-generation",
            data="{invalid json}",
            headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
        )
        
        assert response.status_code == 400

    def test_predict_invalid_latitude_type(
        self, client: FlaskClient, test_api_key: str
    ):
        """Test predict endpoint with non-numeric latitude returns 400."""
        response = client.post(
            "/api/v1/predict-generation",
            json={"latitude": "not_a_number", "longitude": 36.8219},
            headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
        )
        
        assert response.status_code == 422
        data = response.get_json()
        assert data["status"] == "error"

    def test_predict_invalid_longitude_type(
        self, client: FlaskClient, test_api_key: str
    ):
        """Test predict endpoint with non-numeric longitude returns 400."""
        response = client.post(
            "/api/v1/predict-generation",
            json={"latitude": -1.2921, "longitude": "not_a_number"},
            headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
        )
        
        assert response.status_code == 422
        data = response.get_json()
        assert data["status"] == "error"

    def test_predict_invalid_month_type(
        self, client: FlaskClient, test_api_key: str, mock_validate_coordinates: Any
    ):
        """Test predict endpoint with non-integer month returns 400."""
        response = client.post(
            "/api/v1/predict-generation",
            json={
                "latitude": -1.2921,
                "longitude": 36.8219,
                "month": "not_an_integer",
            },
            headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        assert "month" in data["message"].lower()

    def test_predict_invalid_month_range_low(
        self, client: FlaskClient, test_api_key: str, mock_validate_coordinates: Any
    ):
        """Test predict endpoint with month < 1 returns 400."""
        response = client.post(
            "/api/v1/predict-generation",
            json={"latitude": -1.2921, "longitude": 36.8219, "month": 0},
            headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        assert "month" in data["message"].lower()

    def test_predict_invalid_month_range_high(
        self, client: FlaskClient, test_api_key: str, mock_validate_coordinates: Any
    ):
        """Test predict endpoint with month > 12 returns 400."""
        response = client.post(
            "/api/v1/predict-generation",
            json={"latitude": -1.2921, "longitude": 36.8219, "month": 13},
            headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        assert "month" in data["message"].lower()

    def test_predict_invalid_coordinates_out_of_range(
        self, client: FlaskClient, test_api_key: str
    ):
        """Test predict endpoint with coordinates outside SSA range returns 400."""
        with patch("solar_climatology_api.validate_coordinates") as mock_validate:
            mock_validate.return_value = {
                "status": "error",
                "message": "Coordinates are outside the model's calibrated Sub-Saharan Africa coverage",
            }
            
            response = client.post(
                "/api/v1/predict-generation",
                json={"latitude": -40.0, "longitude": 60.0},
                headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
            )
            
            assert response.status_code == 400
            data = response.get_json()
            assert data["status"] == "error"
            assert "coordinate" in data["message"].lower() or "outside" in data["message"].lower()

    def test_predict_coordinates_with_warning(
        self,
        client: FlaskClient,
        test_api_key: str,
        mock_predict_solar_generation: Any,
        mock_predict_lifetime_generation: Dict[str, Any],
    ):
        """Test predict endpoint with coordinates near edge (warning but valid)."""
        with patch("solar_climatology_api.validate_coordinates") as mock_validate:
            mock_validate.return_value = {
                "status": "valid",
                "warnings": ["Latitude is near the edge of the training coverage"],
            }
            
            response = client.post(
                "/api/v1/predict-generation",
                json={"latitude": -21.0, "longitude": 28.0},
                headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data["status"] == "success"
            assert len(data["coordinate_validation"]["warnings"]) > 0

    def test_predict_invalid_hours_per_day_negative(
        self, client: FlaskClient, test_api_key: str, mock_validate_coordinates: Any
    ):
        """Test predict endpoint with negative hours_per_day returns 400."""
        response = client.post(
            "/api/v1/predict-generation",
            json={
                "latitude": -1.2921,
                "longitude": 36.8219,
                "hours_per_day": -1,
            },
            headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        assert "details" in data
        assert any("hours_per_day" in str(err).lower() for err in data["details"])

    def test_predict_invalid_hours_per_day_too_high(
        self, client: FlaskClient, test_api_key: str, mock_validate_coordinates: Any
    ):
        """Test predict endpoint with hours_per_day > 24 returns 400."""
        response = client.post(
            "/api/v1/predict-generation",
            json={
                "latitude": -1.2921,
                "longitude": 36.8219,
                "hours_per_day": 25,
            },
            headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        assert "details" in data

    def test_predict_invalid_equipment_units_negative(
        self, client: FlaskClient, test_api_key: str, mock_validate_coordinates: Any
    ):
        """Test predict endpoint with negative equipment_units returns 400."""
        response = client.post(
            "/api/v1/predict-generation",
            json={
                "latitude": -1.2921,
                "longitude": 36.8219,
                "equipment_units": -1,
            },
            headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        assert "details" in data

    def test_predict_invalid_equipment_units_too_high(
        self, client: FlaskClient, test_api_key: str, mock_validate_coordinates: Any
    ):
        """Test predict endpoint with equipment_units > 500 returns 400."""
        response = client.post(
            "/api/v1/predict-generation",
            json={
                "latitude": -1.2921,
                "longitude": 36.8219,
                "equipment_units": 501,
            },
            headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        assert "details" in data

    def test_predict_invalid_monthly_cost_negative(
        self, client: FlaskClient, test_api_key: str, mock_validate_coordinates: Any
    ):
        """Test predict endpoint with negative monthly_cost returns 400."""
        response = client.post(
            "/api/v1/predict-generation",
            json={
                "latitude": -1.2921,
                "longitude": 36.8219,
                "monthly_cost": -100,
            },
            headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        assert "details" in data

    def test_predict_invalid_monthly_consumption_negative(
        self, client: FlaskClient, test_api_key: str, mock_validate_coordinates: Any
    ):
        """Test predict endpoint with negative monthly_consumption_kwh returns 400."""
        response = client.post(
            "/api/v1/predict-generation",
            json={
                "latitude": -1.2921,
                "longitude": 36.8219,
                "monthly_consumption_kwh": -50,
            },
            headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        assert "details" in data

    def test_predict_invalid_business_type_empty_string(
        self, client: FlaskClient, test_api_key: str, mock_validate_coordinates: Any
    ):
        """Test predict endpoint with empty business_type returns 400."""
        response = client.post(
            "/api/v1/predict-generation",
            json={
                "latitude": -1.2921,
                "longitude": 36.8219,
                "business_type": "",
            },
            headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        assert "details" in data

    def test_predict_invalid_location_empty_string(
        self, client: FlaskClient, test_api_key: str, mock_validate_coordinates: Any
    ):
        """Test predict endpoint with empty location returns 400."""
        response = client.post(
            "/api/v1/predict-generation",
            json={
                "latitude": -1.2921,
                "longitude": 36.8219,
                "location": "   ",
            },
            headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        assert "details" in data

    def test_predict_valid_optional_fields(
        self,
        client: FlaskClient,
        test_api_key: str,
        mock_predict_solar_generation: Any,
        mock_predict_lifetime_generation: Dict[str, Any],
        mock_validate_coordinates: Any,
    ):
        """Test predict endpoint accepts valid optional business fields."""
        payload = {
            "latitude": -1.2921,
            "longitude": 36.8219,
            "hours_per_day": 12.5,
            "equipment_units": 10,
            "monthly_cost": 100.0,
            "monthly_consumption_kwh": 500.0,
            "business_type": "Retail",
            "location": "Nairobi",
        }
        
        response = client.post(
            "/api/v1/predict-generation",
            json=payload,
            headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"

    def test_predict_edge_case_latitude_min(
        self,
        client: FlaskClient,
        test_api_key: str,
        mock_predict_solar_generation: Any,
        mock_predict_lifetime_generation: Dict[str, Any],
    ):
        """Test predict endpoint with minimum valid latitude (-26)."""
        with patch("solar_climatology_api.validate_coordinates") as mock_validate:
            mock_validate.return_value = {"status": "valid", "warnings": []}
            
            response = client.post(
                "/api/v1/predict-generation",
                json={"latitude": -26.0, "longitude": 20.0},
                headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data["status"] == "success"

    def test_predict_edge_case_latitude_max(
        self,
        client: FlaskClient,
        test_api_key: str,
        mock_predict_solar_generation: Any,
        mock_predict_lifetime_generation: Dict[str, Any],
    ):
        """Test predict endpoint with maximum valid latitude (6)."""
        with patch("solar_climatology_api.validate_coordinates") as mock_validate:
            mock_validate.return_value = {"status": "valid", "warnings": []}
            
            response = client.post(
                "/api/v1/predict-generation",
                json={"latitude": 6.0, "longitude": 20.0},
                headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data["status"] == "success"

    def test_predict_edge_case_longitude_min(
        self,
        client: FlaskClient,
        test_api_key: str,
        mock_predict_solar_generation: Any,
        mock_predict_lifetime_generation: Dict[str, Any],
    ):
        """Test predict endpoint with minimum valid longitude (-18)."""
        with patch("solar_climatology_api.validate_coordinates") as mock_validate:
            mock_validate.return_value = {"status": "valid", "warnings": []}
            
            response = client.post(
                "/api/v1/predict-generation",
                json={"latitude": -10.0, "longitude": -18.0},
                headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data["status"] == "success"

    def test_predict_edge_case_longitude_max(
        self,
        client: FlaskClient,
        test_api_key: str,
        mock_predict_solar_generation: Any,
        mock_predict_lifetime_generation: Dict[str, Any],
    ):
        """Test predict endpoint with maximum valid longitude (44)."""
        with patch("solar_climatology_api.validate_coordinates") as mock_validate:
            mock_validate.return_value = {"status": "valid", "warnings": []}
            
            response = client.post(
                "/api/v1/predict-generation",
                json={"latitude": -10.0, "longitude": 44.0},
                headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data["status"] == "success"

    def test_predict_all_months_valid(
        self,
        client: FlaskClient,
        test_api_key: str,
        mock_predict_solar_generation: Any,
        mock_predict_lifetime_generation: Dict[str, Any],
        mock_validate_coordinates: Any,
    ):
        """Test predict endpoint with all valid month values (1-12)."""
        for month in range(1, 13):
            response = client.post(
                "/api/v1/predict-generation",
                json={
                    "latitude": -1.2921,
                    "longitude": 36.8219,
                    "month": month,
                },
                headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data["status"] == "success"
            assert len(data["monthly_generation"]) == 1
            assert data["monthly_generation"][0]["month_index"] == month

    def test_predict_large_valid_inputs(
        self,
        client: FlaskClient,
        test_api_key: str,
        mock_predict_solar_generation: Any,
        mock_predict_lifetime_generation: Dict[str, Any],
        mock_validate_coordinates: Any,
    ):
        """Test predict endpoint with large but valid numeric inputs."""
        payload = {
            "latitude": -1.2921,
            "longitude": 36.8219,
            "hours_per_day": 24.0,
            "equipment_units": 500,
            "monthly_cost": 999999.99,
            "monthly_consumption_kwh": 999999.99,
        }
        
        response = client.post(
            "/api/v1/predict-generation",
            json=payload,
            headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"

    def test_predict_unexpected_extra_fields(
        self,
        client: FlaskClient,
        test_api_key: str,
        mock_predict_solar_generation: Any,
        mock_predict_lifetime_generation: Dict[str, Any],
        mock_validate_coordinates: Any,
    ):
        """Test predict endpoint ignores unexpected extra fields (should still work)."""
        payload = {
            "latitude": -1.2921,
            "longitude": 36.8219,
            "unexpected_field": "should_be_ignored",
            "another_field": 12345,
        }
        
        response = client.post(
            "/api/v1/predict-generation",
            json=payload,
            headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"

    def test_predict_response_schema_consistency(
        self,
        client: FlaskClient,
        test_api_key: str,
        valid_payload: Dict[str, Any],
        mock_predict_solar_generation: Any,
        mock_predict_lifetime_generation: Dict[str, Any],
        mock_validate_coordinates: Any,
    ):
        """Test that response schema is consistent and complete."""
        response = client.post(
            "/api/v1/predict-generation",
            json=valid_payload,
            headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Check all required top-level keys
        required_keys = [
            "status",
            "location",
            "coordinate_validation",
            "monthly_generation",
            "annual_summary",
            "assumptions",
            "confidence",
            "note",
        ]
        for key in required_keys:
            assert key in data, f"Missing required key: {key}"
        
        # Check location structure
        assert "latitude" in data["location"]
        assert "longitude" in data["location"]
        
        # Check monthly_generation structure
        assert isinstance(data["monthly_generation"], list)
        for month_data in data["monthly_generation"]:
            assert "month" in month_data
            assert "month_index" in month_data
            assert "daily_kwh" in month_data
            assert "is_dry_season" in month_data
            assert isinstance(month_data["daily_kwh"], (int, float))
            assert month_data["daily_kwh"] >= 0  # Non-negative energy
        
        # Check annual_summary structure
        assert "year_1_generation_kwh" in data["annual_summary"]
        assert "average_daily_kwh" in data["annual_summary"]
        assert data["annual_summary"]["year_1_generation_kwh"] >= 0
        assert data["annual_summary"]["average_daily_kwh"] >= 0

    def test_predict_logical_consistency_annual_calculation(
        self,
        client: FlaskClient,
        test_api_key: str,
        mock_predict_solar_generation: Any,
        mock_predict_lifetime_generation: Dict[str, Any],
        mock_validate_coordinates: Any,
    ):
        """Test that annual summary is logically consistent (365 * daily = annual)."""
        # Mock predict_solar_generation to return a known value
        with patch("solar_climatology_api.predict_solar_generation") as mock_predict:
            mock_predict.return_value = 5.5  # 5.5 kWh/day
            
            response = client.post(
                "/api/v1/predict-generation",
                json={"latitude": -1.2921, "longitude": 36.8219},
                headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
            )
            
            assert response.status_code == 200
            data = response.get_json()
            
            # Verify annual calculation: daily * 365 ≈ annual
            daily = data["annual_summary"]["average_daily_kwh"]
            annual = data["annual_summary"]["year_1_generation_kwh"]
            expected_annual = daily * 365.0
            
            # Allow small floating point differences
            assert abs(annual - expected_annual) < 0.01

    def test_predict_server_error_on_prediction_failure(
        self, client: FlaskClient, test_api_key: str, mock_validate_coordinates: Any
    ):
        """Test predict endpoint returns 500 when prediction function fails."""
        with patch("solar_climatology_api.predict_solar_generation") as mock_predict:
            mock_predict.side_effect = Exception("Model prediction failed")
            
            response = client.post(
                "/api/v1/predict-generation",
                json={"latitude": -1.2921, "longitude": 36.8219},
                headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
            )
            
            assert response.status_code == 500
            data = response.get_json()
            assert data["status"] == "error"
            assert data["message"] == "Internal Server Error"

    def test_predict_server_error_on_lifetime_failure(
        self,
        client: FlaskClient,
        test_api_key: str,
        mock_predict_solar_generation: Any,
        mock_validate_coordinates: Any,
    ):
        """Test predict endpoint returns 500 when lifetime prediction fails."""
        with patch("solar_climatology_api.predict_lifetime_generation") as mock_lifetime:
            mock_lifetime.side_effect = Exception("Lifetime prediction failed")
            
            response = client.post(
                "/api/v1/predict-generation",
                json={"latitude": -1.2921, "longitude": 36.8219, "include_lifetime": True},
                headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
            )
            
            assert response.status_code == 500
            data = response.get_json()
            assert data["status"] == "error"
            assert data["message"] == "Internal Server Error"

    def test_predict_negative_energy_output_clamped(
        self,
        client: FlaskClient,
        test_api_key: str,
        mock_validate_coordinates: Any,
        mock_predict_lifetime_generation: Dict[str, Any],
    ):
        """Test that negative energy outputs are clamped to zero."""
        with patch("solar_climatology_api.predict_solar_generation") as mock_predict:
            mock_predict.return_value = -10.0  # Negative value (shouldn't happen, but test clamping)
            
            response = client.post(
                "/api/v1/predict-generation",
                json={"latitude": -1.2921, "longitude": 36.8219, "include_lifetime": False},
                headers={"X-API-KEY": test_api_key, "Content-Type": "application/json"},
            )
            
            assert response.status_code == 200
            data = response.get_json()
            # All energy values should be non-negative
            assert data["annual_summary"]["average_daily_kwh"] >= 0
            assert data["annual_summary"]["year_1_generation_kwh"] >= 0
            for month_data in data["monthly_generation"]:
                assert month_data["daily_kwh"] >= 0

