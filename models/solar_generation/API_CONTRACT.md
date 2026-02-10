### API Contract: Climatological Solar Generation Service

**Base URL (local dev)**: `http://localhost:8000`

No authentication is required for local development. For production, place the service behind an API gateway or add auth middleware.

---

### 1. POST `/api/v1/predict-generation`

Predict typical solar generation for a point location, with optional lifetime projection.

#### Request

**Headers**
- `Content-Type: application/json`

**Body**
```json
{
  "latitude": -1.2921,
  "longitude": 36.8219,
  "month": 6,
  "include_lifetime": true
}
```

- `latitude` (float, required): -26 to 6.
- `longitude` (float, required): -18 to 44.
- `month` (int, optional): 1–12. If omitted, returns a full 12‑month climatology.
- `include_lifetime` (bool, optional): default `true`. If true, includes 25‑year projection.

#### Successful Response (200)

```json
{
  "status": "success",
  "location": {"latitude": -1.2921, "longitude": 36.8219},
  "coordinate_validation": {
    "status": "valid",
    "warnings": []
  },
  "monthly_generation": [
    {
      "month": "January",
      "month_index": 1,
      "daily_kwh": 5.8,
      "is_dry_season": true
    }
  ],
  "annual_summary": {
    "year_1_generation_kwh": 2117.0,
    "average_daily_kwh": 5.8
  },
  "lifetime_prediction": {
    "year_1_generation_kwh": 2117.0,
    "lifetime_total_kwh": 49000.0,
    "lifetime_average_annual_kwh": 1960.0,
    "yearly_breakdown": [
      {
        "year": 1,
        "generation_kwh": 2117.0,
        "efficiency_pct": 100.0,
        "confidence_low_kwh": 1905.3,
        "confidence_high_kwh": 2328.7,
        "confidence_band_pct": 10.0
      }
    ],
    "assumptions": {
      "panel_area_m2": 10.0,
      "panel_efficiency_pct": 20.0,
      "lifetime_years": 25,
      "annual_degradation_pct": 0.7,
      "dry_months": [1, 2, 6, 7, 8, 12]
    },
    "confidence": {
      "year_1_band_pct": 10.0,
      "years_1_5_band_pct": 10.0,
      "years_6_15_band_pct": 15.0,
      "years_16_25_band_pct": 20.0
    },
    "monthly_generation_climatology": [...]
  },
  "assumptions": {...},
  "confidence": {...},
  "note": "Predictions represent typical expected generation, not a daily weather forecast."
}
```

#### Error Responses

- **400 Bad Request**
  - Missing or invalid inputs:
    ```json
    {"status": "error", "message": "Request must include 'latitude' and 'longitude'."}
    ```
  - Out-of-bounds coordinates:
    ```json
    {
      "status": "error",
      "message": "Coordinates are outside the model's calibrated Sub-Saharan Africa coverage (lat: -26 to 6, lon: -18 to 44)."
    }
    ```

- **500 Internal Server Error**
  - Model artifacts missing, or unexpected error:
    ```json
    {"status": "error", "message": "Missing model artifacts: ..."}
    ```

---

### 2. GET `/api/v1/health`

Lightweight health and readiness probe.

#### Response (200)

```json
{
  "status": "ok",
  "model_type": "XGBoost climatological regression",
  "last_trained_at": "2026-02-10T19:18:41Z",
  "validation_mape": 0.0746
}
```

- If metadata/model is missing, returns 500 with error message.

---

### 3. GET `/api/v1/model-info`

Returns model configuration and training details.

#### Response (200)

```json
{
  "model_type": "XGBoost climatological regression",
  "validation_mape": 0.0746,
  "training_locations": [
    "Accra_Ghana",
    "Addis_Ababa_Ethiopia",
    "Dakar_Senegal",
    "Johannesburg_SA",
    "Kampala_Uganda",
    "Lagos_Nigeria",
    "Nairobi_Kenya"
  ],
  "feature_columns": [
    "latitude",
    "longitude",
    "abs_latitude",
    "month",
    "is_dry_season"
  ]
}
```

If metadata is missing, returns 500 with an explanatory error.

---

### 4. Error Codes and Messages

- **400 Bad Request**
  - Invalid or missing fields (`latitude`, `longitude`, `month`).
  - Coordinates outside supported region.

- **500 Internal Server Error**
  - Missing or unreadable model artifacts.
  - Unexpected server-side exceptions.

Errors always return JSON with:

```json
{"status": "error", "message": "<human-readable description>"}
```

---

### 5. Rate Limiting

- No explicit rate limiting is enforced in this implementation.
- In production, it is recommended to enforce rate limits at the API gateway or load balancer level.


