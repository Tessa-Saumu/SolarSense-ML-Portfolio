# Solar component: current evaluated model

The personal portfolio scenario uses `flagship_solar_xgb.json`: a fixed XGBoost regression model evaluated on five complete held-out cities. The target is **irradiance-derived theoretical output**, not measured electricity from real installations.

## Data and target

The inherited `solar_data_20cities_4yr.csv` contains **29,200 daily records for 20 cities**, dated **2022-02-22 to 2026-02-20**. This corrects the earlier card's two-year description. The repository labels it NASA POWER data; original upstream responses and extraction receipts were not independently verified in this release.

The script strips whitespace from headers and city labels, excludes **100 missing GHI values** despite their `good` quality flags, checks duplicate city/date records and positive finite irradiance, and aggregates **29,100 usable observations into 240 city/month means**. GHI means global horizontal irradiance, measured here in kWh/m²/day.

Target = monthly mean GHI × **10 m²** reference panel area × **0.20** efficiency. These fixed assumptions are not installation measurements. There is no tilt, shade, weather forecasting or inverter-loss model.

## Features and frozen split

Features: latitude, longitude, absolute latitude, month, and a fixed dry-season indicator for months 12, 1, 2, 6, 7 and 8. This flag is a broad inherited assumption, not a local climate classification.

The holdout list was declared before fitting: **Abidjan, Cape Town, Johannesburg, Lusaka and Nairobi**. All 12 monthly rows from each are excluded from training: **15 training cities / 180 rows; 5 test cities / 60 rows**. Nairobi was included so the demo exercises an unseen city. Historical Nairobi observations are evaluation labels, not model inputs. No future-time holdout is claimed.

XGBoost uses 400 trees, depth 4, learning rate 0.05, row/column subsampling 0.9, seed 42, histogram trees and one worker. Parameters were fixed from the inherited script; no search, early stopping or all-city refit. The baseline predicts each calendar month's average target **using training cities only**, without coordinates.

## Fresh evaluation

| Metric | XGBoost | Month-only baseline |
|---|---:|---:|
| Mean absolute error, kWh/day | 1.2442 | 1.6306 |
| Root mean squared error, kWh/day | 1.7607 | 2.1182 |
| Mean absolute percentage error | 11.2056% | 16.0544% |
| R² | 0.4800 | 0.2473 |

These measure prediction of the derived reference-system target, not observed solar yield. R² compares error with a mean-target predictor; negative R² means worse than that reference for the evaluated city.

| Held-out city | Model percentage error | Baseline percentage error |
|---|---:|---:|
| Abidjan | 6.07% | 16.21% |
| Cape Town | 24.04% | 34.08% |
| Johannesburg | 8.80% | 12.95% |
| Lusaka | 4.59% | 8.60% |
| Nairobi | **12.53%** | **8.43%** |

The model improves aggregate error but **loses to the baseline in Nairobi**, the demo city. Nairobi R² is -0.5586. Cape Town's error is substantial; its latitude also lies outside the training-city range, without establishing that as the cause. Neither failure is hidden and the model was not tuned after inspecting them.

## Reproduce and identify the exact artifact

From the repository root after installing pinned requirements:

```sh
python scripts/evaluate_solar.py
python -m pytest tests/test_solar_evaluation.py -q
```

Outputs:

- `models/solar_generation/models/flagship_solar_xgb.json`: **training-only evaluated model**, used by the personal scenario endpoint.
- `flagship_solar_metadata.json`: dataset/model SHA256 checksums, features, parameters, dependency versions, split identities, baseline monthly values, coordinate/target ranges and all metrics.
- `evidence/solar_monthly_split.csv`: aggregated rows with train/test membership.
- `evidence/solar_holdout_predictions.csv`: targets and both predictions for independent recomputation.
- `evidence/solar_evaluation.json`: full evaluation record.

Three evaluation tests independently recompute saved-model predictions and the baseline, verify split/data identities, and retrain in a temporary directory to check deterministic model hashes without overwriting the serving model. Percentage error is not a confidence interval or model accuracy probability.

## Historical records and limitations

Inherited `xgboost_climatological_model_v2.json`, metadata, notebook and training export remain historical team artifacts for older component routes. The old card's **7.46%**, inherited metadata's **11.41%**, and this release's **11.2056%** refer to different records; the first two are not current flagship metrics. The legacy export hard-codes a local Windows path and contains an all-city final refit; use the script above for this release.

Only the personal scenario path uses the new artifact. Historical lifetime bands do not establish empirical uncertainty or installation validation. A small inherited city sample cannot establish broad geographic reliability, real customer demand, measured savings, tariff accuracy or financial suitability.
