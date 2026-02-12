
================================================================================
MODEL CARD: Energy Consumption Prediction for African Food Retail SMEs
================================================================================

1. MODEL PURPOSE AND USE CASE
--------------------------------------------------------------------------------
This model predicts monthly electricity consumption (kWh) for refrigeration-heavy
food retail businesses (butcheries, grocers, mini-supermarkets) in Sub-Saharan Africa.

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
- Target: Annual electricity consumption (kWh)

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

4. MODEL PERFORMANCE METRICS
--------------------------------------------------------------------------------
Best Model: Gradient Boosting (Log)
Target Transformation: Log-transformed

Performance Metrics:
- Test R² Score: 0.9830
- Test MAPE: 14.52%
- Cross-Validation R²: 0.8683 ± 0.1255

Interpretation:
- R² of 0.9830 indicates the model explains 98.3% of variance in energy consumption
- MAPE of 14.52% means predictions are within ±14.5% on average
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

Input Requirements:
- Business type (butchery/grocery/mini_supermarket)
- Floor area (m² or sqft)
- Weekly operating hours
- Number of refrigeration units
- Location (for climate adjustment)
- Optional: Number of workers, months per year

7. AFRICAN ADAPTATION NOTES
--------------------------------------------------------------------------------
Climate Adjustments:
- Applied 86.8% increase for Sub-Saharan African climates
- Factors range from 1.18 (moderate) to 1.35 (hot/humid)
- Based on increased refrigeration load in hot climates

Business Context Adaptations:
- Assumes single-floor operations (typical for African SMEs)
- Defaults to moderate construction age (YRCONC=5)
- Uses conservative worker-to-space ratios

Refrigeration Focus:
- Model emphasizes refrigeration equipment (50-70% of consumption)
- Critical for food retail businesses in hot climates
- Accounts for higher cooling loads in African context

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

9. FUTURE IMPROVEMENTS
--------------------------------------------------------------------------------
- Collect and train on African SME energy consumption data
- Add more granular climate zones and seasonal adjustments
- Include equipment-specific power ratings
- Account for grid reliability and backup power usage
- Expand to other business types beyond food retail

================================================================================
