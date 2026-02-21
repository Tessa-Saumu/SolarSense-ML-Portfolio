# SolarSense AI ML Microservice

A unified Flask API gateway serving three independent machine learning microservices for solar energy analysis: Energy Consumption Prediction, Solar Generation Forecasting, and ROI Calculation.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Project Structure](#project-structure)
3. [Installation & Setup](#installation--setup)
4. [Environment Variables Configuration](#environment-variables-configuration)
5. [Local Testing Instructions](#local-testing-instructions)
6. [Running Test Suites](#running-test-suites)
7. [Deployment Guide](#deployment-guide)
8. [API Usage](#api-usage)
9. [Troubleshooting](#troubleshooting)

---

## Project Overview

This repository contains three ML-powered microservices unified under a single Flask gateway:

1. **Model 1: Energy Consumption Prediction** (`/api/v1/estimate-consumption`)
   - Predicts monthly energy consumption (kWh) for African SMEs
   - Uses XGBoost regression trained on commercial building data
   - Accounts for business type, floor area, operating hours, refrigeration units, and climate zones

2. **Model 2: Solar Generation Forecasting** (`/api/v1/predict-generation`)
   - Predicts typical solar generation (kWh) based on geographic coordinates
   - Uses XGBoost climatological regression model
   - Supports full 12-month climatology and 25-year lifetime projections

3. **Model 3: ROI Calculation** (`/api/v1/calculate-roi`)
   - Calculates monthly savings and annual ROI percentage
   - Deterministic formula-based calculation (no ML)
   - Takes consumption, generation, tariff, and system cost as inputs

**Architecture:**
- **Unified Gateway**: Single entry point (`api/main.py`) that routes requests to appropriate model services
- **Independent Services**: Each model maintains its own Flask app, validation logic, and security
- **Shared Authentication**: All three models use the same `API_KEY` environment variable
- **Preserved Endpoints**: All original endpoint paths and behaviors remain unchanged

---

## Project Structure

```
Model-1-branch/
├── api/
│   └── main.py                    # Unified Flask gateway (entry point)
├── models/
│   ├── energy_consumption/        # Model 1: Energy Consumption
│   │   ├── src/
│   │   │   └── app_ml.py         # Flask API for energy consumption prediction
│   │   ├── models/                # Model artifacts (.joblib files), Jupyter notebooks, dataset
│   │   ├── tests/                 # Unit and integration tests
│   │   └── archive/               # Archived docs, old requirements, etc.
│   ├── solar_generation/          # Model 2: Solar Generation
│   │   ├── src/
│   │   │   ├── solar_climatology_api.py      # Flask API
│   │   │   ├── solar_climatology_service.py  # Core prediction logic
│   │   ├── models/                # Model artifacts (.pkl files), Jupyter notebooks, dataset
│   │   ├── tests/                 # Unit and integration tests
│   │   └── archive/               # Archived docs, notebooks, data
│   ├── roi_calculation/           # Model 3: ROI Calculation
│   │   ├── src/
│   │   │   └── roi_calculation_api.py  # Flask API (deterministic calculation)
│   │   ├── tests/                 # Unit tests
│   │   └── archive/               # Archived docs, old requirements
│   └── recommendations/           # Model 4: (Not yet implemented)
├── tests/                         # Integration tests
├── docs/                          # Additional documentation
├── requirements.txt               # Unified production dependencies
├── requirements-dev.txt           # Development dependencies (pytest, etc.)
├── Procfile                       # Railway deployment configuration
├── railway.json                   # Railway platform configuration
├── pytest.ini                     # Pytest configuration
├── runtime.txt                    # Python version specification
└── README.md                      # This file
```

**Key Files:**
- `api/main.py`: Gateway that dispatches requests to model services
- `requirements.txt`: All production dependencies (merged from all three models)
- `Procfile`: Gunicorn command for Railway deployment
- `railway.json`: Railway deployment settings (healthcheck, restart policy)

**Archive Folders:**
- Each model has an `archive/` folder containing:
  - Old documentation, integration guides, API contracts
  - Legacy notebooks and training scripts
  - Previous `requirements.txt` files
  - Sample requests and test data
- These files are preserved but not used at runtime

---

## Installation & Setup

### Prerequisites

- **Python 3.8+** (tested with Python 3.9, 3.10, 3.12)
- **pip** (Python package manager)
- **Git** (for cloning the repository)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd Model-1-branch
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (for running tests)
pip install -r requirements-dev.txt
```

### Step 4: Verify Installation

```bash
python --version  # Should show Python 3.8+
pip list          # Should show Flask, numpy, xgboost, etc.
```

---

## Environment Variables Configuration

Create a `.env` file in the repository root:

```bash
# .env file
API_KEY=your_secure_api_key_here_minimum_32_characters

# Optional: Server port (default: 8000)
PORT=8000

# Optional: Model-specific overrides (only needed if running models standalone)
MODEL_DIR=models/solar_generation/models
MODEL1_PORT=8001
```

**Required Variables:**
- `API_KEY`: **Required**. Secret key for API authentication. Must be set for all three models to work. Use a strong random string (minimum 32 characters recommended).

**Optional Variables:**
- `PORT`: Server port for the unified gateway (default: `8000`)
- `MODEL_DIR`: Directory containing solar generation model artifacts (default: `models` relative to `solar_climatology_service.py`)
- `MODEL1_PORT`: Port for Model 1 if running standalone (default: `8001`)

**Security Notes:**
- **Never commit `.env` to version control** (it's in `.gitignore`)
- Use different API keys for development and production
- Rotate API keys periodically in production

---

## Local Testing Instructions

### Running the Unified Gateway

**Start the gateway server:**
```bash
# From repository root
python api/main.py
```

Or using Gunicorn (production-like):
```bash
gunicorn api.main:app --workers 2 --bind 0.0.0.0:8000 --timeout 120
```

The server will start on `http://localhost:8000` (or your configured `PORT`).

### Testing Endpoints

**1. Gateway Health Check:**
```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "gateway"
}
```

**2. Model 1 - Energy Consumption Prediction:**
```bash
curl -X POST http://localhost:8000/api/v1/estimate-consumption \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: your_secure_api_key_here" \
  -d '{
    "business_type": "butchery",
    "sqft_m2": 60.0,
    "operating_hours_weekly": 98.0,
    "num_refrigeration_units": 3,
    "location": "Lagos, Nigeria",
    "num_workers": 3,
    "months_per_year": 12
  }'
```

Expected response:
```json
{
  "estimated_consumption_kwh_monthly": 335.25,
  "confidence_score": 0.85,
  "breakdown": {
    "refrigeration": 201.15,
    "other": 134.10
  },
  "climate_adjustment_factor": 1.35,
  "equipment_summary": {
    "total_refrigeration_units": 3,
    "total_other_equipment": 0
  }
}
```

**3. Model 2 - Solar Generation Prediction:**
```bash
curl -X POST http://localhost:8000/api/v1/predict-generation \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: your_secure_api_key_here" \
  -d '{
    "latitude": -1.2921,
    "longitude": 36.8219,
    "include_lifetime": true
  }'
```

Expected response:
```json
{
  "status": "success",
  "location": {
    "latitude": -1.2921,
    "longitude": 36.8219
  },
  "monthly_generation": [...],
  "annual_summary": {
    "year_1_generation_kwh": 2142.55,
    "average_daily_kwh": 5.87
  },
  "lifetime_prediction": {...}
}
```

**4. Model 3 - ROI Calculation:**
```bash
curl -X POST http://localhost:8000/api/v1/calculate-roi \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: your_secure_api_key_here" \
  -d '{
    "consumption_kwh": 450.0,
    "generation_kwh": 500.0,
    "tariff_per_kwh": 0.20,
    "system_cost_usd": 6000.0
  }'
```

Expected response:
```json
{
  "monthly_savings_usd": 90.0,
  "roi_percentage": 18.0,
  "system_cost_usd": 6000.0
}
```

**5. Model 2 - Model Info:**
```bash
curl -H "X-API-KEY: your_secure_api_key_here" \
  http://localhost:8000/api/v1/model-info
```

**6. Model 1 - Health Check:**
```bash
curl -H "X-API-KEY: your_secure_api_key_here" \
  http://localhost:8000/api/v1/health
```

**Note:** Model-specific health endpoints require authentication. The gateway health endpoint (`/api/v1/health`) does not require authentication.

### Running Models Standalone (Optional)

You can also run each model independently for development/testing:

**Model 1:**
```bash
cd models/energy_consumption/src
python app_ml.py
# Runs on port 8001 (or MODEL1_PORT)
```

**Model 2:**
```bash
cd models/solar_generation/src
python solar_climatology_api.py
# Runs on port 8000 (or PORT)
```

**Model 3:**
```bash
cd models/roi_calculation/src
python roi_calculation_api.py
# Runs on port 5000 (or PORT)
```

---

## Running Test Suites

### Prerequisites

Ensure development dependencies are installed:
```bash
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
# From repository root
pytest
```

### Run Specific Test Suites

**Model 1 Tests:**
```bash
pytest models/energy_consumption/tests/
```

**Model 3 Tests:**
```bash
pytest models/roi_calculation/src/test_roi_api.py
pytest tests/roi_calculation/
```

**Integration Tests:**
```bash
pytest tests/
```

### Test Coverage

```bash
pytest --cov=models --cov=api --cov-report=html
```

### Common Test Issues

- **Import Errors**: Ensure you're running tests from the repository root
- **Missing API_KEY**: Tests use `test-api-key` by default; set `API_KEY` env var if needed
- **Model Files Not Found**: Some tests mock model loading; ensure model artifacts exist for integration tests

---

## Deployment Guide

### Railway Deployment

**Step 1: Prepare Repository**
- Ensure all code is committed and pushed to your Git repository
- Verify `Procfile` and `railway.json` exist in the root directory

**Step 2: Create Railway Project**
1. Log in to [Railway](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo" (or connect your Git provider)
4. Select your repository

**Step 3: Configure Environment Variables**
In Railway dashboard → Variables tab, add:
```
API_KEY=your_production_api_key_here
PORT=8000  # Railway sets this automatically, but you can override
```

**Step 4: Deploy**
- Railway will automatically detect `Procfile` and deploy using Gunicorn
- The healthcheck endpoint (`/api/v1/health`) will be monitored automatically
- Check deployment logs in Railway dashboard

**Step 5: Verify Deployment**
```bash
curl https://your-app.railway.app/api/v1/health
```

### Railway Configuration Files

**`Procfile`:**
```
web: gunicorn api.main:app --workers 2 --bind 0.0.0.0:$PORT --timeout 120
```

**`railway.json`:**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn api.main:app --workers 2 --bind 0.0.0.0:$PORT --timeout 120",
    "healthcheckPath": "/api/v1/health",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

### Post-Deployment Checklist

- [ ] Health check endpoint returns 200 OK
- [ ] All three model endpoints respond correctly
- [ ] API key authentication works
- [ ] Rate limiting is active (100 requests/minute)
- [ ] CORS headers are present
- [ ] Logs show no errors

---

## API Usage

### Authentication

All API endpoints (except gateway health check) require authentication via the `X-API-KEY` header:

```bash
curl -H "X-API-KEY: your_api_key_here" ...
```

**Authentication Errors:**
- `401 Unauthorized`: Missing or invalid API key
- `500 Internal Server Error`: API key not configured on server (misconfiguration)

### Rate Limiting

- **Limit**: 100 requests per minute per IP address
- **Error Response**: `429 Too Many Requests` with message `"Rate limit exceeded"`
- **Headers**: Rate limit info may be included in response headers (if supported by Flask-Limiter)

### Endpoints

#### Gateway Endpoints

**GET `/`**
- **Description**: Root endpoint, returns service status
- **Authentication**: Not required
- **Response**:
```json
{
  "message": "SolarSense API running",
  "status": "ok"
}
```

**GET `/api/v1/health`**
- **Description**: Gateway health check (used by Railway)
- **Authentication**: Not required
- **Response**:
```json
{
  "status": "ok",
  "service": "gateway"
}
```

#### Model 1: Energy Consumption

**POST `/api/v1/estimate-consumption`**
- **Description**: Predict monthly energy consumption for an SME
- **Authentication**: Required (`X-API-KEY` header)
- **Request Body**:
```json
{
  "business_type": "butchery" | "grocery" | "mini_supermarket",
  "sqft_m2": 60.0,                    // Required: > 0, <= 10000
  "operating_hours_weekly": 98.0,     // Required: > 0, <= 168
  "num_refrigeration_units": 3,       // Required: >= 0, <= 500
  "location": "Lagos, Nigeria",       // Required: string, max 200 chars
  "num_workers": 3,                   // Optional: defaults to 5, max 1000
  "months_per_year": 12               // Optional: defaults to 12, max 12
}
```
- **Response** (200 OK):
```json
{
  "estimated_consumption_kwh_monthly": 335.25,
  "confidence_score": 0.85,
  "breakdown": {
    "refrigeration": 201.15,
    "other": 134.10
  },
  "climate_adjustment_factor": 1.35,
  "equipment_summary": {
    "total_refrigeration_units": 3,
    "total_other_equipment": 0
  }
}
```
- **Error Responses**:
  - `400 Bad Request`: Missing fields, invalid types, out-of-range values
  - `401 Unauthorized`: Missing or invalid API key
  - `429 Too Many Requests`: Rate limit exceeded
  - `500 Internal Server Error`: Model loading or prediction error

**GET `/api/v1/health`** (Model 1 specific)
- **Description**: Model 1 health check
- **Authentication**: Required
- **Response**:
```json
{
  "status": "healthy"
}
```

#### Model 2: Solar Generation

**POST `/api/v1/predict-generation`**
- **Description**: Predict solar generation for a geographic location
- **Authentication**: Required (`X-API-KEY` header)
- **Request Body**:
```json
{
  "latitude": -1.2921,              // Required: float between -26 and 6
  "longitude": 36.8219,             // Required: float between -18 and 44
  "month": 6,                       // Optional: integer 1-12 (omitted = full climatology)
  "include_lifetime": true          // Optional: boolean, default true
}
```
- **Response** (200 OK):
```json
{
  "status": "success",
  "location": {
    "latitude": -1.2921,
    "longitude": 36.8219
  },
  "coordinate_validation": {
    "status": "valid",
    "warnings": []
  },
  "monthly_generation": [
    {
      "month": "June",
      "month_index": 6,
      "daily_kwh": 5.87,
      "is_dry_season": true
    }
  ],
  "annual_summary": {
    "year_1_generation_kwh": 2142.55,
    "average_daily_kwh": 5.87
  },
  "lifetime_prediction": {
    "year_1_generation_kwh": 2142.55,
    "lifetime_total_kwh": 49000.0,
    "lifetime_average_annual_kwh": 1960.0,
    "yearly_breakdown": [...],
    "assumptions": {...},
    "confidence": {...}
  },
  "assumptions": {...},
  "confidence": {...},
  "note": "Predictions represent typical expected generation, not a daily weather forecast."
}
```
- **Error Responses**:
  - `400 Bad Request`: Missing coordinates, invalid ranges, out-of-bounds coordinates
  - `401 Unauthorized`: Missing or invalid API key
  - `429 Too Many Requests`: Rate limit exceeded
  - `500 Internal Server Error`: Model loading or prediction error

**GET `/api/v1/model-info`**
- **Description**: Get model metadata and training configuration
- **Authentication**: Required
- **Response**:
```json
{
  "model_type": "XGBoost climatological regression",
  "validation_mape": 0.0746,
  "training_locations": [...],
  "feature_columns": [...]
}
```

**GET `/api/v1/health`** (Model 2 specific)
- **Description**: Model 2 health check with metadata
- **Authentication**: Required
- **Response**:
```json
{
  "status": "ok",
  "model_type": "XGBoost climatological regression",
  "last_trained_at": "2026-02-10T19:18:41Z",
  "validation_mape": 0.0746
}
```

#### Model 3: ROI Calculation

**POST `/api/v1/calculate-roi`**
- **Description**: Calculate monthly savings and ROI percentage
- **Authentication**: Required (`X-API-KEY` header)
- **Request Body**:
```json
{
  "consumption_kwh": 450.0,        // Required: > 0, <= 100000
  "generation_kwh": 500.0,          // Required: > 0, <= 100000
  "tariff_per_kwh": 0.20,           // Required: > 0, <= 100
  "system_cost_usd": 6000.0         // Required: > 0, <= 1,000,000
}
```
- **Response** (200 OK):
```json
{
  "monthly_savings_usd": 90.0,
  "roi_percentage": 18.0,
  "system_cost_usd": 6000.0
}
```
- **Error Responses**:
  - `400 Bad Request`: Missing fields, invalid types, out-of-range values
  - `401 Unauthorized`: Missing or invalid API key
  - `413 Payload Too Large`: Request body exceeds 100 KB
  - `429 Too Many Requests`: Rate limit exceeded
  - `500 Internal Server Error`: Calculation error

**GET `/api/v1/health`** (Model 3 specific)
- **Description**: Model 3 health check
- **Authentication**: Required
- **Response**:
```json
{
  "status": "ok",
  "service": "roi-calculation"
}
```

### Error Response Format

All error responses follow this structure:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "status": 400
  }
}
```

Or (for some endpoints):
```json
{
  "status": "error",
  "message": "Human-readable error message"
}
```

**Common Error Codes:**
- `MISSING_FIELD`: Required field is missing
- `INVALID_FIELD_TYPE`: Wrong data type
- `INVALID_FIELD_VALUE`: Out-of-range value
- `INVALID_BUSINESS_TYPE`: Invalid business_type value
- `INVALID_JSON`: Malformed JSON body
- `UNSUPPORTED_MEDIA_TYPE`: Non-JSON content type
- `UNAUTHORIZED`: Missing or invalid API key
- `PREDICTION_ERROR`: Internal model error
- `Rate limit exceeded`: Too many requests

---

## Troubleshooting

### Common Errors

**1. `ModuleNotFoundError: No module named 'models'`**
- **Cause**: Running code from wrong directory or Python path not set
- **Solution**: Always run from repository root, or ensure repo root is on `PYTHONPATH`

**2. `401 Unauthorized`**
- **Cause**: Missing or incorrect `X-API-KEY` header, or `API_KEY` env var not set
- **Solution**: 
  - Check `.env` file exists and contains `API_KEY=...`
  - Verify header name is exactly `X-API-KEY` (case-sensitive)
  - Ensure API key matches between client and server

**3. `500 Internal Server Error`**
- **Cause**: Model files not found, missing dependencies, or internal error
- **Solution**:
  - Check model artifacts exist in expected locations:
    - Model 1: `models/energy_consumption/models/*.joblib`
    - Model 2: `models/solar_generation/src/models/*.pkl`
  - Verify all dependencies installed: `pip install -r requirements.txt`
  - Check server logs for detailed error messages

**4. `FileNotFoundError` for model artifacts**
- **Cause**: Model files moved or paths incorrect
- **Solution**:
  - Verify model files exist in `models/energy_consumption/models/` and `models/solar_generation/src/models/`
  - Check `MODEL_DIR` environment variable if using Model 2 standalone

**5. `429 Too Many Requests`**
- **Cause**: Rate limit exceeded (100 requests/minute per IP)
- **Solution**: Wait 1 minute or implement request caching/throttling in client

**6. Port Already in Use**
- **Cause**: Another process using the port
- **Solution**:
  - Windows: `netstat -ano | findstr :8000` then `taskkill /PID <pid> /F`
  - macOS/Linux: `lsof -i :8000` then `kill -9 <pid>`
  - Or change `PORT` in `.env`

**7. Import Errors in Tests**
- **Cause**: Test files importing from wrong paths or `sys.path` not set
- **Solution**: Run tests from repository root: `pytest` (not from subdirectories)

**8. CORS Errors (Browser)**
- **Cause**: CORS not enabled or misconfigured
- **Solution**: CORS is enabled by default; verify `flask-cors` is installed

### Debugging Tips

**Enable Debug Logging:**
```python
# In api/main.py or model files, change:
logging.basicConfig(level=logging.DEBUG)
```

**Check Environment Variables:**
```bash
# Windows PowerShell
$env:API_KEY

# macOS/Linux
echo $API_KEY
```

**Test Individual Models:**
Run each model standalone to isolate issues:
```bash
cd models/energy_consumption/src
python app_ml.py
```

**Verify Dependencies:**
```bash
pip list | grep -E "flask|numpy|xgboost|joblib"
```

**Check Model Files:**
```bash
# Model 1
ls models/energy_consumption/models/

# Model 2
ls models/solar_generation/src/models/
```

### Getting Help

1. **Check Logs**: Server logs show detailed error messages
2. **Review Documentation**: See `docs/` folder for integration guides
3. **Run Tests**: `pytest` to verify installation
4. **Check Environment**: Verify `.env` file exists and contains required variables

---

## Additional Resources

- **Integration Guides**: See `models/*/archive/` folders for detailed integration documentation
- **API Contracts**: See `models/*/archive/API_CONTRACT.md` for detailed endpoint specifications
- **Model Cards**: See `models/*/archive/MODEL_CARD.md` for model architecture details

---

## License

[Add your license information here]

---

## Support

For issues or questions:
- Check the Troubleshooting section above
- Review integration guides in `archive/` folders
- Contact the development team

---

**Last Updated**: 2026-02-12