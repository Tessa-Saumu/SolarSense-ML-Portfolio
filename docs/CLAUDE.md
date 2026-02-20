# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SolarSense AI ML Microservice — a unified Flask API gateway serving four independent ML microservices for solar energy analysis targeting African SMEs. Deployed on Railway.

## Commands

### Install
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Run the server
```bash
python api/main.py                    # dev server on port 8000
gunicorn api.main:app --workers 2 --bind 0.0.0.0:8000 --timeout 120  # production-like
```

### Run tests
```bash
pytest                                              # all tests
pytest models/energy_consumption/tests/             # Model 1 tests
pytest models/solar_generation/tests/               # Model 2 tests
pytest models/roi_calculation/tests/                # Model 3 tests
pytest models/roi_calculation/src/test_roi_api.py   # Model 3 API test (separate location)
pytest models/recommendations/test_diesel_mvp.py    # Model 4 tests
pytest -k "test_name"                               # single test by name
pytest --cov=models --cov=api --cov-report=html     # with coverage
```

### Run models standalone (for development)
```bash
python models/energy_consumption/src/app_ml.py          # port 8001
python models/solar_generation/src/solar_climatology_api.py  # port 8000
python models/roi_calculation/src/roi_calculation_api.py     # port 5000
```

## Architecture

### Gateway Pattern (WSGI Dispatcher)
`api/main.py` is the single entry point. It uses a custom `MultiModelDispatcher` that intercepts WSGI calls and routes to the correct model Flask app based on URL path — it does NOT use Flask blueprints. Each model is a fully independent Flask app with its own auth, rate limiting, CORS, and validation. The gateway creates each via `create_app()` factory functions and wraps `app.wsgi_app` with the dispatcher.

Route mapping in the dispatcher:
- `/` and `/api/v1/health` → gateway (main_app)
- `/api/v1/estimate-consumption` → energy_app (Model 1)
- `/api/v1/predict-generation` and `/api/v1/model-info` → solar_app (Model 2)
- `/api/v1/calculate-roi` → roi_app (Model 3)
- `/api/v1/analyze` → recommendations_app (Model 4)

### Model Services

**Model 1 — Energy Consumption** (`models/energy_consumption/src/app_ml.py`): XGBoost regression predicting monthly kWh for African SMEs. Loads `.joblib` artifacts (model, scaler, feature columns, mappings) from `models/energy_consumption/models/`. Uses climate zone adjustment factors. `create_app()` accepts optional model paths and `test_mode`/`disable_auth` flags for testing.

**Model 2 — Solar Generation** (`models/solar_generation/src/`): XGBoost climatological model. Split into API layer (`solar_climatology_api.py`) and service layer (`solar_climatology_service.py`). Loads `.pkl`/`.json` artifacts from `src/models/`. Service layer handles coordinate validation, prediction, and lifetime projections. `create_app()` takes an optional `config` dict.

**Model 3 — ROI Calculation** (`models/roi_calculation/src/roi_calculation_api.py`): Deterministic formula (no ML). Calculates monthly savings and annual ROI from consumption, generation, tariff, and system cost. Has both module-level `app` and a `create_app()` factory.

**Model 4 — Recommendations** (`models/recommendations/model4_app.py`): Orchestration layer that calls Models 1-3 via HTTP (using `MODELS_BASE_URL` env var) and generates AI-powered recommendations. Converts equipment lists to business metrics for Model 1. Requires both `API_KEY` and `MODELS_BASE_URL` environment variables.

### Shared Patterns
- All models use `X-API-KEY` header authentication against the `API_KEY` env var
- All models use Flask-Limiter at 100 requests/minute per IP
- All models use Flask-CORS
- All models load env from `.env` via `python-dotenv`
- `pytest.ini` excludes `models/solar_generation/archive` and `api/model3_api` from test discovery

## Environment Variables

- `API_KEY` (required): Shared authentication key for all endpoints
- `PORT` (optional, default 8000): Server port
- `MODELS_BASE_URL` (required for Model 4): Base URL for calling Models 1-3
- `MODEL_DIR` (optional): Override model artifact directory for solar generation

## Key Conventions

- Python 3.11.9 (specified in `runtime.txt`)
- Each model has an `archive/` folder with legacy code — not used at runtime
- Tests run from repository root (required for correct imports)
- `api/main.py` adds the repo root to `sys.path` for cross-model imports
- Model 4 is the newest addition and orchestrates the other three models