# Minimal-input viability assessment

The public prototype accepts details a shop owner can reasonably know: business type, floor area, weekly opening hours, refrigeration count and power source. It estimates consumption, sizes a possible solar system, estimates generation and shows conditional costs, payback and next steps. Consumption, panel capacity, installation prices and tariffs are outputs or editable assumptions, rather than required technical inputs.

## Consumption model repair

The inherited consumption API loaded a trained artifact but served an area/hours/refrigeration formula. That behavior already existed in commit `6bb92fb`, before the portfolio changes. It was not introduced by the scenario extension. The previous extension nevertheless made the wrong product choice: it asked users to supply electrical consumption instead of connecting the consumption estimator to the viability flow.

Simply calling the inherited artifact is not defensible. Its notebook calculates `kwh_per_sqft = ELCNS / SQFT`, then retains this target-derived value as a predictor. Unknown consumption therefore cannot be estimated without supplying a feature derived from the unknown answer. Its high historical scores are not valid performance evidence for this use case. The same notebook mislabels activity codes 11 and 12 as food sales and food service. The [official EIA 2018 questionnaire](https://www.eia.gov/consumption/commercial/data/2018/pdf/eia871aij_2018.pdf) identifies food sales as code 6 and food service as code 15.

`scripts/train_consumption_observable.py` trains a separate gradient-boosted regression model on the retained CBECS 2018 CSV. It uses only floor area, weekly hours, refrigeration-unit count and a broad food-service indicator. It filters to the correct 309 food sales/service buildings with positive available electricity, floor area and hours. It makes a fixed, stratified 80/20 split: 247 training buildings and 62 held-out buildings. Missing refrigeration counts are imputed with the training median; 241 of 309 records have this missing value. There is no target trimming, target-derived feature, holdout-driven tuning or fabricated local calibration. The original artifacts remain unchanged.

The fixed model has 200 depth-3 trees, learning rate 0.1 and seed 42; it fits log1p annual electricity consumption and applies expm1 at inference. On the US building holdout, MAPE is **63.05%**, MAE **211,876 kWh/year**, and R² **0.668**. A training-only median consumption-per-area baseline is better: **59.03% MAPE**, MAE **176,200 kWh/year**, R² **0.824**. A constant training-median baseline has 97.35% MAPE. This is an exploratory model demonstration, not evidence of accurate African SME prediction. Floor areas below the training range produce an explicit warning. Cold storage is a food-sales proxy, not a validated warehouse model. No confidence percentage is invented.

The model is exported as exact tree nodes, thresholds and leaf values in `consumption_observable_v1.json`. Python and browser inference both use float32 features for sklearn-compatible comparisons, sum the same trees and convert annual to monthly by dividing by 12. The export is checked against sklearn predictions on every holdout record before saving. The API checks the exported model's SHA-256 against the evaluation receipt. Browser code runs these trees locally for arbitrary supported inputs; it does not look up a canned scenario or need a hosted backend.

## Appliances and system sizing

Equipment counts feed the model's combined refrigeration count; subtype-specific hours are not learned model features. A separate visible equipment crosscheck uses quantity × hours/day × watts × 365/12 / 1,000. Freezer (300 W), fridge (200 W), cold room (6,000 W) and lighting (60 W) follow the inherited MVP defaults; display cooler (350 W) and ice machine (500 W) are new illustrative values. These wattages are assumptions, not measured appliance ratings. Crosscheck values do not silently change the learned consumption output or size the system.

Solar sizing starts with modeled annual consumption. The available roof defaults to 60% of floor area; target annual solar offset is 80%, estimated self-consumption 80%, panel efficiency 20%, panel rating 0.4 kW and performance ratio 85%. Capacity is limited by assumed roof area and rounded down to whole panels. All of these are visible, editable demonstration assumptions; a roof survey can give a different answer.

Generation uses the retained monthly Nairobi solar baseline because it performed better on Nairobi's held-out irradiance-derived target: 8.43% MAPE versus XGBoost's 12.53%. That comparison does not validate a real installation. Generation is scaled by capacity and performance ratio; usable offset is capped against modeled consumption separately each month. No exports, batteries or hourly dispatch are simulated.

## Costs and recommendations

Illustrative prices are KES 25/kWh for grid electricity, KES 55/kWh for diesel-equivalent electricity, KES 100,000 per installed kW and annual maintenance of 1% of installation cost. Hybrid supply assumes 40% diesel share. These are fictional settings, not current Kenyan tariff research or installer quotations. Costs compare annual modeled demand with solar offset, subtract maintenance from gross avoided cost, and report simple payback only for positive net savings and nonzero installation cost. Financing, tax, replacements and discounting are omitted.

The recommendation is a transparent screening rule, not another trained model. Payback up to 10 years without training-range warnings produces “promising under assumptions”; other cases require site assessment. Every case still requires bills, roof inspection and a quote. No implementation should present conditional savings as observed savings.

## Reproduction and local endpoints

From the repository's documented Python environment:

```powershell
python scripts/train_consumption_observable.py
python scripts/export_assessment.py
python -m pytest -q
```

`GET /api/v1/assessment/evidence` serves the evaluated tree export, solar profiles, assumptions and provenance. `POST /api/v1/assessment` accepts the minimal input contract in `solar_scenario/assessment.py`. The existing gateway registers these routes. Bad input returns 400 and missing or mismatched artifacts return 503. Legacy authenticated endpoints and the older optional `/api/v1/scenario` arithmetic endpoint remain available; they are not the public wizard's primary path.
