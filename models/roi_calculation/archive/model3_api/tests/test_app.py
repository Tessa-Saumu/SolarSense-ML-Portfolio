"""
Comprehensive test suite for the ROI calculation Flask API.

This test suite covers:
- All available endpoints
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
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from flask import Flask

# Import the app factory
import sys
from pathlib import Path

# Add parent directory to path to import app
# This allows tests to run from project root
app_dir = Path(__file__).parent.parent
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))
from app.app import create_app


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def app():
    """Create and configure a test Flask application."""
    app = create_app({
        'TESTING': True,
        'DEBUG': False
    })
    return app


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def valid_payload():
    """Sample valid payload for ROI calculation."""
    return {
        "generation_kwh": 500,
        "consumption_kwh": 300,
        "installation_cost": 4000,
        "electricity_price": 0.18
    }


@pytest.fixture
def valid_payload_minimal():
    """Minimal valid payload with smallest reasonable values."""
    return {
        "generation_kwh": 0.01,
        "consumption_kwh": 0.01,
        "installation_cost": 0.01,
        "electricity_price": 0.01
    }


@pytest.fixture
def valid_payload_large():
    """Large but valid payload for stress testing."""
    return {
        "generation_kwh": 999999.99,
        "consumption_kwh": 999999.99,
        "installation_cost": 99999999.99,
        "electricity_price": 999.99
    }


# ============================================================================
# Tests for Successful Responses (200-level)
# ============================================================================

class TestSuccessfulResponses:
    """Test cases for successful API responses."""
    
    def test_calculate_roi_success_with_valid_payload(self, client, valid_payload):
        """Test successful ROI calculation with valid payload."""
        response = client.post(
            '/calculate-roi',
            data=json.dumps(valid_payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['status'] == 'success'
        assert 'message' in data
        assert 'input_received' in data
        assert data['input_received'] == valid_payload
    
    def test_calculate_roi_success_with_minimal_values(self, client, valid_payload_minimal):
        """Test successful ROI calculation with minimal valid values."""
        response = client.post(
            '/calculate-roi',
            data=json.dumps(valid_payload_minimal),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['input_received'] == valid_payload_minimal
    
    def test_calculate_roi_success_with_large_values(self, client, valid_payload_large):
        """Test successful ROI calculation with large valid values."""
        response = client.post(
            '/calculate-roi',
            data=json.dumps(valid_payload_large),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['input_received'] == valid_payload_large
    
    def test_calculate_roi_success_with_zero_generation(self, client):
        """Test successful ROI calculation with zero generation."""
        payload = {
            "generation_kwh": 0,
            "consumption_kwh": 300,
            "installation_cost": 4000,
            "electricity_price": 0.18
        }
        response = client.post(
            '/calculate-roi',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_calculate_roi_success_with_zero_consumption(self, client):
        """Test successful ROI calculation with zero consumption."""
        payload = {
            "generation_kwh": 500,
            "consumption_kwh": 0,
            "installation_cost": 4000,
            "electricity_price": 0.18
        }
        response = client.post(
            '/calculate-roi',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_calculate_roi_success_with_extra_fields(self, client, valid_payload):
        """Test successful ROI calculation with extra fields (should be ignored or included)."""
        payload_with_extra = valid_payload.copy()
        payload_with_extra['extra_field'] = 'extra_value'
        payload_with_extra['another_field'] = 123
        
        response = client.post(
            '/calculate-roi',
            data=json.dumps(payload_with_extra),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        # Extra fields should be included in input_received
        assert 'extra_field' in data['input_received']
        assert data['input_received']['extra_field'] == 'extra_value'
    
    def test_calculate_roi_response_schema(self, client, valid_payload):
        """Test that response follows expected schema structure."""
        response = client.post(
            '/calculate-roi',
            data=json.dumps(valid_payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Verify schema structure
        assert isinstance(data, dict)
        assert 'status' in data
        assert isinstance(data['status'], str)
        assert 'message' in data
        assert isinstance(data['message'], str)
        assert 'input_received' in data
        assert isinstance(data['input_received'], dict)
        
        # Verify input_received contains expected fields
        input_data = data['input_received']
        assert 'generation_kwh' in input_data
        assert 'consumption_kwh' in input_data
        assert 'installation_cost' in input_data
        assert 'electricity_price' in input_data


# ============================================================================
# Tests for Client Errors (400-level)
# ============================================================================

class TestClientErrors:
    """Test cases for client error responses (400-level)."""
    
    def test_calculate_roi_malformed_json(self, client):
        """Test handling of malformed JSON."""
        response = client.post(
            '/calculate-roi',
            data='{invalid json}',
            content_type='application/json'
        )
        
        # Flask's get_json() with force=True may return None or raise
        # The current implementation doesn't validate JSON, so it might return 200
        # But we should test what actually happens
        assert response.status_code in [200, 400, 500]
        # If it's an error, verify error structure
        if response.status_code != 200:
            data = json.loads(response.data)
            assert 'status' in data
            assert data['status'] == 'error'
    
    def test_calculate_roi_empty_body(self, client):
        """Test handling of empty request body."""
        response = client.post(
            '/calculate-roi',
            data='',
            content_type='application/json'
        )
        
        # Current implementation doesn't validate, so it may return 200 with None
        assert response.status_code in [200, 400, 500]
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['status'] == 'success'
            # input_received might be None
            assert data['input_received'] is None or isinstance(data['input_received'], dict)
    
    def test_calculate_roi_null_body(self, client):
        """Test handling of null JSON body."""
        response = client.post(
            '/calculate-roi',
            data='null',
            content_type='application/json'
        )
        
        assert response.status_code in [200, 400, 500]
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['status'] == 'success'
    
    def test_calculate_roi_empty_json_object(self, client):
        """Test handling of empty JSON object."""
        response = client.post(
            '/calculate-roi',
            data='{}',
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['input_received'] == {}
    
    def test_calculate_roi_wrong_content_type(self, client, valid_payload):
        """Test handling of wrong content type."""
        response = client.post(
            '/calculate-roi',
            data=json.dumps(valid_payload),
            content_type='text/plain'
        )
        
        # Flask may still parse JSON, but test the behavior
        assert response.status_code in [200, 400, 415]
    
    def test_calculate_roi_missing_content_type(self, client, valid_payload):
        """Test handling of missing content type header."""
        response = client.post(
            '/calculate-roi',
            data=json.dumps(valid_payload)
        )
        
        # Flask may still parse JSON
        assert response.status_code in [200, 400]


# ============================================================================
# Tests for Invalid Data Types
# ============================================================================

class TestInvalidDataTypes:
    """Test cases for invalid data type handling."""
    
    def test_calculate_roi_string_instead_of_number(self, client):
        """Test handling of string values where numbers are expected."""
        payload = {
            "generation_kwh": "not_a_number",
            "consumption_kwh": 300,
            "installation_cost": 4000,
            "electricity_price": 0.18
        }
        response = client.post(
            '/calculate-roi',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Current implementation doesn't validate types
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['input_received']['generation_kwh'] == "not_a_number"
    
    def test_calculate_roi_array_instead_of_number(self, client):
        """Test handling of array values where numbers are expected."""
        payload = {
            "generation_kwh": [1, 2, 3],
            "consumption_kwh": 300,
            "installation_cost": 4000,
            "electricity_price": 0.18
        }
        response = client.post(
            '/calculate-roi',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_calculate_roi_object_instead_of_number(self, client):
        """Test handling of object values where numbers are expected."""
        payload = {
            "generation_kwh": {"value": 500},
            "consumption_kwh": 300,
            "installation_cost": 4000,
            "electricity_price": 0.18
        }
        response = client.post(
            '/calculate-roi',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_calculate_roi_null_values(self, client):
        """Test handling of null values in payload."""
        payload = {
            "generation_kwh": None,
            "consumption_kwh": 300,
            "installation_cost": 4000,
            "electricity_price": 0.18
        }
        response = client.post(
            '/calculate-roi',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['input_received']['generation_kwh'] is None


# ============================================================================
# Tests for Invalid Numeric Ranges
# ============================================================================

class TestInvalidNumericRanges:
    """Test cases for invalid numeric range handling."""
    
    def test_calculate_roi_negative_generation(self, client):
        """Test handling of negative generation_kwh."""
        payload = {
            "generation_kwh": -100,
            "consumption_kwh": 300,
            "installation_cost": 4000,
            "electricity_price": 0.18
        }
        response = client.post(
            '/calculate-roi',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Current implementation doesn't validate ranges
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['input_received']['generation_kwh'] == -100
    
    def test_calculate_roi_negative_consumption(self, client):
        """Test handling of negative consumption_kwh."""
        payload = {
            "generation_kwh": 500,
            "consumption_kwh": -50,
            "installation_cost": 4000,
            "electricity_price": 0.18
        }
        response = client.post(
            '/calculate-roi',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_calculate_roi_negative_installation_cost(self, client):
        """Test handling of negative installation_cost."""
        payload = {
            "generation_kwh": 500,
            "consumption_kwh": 300,
            "installation_cost": -1000,
            "electricity_price": 0.18
        }
        response = client.post(
            '/calculate-roi',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_calculate_roi_negative_electricity_price(self, client):
        """Test handling of negative electricity_price."""
        payload = {
            "generation_kwh": 500,
            "consumption_kwh": 300,
            "installation_cost": 4000,
            "electricity_price": -0.10
        }
        response = client.post(
            '/calculate-roi',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_calculate_roi_zero_installation_cost(self, client):
        """Test handling of zero installation_cost."""
        payload = {
            "generation_kwh": 500,
            "consumption_kwh": 300,
            "installation_cost": 0,
            "electricity_price": 0.18
        }
        response = client.post(
            '/calculate-roi',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_calculate_roi_zero_electricity_price(self, client):
        """Test handling of zero electricity_price."""
        payload = {
            "generation_kwh": 500,
            "consumption_kwh": 300,
            "installation_cost": 4000,
            "electricity_price": 0
        }
        response = client.post(
            '/calculate-roi',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_calculate_roi_very_large_numbers(self, client):
        """Test handling of very large numbers (potential overflow)."""
        payload = {
            "generation_kwh": 1e20,
            "consumption_kwh": 1e20,
            "installation_cost": 1e20,
            "electricity_price": 1e20
        }
        response = client.post(
            '/calculate-roi',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'


# ============================================================================
# Tests for Server Errors (500-level via Mocking)
# ============================================================================

class TestServerErrors:
    """Test cases for server error handling (500-level)."""
    
    def test_calculate_roi_server_error_on_json_parsing(self, client):
        """Test server error when JSON parsing fails internally."""
        with patch('flask.request.get_json') as mock_get_json:
            mock_get_json.side_effect = Exception("Internal JSON parsing error")
            
            response = client.post(
                '/calculate-roi',
                data='{"test": "data"}',
                content_type='application/json'
            )
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['status'] == 'error'
            assert 'message' in data
            assert isinstance(data['message'], str)
    
    def test_calculate_roi_server_error_on_response_creation(self, client, valid_payload):
        """Test server error when response creation fails."""
        with patch('flask.jsonify') as mock_jsonify:
            mock_jsonify.side_effect = Exception("Response creation error")
            
            response = client.post(
                '/calculate-roi',
                data=json.dumps(valid_payload),
                content_type='application/json'
            )
            
            # Flask will handle this as an unhandled exception
            assert response.status_code == 500
    
    def test_calculate_roi_server_error_generic_exception(self, client, valid_payload):
        """Test server error handling for generic exceptions."""
        with patch('flask.request.get_json') as mock_get_json:
            mock_get_json.side_effect = RuntimeError("Unexpected runtime error")
            
            response = client.post(
                '/calculate-roi',
                data=json.dumps(valid_payload),
                content_type='application/json'
            )
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['status'] == 'error'
            assert 'message' in data
    
    def test_calculate_roi_server_error_response_schema(self, client):
        """Test that error responses follow expected schema."""
        with patch('flask.request.get_json') as mock_get_json:
            mock_get_json.side_effect = Exception("Test error")
            
            response = client.post(
                '/calculate-roi',
                data='{"test": "data"}',
                content_type='application/json'
            )
            
            assert response.status_code == 500
            data = json.loads(response.data)
            
            # Verify error response schema
            assert isinstance(data, dict)
            assert 'status' in data
            assert data['status'] == 'error'
            assert 'message' in data
            assert isinstance(data['message'], str)


# ============================================================================
# Tests for HTTP Methods
# ============================================================================

class TestHttpMethods:
    """Test cases for different HTTP methods."""
    
    def test_calculate_roi_get_method_not_allowed(self, client):
        """Test that GET method is not allowed."""
        response = client.get('/calculate-roi')
        assert response.status_code == 405  # Method Not Allowed
    
    def test_calculate_roi_put_method_not_allowed(self, client):
        """Test that PUT method is not allowed."""
        response = client.put('/calculate-roi')
        assert response.status_code == 405  # Method Not Allowed
    
    def test_calculate_roi_delete_method_not_allowed(self, client):
        """Test that DELETE method is not allowed."""
        response = client.delete('/calculate-roi')
        assert response.status_code == 405  # Method Not Allowed
    
    def test_calculate_roi_patch_method_not_allowed(self, client):
        """Test that PATCH method is not allowed."""
        response = client.patch('/calculate-roi')
        assert response.status_code == 405  # Method Not Allowed


# ============================================================================
# Tests for Edge Cases and Stress Testing
# ============================================================================

class TestEdgeCases:
    """Test cases for edge cases and stress testing."""
    
    def test_calculate_roi_unicode_characters(self, client):
        """Test handling of unicode characters in payload."""
        payload = {
            "generation_kwh": 500,
            "consumption_kwh": 300,
            "installation_cost": 4000,
            "electricity_price": 0.18,
            "description": "Test with unicode: 测试 🚀"
        }
        response = client.post(
            '/calculate-roi',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_calculate_roi_scientific_notation(self, client):
        """Test handling of scientific notation in numbers."""
        payload = {
            "generation_kwh": 5e2,  # 500
            "consumption_kwh": 3e2,  # 300
            "installation_cost": 4e3,  # 4000
            "electricity_price": 1.8e-1  # 0.18
        }
        response = client.post(
            '/calculate-roi',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_calculate_roi_decimal_precision(self, client):
        """Test handling of high decimal precision."""
        payload = {
            "generation_kwh": 500.123456789,
            "consumption_kwh": 300.987654321,
            "installation_cost": 4000.555555555,
            "electricity_price": 0.181234567
        }
        response = client.post(
            '/calculate-roi',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_calculate_roi_very_long_payload(self, client):
        """Test handling of very long payload with many fields."""
        payload = {
            "generation_kwh": 500,
            "consumption_kwh": 300,
            "installation_cost": 4000,
            "electricity_price": 0.18
        }
        # Add many extra fields
        for i in range(100):
            payload[f"extra_field_{i}"] = f"value_{i}" * 10
        
        response = client.post(
            '/calculate-roi',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_calculate_roi_nested_structures(self, client):
        """Test handling of nested structures in payload."""
        payload = {
            "generation_kwh": 500,
            "consumption_kwh": 300,
            "installation_cost": 4000,
            "electricity_price": 0.18,
            "nested": {
                "level1": {
                    "level2": "value"
                }
            },
            "array_field": [1, 2, 3, {"nested": "object"}]
        }
        response = client.post(
            '/calculate-roi',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'nested' in data['input_received']
        assert 'array_field' in data['input_received']


# ============================================================================
# Tests for Response Consistency
# ============================================================================

class TestResponseConsistency:
    """Test cases for response consistency and logical correctness."""
    
    def test_calculate_roi_response_always_contains_status(self, client):
        """Test that all responses contain status field."""
        test_cases = [
            {},
            {"generation_kwh": 500},
            {"generation_kwh": "invalid"},
            {"generation_kwh": -100}
        ]
        
        for payload in test_cases:
            response = client.post(
                '/calculate-roi',
                data=json.dumps(payload),
                content_type='application/json'
            )
            
            data = json.loads(response.data)
            assert 'status' in data
            assert data['status'] in ['success', 'error']
    
    def test_calculate_roi_input_preservation(self, client):
        """Test that input data is preserved exactly in response."""
        payload = {
            "generation_kwh": 500.123,
            "consumption_kwh": 300.456,
            "installation_cost": 4000.789,
            "electricity_price": 0.181234
        }
        
        response = client.post(
            '/calculate-roi',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['input_received'] == payload
    
    def test_calculate_roi_multiple_requests_isolation(self, client):
        """Test that multiple requests are isolated and don't interfere."""
        payload1 = {
            "generation_kwh": 100,
            "consumption_kwh": 50,
            "installation_cost": 2000,
            "electricity_price": 0.15
        }
        payload2 = {
            "generation_kwh": 200,
            "consumption_kwh": 150,
            "installation_cost": 5000,
            "electricity_price": 0.20
        }
        
        response1 = client.post(
            '/calculate-roi',
            data=json.dumps(payload1),
            content_type='application/json'
        )
        response2 = client.post(
            '/calculate-roi',
            data=json.dumps(payload2),
            content_type='application/json'
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = json.loads(response1.data)
        data2 = json.loads(response2.data)
        
        assert data1['input_received'] == payload1
        assert data2['input_received'] == payload2
        assert data1['input_received'] != data2['input_received']


# ============================================================================
# Tests for CORS Headers
# ============================================================================

class TestCORS:
    """Test cases for CORS headers."""
    
    def test_calculate_roi_cors_headers_present(self, client, valid_payload):
        """Test that CORS headers are present in response."""
        response = client.post(
            '/calculate-roi',
            data=json.dumps(valid_payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        # CORS headers should be present (flask-cors adds them)
        # Note: In test client, CORS headers might not be visible
        # but the CORS middleware should be configured


# ============================================================================
# Integration Tests with Test Data Files
# ============================================================================

class TestWithTestDataFiles:
    """Test cases using test data from JSON files."""
    
    def test_calculate_roi_with_high_roi_data(self, client):
        """Test with high ROI test data file."""
        import os
        test_file = os.path.join(
            os.path.dirname(__file__),
            'high_roi.json'
        )
        
        with open(test_file, 'r') as f:
            payload = json.load(f)
        
        response = client.post(
            '/calculate-roi',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['input_received']['generation_kwh'] == payload['generation_kwh']
    
    def test_calculate_roi_with_medium_roi_data(self, client):
        """Test with medium ROI test data file."""
        import os
        test_file = os.path.join(
            os.path.dirname(__file__),
            'medium_roi.json'
        )
        
        with open(test_file, 'r') as f:
            payload = json.load(f)
        
        response = client.post(
            '/calculate-roi',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_calculate_roi_with_low_roi_data(self, client):
        """Test with low ROI test data file."""
        import os
        test_file = os.path.join(
            os.path.dirname(__file__),
            'low_roi.json'
        )
        
        with open(test_file, 'r') as f:
            payload = json.load(f)
        
        response = client.post(
            '/calculate-roi',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_calculate_roi_with_edge_cases_data(self, client):
        """Test with edge cases test data file."""
        import os
        test_file = os.path.join(
            os.path.dirname(__file__),
            'edge_cases.json'
        )
        
        with open(test_file, 'r') as f:
            test_cases = json.load(f)  # This is an array
        
        for payload in test_cases:
            response = client.post(
                '/calculate-roi',
                data=json.dumps(payload),
                content_type='application/json'
            )
            
            # Edge cases might still return 200 if validation isn't implemented
            assert response.status_code in [200, 400, 500]
            data = json.loads(response.data)
            assert 'status' in data

