## Model 1 – Integration Guide (for Backend / Sarah)

This guide explains how to integrate the **Energy Consumption Estimation** microservice into the wider SolarSense platform.

---

### Service Overview

- **Protocol**: HTTP + JSON
- **Framework**: Flask
- **Base URL (local dev)**: `http://localhost:8001`
- **Primary endpoint**: `POST /api/v1/estimate-consumption`
- **Health checks**:
  - `GET /api/v1/health`
  - `GET /health` (legacy)

Expected response latency (local, small payloads): **< 50 ms** per request.

---

### Request Contract

`POST /api/v1/estimate-consumption`

Body (JSON):

```json
{
  "business_type": "butchery",
  "operating_hours": 12,
  "equipment": [
    {
      "type": "refrigerator",
      "quantity": 3,
      "size_capacity": "500L",
      "daily_operating_hours": 24
    }
  ],
  "location": "Lagos, Nigeria"
}
```

See `README.md` in this folder for the full schema and validation rules.

---

### Response Contract

**Success – 200**

```json
{
  "estimated_consumption_kwh_monthly": 1200.5,
  "confidence_score": 0.85,
  "breakdown": {
    "refrigeration": 720.3,
    "lighting": 180.0,
    "hvac": 200.2,
    "other": 100.0
  },
  "climate_adjustment_factor": 1.25,
  "equipment_summary": {
    "total_refrigeration_units": 6,
    "total_other_equipment": 4
  }
}
```

**Error – 400**

```json
{
  "error": {
    "code": "INVALID_EQUIPMENT",
    "message": "At least one refrigeration equipment item required",
    "status": 400
  }
}
```

The `code` field is stable and should be used for programmatic handling.

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

If the error is **4xx (validation)**:

- Bubble up the `error.message` to the caller (frontend or orchestrator) for user feedback.
- Use `error.code` to map to user-friendly messages if needed.

---

### Recommended Calling Pattern (Python Example)

```python
import requests

BASE_URL = "http://localhost:8001"

payload = {
    "business_type": "butchery",
    "operating_hours": 12,
    "equipment": [
        {
            "type": "refrigerator",
            "quantity": 3,
            "size_capacity": "500L",
            "daily_operating_hours": 24,
        },
        {
            "type": "lights",
            "quantity": 8,
            "size_capacity": "medium",
            "daily_operating_hours": 12,
        },
    ],
    "location": "Lagos, Nigeria",
}

resp = requests.post(f"{BASE_URL}/api/v1/estimate-consumption", json=payload, timeout=3)
resp.raise_for_status()
data = resp.json()
```

---

### Known Limitations

- Formula-based (not trained on local smart-meter data yet) – **MVP approximation** with ±20% target error.
- Equipment power ratings and climate factors are **heuristic** and meant to be refined.
- Location → climate zone mapping is currently **city-name substring based** (e.g. `"Lagos"` in `"Lagos, Nigeria"`).
- Legacy XGBoost artefacts in this repo are **not used** by this microservice.

---

### Versioning

- All endpoints are under `/api/v1/` to allow future breaking changes via `/api/v2/`.
- Any new fields will be added in a **backwards-compatible** way where possible.


