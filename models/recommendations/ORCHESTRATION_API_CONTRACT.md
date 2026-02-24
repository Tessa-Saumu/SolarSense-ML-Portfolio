# API CONTRACT
## SolarSense — Model 4 Orchestration API

**Version:** 1.2.0-mvp-diesel
**Base URL (Production):** `https://<model4-railway-url>.railway.app`
**Models 1–3 Base URL:** `https://dse-models-production.up.railway.app/api/v1`
**Issued to:** Backend Integration Team
**Date:** February 15, 2026

---

## AUTHENTICATION

All `/api/v1/*` endpoints require an API key passed as a request header:

```
X-API-KEY: <api_key>
```

Missing or incorrect key returns `401 Unauthorized`. There is no token expiry — rotate keys manually when needed.

---

## ENDPOINTS

### 1. Health Check

```
GET /health
```

No authentication required.

**Response 200:**
```json
{
  "status": "healthy",
  "service": "Model 4 Orchestration (MVP + Diesel)",
  "timestamp": "2026-02-15T10:30:00.000000",
  "version": "1.2.0-mvp-diesel"
}
```

---

### 2. Solar Viability Analysis

```
POST /api/v1/analyze
Content-Type: application/json
X-API-KEY: <api_key>
```

This is the primary endpoint. It orchestrates Models 1–3 and returns a complete solar viability assessment.

---

#### REQUEST BODY

##### Required Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `business_name` | string | 1–200 chars | Business display name |
| `business_type` | string | See enum | Type of business |
| `location` | string | Non-empty | Human-readable location (e.g. "Nairobi, Kenya") |
| `latitude` | float | -90 to 90 | Decimal degrees. **Model 2 only covers -26 to 6 (SSA)** |
| `longitude` | float | -180 to 180 | Decimal degrees. **Model 2 only covers -18 to 44 (SSA)** |

**Plus one of these two input modes:**

**Mode A — Equipment List (recommended):**

| Field | Type | Constraints |
|-------|------|-------------|
| `equipment_list` | array | List of equipment items |
| `equipment_list[].equipment_type` | string | See equipment types below |
| `equipment_list[].quantity` | integer | 0–100 |
| `equipment_list[].hours_per_day` | float | 0–24. Optional, default 12 |

**Mode B — Direct Business Metrics:**

| Field | Type | Constraints |
|-------|------|-------------|
| `sqft_m2` | float | 0–10,000 |
| `operating_hours_weekly` | float | 0–168 |
| `num_refrigeration_units` | integer | 0–500 |

##### Optional Fields

*Note: `tariff` is not used. Grid tariff is automatically resolved from coordinates via an internal country lookup. If coordinates do not map to a supported country, the endpoint returns 400 Unsupported Location.*

| Field | Type | Default | Constraints | Description |
|-------|------|---------|-------------|-------------|
| `num_workers` | integer | 5 | — | Number of employees |
| `months_per_year` | integer | 12 | — | Operating months per year |
| `uses_diesel` | boolean | false | — | Enable diesel replacement economics |
| `diesel_hours_per_day` | float | 12 | 0–24 | Hours/day generator runs (only used if `uses_diesel=true`) |
| `diesel_price_per_liter` | float | 1.20 | 0–10 | Diesel fuel cost in USD (only used if `uses_diesel=true`) |

##### Allowed Business Types

```
Restaurant, Retail, Office, Hotel, Healthcare, Education,
Manufacturing, Food & Beverage, Cafe, Gym, Bakery, Entertainment, Workshop
```

##### Supported Equipment Types

```
refrigerator, freezer, fridge, cold_room, display_cooler, ice_maker,
oven, stove, microwave, grill, fryer, espresso_machine, coffee_maker,
air_conditioner, ac, fan, heater,
lights, led_lights, fluorescent,
computer, printer, monitor,
treadmill, water_cooler, water_heater, dishwasher, washing_machine
```

Equipment types must match the allowlist exactly (case-insensitive). Unrecognised types return 400 Bad Request.

---

#### REQUEST EXAMPLES

**Grid-only (equipment list):**
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

**Diesel replacement:**
```json
{
  "business_name": "Mombasa Cold Storage",
  "business_type": "Retail",
  "location": "Mombasa, Kenya",
  "latitude": -4.0435,
  "longitude": 39.6682,
  "equipment_list": [
    { "equipment_type": "cold_room", "quantity": 1, "hours_per_day": 24 },
    { "equipment_type": "refrigerator", "quantity": 4, "hours_per_day": 24 },
    { "equipment_type": "lights", "quantity": 8, "hours_per_day": 12 }
  ],
  "tariff": 0.18,
  "uses_diesel": true,
  "diesel_hours_per_day": 18,
  "diesel_price_per_liter": 1.35
}
```

---

#### RESPONSE — 200 OK

All successful responses include the following fields.

##### Core Fields (always present)

| Field | Type | Description |
|-------|------|-------------|
| `business_name` | string | Echoed from request |
| `business_type` | string | Echoed from request |
| `location` | string | Echoed from request |
| `analyzed_at` | string | ISO 8601 timestamp |
| `estimated_consumption_kwh` | float | Monthly energy consumption (kWh) from Model 1 |
| `predicted_generation_kwh` | float | Monthly solar generation (kWh) scaled to recommended system size |
| `recommended_panel_area_m2` | float | Recommended solar panel area. Capped at 50m² (~$20,000) for SME realism |
| `system_cost` | float | Estimated system cost in USD. Uses tiered pricing: $750/m² for ≤10m², linearly ramped to $650/m² for ≤20m², $650/m² for ≤35m², $600/m² for >35m². A country-level adjustment factor (0.90–1.15) is then applied. The max is not a fixed $20,000. |
| `roi_percentage` | float | Annual ROI percentage |
| `monthly_savings` | float | Monthly savings in USD |
| `recommendation` | string | `"High"`, `"Medium"`, or `"Low"` |
| `viability_score` | float | Score 0–100 (see thresholds below) |
| `status` | string | `"HIGHLY VIABLE"`, `"MODERATELY VIABLE"`, or `"NOT VIABLE"` |
| `explanation` | string | Human-readable reasoning for the recommendation |
| `confidence` | float | Model confidence 0–100 |
| `energy_scenario` | string | `"grid_only"` or `"diesel_replacement"` |
| `current_energy_cost.total_monthly` | float | Current total energy cost (USD/month) |
| `current_energy_cost.diesel_monthly` | float | Diesel portion (0 if grid_only) |
| `current_energy_cost.grid_monthly` | float | Grid electricity portion |
| `lifetime_prediction` | object | 25-year generation projection from Model 2, scaled to the recommended panel area. Contains year_1_generation_kwh, lifetime_total_kwh, lifetime_average_annual_kwh, yearly_breakdown array, assumptions, and confidence objects. Present when Model 2 returns include_lifetime data. |

*Note: The tariff used in ROI and savings calculations is resolved automatically from the business coordinates — the optional tariff request field is not read by the current implementation.*

##### Diesel-Only Fields (present when `uses_diesel=true`)

| Field | Type | Description |
|-------|------|-------------|
| `diesel_details.hours_per_day` | float | Generator runtime hours/day |
| `diesel_details.price_per_liter` | float | Diesel price used in calculation |
| `diesel_details.monthly_liters` | float | Estimated diesel consumed per month |
| `diesel_details.effective_tariff` | float | Effective cost per kWh from diesel |
| `diesel_details.diesel_kwh_monthly` | float | kWh generated by diesel per month |

##### Viability Score Thresholds

| Score | `recommendation` | `status` |
|-------|-----------------|---------|
| ≥ 65 | `"High"` | `"HIGHLY VIABLE"` |
| 40–64 | `"Medium"` | `"MODERATELY VIABLE"` |
| < 40 | `"Low"` | `"NOT VIABLE"` |

**Important for frontend teams:** A `"Low"` recommendation for a grid-only business is correct and expected. African grid tariffs of $0.12–0.18/kWh produce 2–5% solar ROI. The UI should treat diesel replacement scenarios separately — heavy diesel users (18h/day) can reach 37–41% ROI and `"High"` viability.

---

#### RESPONSE EXAMPLES

**Grid-only response:**
```json
{
  "business_name": "Joe's Coffee Shop",
  "business_type": "Cafe",
  "location": "Nairobi, Kenya",
  "analyzed_at": "2026-02-15T10:30:00.000000",
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
  "energy_scenario": "grid_only",
  "current_energy_cost": {
    "total_monthly": 33.11,
    "diesel_monthly": 0,
    "grid_monthly": 33.11
  }
}
```

**Diesel replacement response:**
```json
{
  "business_name": "Mombasa Cold Storage",
  "business_type": "Retail",
  "location": "Mombasa, Kenya",
  "analyzed_at": "2026-02-15T10:30:00.000000",
  "estimated_consumption_kwh": 223.4,
  "predicted_generation_kwh": 201.1,
  "recommended_panel_area_m2": 16.2,
  "system_cost": 9693,
  "roi_percentage": 41.28,
  "monthly_savings": 333.48,
  "recommendation": "High",
  "viability_score": 77.0,
  "status": "HIGHLY VIABLE",
  "explanation": "Solar is highly viable because: Strong ROI of 41.3%; Excellent solar coverage (90%); Significant savings ($333/mo).",
  "confidence": 85.0,
  "energy_scenario": "diesel_replacement",
  "current_energy_cost": {
    "total_monthly": 370.53,
    "diesel_monthly": 360.48,
    "grid_monthly": 10.05
  },
  "diesel_details": {
    "hours_per_day": 18,
    "price_per_liter": 1.35,
    "monthly_liters": 60.3,
    "effective_tariff": 1.99,
    "diesel_kwh_monthly": 167.6
  }
}
```

---

#### ERROR RESPONSES

All error responses follow this shape:
```json
{
  "error": "<category>",
  "message": "<human-readable detail>"
}
```

| Status | `error` value | When |
|--------|--------------|------|
| `400` | `"Bad Request"` | Missing required fields, out-of-range values, wrong types |
| `401` | `"Unauthorized"` | Missing or invalid `X-API-KEY` |
| `429` | `"Too Many Requests"` | Rate limit exceeded (100 req/min per IP) |
| `500` | `"Internal Server Error"` | Unexpected internal error (no details exposed) |
| `503` | `"Service Unavailable"` | Out-of-region coordinates are caught by Model 4's internal country lookup before Model 2 is called. These return 400 Unsupported Location, not 503. A 503 occurs only when Models 1–3 are called and return an unexpected error. |

**503 response includes additional fields:**
```json
{
  "error": "Service Unavailable",
  "message": "Unable to complete analysis",
  "business_name": "Joe's Coffee Shop",
  "status": "INCOMPLETE"
}
```

The most common cause of 503 is coordinates outside Model 2's geographic coverage (lat must be -26 to 6). Validate coordinates on the frontend before sending.

---

## RATE LIMITS

| Limit | Value |
|-------|-------|
| Requests per minute | 100 per IP |
| Response on exceed | `429 Too Many Requests` |

---

## KNOWN CONSTRAINTS

| Constraint | Detail |
|------------|--------|
| Geographic coverage | Model 2 only covers Sub-Saharan Africa: lat -34 to 16, lon -18 to 45. Note that Model 4's own country lookup may reject coordinates before Model 2 is reached. |
| Max system size | 50m² (~$20,000). Larger systems not modelled for SME context |
| Diesel fuel efficiency | Model uses 0.40 L/kWh (partial load). Full-load rated efficiency is 0.25 L/kWh |
| Generation month | Uses current calendar month for solar prediction (not annual average) |
| No battery storage | Battery/storage scenarios not yet modelled (v1.3.0 planned) |

---

## INTEGRATION NOTES FOR BACKEND

1. **Always validate latitude/longitude** before sending — If coordinates fall outside SSA bounds (lat [-34, 16], lon [-18, 45]) or outside Model 4's supported country list, the API returns 400 (not 503). Display a friendly location-not-supported message for both 400 Unsupported Location and any remaining 503.

2. **Grid-only "Low" is not an error** — display it honestly but suggest the user check if they use a diesel generator, as that scenario typically scores much higher.

3. **`diesel_details` is conditionally present** — only render the diesel breakdown UI if `energy_scenario === "diesel_replacement"`.

4. **`system_cost` is in USD** — convert to local currency for display.

5. **Typical response time is 3–7 seconds** — show a loading state. Models 1–3 are called sequentially.

---

**Issued by:** SolarSense ML Team
**Owner:** Bella | **Updates:** Tessa
**Version:** 1.2.0-mvp-diesel | February 15, 2026