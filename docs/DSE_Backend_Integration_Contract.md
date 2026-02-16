# DSE → Backend Integration Contract

**Document Type:** Internal — Backend Engineering Reference  
**Version:** 1.0  
**Project:** SolarSense AI — Team 58  
**Scope:** Full request/response schema for all four DSE model endpoints, plus orchestration logic for the master response assembled by Model 4.

---

## Preamble: Architecture Agreement — Grid Scenario Coverage

### What DSE Models

The DSE codebase supports **exactly two energy scenarios**, determined by the `uses_diesel` boolean in the `/analyze` request:

| Scenario | `uses_diesel` | `energy_scenario` in Response | Description |
|----------|--------------|-------------------------------|-------------|
| Grid-Only | `false` | `"grid_only"` | Business draws fully from the grid; solar offsets grid consumption at the stated tariff |
| Diesel Replacement | `true` | `"diesel_replacement"` | Business uses diesel for a portion of the day and grid for the remainder; solar replaces both; ROI uses a blended tariff |

### What DSE Does NOT Model

The following scenarios have **no DSE allocation** and no corresponding logic in any of the four models:

| Frontend Option | DSE Coverage | Impact |
|----------------|-------------|--------|
| **Intermittent grid (no diesel)** | ❌ None | The ROI model has no mechanism to account for outage hours without an associated diesel cost. A business with an unreliable grid but no diesel generator cannot be modelled accurately — savings are understated because lost-production hours are ignored. |
| **Fully off-grid** | ❌ None | Model 3 calculates savings as `energy_offset × tariff_per_kwh`. With no grid tariff, this collapses to $0. Off-grid economics (generator replacement, battery sizing, energy autonomy) are out of scope for v1. |
| **Hybrid (solar + battery + grid + diesel)** | ❌ None | No battery storage modelling exists. Complex multi-source dispatch is not handled. |
| **Intermittent grid + diesel** | ⚠️ Proxy only | This can be approximated using the `diesel_replacement` path — the user enters how many hours/day the diesel runs. This is a reasonable proxy but is not a true intermittent-grid model (outage duration variability, load-shedding schedules, etc. are not modelled). |

**Frontend consequence:** Any grid-selector UI options beyond "on grid" and "off grid with diesel" must either be hidden, disabled, or mapped explicitly to the two supported scenarios. Presenting an "intermittent grid" option without flagging model limitations risks misleading users.

---

The DSE codebase owns all algorithms, thresholds, input/output schemas, and decision logic. Backend's role is to:

1. Authenticate and forward requests to the deployed DSE endpoint cluster.
2. Store assessment results as needed (database writes, user session management).
3. Return the DSE-generated master response verbatim to the frontend.

Backend **must not** modify, re-calculate, or override any field emitted by the DSE models. The models are the source of truth for all energy, generation, ROI, and viability values.

All four models are deployed as a single unified service behind a gateway at:  
**Base URL:** `https://dse-models-production.up.railway.app/api/v1`  
**Auth header:** `X-API-KEY: <API_KEY>` (required on all `/api/` routes)

---

## Model 1 — Energy Consumption Estimation

### Endpoint
```
POST /api/v1/estimate-consumption
```

### Request Schema

| Field | Type | Required | Validation Rules | Example |
|-------|------|----------|-----------------|---------|
| `business_type` | string | ✅ Required | One of: `"butchery"`, `"grocery"`, `"mini_supermarket"` | `"butchery"` |
| `sqft_m2` | float | ✅ Required | `0 < value ≤ 10,000` | `60.0` |
| `operating_hours_weekly` | float | ✅ Required | `0 < value ≤ 168` | `98.0` |
| `num_refrigeration_units` | integer | ✅ Required | `0 ≤ value ≤ 500` | `3` |
| `location` | string | ✅ Required | Non-empty string, max 200 chars | `"Lagos, Nigeria"` |
| `num_workers` | integer | Optional | `1 ≤ value ≤ 1000` — defaults to `5` | `3` |
| `months_per_year` | integer | Optional | `1 ≤ value ≤ 12` — defaults to `12` | `12` |

**Full example request body:**
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

### Response Schema (HTTP 200)

| Field | Type | Example Value | Notes |
|-------|------|--------------|-------|
| `estimated_consumption_kwh_monthly` | float | `450.25` | Core output — monthly kWh estimate |
| `confidence_score` | float | `0.85` | Range 0.0–1.0; 0.85 if all key inputs provided, 0.75 otherwise |
| `breakdown.refrigeration` | float | `315.18` | 50–70% of monthly consumption |
| `breakdown.other` | float | `135.08` | Remaining consumption (lighting, etc.) |
| `climate_adjustment_factor` | float | `1.35` | Multiplier derived from location; Lagos=1.35, Nairobi=1.20 |
| `equipment_summary.total_refrigeration_units` | integer | `3` | Echoes the input |
| `equipment_summary.total_other_equipment` | integer | `0` | Not tracked in v1, always 0 |

**Full example response:**
```json
{
  "estimated_consumption_kwh_monthly": 450.25,
  "confidence_score": 0.85,
  "breakdown": {
    "refrigeration": 315.18,
    "other": 135.08
  },
  "climate_adjustment_factor": 1.35,
  "equipment_summary": {
    "total_refrigeration_units": 3,
    "total_other_equipment": 0
  }
}
```

### Notable Logic
- **Climate zones** baked into the model: Lagos/Dar es Salaam/Kinshasa = 1.35, Accra/Abidjan = 1.30, Kampala = 1.25, Nairobi/Johannesburg = 1.20, all others default to 1.20.
- **Business type mapping** (applied internally when called from Model 4): "Restaurant", "Retail", "Office", "Hotel", "Cafe", "Gym" → mapped to `"grocery"`; "Bakery" → `"butchery"`.
- **Refrigeration share** = `min(0.70, max(0.50, num_refrigeration_units / (num_workers * 2)))`.

---

## Model 2 — Solar Generation Prediction

### Endpoints
```
POST /api/v1/predict-generation
GET  /api/v1/model-info
```

### Request Schema — `/api/v1/predict-generation`

| Field | Type | Required | Validation Rules | Example |
|-------|------|----------|-----------------|---------|
| `latitude` | float | ✅ Required | `-26 ≤ value ≤ 6` (SSA coverage); warning if `< -20` or `> 2` | `-1.2921` |
| `longitude` | float | ✅ Required | `-18 ≤ value ≤ 44` (SSA coverage) | `36.8219` |
| `month` | integer | Optional | `1–12`; if omitted, returns full 12-month climatology | `6` |
| `include_lifetime` | boolean | Optional | Defaults to `true` | `true` |

**Full example request body:**
```json
{
  "latitude": -1.2921,
  "longitude": 36.8219,
  "month": 6,
  "include_lifetime": true
}
```

### Response Schema (HTTP 200)

**Top-level fields:**

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `status` | string | `"success"` | Always `"success"` on 200 |
| `location.latitude` | float | `-1.2921` | Echoes input |
| `location.longitude` | float | `36.8219` | Echoes input |
| `coordinate_validation.status` | string | `"valid"` | `"valid"` or `"error"` |
| `coordinate_validation.warnings` | array | `[]` | Non-empty if near edge of coverage area |
| `note` | string | `"Predictions represent..."` | Disclaimer string |

**`monthly_generation` array** — one entry per requested month (12 entries if `month` omitted):

| Sub-field | Type | Example | Notes |
|-----------|------|---------|-------|
| `month` | string | `"June"` | Full month name |
| `month_index` | integer | `6` | Numeric month (1–12) |
| `daily_kwh` | float | `5.2` | Predicted daily generation for 10m² @ 20% efficiency |
| `is_dry_season` | boolean | `true` | Dry months: Dec, Jan, Feb, Jun, Jul, Aug |

**`annual_summary` object:**

| Sub-field | Type | Example | Notes |
|-----------|------|---------|-------|
| `year_1_generation_kwh` | float | `1898.0` | `average_daily_kwh × 365` |
| `average_daily_kwh` | float | `5.2` | Mean across all requested months |

**`lifetime_prediction` object** (present when `include_lifetime: true`):

| Sub-field | Type | Example | Notes |
|-----------|------|---------|-------|
| `year_1_generation_kwh` | float | `1898.0` | Annual generation at full efficiency |
| `lifetime_total_kwh` | float | `39,250.0` | Sum across all 25 years with degradation |
| `lifetime_average_annual_kwh` | float | `1,570.0` | `lifetime_total / 25` |
| `yearly_breakdown` | array | See below | 25 entries, one per year |
| `assumptions` | object | See below | Model configuration |
| `confidence` | object | See below | Confidence band summary |
| `monthly_generation_climatology` | array | See below | 12-month typical profile |

**`lifetime_prediction.yearly_breakdown` — array of 25 objects:**

| Sub-field | Type | Example (Year 1) | Notes |
|-----------|------|-----------------|-------|
| `year` | integer | `1` | 1 through 25 |
| `generation_kwh` | float | `1898.0` | Annual generation for this year |
| `efficiency_pct` | float | `100.0` | `(1 - 0.007)^(year-1) × 100` |
| `confidence_low_kwh` | float | `1708.2` | Lower bound |
| `confidence_high_kwh` | float | `2087.8` | Upper bound |
| `confidence_band_pct` | float | `10.0` | Band width percentage |

**`lifetime_prediction.assumptions` object:**

| Sub-field | Type | Example | Notes |
|-----------|------|---------|-------|
| `panel_area_m2` | float | `10.0` | Fixed 10m² basis for all Model 2 outputs |
| `panel_efficiency_pct` | float | `20.0` | Fixed 20% efficiency |
| `lifetime_years` | integer | `25` | Fixed 25-year projection |
| `annual_degradation_pct` | float | `0.7` | 0.7% per year compounding |
| `dry_months` | array | `[1, 2, 6, 7, 8, 12]` | Climatological dry season months |

**`lifetime_prediction.confidence` object:**

| Sub-field | Type | Example | Notes |
|-----------|------|---------|-------|
| `year_1_band_pct` | float | `10.0` | ±10% band for year 1 |
| `years_1_5_band_pct` | float | `10.0` | ±10% for years 1–5 |
| `years_6_15_band_pct` | float | `15.0` | ±15% for years 6–15 |
| `years_16_25_band_pct` | float | `20.0` | ±20% for years 16–25 |

**`lifetime_prediction.monthly_generation_climatology` — array of 12 objects:**

| Sub-field | Type | Example | Notes |
|-----------|------|---------|-------|
| `month` | integer | `1` | Numeric month index |
| `daily_kwh` | float | `5.1` | Typical daily generation for that month |
| `is_dry_season` | boolean | `true` | Whether month is in dry season |

**Full example response (with `month: 6`, `include_lifetime: true`):**
```json
{
  "status": "success",
  "location": { "latitude": -1.2921, "longitude": 36.8219 },
  "coordinate_validation": { "status": "valid", "warnings": [] },
  "monthly_generation": [
    { "month": "June", "month_index": 6, "daily_kwh": 5.2, "is_dry_season": true }
  ],
  "annual_summary": {
    "year_1_generation_kwh": 1898.0,
    "average_daily_kwh": 5.2
  },
  "lifetime_prediction": {
    "year_1_generation_kwh": 1898.0,
    "lifetime_total_kwh": 39250.0,
    "lifetime_average_annual_kwh": 1570.0,
    "yearly_breakdown": [
      {
        "year": 1,
        "generation_kwh": 1898.0,
        "efficiency_pct": 100.0,
        "confidence_low_kwh": 1708.2,
        "confidence_high_kwh": 2087.8,
        "confidence_band_pct": 10.0
      },
      {
        "year": 2,
        "generation_kwh": 1884.7,
        "efficiency_pct": 99.3,
        "confidence_low_kwh": 1696.2,
        "confidence_high_kwh": 2073.2,
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
    "monthly_generation_climatology": [
      { "month": 1, "daily_kwh": 5.1, "is_dry_season": true },
      { "month": 2, "daily_kwh": 4.9, "is_dry_season": true },
      { "month": 3, "daily_kwh": 4.8, "is_dry_season": false },
      { "month": 4, "daily_kwh": 4.5, "is_dry_season": false },
      { "month": 5, "daily_kwh": 4.3, "is_dry_season": false },
      { "month": 6, "daily_kwh": 5.2, "is_dry_season": true },
      { "month": 7, "daily_kwh": 5.4, "is_dry_season": true },
      { "month": 8, "daily_kwh": 5.3, "is_dry_season": true },
      { "month": 9, "daily_kwh": 4.6, "is_dry_season": false },
      { "month": 10, "daily_kwh": 4.4, "is_dry_season": false },
      { "month": 11, "daily_kwh": 4.7, "is_dry_season": false },
      { "month": 12, "daily_kwh": 5.0, "is_dry_season": true }
    ]
  },
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
  "note": "Predictions represent typical expected generation, not a daily weather forecast."
}
```

### Notable Logic
- **25-year degradation formula:** `efficiency = (1 - 0.007)^(year - 1)` — compounding from Year 1 at 100%.
- **Confidence bands widen over time:** ±10% years 1–5, ±15% years 6–15, ±20% years 16–25.
- **All outputs are for a 10m² system at 20% panel efficiency.** Model 4 scales these up using intelligent sizing (see below).
- **Payback period is explicitly descoped** — it does not appear anywhere in the output and must not be added by backend.
- **Geographic coverage:** SSA only. Coordinates outside lat −26→6, lon −18→44 return a 400 error.

---

## Model 3 — ROI Calculation

### Endpoint
```
POST /api/v1/calculate-roi
```

### Request Schema

| Field | Type | Required | Validation Rules | Example |
|-------|------|----------|-----------------|---------|
| `consumption_kwh` | float | ✅ Required | `0 < value ≤ 100,000` | `450.0` |
| `generation_kwh` | float | ✅ Required | `0 < value ≤ 100,000` | `500.0` |
| `tariff_per_kwh` | float | ✅ Required | `0 < value ≤ 100.0` | `0.20` |
| `system_cost_usd` | float | ✅ Required | `0 < value ≤ 1,000,000` | `6000.0` |
| `operating_hours` | float | Optional | `0–24` | `12.0` |
| `equipment_units` | integer | Optional | `0–500` | `3` |
| `business_type` | string | Optional | Non-empty, safe char set, max 64 chars | `"butchery"` |
| `location` | string | Optional | Non-empty string, max 128 chars | `"Nairobi, Kenya"` |

**Full example request body:**
```json
{
  "consumption_kwh": 450.0,
  "generation_kwh": 500.0,
  "tariff_per_kwh": 0.20,
  "system_cost_usd": 6000.0
}
```

### Response Schema (HTTP 200)

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `monthly_savings_usd` | float | `90.0` | `energy_offset_kwh × tariff_per_kwh` |
| `roi_percentage` | float | `18.0` | `(annual_savings / system_cost) × 100`, clamped 0–100% |
| `system_cost_usd` | float | `6000.0` | Echoes the input |

**Full example response:**
```json
{
  "monthly_savings_usd": 90.0,
  "roi_percentage": 18.0,
  "system_cost_usd": 6000.0
}
```

### Notable Logic
- **Energy offset** = `min(consumption_kwh, generation_kwh)` — generation in excess of consumption provides no additional savings.
- **ROI formula:** `(monthly_savings × 12 / system_cost) × 100`.
- **ROI clamped 0–100%** — no negative ROI or >100% values ever emitted.
- **Payback period: explicitly descoped** — not calculated, not returned.
- When called by Model 4 in the diesel scenario, `tariff_per_kwh` is replaced by the **blended tariff** (see Model 4 below), which reflects the weighted cost of grid + diesel power.

---

## Model 4 — Orchestration, System Sizing & Recommendation Engine

### Endpoint
```
POST /api/v1/analyze
```

This is the **single endpoint backend calls**. Model 4 internally calls Models 1, 2, and 3, then synthesises and returns the master response.

### Request Schema

**Required base fields:**

| Field | Type | Required | Validation Rules | Example |
|-------|------|----------|-----------------|---------|
| `business_name` | string | ✅ Required | 1–200 chars | `"Joe's Coffee Shop"` |
| `business_type` | string | ✅ Required | Any of: `"Restaurant"`, `"Retail"`, `"Office"`, `"Hotel"`, `"Cafe"`, `"Gym"`, `"Bakery"`, `"butchery"`, `"grocery"`, `"mini_supermarket"` | `"Cafe"` |
| `location` | string | ✅ Required | Non-empty string | `"Nairobi, Kenya"` |
| `latitude` | float | ✅ Required | `-90 ≤ value ≤ 90` | `-1.2921` |
| `longitude` | float | ✅ Required | `-180 ≤ value ≤ 180` | `36.8219` |

**Plus EITHER equipment_list OR business metrics (one of the two blocks is required):**

**Option A — `equipment_list` (preferred for frontend UX):**

| Field | Type | Required | Validation | Example |
|-------|------|----------|-----------|---------|
| `equipment_list` | array of objects | ✅ (if no metrics) | At least one object | See below |
| `equipment_list[].equipment_type` | string | ✅ | Any type from equipment dictionary | `"refrigerator"` |
| `equipment_list[].quantity` | integer | ✅ | Positive integer | `2` |
| `equipment_list[].hours_per_day` | float | ✅ | `0–24` | `24` |

Supported `equipment_type` values and their wattage estimates: `refrigerator` (150W), `freezer` (200W), `fridge` (150W), `cold_room` (500W), `display_cooler` (250W), `ice_maker` (300W), `oven` (2500W), `stove` (1500W), `microwave` (1000W), `grill` (2000W), `fryer` (2500W), `espresso_machine` (1500W), `coffee_maker` (800W), `air_conditioner` (1500W), `fan` (75W), `heater` (1500W), `lights` (60W), `led_lights` (20W), `fluorescent` (40W), `computer` (200W), `treadmill` (700W), `water_heater` (3000W), `dishwasher` (1800W). Unknown types default to 100W.

**Option B — Raw business metrics:**

| Field | Type | Required | Validation |
|-------|------|----------|-----------|
| `sqft_m2` | float | ✅ (if no equipment_list) | `0 < value ≤ 10,000` |
| `operating_hours_weekly` | float | ✅ (if no equipment_list) | `0 < value ≤ 168` |
| `num_refrigeration_units` | integer | ✅ (if no equipment_list) | `0 ≤ value ≤ 500` |

**Optional fields (all scenarios):**

| Field | Type | Default | Validation | Notes |
|-------|------|---------|-----------|-------|
| `tariff` | float | `0.15` | Positive float | Grid electricity cost, USD/kWh |
| `uses_diesel` | boolean | `false` | `true` or `false` | Triggers diesel replacement economics |
| `diesel_hours_per_day` | float | `12` | `0–24` | Only used if `uses_diesel: true` |
| `diesel_price_per_liter` | float | `1.20` | `0–10` | USD/liter |
| `num_workers` | integer | `5` | `1–1000` | Passed through to Model 1 |
| `months_per_year` | integer | `12` | `1–12` | Passed through to Model 1 |

**Full example request — equipment_list path (grid-only):**
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
    { "equipment_type": "lights", "quantity": 15, "hours_per_day": 12 }
  ],
  "tariff": 0.15,
  "uses_diesel": false
}
```

**Full example request — diesel replacement:**
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

### Internal Orchestration Flow (What Model 4 Does Before Responding)

```
1. Receive /api/v1/analyze request
2. If equipment_list provided → convert to {sqft_m2, operating_hours_weekly, num_refrigeration_units}
3. Call Model 1 → get estimated_consumption_kwh_monthly
4. Call Model 2 (current month, include_lifetime=true) → get base generation for 10m² system
5. Intelligent System Sizing:
     target_coverage = 0.90
     required_generation = consumption_kwh × 0.90
     scaling_factor = required_generation / base_generation_10m2_kwh
     scaling_factor = clamp(scaling_factor, min=1.0, max=5.0)
     scaled_generation_kwh = base_generation_kwh × scaling_factor
     recommended_panel_area_m2 = 10.0 × scaling_factor  (max 50m²)
     system_cost_usd = 6000 × scaling_factor  (base $600/m²)
6. Diesel Economics (if uses_diesel = true):
     diesel_fraction = diesel_hours_per_day / 24
     diesel_kwh_monthly = consumption_kwh × diesel_fraction
     liters_per_kwh = 0.40  (partial load efficiency for small generators)
     diesel_liters_monthly = diesel_kwh_monthly × 0.40
     diesel_fuel_cost = diesel_liters_monthly × diesel_price_per_liter
     diesel_maintenance_cost = diesel_hours_per_day × 30 × $0.50/hour
     blended_tariff = total_monthly_cost / consumption_kwh
7. Call Model 3 with:
     consumption_kwh = estimated_consumption_kwh_monthly
     generation_kwh = scaled_generation_kwh
     tariff_per_kwh = blended_tariff (or grid tariff if grid-only)
     system_cost_usd = scaled_system_cost
8. Viability Scoring:
     roi_score:
       roi ≤ 0%      → 0 pts
       roi ≤ 5%      → roi × 3          (max 15 pts)
       roi ≤ 20%     → 15 + (roi-5)×1.5  (max 37.5 pts)
       roi > 20%     → min(50, 37.5 + (roi-20)×0.625)
     coverage_ratio = (generation_kwh / consumption_kwh) × 100
     coverage_score = min(30, coverage_ratio × 0.3)
     savings_score  = min(20, monthly_savings / 25)
     viability_score = roi_score + coverage_score + savings_score  (max 100)
     
     viability_score ≥ 65 → "High" / "HIGHLY VIABLE"
     viability_score ≥ 40 → "Medium" / "MODERATELY VIABLE"
     viability_score < 40 → "Low" / "NOT VIABLE"
9. Compose and return master response (see below)
```

---

### Response Schema — `/api/v1/analyze` (HTTP 200)

**Core fields (always present):**

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `business_name` | string | `"Joe's Coffee Shop"` | Echoes input |
| `business_type` | string | `"Cafe"` | Echoes input |
| `location` | string | `"Nairobi, Kenya"` | Echoes input |
| `estimated_consumption_kwh` | float | `450.0` | From Model 1 |
| `predicted_generation_kwh` | float | `405.0` | Scaled from Model 2 (not 10m² base) |
| `recommended_panel_area_m2` | float | `10.0` | Result of intelligent sizing; 10–50m² |
| `roi_percentage` | float | `18.0` | From Model 3 |
| `monthly_savings` | float | `90.0` | From Model 3 (`monthly_savings_usd`) |
| `system_cost` | float | `6000.0` | Scaled system cost ($600/m²) |
| `recommendation` | string | `"Medium"` | `"High"`, `"Medium"`, or `"Low"` |
| `viability_score` | float | `55.0` | Composite score 0–100 |
| `status` | string | `"MODERATELY VIABLE"` | `"HIGHLY VIABLE"`, `"MODERATELY VIABLE"`, `"NOT VIABLE"` |
| `explanation` | string | `"Solar is moderately viable because: ..."` | Human-readable explanation string |
| `confidence` | float | `85.0` | Percentage (0–100); derived from Model 1 confidence_score × 100 |
| `analyzed_at` | string (ISO 8601) | `"2025-01-15T10:30:00.000000"` | Timestamp of analysis |
| `energy_scenario` | string | `"grid_only"` | `"grid_only"` or `"diesel_replacement"` |
| `current_energy_cost.total_monthly` | float | `67.50` | Total baseline monthly energy cost (USD) |
| `current_energy_cost.diesel_monthly` | float | `0.0` | Diesel portion (0 if grid-only) |
| `current_energy_cost.grid_monthly` | float | `67.50` | Grid portion |

**`lifetime_prediction` object (always present — forwarded from Model 2):**

> **Implementation note for backend/DSE:** Model 4 already calls Model 2 with `include_lifetime=True` and the full `lifetime_prediction` object is available in `generation_data` at the point where the `result` dict is assembled. The only change required is adding one line to the `analyze()` result dict in `model4_app.py`:
> ```python
> 'lifetime_prediction': generation_data.get('lifetime_prediction'),
> ```
> No additional Model 2 call is needed. The data is already in memory.

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `lifetime_prediction.year_1_generation_kwh` | float | `1898.0` | Annual generation at full system efficiency (Year 1) |
| `lifetime_prediction.lifetime_total_kwh` | float | `39250.0` | Cumulative generation across 25 years with degradation |
| `lifetime_prediction.lifetime_average_annual_kwh` | float | `1570.0` | `lifetime_total / 25` |
| `lifetime_prediction.yearly_breakdown` | array (25 objects) | See below | One entry per year |
| `lifetime_prediction.yearly_breakdown[].year` | integer | `1` | Year number 1–25 |
| `lifetime_prediction.yearly_breakdown[].generation_kwh` | float | `1898.0` | Annual generation for that year |
| `lifetime_prediction.yearly_breakdown[].efficiency_pct` | float | `100.0` | `(1 - 0.007)^(year-1) × 100` |
| `lifetime_prediction.yearly_breakdown[].confidence_low_kwh` | float | `1708.2` | Lower confidence bound |
| `lifetime_prediction.yearly_breakdown[].confidence_high_kwh` | float | `2087.8` | Upper confidence bound |
| `lifetime_prediction.yearly_breakdown[].confidence_band_pct` | float | `10.0` | Band percentage (10% yrs 1–5, 15% yrs 6–15, 20% yrs 16–25) |
| `lifetime_prediction.assumptions.panel_area_m2` | float | `10.0` | **Note:** This reflects the 10m² Model 2 base. The actual system area is `recommended_panel_area_m2`. Generation values are already scaled. |
| `lifetime_prediction.assumptions.panel_efficiency_pct` | float | `20.0` | Fixed 20% efficiency assumption |
| `lifetime_prediction.assumptions.lifetime_years` | integer | `25` | Fixed 25-year projection |
| `lifetime_prediction.assumptions.annual_degradation_pct` | float | `0.7` | 0.7% per year compounding |
| `lifetime_prediction.assumptions.dry_months` | array | `[1, 2, 6, 7, 8, 12]` | Climatological dry season months |
| `lifetime_prediction.confidence.year_1_band_pct` | float | `10.0` | ±10% for year 1 |
| `lifetime_prediction.confidence.years_1_5_band_pct` | float | `10.0` | ±10% for years 1–5 |
| `lifetime_prediction.confidence.years_6_15_band_pct` | float | `15.0` | ±15% for years 6–15 |
| `lifetime_prediction.confidence.years_16_25_band_pct` | float | `20.0` | ±20% for years 16–25 |
| `lifetime_prediction.monthly_generation_climatology` | array (12 objects) | See below | 12-month typical daily profile |
| `lifetime_prediction.monthly_generation_climatology[].month` | integer | `6` | Month index 1–12 |
| `lifetime_prediction.monthly_generation_climatology[].daily_kwh` | float | `5.2` | Typical daily generation for that month |
| `lifetime_prediction.monthly_generation_climatology[].is_dry_season` | boolean | `true` | Whether month falls in dry season |

**Conditional `diesel_details` object (only present when `uses_diesel: true`):**

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `diesel_details.hours_per_day` | float | `18` | Diesel generator runtime |
| `diesel_details.price_per_liter` | float | `1.35` | Input diesel price |
| `diesel_details.monthly_liters` | float | `194.4` | `diesel_kwh_monthly × 0.40 liters/kWh` |
| `diesel_details.effective_tariff` | float | `0.63` | True cost of diesel power (USD/kWh) |
| `diesel_details.diesel_kwh_monthly` | float | `337.5` | Energy served by diesel each month |

**Full example response — grid-only:**
```json
{
  "business_name": "Joe's Coffee Shop",
  "business_type": "Cafe",
  "location": "Nairobi, Kenya",
  "estimated_consumption_kwh": 450.0,
  "predicted_generation_kwh": 405.0,
  "recommended_panel_area_m2": 10.0,
  "roi_percentage": 18.0,
  "monthly_savings": 90.0,
  "system_cost": 6000.0,
  "recommendation": "Medium",
  "viability_score": 55.0,
  "status": "MODERATELY VIABLE",
  "explanation": "Solar is moderately viable because: Moderate ROI of 18.0%; Good solar coverage (90%).",
  "confidence": 85.0,
  "analyzed_at": "2025-01-15T10:30:00.000000",
  "energy_scenario": "grid_only",
  "current_energy_cost": {
    "total_monthly": 67.50,
    "diesel_monthly": 0.0,
    "grid_monthly": 67.50
  },
  "lifetime_prediction": {
    "year_1_generation_kwh": 1898.0,
    "lifetime_total_kwh": 39250.0,
    "lifetime_average_annual_kwh": 1570.0,
    "yearly_breakdown": [
      {
        "year": 1, "generation_kwh": 1898.0, "efficiency_pct": 100.0,
        "confidence_low_kwh": 1708.2, "confidence_high_kwh": 2087.8, "confidence_band_pct": 10.0
      },
      {
        "year": 2, "generation_kwh": 1884.7, "efficiency_pct": 99.3,
        "confidence_low_kwh": 1696.2, "confidence_high_kwh": 2073.2, "confidence_band_pct": 10.0
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
    "monthly_generation_climatology": [
      { "month": 1, "daily_kwh": 5.1, "is_dry_season": true },
      { "month": 6, "daily_kwh": 5.2, "is_dry_season": true }
    ]
  }
}
```

**Full example response — diesel replacement:**
```json
{
  "business_name": "Mombasa Cold Storage",
  "business_type": "Retail",
  "location": "Mombasa, Kenya",
  "estimated_consumption_kwh": 756.0,
  "predicted_generation_kwh": 680.4,
  "recommended_panel_area_m2": 30.0,
  "roi_percentage": 34.5,
  "monthly_savings": 285.0,
  "system_cost": 18000.0,
  "recommendation": "High",
  "viability_score": 78.2,
  "status": "HIGHLY VIABLE",
  "explanation": "Solar is highly viable because: Strong ROI of 34.5%; Excellent solar coverage (90%).; Significant savings ($285/mo).",
  "confidence": 85.0,
  "analyzed_at": "2025-01-15T10:30:00.000000",
  "energy_scenario": "diesel_replacement",
  "current_energy_cost": {
    "total_monthly": 492.0,
    "diesel_monthly": 356.0,
    "grid_monthly": 136.0
  },
  "diesel_details": {
    "hours_per_day": 18,
    "price_per_liter": 1.35,
    "monthly_liters": 194.4,
    "effective_tariff": 0.63,
    "diesel_kwh_monthly": 378.0
  }
}
```

### Error Response (HTTP 503 — one or more models failed)
```json
{
  "error": "Service Unavailable",
  "message": "Unable to complete analysis",
  "business_name": "Joe's Coffee Shop",
  "status": "INCOMPLETE"
}
```

---

## Cross-Model Data Flow Summary

```
Frontend/Backend → POST /api/v1/analyze (Model 4)
                        │
                        ├─→ Model 1: estimate-consumption
                        │     In:  business_type, sqft_m2, hours_weekly, 
                        │          num_refrigeration_units, location
                        │     Out: estimated_consumption_kwh_monthly, 
                        │          confidence_score, breakdown
                        │
                        ├─→ Model 2: predict-generation
                        │     In:  latitude, longitude, month (current), 
                        │          include_lifetime=true
                        │     Out: monthly_generation, annual_summary,
                        │          lifetime_prediction (25yr array)
                        │
                        │   [Intelligent sizing: scale 10m² base to 90% coverage]
                        │   [Diesel economics: compute blended tariff if applicable]
                        │
                        ├─→ Model 3: calculate-roi
                        │     In:  consumption_kwh, scaled_generation_kwh,
                        │          blended_tariff_per_kwh, system_cost_usd
                        │     Out: monthly_savings_usd, roi_percentage, 
                        │          system_cost_usd
                        │
                        └─→ Compose master response → return to Backend/Frontend
```

---

## Explicitly Descoped Fields

The following fields are confirmed out of scope and must not appear in any response, be computed by backend, or be referenced in the UI:

| Field | Reason |
|-------|--------|
| `payback_period_years` | Explicitly removed from project; noted in both Model 2 and Model 3 source code comments |
| Any installer/vendor recommendation | Product is vendor-agnostic |
| Live energy monitoring data | SolarSense is pre-investment decision support only |

---

## Authentication & Rate Limits

| Concern | Specification |
|---------|--------------|
| Auth header | `X-API-KEY: <value>` on all `/api/` routes |
| Missing/invalid key | HTTP 401 |
| Rate limit | 100 requests/minute per IP |
| Rate limit exceeded | HTTP 429 |
| Max request size | 100 KB |
| Payload too large | HTTP 413 |
