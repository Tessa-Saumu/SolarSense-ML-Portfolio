# MODEL 4: AI RECOMMENDATION ENGINE & ORCHESTRATION

**Solar Viability Assessment System**
**Owner:** Bella
**Version:** 1.2.0-mvp-diesel
**Last Updated:** February 15, 2026

---

## TABLE OF CONTENTS

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Quick Start](#quick-start)
4. [API Documentation](#api-documentation)
5. [Security Features](#security-features)
6. [Integration with Models 1-3](#integration-with-models-1-3)
7. [Testing](#testing)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)

---

## OVERVIEW

Model 4 is the **master orchestration layer** that coordinates Models 1–3 and generates final solar viability recommendations. It supports both grid-only and diesel replacement scenarios, and intelligently sizes solar systems based on actual business consumption.

### What It Does

1. Accepts business input (equipment list or direct metrics)
2. Converts equipment list → business metrics for Model 1
3. Calls Model 1 → Energy Consumption Estimation
4. Calls Model 2 → Solar Generation Prediction
5. Intelligently sizes solar system to 90% consumption coverage (capped at 50m² / ~$20k for SME realism)
6. Calculates diesel economics and blended tariff (if applicable)
7. Calls Model 3 → ROI Calculation using blended tariff
8. Applies viability scoring and returns recommendation

### Key Features

- **Dual Input Mode** — accepts equipment lists OR direct business metrics
- **Diesel Replacement Economics** — models grid-only and diesel hybrid scenarios
- **Intelligent System Sizing** — auto-scales panel area to 90% coverage (SME-capped)
- **Secure** — API key authentication, rate limiting, input/output validation
- **Explainable** — clear reasoning attached to every recommendation
- **Resilient** — graceful degradation if any upstream model is unavailable

---

## ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT                              │
│            (Web App / Mobile / API Consumer)                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ POST /api/v1/analyze
                         │ (with X-API-KEY header)
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                       MODEL 4                               │
│            AI Recommendation Engine v1.2.0                  │
│                                                             │
│  1. Validate & convert input                                │
│  2. Call Model 1 → Consumption                              │
│  3. Call Model 2 → Base generation (10m²)                   │
│  4. Scale system to 90% coverage (max 50m²)                 │
│  5. Calculate diesel economics + blended tariff             │
│  6. Call Model 3 → ROI                                      │
│  7. Score viability & return recommendation                 │
└─────────┬──────────┬──────────┬────────────────────────────┘
          │          │          │
          │          │          │  (Railway API — shared key)
          ▼          ▼          ▼
    ┌─────────┐ ┌─────────┐ ┌─────────┐
    │ Model 1 │ │ Model 2 │ │ Model 3 │
    │ Energy  │ │ Solar   │ │   ROI   │
    │ Consump.│ │ Gener.  │ │  Calc.  │
    └─────────┘ └─────────┘ └─────────┘
```

---

## QUICK START

### Prerequisites

- Python 3.8+
- pip
- Models 1–3 deployed on Railway (already live)

### Installation

```bash
# 1. Clone repository
git clone <your-repo-url>
cd model4

# 2. Install dependencies
pip install -r requirements_model4.txt

# 3. Create .env file
cp .env_model4 .env

# 4. Generate your API key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 5. Edit .env — add generated key to API_KEY
# MODELS_API_KEY = the shared key for Models 1-3
# MODELS_BASE_URL = https://dse-models-production.up.railway.app/api/v1

# 6. Run
python model4_app.py
```

### Verify It's Working

```bash
# Health check (no auth needed)
curl http://127.0.0.1:5000/health
# Expected: {"status": "healthy", ...}
```

---

## API DOCUMENTATION

### Base URL

```
Local:      http://127.0.0.1:5000
Production: https://<your-railway-url>.railway.app
```

### Authentication

All `/api/v1/*` endpoints require:
```
X-API-KEY: your_api_key_here
```

---

### ENDPOINT 1: Health Check

No authentication required.

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Model 4 Orchestration (MVP + Diesel)",
  "timestamp": "2026-02-15T10:30:00.000000",
  "version": "1.2.0-mvp-diesel"
}
```

---

### ENDPOINT 2: API Info

No authentication required.

```http
GET /
```

**Response:**
```json
{
  "service": "Solar Viability Assessment - Model 4",
  "version": "1.2.0-mvp-diesel",
  "description": "MVP: Diesel replacement economics + intelligent system sizing",
  "endpoints": {
    "health": "GET /health",
    "analyze": "POST /api/v1/analyze (requires X-API-KEY header)"
  },
  "new_inputs": {
    "uses_diesel": "boolean (optional, default false)",
    "diesel_hours_per_day": "number 0-24 (optional, default 12)",
    "diesel_price_per_liter": "USD per liter (optional, default 1.20)"
  }
}
```

---

### ENDPOINT 3: Solar Viability Analysis

**Requires authentication.**

```http
POST /api/v1/analyze
Content-Type: application/json
X-API-KEY: your_api_key_here
```

#### Request — Equipment List Mode (recommended)

```json
{
  "business_name": "Joe's Coffee Shop",
  "business_type": "Cafe",
  "location": "Nairobi, Kenya",
  "latitude": -1.2921,
  "longitude": 36.8219,
  "equipment_list": [
    { "equipment_type": "refrigerator", "quantity": 2, "hours_per_day": 24 },
    { "equipment_type": "espresso_machine", "quantity": 1, "hours_per_day": 10 },
    { "equipment_type": "lights", "quantity": 15, "hours_per_day": 12 },
    { "equipment_type": "air_conditioner", "quantity": 2, "hours_per_day": 8 }
  ],
  "tariff": 0.15,
  "uses_diesel": false
}
```

#### Request — Diesel Replacement Mode

```json
{
  "business_name": "Lagos Butchery",
  "business_type": "Bakery",
  "location": "Lagos, Nigeria",
  "latitude": 5.5244,
  "longitude": 3.3792,
  "equipment_list": [
    { "equipment_type": "refrigerator", "quantity": 3, "hours_per_day": 24 },
    { "equipment_type": "freezer", "quantity": 2, "hours_per_day": 24 },
    { "equipment_type": "lights", "quantity": 10, "hours_per_day": 12 }
  ],
  "tariff": 0.12,
  "uses_diesel": true,
  "diesel_hours_per_day": 12,
  "diesel_price_per_liter": 1.20
}
```

#### Required Fields

| Field | Type | Constraints |
|-------|------|-------------|
| `business_name` | string | 1–200 characters |
| `business_type` | string | See allowed values below |
| `location` | string | Human-readable |
| `latitude` | float | -90 to 90; Model 2 valid range: **-26 to 6** (Sub-Saharan Africa) |
| `longitude` | float | -180 to 180; Model 2 valid range: **-18 to 44** |
| `equipment_list` OR (`sqft_m2` + `operating_hours_weekly` + `num_refrigeration_units`) | — | One input mode required |

#### Optional Fields

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `tariff` | float | 0.15 | Grid electricity cost ($/kWh) |
| `uses_diesel` | boolean | false | Enable diesel replacement mode |
| `diesel_hours_per_day` | float | 12 | Generator runtime per day (0–24) |
| `diesel_price_per_liter` | float | 1.20 | Diesel fuel price in USD (0–10) |
| `num_workers` | integer | 5 | Number of employees |
| `months_per_year` | integer | 12 | Operating months |

#### Allowed Business Types

`Restaurant`, `Retail`, `Office`, `Hotel`, `Healthcare`, `Education`, `Manufacturing`, `Food & Beverage`, `Cafe`, `Gym`, `Bakery`, `Entertainment`, `Workshop`

#### Supported Equipment Types

`refrigerator`, `freezer`, `fridge`, `cold_room`, `display_cooler`, `ice_maker`, `oven`, `stove`, `microwave`, `grill`, `fryer`, `espresso_machine`, `coffee_maker`, `air_conditioner`, `ac`, `fan`, `heater`, `lights`, `led_lights`, `fluorescent`, `computer`, `printer`, `monitor`, `treadmill`, `water_cooler`, `water_heater`, `dishwasher`, `washing_machine`

Unknown types default to 100W power estimate.

---

#### Success Response (200 OK) — Grid Only

```json
{
  "business_name": "Joe's Coffee Shop",
  "business_type": "Cafe",
  "location": "Nairobi, Kenya",
  "estimated_consumption_kwh": 220.8,
  "predicted_generation_kwh": 198.7,
  "recommended_panel_area_m2": 24.5,
  "system_cost": 14707,
  "roi_percentage": 2.43,
  "monthly_savings": 29.80,
  "recommendation": "Low",
  "viability_score": 34.3,
  "status": "NOT VIABLE",
  "explanation": "Solar is not viable because: Low ROI of 2.4%; Excellent solar coverage (90%); Low savings ($29.80/mo).",
  "confidence": 85.0,
  "analyzed_at": "2026-02-15T10:30:00.000000",
  "energy_scenario": "grid_only",
  "current_energy_cost": {
    "total_monthly": 33.11,
    "diesel_monthly": 0,
    "grid_monthly": 33.11
  }
}
```

#### Success Response (200 OK) — Diesel Replacement

```json
{
  "business_name": "Lagos Butchery",
  "business_type": "Bakery",
  "location": "Lagos, Nigeria",
  "estimated_consumption_kwh": 251.3,
  "predicted_generation_kwh": 226.2,
  "recommended_panel_area_m2": 50.0,
  "system_cost": 30000,
  "roi_percentage": 5.36,
  "monthly_savings": 134.02,
  "recommendation": "Low",
  "viability_score": 31.3,
  "status": "NOT VIABLE",
  "explanation": "Solar is not viable because: Low ROI of 5.4%; ...",
  "confidence": 85.0,
  "analyzed_at": "2026-02-15T10:30:00.000000",
  "energy_scenario": "diesel_replacement",
  "current_energy_cost": {
    "total_monthly": 255.40,
    "diesel_monthly": 240.32,
    "grid_monthly": 15.08
  },
  "diesel_details": {
    "hours_per_day": 12,
    "price_per_liter": 1.20,
    "monthly_liters": 50.3,
    "effective_tariff": 1.91,
    "diesel_kwh_monthly": 125.7
  }
}
```

#### Viability Score Thresholds

| Score | Recommendation | Status |
|-------|---------------|--------|
| ≥ 65 | High | HIGHLY VIABLE |
| 40–64 | Medium | MODERATELY VIABLE |
| < 40 | Low | NOT VIABLE |

> **Note:** African grid-only scenarios with tariffs of $0.12–0.18/kWh realistically produce Low ratings (2–5% ROI). Heavy diesel users (18h/day) can reach High (37–41% ROI). This is by design — the model reflects market reality.

#### Error Responses

```json
// 400 — Invalid input
{ "error": "Bad Request", "message": "latitude must be between -90 and 90" }

// 401 — Missing/invalid API key
{ "error": "Unauthorized", "message": "API key is required" }

// 429 — Rate limit exceeded
{ "error": "Too Many Requests", "message": "Rate limit exceeded" }

// 503 — Models 1-3 unavailable
{
  "error": "Service Unavailable",
  "message": "Unable to complete analysis",
  "business_name": "Joe's Coffee Shop",
  "status": "INCOMPLETE"
}

// 500 — Internal error (no details exposed)
{ "error": "Internal Server Error", "message": "An error occurred" }
```

---

## SECURITY FEATURES

### API Key Authentication
All `/api/v1/*` endpoints enforce `X-API-KEY` header validation. Missing or invalid keys return 401 immediately.

### Rate Limiting
100 requests per minute per IP. Returns 429 if exceeded. Production deployments should use Redis storage for the limiter.

### Input Validation
All inputs are validated for presence, type, and range before any model calls are made. See field constraints above.

### Output Sanitization
All energy values are clamped to non-negative. Viability score is bounded 0–100. No internal paths, stack traces, or model details are exposed in error responses.

---

## INTEGRATION WITH MODELS 1-3

**Base URL:** `https://dse-models-production.up.railway.app/api/v1`
**Auth header:** `X-API-KEY` (same shared key for all three)

| Model | Endpoint | Sends | Receives |
|-------|----------|-------|----------|
| Model 1 | `POST /estimate-consumption` | `business_type`, `sqft_m2`, `operating_hours_weekly`, `num_refrigeration_units`, `location`, `num_workers`, `months_per_year` | `estimated_consumption_kwh_monthly`, `confidence_score` |
| Model 2 | `POST /predict-generation` | `latitude`, `longitude`, `month`, `include_lifetime` | `monthly_generation[].daily_kwh`, `annual_summary` |
| Model 3 | `POST /calculate-roi` | `consumption_kwh`, `generation_kwh`, `tariff_per_kwh`, `system_cost_usd` | `roi_percentage`, `monthly_savings_usd` |

**Important geographic constraint:** Model 2 only covers Sub-Saharan Africa (lat: -26 to 6, lon: -18 to 44). Requests outside this range will cause a 503 from Model 4 because Model 2 will reject them with 400.

If any upstream model fails, Model 4 logs the error and returns 503 to the client. No automatic retries (to respect upstream rate limits).

---

## TESTING

```bash
# Run diesel MVP test suite
python test_diesel_mvp.py

# Expected: All 3 tests pass with 200 OK
# Test 1: Grid-only → Low viability (realistic for low tariffs)
# Test 2: Diesel 12h/day → Low/Medium viability
# Test 3: Heavy diesel 18h/day → High viability (37-41% ROI)
```

Manual curl test:
```bash
curl -X POST http://127.0.0.1:5000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: your_api_key_here" \
  -d @test_diesel_mvp.json
```

---

## DEPLOYMENT

### Deploy to Railway

```bash
# 1. Create Procfile
echo "web: gunicorn model4_app:app" > Procfile

# 2. Create runtime.txt
echo "python-3.11.0" > runtime.txt

# 3. Install Railway CLI and deploy
npm install -g @railway/cli
railway login
railway init
railway up

# 4. Set environment variables
railway variables set API_KEY=your_generated_key
railway variables set MODELS_API_KEY=QfBmvo3htYQPSJWYYLcChxXvZonTuC2U
railway variables set MODELS_BASE_URL=https://dse-models-production.up.railway.app/api/v1

# 5. Verify
curl https://your-railway-url.railway.app/health
```

---

## TROUBLESHOOTING

**401 Unauthorized** — API key in request header doesn't match `API_KEY` in `.env`. Verify both match exactly.

**503 Service Unavailable** — One of Models 1–3 is down or returned an error. Most common causes:
- Model 2 rejection due to coordinates outside SSA bounds (check lat/lon)
- Models 1–3 Railway service sleeping (first request wakes it, retry after 10s)

**App won't start** — `API_KEY` or `MODELS_API_KEY` not set in `.env`. Both are required at startup.

**Low viability on all scenarios** — Expected for African grid-only businesses at $0.12–0.15/kWh. Recommend testing with `uses_diesel: true` if the business uses a generator — these scenarios show significantly higher ROI.

---

## SUPPORT

**Owner:** Bella
**Updates:** Tessa
**Project:** SolarSense AI — Model 4 Orchestration
**Version:** 1.2.0-mvp-diesel | February 15, 2026