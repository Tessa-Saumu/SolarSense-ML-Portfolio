# Test Suite for ML-Based Energy Consumption API

## Overview

This test suite (`test_api_ml.py`) provides comprehensive automated testing for the ML-based Energy Consumption API (`app_ml.py`).

## Test Coverage

### ✅ Endpoints Tested
- `GET /api/v1/health` - Health check endpoint
- `POST /api/v1/estimate-consumption` - Energy consumption prediction

### ✅ Test Categories

#### 1. **Health Endpoint Tests**
- Successful health check (200)
- Method not allowed (405)

#### 2. **Successful Prediction Tests**
- Valid payload with all fields
- All business types (butchery, grocery, mini_supermarket)
- All climate zones (Lagos, Accra, Nairobi, etc.)
- Optional fields with defaults
- Case-insensitive business types

#### 3. **Input Validation - Missing Fields**
- Missing `business_type`
- Missing `sqft_m2`
- Missing `operating_hours_weekly`
- Missing `num_refrigeration_units`
- Missing `location`

#### 4. **Input Validation - Invalid Business Type**
- Invalid business type value
- Case-insensitive validation

#### 5. **Input Validation - Invalid Numeric Values**
- Negative `sqft_m2`
- Zero `sqft_m2`
- Negative `operating_hours_weekly`
- Excessive `operating_hours_weekly` (> 168)
- Negative `num_refrigeration_units`
- Zero `num_refrigeration_units` (allowed)

#### 6. **Input Validation - Invalid Types**
- Non-numeric `sqft_m2`
- Non-numeric `operating_hours_weekly`
- Non-integer `num_refrigeration_units`
- Non-string `business_type`
- Non-string `location`

#### 7. **Malformed Request Tests**
- Empty request body
- Malformed JSON
- Non-JSON content type
- Null JSON body

#### 8. **Unexpected Fields**
- Extra fields in payload (should be ignored)

#### 9. **Edge Cases & Stress Tests**
- Very large `sqft_m2` (10,000 m²)
- Very small `sqft_m2` (1 m²)
- Maximum `operating_hours_weekly` (168 = 24/7)
- Minimum `operating_hours_weekly` (0.1)
- Large number of refrigeration units (100)
- Boundary size categories (small/medium/large)

#### 10. **Model Failure Tests**
- Model not loaded (None)
- Model prediction exception
- Scaler transform exception
- Label encoder exception

#### 11. **Log-Transformed Target Tests**
- Prediction with log-transformed target model

#### 12. **Response Schema Validation**
- All required fields present
- Correct field types
- Valid value ranges
- Logical consistency (refrigeration share 50-70%)

#### 13. **Method Not Allowed Tests**
- GET on estimate-consumption
- PUT on estimate-consumption
- DELETE on estimate-consumption

#### 14. **Deterministic Output Tests**
- Same input produces same output (with mocked model)

#### 15. **Integration Tests**
- Multiple sequential requests

## Running the Tests

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt
```

### Run All Tests

```bash
# From project root
pytest models/energy_consumption/tests/test_api_ml.py -v

# From models/energy_consumption directory
pytest tests/test_api_ml.py -v
```

### Run Specific Test Categories

```bash
# Health endpoint tests only
pytest tests/test_api_ml.py -k "health" -v

# Validation tests only
pytest tests/test_api_ml.py -k "validation" -v

# Error handling tests only
pytest tests/test_api_ml.py -k "exception or error" -v

# Edge case tests only
pytest tests/test_api_ml.py -k "edge or stress or large" -v
```

### Run with Coverage

```bash
# Install coverage tool
pip install pytest-cov

# Run with coverage report
pytest tests/test_api_ml.py --cov=src/app_ml --cov-report=html -v

# View coverage report
# Open htmlcov/index.html in browser
```

## Test Fixtures

### `app`
Creates Flask app instance in test mode (models not loaded).

### `client`
Creates Flask test client for making requests.

### `mock_model_components`
Provides mocked model, scaler, and label encoders for testing.

### `app_with_mocked_model`
App instance with mocked model components configured.

### `valid_payload`
Sample valid request payload matching ML API schema.

## Key Features

### ✅ Comprehensive Coverage
- **100+ test cases** covering all scenarios
- Tests both success and failure paths
- Validates edge cases and boundary conditions

### ✅ Isolated Tests
- Uses mocks to avoid dependency on actual model files
- Tests are deterministic and repeatable
- No side effects between tests

### ✅ Proper Error Handling
- Tests all error codes (400, 405, 500)
- Validates error response structure
- Tests exception scenarios

### ✅ Response Validation
- Verifies response schema structure
- Validates field types and ranges
- Checks logical consistency

### ✅ No Hardcoded Paths
- Uses `Path(__file__).resolve().parents[1]` for relative paths
- Tests run from any directory
- Compatible with CI/CD pipelines

## Expected Test Results

When all tests pass, you should see:

```
tests/test_api_ml.py::test_health_endpoint PASSED
tests/test_api_ml.py::test_estimate_consumption_success PASSED
tests/test_api_ml.py::test_estimate_consumption_all_business_types PASSED
... (100+ tests)
======================== 100+ passed in X.XXs ========================
```

## Notes

- Tests use **mocked models** to avoid requiring actual model files
- Tests are **isolated** - each test is independent
- Tests validate both **API contract** and **business logic**
- All tests use **pytest fixtures** for setup/teardown
- Tests follow **AAA pattern** (Arrange, Act, Assert)

## Troubleshooting

### Import Errors
If you see import errors, ensure:
1. Virtual environment is activated
2. All dependencies are installed: `pip install -r requirements.txt`
3. You're running from the correct directory

### Model Loading Errors
Tests use mocked models, so actual model files are not required. If you see model loading errors in tests, check that the `test_mode=True` parameter is being used.

### Path Issues
Tests use relative paths from the test file location. Ensure you're running from the project root or `models/energy_consumption` directory.

