
================================================================================
MODEL CARD: Energy Consumption Prediction for African Food Retail SMEs
================================================================================

1. MODEL PURPOSE AND USE CASE
--------------------------------------------------------------------------------
This model predicts **annual** electricity consumption (kWh) for commercial food retail
buildings (food sales / food service) and is then adapted to provide **monthly**
estimates for refrigeration-heavy food retail SMEs (butcheries, grocers,
mini-supermarkets) in Sub-Saharan Africa.

Primary Use Case:
- Estimate energy consumption when smart meter data is unavailable
- Support solar viability assessments for African SMEs
- Provide energy breakdown (refrigeration vs. other equipment)

Target Users:
- Solar energy providers assessing SME viability
- Business owners planning energy infrastructure
- Financial institutions evaluating solar loan applications

2. TRAINING DATA DESCRIPTION
--------------------------------------------------------------------------------
Dataset: CBECS 2018 (US Commercial Buildings Energy Consumption Survey)
- Filtered to food-related businesses (PBA codes 11 and 12)
- PBA 11: Food Sales (Grocery stores, supermarkets)
- PBA 12: Food Service (Restaurants, cafeterias)

Training Set:
- Samples: 232
- Features: 17
- Target: **Annual** electricity consumption (kWh)

Test Set:
- Samples: 59
- Test R² Score: 0.9830
- MAPE: 14.52%

3. FEATURE DESCRIPTIONS
--------------------------------------------------------------------------------
Core Features:
- SQFT: Square footage (building size)
- WKHRS: Weekly operating hours
- RFGCOMPN: Number of refrigeration/freezer units
- NFLOOR: Number of floors
- NWKER: Number of workers
- MONUSE: Months in use per year
- YRCONC: Year of construction category

Engineered Features:
- kwh_per_sqft: Energy intensity (kWh per square foot)
- sqft_per_worker: Space efficiency metric
- wkhrs_per_week_normalized: Fraction of full week operating
- annual_operating_hours: Estimated annual operating hours
- refrigeration_density: Refrigeration units per 1000 sqft
- is_high_refrigeration: Binary indicator (> median units)
- is_extended_hours: Binary indicator (> 60 hours/week)
- size_category: Categorical (small/medium/large)

Encoded Features:
- pba_encoded: Label-encoded business type
- cendiv_encoded: Label-encoded census division
- size_category_encoded: Label-encoded size category

4. MODEL PERFORMANCE & TARGET TRANSFORMATION
--------------------------------------------------------------------------------
Best Model: Gradient Boosting Regressor (with optional log-transformed target)

Target Transformation:
- Training target: `y = annual_kwh`
- For the selected best model, training is performed on:
  - `log_y = log1p(annual_kwh)` when `use_log_target=True`
- At prediction time (when `use_log_target=True`):
  - `annual_kwh_pred = expm1(model.predict(features))`
- The deployed API (`app_ml.py`) always returns **monthly** kWh:
  - `monthly_kwh = (annual_kwh_pred * climate_factor) / 12`

Performance Metrics (on annual target):
- Test R² Score: 0.9830
- Test MAPE: 14.52%
- Cross-Validation R²: 0.8683 ± 0.1255

Interpretation:
- R² of 0.9830 indicates the model explains 98.3% of variance in annual energy consumption
- MAPE of 14.52% means predictions are within ~14.5% on average
- Acceptable for MVP with ±20% target error margin

5. LIMITATIONS AND KNOWN BIASES
--------------------------------------------------------------------------------
Data Source Limitations:
- Trained on US commercial building data (CBECS 2018)
- May not fully capture African SME operational patterns
- US building standards and equipment efficiency differ from African context

Geographic Limitations:
- Climate adjustments are approximate (city-level factors)
- Does not account for local grid reliability issues
- May underestimate consumption in areas with frequent power outages

Business Type Limitations:
- Generalizes across butchery/grocery/mini-supermarket types
- Does not account for specific refrigeration technologies
- Assumes standard equipment efficiency

Model Limitations:
- ±20% error margin acceptable for MVP
- Predictions are estimates, not guarantees
- Should be validated with real-world African SME data when available

6. RECOMMENDED USAGE
--------------------------------------------------------------------------------
When to Use:
- Initial energy consumption estimates for solar viability assessment
- Planning energy infrastructure for new businesses
- Comparing energy needs across similar businesses

When NOT to Use:
- Precise billing or financial calculations requiring exact kWh
- Businesses with highly specialized equipment not represented in training data
- Non-food retail businesses (model trained on food retail only)

Input Requirements (deployed API, `app_ml.py`):
- `business_type` (one of: `butchery`, `grocery`, `mini_supermarket`)
- `sqft_m2` (approximate floor area in m²; 0 < `sqft_m2` ≤ 10,000)
- `operating_hours_weekly` (0 < hours ≤ 168)
- `num_refrigeration_units` (0 ≤ units ≤ 500)
- `location` (city, country – used for climate adjustment)
- Optional: `num_workers` (defaults to 5, capped at 1000), `months_per_year` (defaults to 12)

7. AFRICAN ADAPTATION & POST-PROCESSING
--------------------------------------------------------------------------------
Climate Adjustments:
- Climate adjustment factor derived from city substring in `location`
- Factors range approximately from 1.18 (moderate) to 1.35 (hot/humid)
- If no city match is found, a default factor of 1.20 is applied

Business Context Adaptations:
- Assumes single-floor operations (NFLOOR=1) typical for African SMEs
- Defaults to moderate construction age (YRCONC=5)
- Uses conservative worker-to-space ratios via `sqft_per_worker`

Refrigeration Focus & Breakdown:
- Refrigeration share enforced between 50% and 70% of total monthly kWh
- `refrigeration_kwh = monthly_kwh * refrigeration_share`
- `other_kwh = monthly_kwh * (1 - refrigeration_share)`
- Refrigeration share heuristic increases with `num_refrigeration_units` relative to `num_workers`

API Output Post-Processing:
- Annual kWh prediction is multiplied by climate factor and divided by 12 to obtain monthly kWh
- Monthly kWh is capped at a maximum of 1,000,000 kWh to avoid unrealistic values
- Negative energy values (if any) are reset to zero
- Confidence score is kept within [0, 1] (typically 0.75 or 0.85 depending on data completeness)

8. MODEL VERSION AND METADATA
--------------------------------------------------------------------------------
Model Version: v1.0
Training Date: 2026-02-12
Framework: Gradient Boosting
Python Version: 3.x
Dependencies: scikit-learn, xgboost, pandas, numpy, joblib

Model Files:
- energy_consumption_model_v1.joblib (model + metadata)
- energy_scaler_v1.joblib (feature scaler)
- feature_columns_v1.joblib (feature names)
- sme_mappings_v1.joblib (encoders + mappings)

9. VALIDATION CONSTRAINTS (DEPLOYED API)
--------------------------------------------------------------------------------
Key validation rules enforced in the Flask API (`app_ml.py`):

- **business_type**:
  - Must be one of: `butchery`, `grocery`, `mini_supermarket` (case-insensitive input)
- **sqft_m2**:
  - Must be > 0 and ≤ 10,000
- **operating_hours_weekly**:
  - Must be > 0 and ≤ 168 (hours per week)
- **num_refrigeration_units**:
  - Must be ≥ 0 and ≤ 500
- **num_workers** (optional):
  - Defaults to 5 if missing/invalid
  - Must not exceed 1000 (otherwise rejected)
- **months_per_year** (optional):
  - Defaults to 12 if missing/invalid
  - Reset to 12 if ≤ 0 or > 12
- **location**:
  - Must be a string with length ≤ 200 characters

These constraints ensure numerical stability and protect against obviously incorrect inputs.

10. FUTURE IMPROVEMENTS
--------------------------------------------------------------------------------
- Collect and train on African SME energy consumption data
- Add more granular climate zones and seasonal adjustments
- Include equipment-specific power ratings
- Account for grid reliability and backup power usage
- Expand to other business types beyond food retail

================================================================================




