### API Contract: Climatological Solar Generation Service

**Base URL (local dev)**: `http://localhost:8000`

Authentication is required for all `/api/v1/*` endpoints via an API key header. The key is loaded from the `API_KEY` environment variable (typically via `.env`).

---

### 1. POST `/api/v1/predict-generation`

Predict typical solar generation for a point location, with optional lifetime projection.

#### Request

**Headers**
- `Content-Type: application/json`
- `X-API-KEY: <your_api_key>`

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
  - Other validation failures (e.g. invalid `month`, bad optional business fields) return:
    ```json
    {"status": "error", "message": "Invalid input.", "details": ["..."]}
    ```

- **401 Unauthorized**
  - Missing or incorrect API key:
    ```json
    {"status": "error", "message": "Unauthorized"}
    ```

- **500 Internal Server Error**
  - Any unexpected server-side exception (including missing artifacts/metadata) returns a generic error:
    ```json
    {"status": "error", "message": "Internal Server Error"}
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

If metadata is missing or unreadable, returns 500 with a generic `"Internal Server Error"` message.

---

### 4. Error Codes and Messages

- **400 Bad Request**
  - Invalid or missing fields (`latitude`, `longitude`, `month`).
  - Coordinates outside supported region.
  - Invalid numeric ranges for optional fields (`hours_per_day`, `equipment_units`, `monthly_cost`, `monthly_consumption_kwh`).

- **401 Unauthorized**
  - Missing or incorrect `X-API-KEY` header.

- **500 Internal Server Error**
  - Missing or unreadable model artifacts/metadata.
  - Unexpected server-side exceptions.

Errors always return JSON with:

```json
{"status": "error", "message": "<short description>"}
```

---

### 5. Rate Limiting

- Rate limiting is enforced in-process using **Flask-Limiter**.
- Global default: **100 requests per minute per client IP**.
- All documented endpoints (`/api/v1/health`, `/api/v1/model-info`, `/api/v1/predict-generation`) are decorated with `@limiter.limit("100 per minute")`.

---

### 6. Environment Variables

- `API_KEY` (required): API key expected in `X-API-KEY` header.
- `MODEL_DIR` (optional, default `models`): Directory containing model artifacts (`xgboost_climatological_model.pkl`, `feature_columns.pkl`, metadata JSON).
- `PORT` (optional, default `8000`): Port on which the Flask app listens in local development.

---

### 7. CORS Policy

- CORS is enabled globally via `flask_cors.CORS(app)`.
- All origins are allowed; for production, you may wish to restrict allowed origins at the gateway or application level.