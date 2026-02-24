### Model Card: Climatological Solar Generation – XGBoost

**Model name**: XGBoost Climatological Solar Generation Regressor  
**Version**: 1.0  
**Owner**: SolarSense DSE Team – Model 2 (Solar Generation)

---

### 1. Purpose and Scope

- **Goal**: Estimate **typical daily solar energy generation** (kWh/day) for small solar systems in Sub-Saharan Africa, not short-term weather forecasts.
- **Primary use case**: Support solar viability assessment for SMEs and households by:
  - Quantifying expected daily output for given coordinates.
  - Feeding downstream financial and sizing models.
- **Out of scope**:
  - Hour-by-hour or day-by-day forecasting.
  - Cloud-resolving weather prediction.

---

### 2. Inputs

- **Features (all numeric):**
  - `latitude` – decimal degrees.
  - `longitude` – decimal degrees.
  - `abs_latitude` – absolute latitude (|latitude|).
  - `month` – integer (1–12).
  - `is_dry_season` – binary (1 if month in {12,1,2,6,7,8}, else 0).

- **Coordinate validity:**
  - Hard error: lat [-34, 16], lon [-18, 45].
  - Warning zone: lat < -26 or lat > 12 (predictions returned with a warning flag).

---

### 3. Outputs

- **Core prediction**:
  - `generation_kwh` – typical daily generation (kWh/day) for:
    - 10 m² of panels.
    - 20% panel efficiency.

- **Lifetime projection (via helper)**:
  - `year_1_generation_kwh`
  - `lifetime_total_kwh`
  - `lifetime_average_annual_kwh`
  - `yearly_breakdown` (per-year generation, efficiency %, and confidence band).

---

### 4. Data and Training

- **Source**: NASA POWER API (Renewable Energy community).
- **Coverage**:
  - **20 SSA cities** (Full list returned by `GET /api/v1/model-info`).
  - **Period**: 2 years of daily GHI data per site.

- **Preprocessing**:
  - Filter to `data_quality == "good"`.
  - Aggregate to **monthly mean GHI** per city.
  - Derive:
    - `abs_latitude`
    - `is_dry_season`
  - Target:
    - `target_avg_generation_kwh = avg_ghi_kwh_m2 * 10 * 0.2`.

- **Model**: XGBoost Booster loaded via native JSON format (XGBoost ≥ 2.0). Inference uses `xgb.DMatrix` and `Booster.predict()`, not the sklearn-compatible `XGBRegressor` API.

---

### 5. Performance

- **Metric**: Mean Absolute Percentage Error (MAPE).
- **Validation scheme**: **Location-based split** (entire cities held out).
- **Reported performance**:
  - Overall validation MAPE: **7.46%**.
  - Target requirement: **≤ 15%** (met).

Per-location MAPE is visualised in `outputs/per_location_validation.png`.

---

### 6. Assumptions and Limitations

- **Assumptions**:
  - 10 m² panel area, 20% efficiency.
  - Typical daily generation is proportional to monthly mean GHI.
  - Annual degradation rate: 0.7%/year (for lifetime projections).
  - Dry-season months: {12, 1, 2, 6, 7, 8}.

- **Limitations**:
  - Coordinates **outside** \[-26, 6] lat and \[-18, 44] lon are not supported.
  - Predictions near edges of the region (lat < -20 or > 2) have higher uncertainty.
  - Does not account for:
    - Shading, tilt, orientation, or local obstructions.
    - System losses (inverters, wiring, soiling) beyond the fixed efficiency assumption.

---

### 7. Artifacts and Loading

- **Artifact paths (relative to `models/solar_generation`)**:
  - Model directory (`MODEL_DIR` env var, default: `models/`)
    - `xgboost_climatological_model_v2.json` – trained XGBoost model (native JSON)
    - `feature_columns_v2.pkl` – ordered feature list used at training/inference
    - `xgboost_climatological_metadata_v2.json` – metadata (type, MAPE, locations, features)
- **Runtime loader**: `solar_climatology_service.load_model_artifacts()`
  - Validates that all three artifacts exist.
  - Used by both the Flask API and the climatological notebook.
  - Loads model via `Booster.load_model()`.

---

### 8. API Usage Examples

- **Core endpoint**: `POST /api/v1/predict-generation`

Example request:

```json
{
  "latitude": -1.2921,
  "longitude": 36.8219,
  "month": 6,
  "include_lifetime": true
}
```

*Note: `include_lifetime` defaults to `false`. The example above passes it explicitly as `true`. Omitting it will return a response without `lifetime_prediction`.*

Example response (truncated):

```json
{
  "status": "success",
  "location": {"latitude": -1.2921, "longitude": 36.8219},
  "monthly_generation": [
    {"month": "June", "month_index": 6, "daily_kwh": 5.9, "is_dry_season": true}
  ],
  "annual_summary": {
    "year_1_generation_kwh": 2150.0,
    "average_daily_kwh": 5.9
  },
  "lifetime_prediction": {
    "total_kwh": 49000.0,
    "average_annual_kwh": 1960.0,
    "lifetime_years": 25,
    "yearly_breakdown": [...]
  },
  "assumptions": {...},
  "confidence": {...}
}
```

---

### 9. Confidence Intervals

- Confidence intervals are **heuristic**, based on the difficulty of long-horizon solar yield prediction rather than strict statistical bounds.
- For year-level projections:
  - Years 1–5: ±10%
  - Years 6–15: ±15%
  - Years 16–25: ±20%
- These are implemented as multiplicative bands around each year's expected generation (`confidence_low_kwh`, `confidence_high_kwh`) in the `yearly_breakdown`.




