## Model 1 – Integration Guide (ML API for Backend)

This guide explains how to integrate the **Model 1 Energy Consumption ML microservice** (`app_ml.py`)
into the wider SolarSense platform.

---

### Service Overview

- **Protocol**: HTTP + JSON
- **Framework**: Flask
- **Base URL (local dev)**: `http://localhost:8001`
- **Primary endpoint**: `POST /api/v1/estimate-consumption`
- **Health checks**:
  - `GET /api/v1/health`

Security & Performance:
- **Authentication**: `X-API-KEY` header (required for `/api/v1/estimate-consumption`)
- **Rate limiting**: 100 requests per minute per client IP (applied to `/api/v1/estimate-consumption`)

Expected response latency (local, small payloads): **< 50 ms** per request (excluding network).

---

### Request Contract (ML API – `app_ml.py`)

**Endpoint**: `POST /api/v1/estimate-consumption`

#### Headers

- `Content-Type: application/json`
- `X-API-KEY: <your-api-key>` – must match the server-side `API_KEY` environment variable

#### Body (JSON)

```json
{
  "business_type": "butchery",
  "sqft_m2": 60.0,
  "operating_hours_weekly": 98.0,
  "num_refrigeration_units": 3,
  "location": "Lagos, Nigeria",
  "num_workers": 3,
  "months_per_year": 12
}
```

#### Field Summary

- `business_type` (string, required)
  - Must be one of: `"butchery"`, `"grocery"`, `"mini_supermarket"` (case-insensitive on input).
- `sqft_m2` (number, required)
  - Floor area in m².
  - Must be > 0 and ≤ 10,000.
- `operating_hours_weekly` (number, required)
  - Weekly operating hours.
  - Must be > 0 and ≤ 168.
- `num_refrigeration_units` (integer, required)
  - Count of refrigeration units (fridges, freezers, cold rooms).
  - Must be ≥ 0 and ≤ 500.
- `location` (string, required)
  - City, country (e.g. `"Lagos, Nigeria"`).
  - Max length: 200 characters.
  - Used to derive a climate adjustment factor.
- `num_workers` (integer, optional)
  - Defaults to 5 if missing/invalid.
  - If ≤ 0 → reset to 5.
  - If > 1000 → request is rejected as invalid.
- `months_per_year` (integer, optional)
  - Defaults to 12 if missing/invalid.
  - If ≤ 0 or > 12 → reset to 12.

For a detailed, authoritative schema and all validation constraints, see `API_CONTRACT.md`.

---

### Response Contract (ML API)

**Success – 200**

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

Notes:

- `estimated_consumption_kwh_monthly`
  - Derived from **annual** ML prediction:
    - `annual_kwh_pred = expm1(model.predict(features))` (log-transformed target)
  - Then:
    - `monthly_kwh = (annual_kwh_pred * climate_factor) / 12`
  - Capped at a maximum of 1,000,000 kWh/month and never negative.
- `breakdown`
  - `refrigeration` is enforced to be 50–70% of `estimated_consumption_kwh_monthly`.
  - `other` is the remainder; both are clipped to be non-negative.
- `climate_adjustment_factor`
  - Based on `location` using city-name substring (e.g. `"lagos"` → 1.35).
  - Defaults to 1.20 when no known city is found.
- `confidence_score`
  - Heuristic in [0, 1]:
    - 0.75 baseline
    - 0.85 when `sqft_m2 > 0`, `operating_hours_weekly > 0`, and `num_refrigeration_units > 0`.

---

### Error Handling Contract

All **validation and server errors** from `/api/v1/estimate-consumption` use this JSON shape:

```json
{
  "error": {
    "code": "SOME_ERROR_CODE",
    "message": "Human-readable explanation",
    "status": 400
  }
}
```

Common error codes:

- `MISSING_FIELD` – required field is missing (`business_type`, `sqft_m2`, `operating_hours_weekly`, `num_refrigeration_units`, or `location`).
- `INVALID_FIELD_TYPE` – wrong data type (e.g. `sqft_m2` not a number, `location` not a string).
- `INVALID_FIELD_VALUE` – out-of-range value (e.g. `sqft_m2 > 10000`, `operating_hours_weekly > 168`, `num_refrigeration_units > 500`, `num_workers > 1000`, `location` too long).
- `INVALID_BUSINESS_TYPE` – `business_type` not in `["butchery", "grocery", "mini_supermarket"]`.
- `INVALID_JSON` – malformed or empty JSON body with `Content-Type: application/json`.
- `UNSUPPORTED_MEDIA_TYPE` – non-JSON content type (e.g. `text/plain`).
- `UNAUTHORIZED` – missing or invalid `X-API-KEY`.
- `PREDICTION_ERROR` – internal model/scaler/encoder error (generic 500; internal details are logged only).

Rate limiting:

- `429 Too Many Requests` – returned by Flask-Limiter when the 100 req/minute limit is exceeded.
  - Body is **text/HTML** from Flask-Limiter (not JSON) in the current implementation.

The `error.code` field is stable and should be used for programmatic handling where present.

---

### Fallback Strategy

If the microservice is unavailable or returns a 5xx error:

1. **Detect failure**:
   - Network error
   - HTTP 5xx
   - Timeout (recommend 2–3 seconds client timeout)
2. **Fallback behaviour** (suggested):
   - Surface a clear message to the user:
     - “We’re unable to estimate energy consumption right now. Please try again later.”
   - Optionally log payload + error to monitoring (for later replay).
3. **Do not** silently proceed with a hardcoded default estimate for production decisions.

If the error is **4xx (validation/auth)**:

- Bubble up the `error.message` to the caller (frontend or orchestrator) for user feedback.
- Use `error.code` to map to user-friendly messages if needed.
- For `UNAUTHORIZED`, prompt for reconfiguration of API key or re-auth.

---

### Recommended Calling Pattern (Python Example)

```python
import os
import requests

BASE_URL = "http://localhost:8001"
API_KEY = os.environ.get("API_KEY")

payload = {
    "business_type": "butchery",
    "sqft_m2": 60.0,
    "operating_hours_weekly": 98.0,
    "num_refrigeration_units": 3,
    "location": "Lagos, Nigeria",
    "num_workers": 3,
    "months_per_year": 12,
}

headers = {
    "Content-Type": "application/json",
    "X-API-KEY": API_KEY,
}

resp = requests.post(
    f"{BASE_URL}/api/v1/estimate-consumption",
    json=payload,
    headers=headers,
    timeout=3,
)
resp.raise_for_status()
data = resp.json()
```

---

### Using ngrok (for External Access)

ngrok can be used to expose the local service for external integration testing.

1. **Start the API locally**

```bash
cd models/energy_consumption/src
python app_ml.py
```

2. **Start ngrok tunnel**

```bash
ngrok http 8001
```

3. **Use the public URL**

Suppose ngrok gives you `https://abc123.ngrok.io`:

```bash
curl -X POST "https://abc123.ngrok.io/api/v1/estimate-consumption" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $API_KEY" \
  -d '{
    "business_type": "butchery",
    "sqft_m2": 60.0,
    "operating_hours_weekly": 98.0,
    "num_refrigeration_units": 3,
    "location": "Lagos, Nigeria"
  }'
```

ngrok tips:

- Free tier URLs change each time you restart ngrok.
- Visit `http://127.0.0.1:4040` to inspect requests.
- Ensure both the Flask app and ngrok are running concurrently.

---

### Versioning

- All endpoints are under `/api/v1/` to allow future breaking changes via `/api/v2/`.
- Any new fields will be added in a **backwards-compatible** way where possible.


