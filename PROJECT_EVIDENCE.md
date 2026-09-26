Project Evidence — SolarSense AI ML Microservice (DSE-models)

Context

When: February 2026. CHANGELOG.md entries dated 2026-02-13 through 2026-02-25, final commit `52b8416 Merge pull request #21` dated 2026-02-27. Model artifacts timestamps: `xgboost_climatological_metadata_v2.json` created_at_utc `2026-02-21T02:39:12Z`. Integration test results in `models/recommendations/tests/test_results/` timestamped 2026-02-24.

Why it existed: Capstone project to build AI solar viability assessment for African SMEs. Per `docs/DSE Team Alignment Document V2.0.txt`: "CRISIS PIVOT: AI-Enhanced Execution Mode" for "AI Solar Viability Assessment - Technical Implementation Plan", 2-3 week timeline, Models 1-2 by Wed Feb 12, Model 3 by Thu Feb 13, Model 4 by Fri Feb 14. README.md describes unified Flask gateway serving three ML microservices for solar energy analysis. `docs/Backend_Frontend_API_Response_Reference.md` states backend provides single endpoint `/api/v1/analyze` to frontend.

Solo / team: Team. Alignment doc lists Active (3): Tessa, Bella, Abishag; Conditional (2): Evelyn, Zainabu; Unavailable (1): Brandy. CHANGELOG maintained by Tessa, Owner Bella for Model 4. `TEAM_WORKFLOW_RULES_README.md` exists (22KB). Git history is shallow (`--shallow`), only commit `52b8416` visible locally, so individual commit authorship cannot be verified from local git log. PR #21 referenced as production merge.

My role: Cannot be proven from repository. No AUTHORS file, no git blame with multiple authors in shallow clone, no CODEOWNERS. CHANGELOG says "Changelog Maintained By: Tessa" and Model 4 "Owner: Bella". That suggests team roles but does not prove my personal contribution. Explicitly stating: authorship boundaries unclear from available evidence.

Problem

What problem was actually being solved?

Real implemented problem:
- Model 1 (`models/energy_consumption/src/app_ml.py`): Predict monthly kWh for food retail SMEs (butchery, grocery, mini_supermarket) given floor area m2, operating hours weekly, refrigeration units, location string, optional workers/months. Uses CBECS 2018 US data adapted to Africa via climate factors. Returns `estimated_consumption_kwh_monthly`, breakdown refrigeration/other, climate factor, confidence.
- Model 2 (`models/solar_generation/src/solar_climatology_api.py` + `solar_climatology_service.py`): Predict typical daily solar generation kWh/day for 10m² 20% system given lat/lon (Sub-Saharan Africa) and optional month, plus 25-year lifetime projection with degradation (0.7%/yr default) and confidence bands. Validates coordinates lat [-34,16] lon [-18,45].
- Model 3 (`models/roi_calculation/src/roi_calculation_api.py`): Deterministic ROI: `energy_offset = min(consumption, generation)`, `monthly_savings = offset * tariff`, `roi = annual_savings / system_cost *100` capped 0-100%. Inputs consumption_kwh, generation_kwh, tariff_per_kwh, system_cost_usd.
- Model 4 (`models/recommendations/model4_app.py`): Orchestrates 1-3 via HTTP (`MODELS_BASE_URL`), converts `equipment_list` to business metrics, calculates diesel economics (blended tariff), dynamically sizes panel area to 90% coverage capped 200m², scales lifetime prediction, calculates tiered system cost by country, returns viability verdict High/Medium/Low with score 0-100.

Aspirational README language:
- README claims "three independent machine learning microservices" but Model 3 is deterministic formula, not ML.
- README and docs claim support for "full 12-month climatology and 25-year lifetime projections" – lifetime is implemented but was buggy until fix documented in CHANGELOG (XGBoost version mismatch).
- Frontend integration implied but no frontend code in this repo; `docs/Backend_Frontend_API_Response_Reference.md` is handoff spec, not implemented UI.
- Claims of "African SMEs" – training data is US CBECS 2018 (`cbecs2018_final_public.csv` 19MB, 932 rows after filter per CHANGELOG), not African data.

What I personally built

Exact components/features/code owned by me: Cannot be determined. Repository does not contain per-file authorship metadata. Shallow git shows single merge commit. CHANGELOG attributes:
- Model 1 retrain for equipment scaling: expanded PBA filter 2→7 codes, 294→932 rows, R² 0.9812 MAPE 9.38% – attributed to Tessa's session notes but not provably my work.
- Model 2 retrain 20 cities 4 years, MAPE 11.41% – Tessa.
- Model 4 dynamic sizing, location-aware pricing, diesel economics, equipment conversion, bug fixes #1-#6 – Bella owner, Tessa updates.

Separate confirmed ownership from unclear ownership:
- Confirmed: All code exists in repo, but ownership unconfirmed.
- Unclear: Whether I built Model 1, 2, 3, 4, gateway, or only documentation. No evidence to assign.

Architecture

Frontend: None in this repo. Only `docs/Backend_Frontend_API_Response_Reference.md` describes expected frontend behavior (viability gauge, metric cards). No `src/`, `public/`, `package.json`, or JS/TS files.

Backend:
- Unified gateway `api/main.py`: Flask app, CORS enabled, `MultiModelDispatcher` WSGI dispatcher routing by PATH_INFO:
  - `/` and `/api/v1/health` → gateway
  - `/api/v1/estimate-consumption` → `models.energy_consumption.src.app_ml.create_app()`
  - `/api/v1/predict-generation` and `/api/v1/model-info` → `models.solar_generation.src.solar_climatology_api.create_app()`
  - `/api/v1/calculate-roi` → `models.roi_calculation.src.roi_calculation_api.create_app()`
  - `/api/v1/analyze` → `models.recommendations.model4_app.create_app()`
- Each model is independent Flask app with own validation, auth, rate limiting (Flask-Limiter 100/min memory://), CORS.
- `api/app.py` exists but is FastAPI stub loading `model/xgboost_energy_model.pkl` (abandoned, not used by gateway). `app_ml.py` at root is duplicate of Model 1 src (24871 bytes).

Data:
- Model 1: `models/energy_consumption/models/cbecs2018_final_public.csv` (19M). Training notebook `model1_energy_consumption_filterchange.ipynb` (138KB). Also archive data `Plant_1_Generation_Data.csv` etc (solar plant data not used in final model, appears abandoned).
- Model 2: `models/solar_generation/models/solar_data_20cities_4yr.csv` (3.1M) daily GHI, aggregated to monthly climatology in notebook `03-climatological-xgboost.ipynb` (502KB). Training script `python_climatological_xgboost_model_train.py`.
- Model 4: Equipment list conversion uses hardcoded per-unit floor areas and power estimates; country tariffs hardcoded in `resolve_country_and_tariff()` (8 countries).
- Data validation: strict type checks rejecting bool (isinstance bool check), range checks per model. Model 1: sqft (0,10000], hours (0,168], units [0,500], workers (0,1000], location ≤200 chars. Model 2: lat/lon numeric, month 1-12, optional business fields hours_per_day 0-24, equipment_units 0-500. Model 3: consumption/generation (0,100000], tariff (0,100], system_cost (0,1e6], MAX_CONTENT_LENGTH 100KB. Model 4: business_name 1-200 chars, lat -90/90 lon -180/180, equipment_type allowlist (29 types), diesel_hours 0-24, diesel_price 0-10.

ML/AI:
- Model 1: GradientBoostingRegressor (per MODEL1_CARD.md) with optional log1p target transformation (`use_log_target`). Feature list 17: SQFT, WKHRS, RFGCOMPN, NFLOOR, NWKER, MONUSE, YRCONC, kwh_per_sqft, sqft_per_worker, wkhrs_per_week_normalized, annual_operating_hours, refrigeration_density, is_high_refrigeration, is_extended_hours, pba_encoded, cendiv_encoded, size_category_encoded. Scaler StandardScaler? `energy_scaler_v1.joblib` 1.5KB. Label encoders in `sme_mappings_v1.joblib`. Climate factor lookup `CLIMATE_ZONES` dict 8 cities.
- Model 2: XGBoost Booster loaded from JSON `xgboost_climatological_model_v2.json` (681KB), not XGBRegressor pickle. Features: latitude, longitude, abs_latitude, month, is_dry_season. DRY_MONTHS {12,1,2,6,7,8}. Training locations 20 cities listed in metadata. Module-level cache `_MODEL_CACHE` to avoid concurrency bug (documented in code comment). Prediction clamps negative to 0.
- Model 3: No ML, formula.
- Model 4: No ML training, but heuristic ML-like logic: equipment→metrics conversion with buckets, refrigeration scaling factor `_compute_refrigeration_scaling_factor` dividing by 5.0, 4.5, 2.0 etc to align with benchmarks `tests/Test Benchmarks.md`, per-country solar baseline adjustment `SOLAR_BASELINE_ADJUST` dict (Kenya 0.80 etc), tiered cost per m² 200→160, country cost factors 0.90-1.20.

Database: None active. Archive contains `models/recommendations/archive/model4database_schema.sql` and `models/solar_generation/archive/Solar.sql`, `queries_pipeline.sql` – not used at runtime, appears abandoned. No ORM, no migrations.

Infrastructure:
- `Procfile`: `web: gunicorn api.main:app --workers 2 --bind 0.0.0.0:$PORT --timeout 120`
- `railway.json`: NIXPACKS builder, healthcheckPath `/api/v1/health`, restartPolicy ON_FAILURE
- `runtime.txt`: python-3.11.9
- `requirements.txt`: appears corrupted with null bytes (UTF-16LE?) but readable: Flask 3.0.2, Flask-Cors 4.0.0, Flask-Limiter 3.7.0, gunicorn 21.2.0, joblib 1.5.3, numpy 2.4.1, pandas 2.2.2, scikit-learn 1.8.0, xgboost 3.1.3, etc. Dependency version conflict resolved per CHANGELOG: xgboost 2.0.3→3.1.3 to fix serialization bug.
- No Dockerfile, no docker-compose, no CI yaml (no `.github/workflows`).
- Env vars: API_KEY required, MODELS_BASE_URL, MODELS_API_KEY, PORT, MODEL_DIR, MODEL1_PORT.

Major data/control flows:
1. Client → gateway `/api/v1/analyze` with business_name, location, lat/lon, equipment_list or metrics, uses_diesel.
2. Model 4 `validate_business_input` → `resolve_country_and_tariff` (lat/lon → country + tariff) → if unsupported returns 400.
3. Model 4 calls Model 1 via HTTP POST to `MODELS_BASE_URL/estimate-consumption` (or internal when testing). Converts equipment list via `convert_equipment_to_business_metrics()` to sqft, hours, units.
4. Model 1: validate → build 17-dim feature vector → scaler.transform → best_model.predict (log1p inverse if needed) → climate factor multiply → monthly kWh = annual/12 → breakdown 50-70% refrigeration → confidence 0.75/0.85 → cap 0-1e6.
5. Model 4 calls Model 2 via HTTP: payload lat, lon, month=current, include_lifetime=True → Model 2 service validates coordinates, builds feature vector per month, Booster.predict via DMatrix, clamps negative, computes annual_summary, calls `predict_lifetime_generation()` which loops 12 months and projects 25 years degradation 0.7% → returns monthly_generation list.
6. Model 4 adjusts Model 2 baseline via `SOLAR_BASELINE_ADJUST` per country to fit benchmarks, calculates scaling factor = (consumption*0.9)/base_monthly, caps 1-20x (200m²), scales generation and lifetime via `scale_lifetime_prediction()`, calculates system cost via `calculate_system_cost()`.
7. Model 4 calculates diesel economics `calculate_diesel_economics()`: diesel_fraction = hours/24, liters_per_kwh 0.40, fuel cost + maintenance $0.50/hr, blended tariff = total_cost/consumption.
8. Model 4 calls Model 3 via HTTP: consumption, generation scaled, tariff blended, system_cost → ROI.
9. Model 4 generates recommendation via `generate_recommendation()`: viability_score = roi_score (tiered 0-5%→0-15pts, 5-20%→15-37.5, 20%+→37.5-50) + coverage_score min(30, coverage*0.3) + savings_score min(20, savings/25). Thresholds High ≥65, Medium ≥40.
10. Returns JSON with consumption, generation, panel area, cost, ROI, savings, viability, diesel breakdown, lifetime.

ML / AI work

Problem formulation:
- Model 1: Regression, annual kWh → monthly. Implemented and verified via `test_api_ml.py` and `MODEL1_CARD.md`. Training notebook exists but model fails to load on newer sklearn (ModuleNotFoundError _loss) – suggests version drift.
- Model 2: Regression, typical daily generation kWh/day for 10m² 20% system. Implemented and verified, but training notebook path hardcoded to Windows `C:\Users\ingex\...` – reproducibility issue.
- Model 3: Deterministic ROI, not ML – implemented and verified.
- Model 4: Orchestration + heuristics, not learned model – implemented and verified.

Target:
- Model 1: annual_kwh (CBECS). Verified in `MODEL1_CARD.md` and `model1_energy_consumption_filterchange.ipynb`.
- Model 2: target_avg_generation_kwh = avg_ghi *10*0.2. Verified in `python_climatological_xgboost_model_train.py`.
- Model 3: monthly_savings_usd, roi_percentage – deterministic.
- Model 4: viability_score, recommendation – heuristic.

Features:
- Model 1: 17 engineered features listed above – implemented and verified in `feature_columns_v1.joblib` and `app_ml.py`.
- Model 2: 5 features latitude, longitude, abs_latitude, month, is_dry_season – verified in `feature_columns_v2.pkl` and `solar_climatology_service.py` FEATURE_COLUMNS.
- Model 3: 4 inputs.
- Model 4: equipment_list conversion features not ML.

Baseline:
- Model 1: No baseline documented in current card; archive mentions old XGBoost model `xgboost_energy_model.pkl` abandoned.
- Model 2: Archive `baseline_model_report.txt` exists but not read; notebook `02-baseline-model-xgboost.ipynb` in archive suggests baseline existed. Current metadata shows only final model.
- Absent/not applicable for Model 3/4.

Models:
- Model 1: Gradient Boosting Regressor (sklearn). Verified via `MODEL1_CARD.md` and joblib dict keys `best_model`, `use_log_target`. File `energy_consumption_model_v1.joblib` 265KB.
- Model 2: XGBoost Booster (native JSON). Verified via `xgboost_climatological_model_v2.json` 681KB, metadata validation_mape 0.11406962697528307 (11.4%).
- Model 3: Formula – `calculate_roi()` function.
- Model 4: No trained model, uses HTTP calls.

Validation methodology:
- Model 1: Train/test split 232/59 per MODEL1_CARD, Test R² 0.9830 MAPE 14.52% (but per CHANGELOG after retrain Test R² 0.9812 MAPE 9.38% with 932 rows – inconsistency). Cross-val R² 0.8683 ±0.1255 documented. No evidence of location-based split; CBECS data US only, so domain shift to Africa not validated. Tests mock model, not real model performance.
- Model 2: Location-based split mentioned in training script (validation_locations Johannesburg_SA, Kigali_Rwanda). MAPE 11.41% per CHANGELOG after 20 cities 4 years, metadata 11.4%. Robustness suite `tests/model2_robustness_tests.py` (43→49 tests) checks coordinate bounds and monthly coverage. However, Cape Town MAPE 25.2% documented as Known Limitation L6 (Mediterranean outlier). Validation methodology partially supports claim but limited to training cities.
- Model 3: No ML validation; logic tests via `test_roi_api.py`.
- Model 4: Integration tests `full_integration_tests.py` 9 suites, 93 checks passing per CHANGELOG 2026-02-22 run. But tests require live server (requests), not unit. No evidence of automated CI run; test results JSONs in `models/recommendations/tests/test_results/` show 6 runs 2026-02-24 with timestamps, but content not examined. Equipment scaling tests `tests/Test Benchmarks.md` defines expected ranges per country (10m² cost $1500-2500, monthly kWh 220-340, equipment consumption per unit). Model 4 code contains hardcoded adjustments to fit those benchmarks (SOLAR_BASELINE_ADJUST, cost factors) – suggests overfitting to test expectations.

Metrics:
- Model 1: Claimed R² 0.9830, MAPE 14.52% (card) vs R² 0.9812 MAPE 9.38% (CHANGELOG after retrain). Not independently reproduced because model fails to load on current env. No metrics file besides card.
- Model 2: MAPE 11.41% (CHANGELOG) vs 0.114 in metadata JSON. Per-location validation image `models/solar_generation/models/outputs/per_location_validation.png` exists but not analyzed. Archive `baseline_model_report.txt` not current.
- Model 3: No ML metrics.
- Model 4: Viability score thresholds, ROI, coverage – no formal metrics, but integration test reports claim 7/7 suites passing 93/93 checks, and robustness reports claim 77/77 Model 1 and 49/49 Model 2 passing.

Final result:
- Implemented and verified: Flask APIs return 200 with expected schemas when mocked (tests passing 51 Model1, 25 ROI, 46/48 solar – 2 failures due to 422 vs 400 expectation).
- Documented but not reproduced: MAPE numbers, R², because training notebooks have hardcoded Windows paths and model loading fails on sklearn 1.9.
- Absent: Real African SME validation data, frontend, database persistence.

Do not call something successful merely because a model achieved a metric. Evaluate whether validation methodology supports the claim:
- Model 1 MAPE 9-14% on US CBECS does not support African SME accuracy; climate factor heuristic (1.18-1.35) is not learned, no validation against African meter data. Confidence score is heuristic 0.75/0.85, not calibrated.
- Model 2 MAPE 11.4% on held-out locations is reasonable for climatological task, but 20 cities only, and Cape Town outlier 25% shows limited generalization. Coordinate validation hard error outside [-34,16] [-18,45] means model cannot be used outside SSA, but training cities are within that. Lifetime projection uses fixed degradation 0.7% not validated.
- Model 3 ROI formula is correct mathematically but caps ROI at 100% (output realism) which hides high diesel scenarios (37% ROI mentioned). No validation against real financial data.
- Model 4 adjustments to fit benchmarks (per-country scaling factors, cost factors) are not learned, they are manual fudge factors to make tests pass – weakens credibility as ML.

Engineering evidence

Tests:
- Model 1: `test_api_ml.py` 51 tests – covers health, success, all business types, climate zones, missing fields, invalid types/values, malformed JSON, edge/boundary, model failure, log target, schema, deterministic, sequential. Uses mocks (MagicMock model returning 12000 annual). All 51 passed locally (pytest 9.1.1).
- Model 1 robustness: `test_robustness.py` 62 tests – auth, content-type, missing fields, invalid types, boundary/range, business type, climate sensitivity, input sensitivity, confidence, output capping, model not loaded. All 62 passed. Report `ROBUSTNESS_REPORT.md` documents acceptable ranges, error codes, behavioral summary.
- Model 1 security: `test_security_ml.py` 11 tests – auth, max values, output validation, error hiding. All 11 passed.
- Model 2: `test_solar_climatology_api.py` 48 tests – health, model-info, predict success full/single/without lifetime, missing/invalid coords, month validation, optional business fields, edge lat/lon, all months, large inputs, extra fields, schema, annual calc, server errors, negative clamp. 46 passed, 2 failed (invalid lat/lon type expects 400 but returns 422 – code returns 422 for non-numeric lat/lon, test expects 400). Mocked artifacts via patch.
- Model 3: `test_roi_api.py` 25 tests – health, success, malformed JSON, empty body, missing field, invalid type, negative/zero ranges, above max caps, extra fields, boundary, 413 payload too large, 429 rate limit, 401 auth, 500 generic. All 25 passed.
- Integration: `full_integration_tests.py` 9 suites – requires live server and API_KEY, uses requests. Cannot run without server. Historical results JSONs in `models/recommendations/tests/test_results/` (6 files) and `tests/outputs/v0_api_test_results.json`, `model1_robustness_report.json`, `model2_robustness_report_v1/v2.json` – existence proves tests were run, but not that they pass currently.
- Robustness external: `tests/model1_robustness_tests.py` and `model2_robustness_tests.py` – standalone scripts that hit live API, produce JSON reports. Not pytest.
- Total identifiable tests: 51+62+11+48+25 = 197 unit tests. Evidence they pass: 195 passed, 2 failed (solar type validation). No CI to enforce.

APIs:
- 7 endpoints verified in gateway:
  - GET / → `{"message":"SolarSense API running","status":"ok"}` (main.py)
  - GET /api/v1/health gateway → ok
  - POST /api/v1/estimate-consumption (Model1)
  - POST /api/v1/predict-generation (Model2)
  - GET /api/v1/model-info (Model2)
  - POST /api/v1/calculate-roi (Model3)
  - POST /api/v1/analyze (Model4)
- Auth: X-API-KEY header, 401 on missing/invalid, 500 if server misconfigured (Model1 returns AUTH_ERROR, others return generic 500).
- Rate limiting: 100/min per IP via Flask-Limiter memory://, 429 handling differs: Model1 returns plain text HTML from limiter (not JSON per MODEL1_API_CONTRACT), Model3 returns JSON `{"error":"Rate limit exceeded"}`, Model2 returns limiter default, Model4 same.
- Validation: strict isinstance checks rejecting bool, range checks, allowlist for business_type and equipment_type.
- Error format: Model1 JSON `{"error":{"code":...,"message":...,"status":...}}`, Model2 `{"status":"error","message":...,"details":...}`, Model3 `{"error":...}` string, Model4 `{"error":...,"message":...}` – inconsistent across services.
- No OpenAPI/Swagger.

CI/CD:
- No `.github/workflows`, no Jenkins, no CircleCI. `pytest.ini` excludes `models/solar_generation/archive` and `api/model3_api` (legacy). No CI evidence.
- Deployment: Railway via Procfile + railway.json. No Docker.

Containers:
- No Dockerfile, no docker-compose. Railway uses NIXPACKS.

Architecture patterns:
- Factory pattern `create_app()` in all 4 models for testability – implemented and verified.
- WSGI dispatcher `MultiModelDispatcher` – custom middleware routing – implemented.
- Module-level model cache `_MODEL_CACHE` in solar service – fixes concurrency bug documented in comment.
- Dependency injection via app.config for mocks – used in tests.
- No repository pattern, no service layer separation beyond solar_climatology_service.py.

Data validation:
- Extensive per-field validation as described, with security focus (bool rejection, max length, max content length 100KB for ROI). Verified in code and tests.
- Output validation: clamping negative to 0, capping monthly kWh 1e6, confidence 0-1, ROI 0-100% – implemented.

Error handling:
- Try/except around model loading, prediction, JSON parsing. Logs via logging module, returns generic 500 without stack trace (security). However Model1 root `app_ml.py` has debug instrumentation writing to hardcoded Windows path `c:\Users\ingex\...\.cursor\debug.log` – leftover debug code, should be removed.
- Model4 catches exceptions and returns 503 if any model fails.

Monitoring:
- Logging INFO level, request logging in solar API `before_request`. No structured logging, no metrics, no Sentry, no Prometheus. Health endpoints exist for Railway.

Security:
- API key auth via env var, not hardcoded – verified. .env in .gitignore. Rate limiting 100/min. Input validation strict. CORS enabled (allow all). No SQL (no DB). No JWT. No HTTPS enforcement in code (Railway provides). Output sanitization via clamping. Security docs `docs/DSE_FULL_SECURITY_CHECKS.md` exists (not read fully). `SECURITY_IMPLEMENTATION.md` in archive.

For tests, include number/type, what they actually test, whether evidence they pass:
- See Tests section above: 197 tests total, 195 passed locally, 2 failed due to status code mismatch. Integration tests require live server, historical JSONs suggest they passed on 2026-02-24 but not currently verified.

Scale

Rows/files/users/models/endpoints/etc.

Only numbers supported by repository evidence:
- Models: 4 services (3 independent + 1 orchestration). Artifacts: Model1 4 joblib files (265KB model + 1.5KB scaler + 286B features + 1.1KB mappings), Model2 1 JSON model 681KB + 78B features + 736B metadata, Model3 no artifact, Model4 no artifact.
- Endpoints: 7 as listed.
- Tests: 197 unit tests across 5 files.
- Data rows: CBECS CSV 19MB – per MODEL1_CARD 232 training + 59 test = 291 total (but CHANGELOG says expanded to 932 after filter). Solar CSV 3.1MB – daily records for 20 cities 4 years: raw daily ~? Grouped to monthly 20*12*4=960 rows estimated, actual monthly climatology rows 240 (20 cities *12 months) per training script logic.
- Files: Root has 234 files total (per initial find). Models directory 6 subfolders.
- Users: No user table, no auth users – only API key.
- Training locations: 20 cities listed in metadata JSON.
- Business types supported: 3 in Model1, 13 mapped in Model4.
- Equipment types allowlist: 29 in Model4.
- Countries supported in Model4 tariff: 8 (Ghana, Nigeria, South Africa, Tanzania, Kenya, Rwanda, Uganda, Ethiopia) per `resolve_country_and_tariff()`.

Outcome

What actually worked?
- Flask gateway routing works – verified via code and manual inspection of `MultiModelDispatcher`.
- Model1 API returns plausible monthly kWh with mocked model – 51 tests pass.
- Model2 API returns 12-month climatology and lifetime projection with mocked predictions – 46 tests pass, cache works.
- Model3 ROI calculation correct for valid inputs – 25 tests pass, including 413 and 429.
- Model4 orchestration logic implemented: equipment conversion, diesel economics, dynamic sizing, cost tiers, lifetime scaling – code complete, but requires live Models 1-3 via HTTP; unit tests missing (only integration tests and `test_diesel_mvp.py` manual script).
- Security: API key auth, rate limiting, input validation – tested.
- Deployment config exists and is syntactically valid.

What measurable result exists?
- Model1: Test R² 0.9812 MAPE 9.38% claimed in CHANGELOG after retrain, but not reproducible currently due to sklearn version mismatch. Card claims R² 0.9830 MAPE 14.52%.
- Model2: validation_mape 0.11406962697528307 (11.4%) in metadata JSON, MAPE 11.41% in CHANGELOG. Per-location validation image exists.
- Model3: No ML metric, but deterministic calculation verified via `calculate_roi()` logic tests.
- Integration: 93/93 checks passing per CHANGELOG 2026-02-22 run, 7/7 suites. Robustness 77/77 Model1 and 49/49 Model2 per CHANGELOG.
- Test evidence: 195/197 unit tests passing locally.

Separate technical output from real-world/product impact:
- Technical output: working APIs, models, tests, docs.
- Real-world impact: None evidenced – no deployment URL live, no user metrics, no business outcome data, no frontend. `FINAL_SME_PROFILES.json` contains 10 SME profiles with outputs (viability Highly viable, monthly usage 2200-5200 kWh, solar coverage 90%, etc) but these are example outputs, not real deployments.

Limitations

What does NOT work?
- Model1 real model fails to load on Python 3.11 + sklearn 1.9 (ModuleNotFoundError _loss) – breaks local run unless using exact pinned versions (sklearn 1.8.0 per requirements.txt). `requirements.txt` corrupted (null bytes) suggests encoding issue.
- Model2 training notebook hardcodes Windows path `C:\Users\ingex\...` – not portable.
- `api/app.py` FastAPI stub references `model/xgboost_energy_model.pkl` path that doesn't exist at runtime (abandoned).
- Model4 requires `MODELS_BASE_URL` and `MODELS_API_KEY` to call Models 1-3 via HTTP – if those env vars not set, calls fail; no fallback to in-process calls. In unified gateway deployment, this causes self-HTTP calls (potential deadlock with gunicorn workers 2).
- Error response formats inconsistent across models (Model1 nested error object, Model2 status/message/details, Model3 simple error string).
- Rate limit 429 responses inconsistent: Model1 returns plain text HTML, not JSON.
- 2 solar tests fail (422 vs 400) – API returns 422 for non-numeric lat/lon, but tests expect 400.

What is unfinished?
- Model4 has no unit tests, only integration tests requiring live server.
- Database layer: `model4database_schema.sql` not integrated, no persistence.
- CI/CD: no automated pipeline.
- Docker: no containerization.
- Frontend: none.
- Model retraining pipeline: no automated retraining, no data versioning, no experiment tracking (MLflow etc).
- Monitoring: no metrics, no alerting beyond Railway healthcheck.
- Documentation: README claims Model 4 panel area 10-50m² but code allows up to 200m²; README not updated for Model 4 bug fixes #1-#6.
- `.gitignore` contains merge conflict markers `<<<<<<< HEAD` `=======` `.venv/` `>>>>>>> origin/production-do-not-push` – indicates unresolved conflict in ignore file.

What would I change?
- Modelling weaknesses:
  - Model1 trained on US data, no African validation – need transfer learning or African data collection.
  - Climate factor heuristic not learned – should be learned or use cooling degree days.
  - Confidence score heuristic – should be calibrated uncertainty.
  - Model2 20 cities only, Mediterranean outlier – need more diverse climate zones, more years, and proper spatial CV.
  - Model4 manual fudge factors (SOLAR_BASELINE_ADJUST, cost factors) – should be data-driven, not hardcoded to pass benchmarks.
- Architecture weaknesses:
  - Model4 calling Models 1-3 via HTTP in same process is fragile – should import service functions directly or use message queue.
  - Inconsistent error formats – standardize.
  - Memory storage for rate limiting not suitable for production (multiple workers).
  - No request ID, no structured logging.
  - Debug log writing to hardcoded Windows path in `app_ml.py` – remove.
- Reproducibility problems:
  - Hardcoded Windows paths in notebooks and debug logs.
  - `requirements.txt` encoding issue, pinned versions conflict with current env.
  - Model artifacts not versioned with DVC, no training script CLI args.
  - No seed set for reproducibility in training script (random_state 42 but not for all).
- Broken/dead integrations:
  - `api/app.py` FastAPI dead code.
  - Archive folders contain old requirements, notebooks, data that are not used but increase repo size.
  - `models/recommendations/src/temp` empty file.
- Deployment issues:
  - No health check for Model4 dependencies – if Model1 fails, gateway still returns 200 for `/api/v1/health` but `/analyze` returns 503.
  - No graceful shutdown, no liveness/readiness probes beyond single health path.
- Technical debt:
  - Duplicate `app_ml.py` at root and in src – drift risk (diff shows auth logic differences).
  - Large CSVs in repo (19M CBECS) – should be in external storage.
  - `__pycache__` directories committed in `models/energy_consumption/src/__pycache__/` and `tests/__pycache__/` – should be ignored.
  - Merge conflict markers in `.gitignore`.
- Unsupported claims:
  - README claims XGBoost for Model1 but it's GradientBoostingRegressor.
  - Claims "three independent ML microservices" but Model3 is deterministic.
  - Claims ±20% error acceptable but no validation against African data.

Current repository status

Runs locally: Partially. Gateway `api/main.py` can start with `API_KEY` set, but Model1 real model fails to load on Python 3.11 + sklearn 1.9 unless using exact pinned versions from requirements.txt (sklearn 1.8.0, xgboost 3.1.3). Tests with `test_mode=True` bypass loading and pass. Solar model loads (XGBoost JSON) and passed startup log. ROI works. Model4 requires `MODELS_BASE_URL` – if not set, `requests.post` fails. Verified via code inspection and local pytest runs (197 tests, 195 pass). No attempt to run full gateway with real models due to missing env and model load failure.

Tests pass: Mostly. Unit tests 195/197 pass locally (2 failures due to expected status code mismatch in solar). Integration tests require live server and API_KEY – not run locally, but historical JSON results exist. No CI evidence.

Deployment: Configured for Railway (Procfile, railway.json). No evidence of current live deployment URL – `MODELS_BASE_URL` defaults to `http://localhost:8000` in integration tests, but env var example in CHANGELOG shows `https://dse-models-production.up.railway.app/api/v1`. No Dockerfile. No recent deployment logs.

README quality: Comprehensive (897 lines) with installation, env vars, local testing, deployment guide, API usage with curl examples, troubleshooting. However, some sections outdated (Model 4 panel area, cost model, README claims XGBoost for Model1). Contains Table of Contents, architecture diagram in text, but no badges, no license.

Demo available: No live demo URL in README. `FINAL_SME_PROFILES.json` contains 10 example SME outputs but not a running demo. No screenshots, no video.

Evidence

Relevant files:
- Gateway: `api/main.py` (MultiModelDispatcher, create_app), `api/app.py` (FastAPI abandoned)
- Model1: `models/energy_consumption/src/app_ml.py` (create_app, estimate_consumption), `models/energy_consumption/models/energy_consumption_model_v1.joblib` (265KB), `energy_scaler_v1.joblib`, `feature_columns_v1.joblib`, `sme_mappings_v1.joblib`, `cbecs2018_final_public.csv` (19M), `model1_energy_consumption_filterchange.ipynb`, `MODEL1_CARD.md`, `MODEL1_API_CONTRACT.md`, `INTEGRATION_GUIDE_MODEL1.md`, `tests/test_api_ml.py` (51 tests), `test_robustness.py` (62), `test_security_ml.py` (11), `conftest.py`, `ROBUSTNESS_REPORT.md`
- Model2: `models/solar_generation/src/solar_climatology_api.py` (create_app, health, model-info, predict-generation), `solar_climatology_service.py` (get_model_paths, load_model_artifacts with _MODEL_CACHE, validate_coordinates lat [-34,16] lon [-18,45], predict_solar_generation, predict_lifetime_generation), `models/xgboost_climatological_model_v2.json` (681KB), `feature_columns_v2.pkl`, `xgboost_climatological_metadata_v2.json` (MAPE 0.114), `solar_data_20cities_4yr.csv` (3.1M), `03-climatological-xgboost.ipynb`, `python_climatological_xgboost_model_train.py`, `MODEL2_CARD.md`, `MODEL2_API_CONTRACT.md`, `MODEL_2_INTEGRATION_GUIDE.md`, `tests/test_solar_climatology_api.py` (48 tests), `conftest.py`
- Model3: `models/roi_calculation/src/roi_calculation_api.py` (calculate_roi, _validate_float_field, health), `ROI_API_CONTRACT.md`, `ROI_ENGINE_INTEGRATION_GUIDE.md`, `tests/test_roi_api.py` (25 tests)
- Model4: `models/recommendations/model4_app.py` (create_app, convert_equipment_to_business_metrics, scale_lifetime_prediction, calculate_diesel_economics, _compute_refrigeration_scaling_factor, call_model1/2/3, generate_recommendation, calculate_system_cost, resolve_country_and_tariff, register_routes), `ORCHESTRATION_API_CONTRACT.md`, `ORCHESTRATION_INTEGRATION_GUIDE.md`, `test_diesel_mvp.py`, `tests/test_results/*.json` (6 files)
- Integration: `full_integration_tests.py` (9 suites, 93 checks), `tests/Test Benchmarks.md` (tariff, roof, cost, equipment benchmarks), `tests/model1_robustness_tests.py`, `model2_robustness_tests.py`, `outputs/v0_api_test_results.json`
- Config: `requirements.txt` (corrupted encoding but contains Flask, xgboost, sklearn etc), `requirements-dev.txt` (pytest, pytest-mock), `pytest.ini` (norecursedirs), `Procfile`, `railway.json`, `runtime.txt`, `.gitignore` (with conflict markers), `FINAL_SME_PROFILES.json` (10 SMEs), `CHANGELOG.md` (detailed bug fixes #1-#6), `README.md`, `TEAM_WORKFLOW_RULES_README.md`, `docs/` (5 docs)
- Notebooks: `models/energy_consumption/models/model1_energy_consumption_filterchange.ipynb`, `models/solar_generation/models/03-climatological-xgboost.ipynb`

PRs: Only PR #21 mentioned in commit message `Merge pull request #21 from SolarSense-Capstone/production-do-not-push`. No local PR list (gh not run). Git shallow so no full history.

Issues: No issues directory, no GitHub issues fetched.

Screenshots: None in repo (no `screenshots/`, `assets/`). `models/solar_generation/models/outputs/per_location_validation.png` exists (validation plot) but not reviewed.

Demo: No live demo. No `demo/` folder. Example outputs in `FINAL_SME_PROFILES.json` and `docs/Backend_Frontend_API_Response_Reference.md` example JSON.

Presentation: No PPT/PDF. `Integration_Test_Report_v2_0.docx`, `Model1_Robustness_Report_v1_1.docx`, `Model2_Robustness_Report_v2_1.docx` mentioned in CHANGELOG as on `tessa-docs` (external), not in repo.

Candidate CV bullets

Leave this section blank.

Work required

Concrete remaining tasks only.

Critical

Problems that prevent the repository from being credible professional evidence:
- Fix `requirements.txt` encoding (currently UTF-16LE with null bytes) and pin exact working versions; ensure `energy_consumption_model_v1.joblib` loads on Python 3.11 (retrain or downgrade sklearn to 1.8.0 and document). Currently model fails with ModuleNotFoundError _loss.
- Remove hardcoded Windows paths: `C:\Users\ingex\...` in `python_climatological_xgboost_model_train.py` and debug log path `c:\Users\ingex\...\.cursor\debug.log` in `models/energy_consumption/src/app_ml.py` and root `app_ml.py` (region agent log). Replace with relative paths or env vars.
- Resolve `.gitignore` merge conflict markers (`<<<<<<< HEAD`, `=======`, `>>>>>>>`).
- Remove committed `__pycache__/` directories (`models/energy_consumption/src/__pycache__/`, `tests/__pycache__/`, etc) and add to .gitignore.
- Standardize error response format across 4 services (choose one schema).
- Fix 2 failing solar tests (422 vs 400) – align code and test expectations for invalid lat/lon type.
- Add missing `MODELS_BASE_URL` handling for Model4 in unified gateway to avoid self-HTTP deadlock – refactor to import service functions directly or document required env vars and provide fallback.
- Remove dead code `api/app.py` FastAPI stub or document why it exists.

High value

Changes that materially increase strength of engineering evidence:
- Add CI workflow `.github/workflows/ci.yml` running pytest (197 tests) on push – proves tests pass in clean env.
- Add Dockerfile and docker-compose for local reproducibility (gateway + models).
- Add unit tests for Model4 (currently 0) – mock Model1/2/3 calls and test equipment conversion, diesel economics, sizing, viability scoring.
- Add integration test that runs without live server (test gateway dispatcher via Flask test client calling all 4 endpoints).
- Move large CSVs (19M CBECS, 3.1M solar) to external storage or DVC and provide download script – reduces repo bloat.
- Add training scripts CLI with argparse (data path, output path, random seed) and document reproduction steps.
- Fix rate limiting storage to use Redis or at least document memory:// limitation for production.
- Add structured logging with request IDs and JSON logs.
- Add OpenAPI spec or Swagger UI for 7 endpoints.
- Document Model1 retrain discrepancy (R² 0.9830 vs 0.9812, 291 vs 932 rows) and provide final metrics file.
- Add `FINAL_SME_PROFILES.json` validation script that checks outputs against benchmarks in `Test Benchmarks.md`.

Optional

Polish that is useful but not necessary:
- Update README Model1 description from XGBoost to GradientBoostingRegressor, update Model4 panel area cap from 50m² to 200m², update cost model description.
- Add screenshots of per_location_validation.png and API responses to README.
- Add LICENSE file (currently placeholder "[Add your license information here]").
- Add Makefile for common tasks (install, test, run).
- Add pre-commit hooks (black, flake8).
- Archive cleanup: move `Plant_*_Generation_Data.csv` (unused) to proper archive or remove.
- Add example `.env.example` file.

Professional Evidence Assessment

1. What engineering capability does this project prove best?
Backend API engineering with Flask factory pattern, WSGI dispatcher for multi-model gateway, strict input validation (type checks rejecting bool, range checks, allowlists), security (API key auth, rate limiting, output clamping, generic 500), and comprehensive unit testing with mocks (197 tests, 195 passing). The gateway pattern in `api/main.py` and module-level cache fix in `solar_climatology_service.py` show production awareness.

2. What ML/AI capability does it prove best?
Applied ML for tabular regression with domain adaptation: Model1 uses CBECS 2018 with 17 engineered features and log target transform, climate factor heuristic; Model2 uses XGBoost climatological regression with spatial-seasonal features (lat, lon, abs_lat, month, dry season) trained on 20 cities 4 years NASA POWER data, with location-based validation and lifetime projection with degradation. Shows ability to take existing datasets and build end-to-end prediction service, though validation against African ground truth is weak.

3. What is the strongest verifiable achievement?
Model2 XGBoost climatological model with metadata JSON showing 20 training locations, MAPE 11.4%, 5 features, 25-year projection, coordinate validation, and module-level cache fix that resolved concurrency bug (documented in code comment and CHANGELOG). Verified by existence of `xgboost_climatological_model_v2.json` (681KB), metadata, training script, and 46 passing API tests. Model4 orchestration that dynamically sizes system to 90% coverage, scales lifetime, calculates diesel economics, and returns viability verdict – complex business logic integrating 3 services, with 6 bug fixes documented (#1-#6) showing iterative debugging.

4. What is the biggest credibility weakness?
Training data mismatch and manual fudge factors: Model1 trained on US commercial buildings (CBECS) not African SMEs, with no African validation; climate factors and confidence scores are heuristics, not learned. Model4 contains hardcoded per-country adjustments (`SOLAR_BASELINE_ADJUST`, `COUNTRY_COST_FACTORS`) to make outputs fit `Test Benchmarks.md` – suggests overfitting to test expectations rather than data-driven model. Combined with `requirements.txt` encoding corruption and model loading failure on current sklearn, and shallow git history preventing authorship proof, this weakens ML credibility.

5. Is there enough here to justify investing additional time in this project?
Yes, for Applied AI / ML Engineer portfolio, because core engineering is solid (gateway, 4 services, 197 tests, security, deployment config) and ML models are end-to-end with artifacts and notebooks. Fixing critical issues (requirements encoding, model loading, hardcoded paths, Model4 unit tests, CI) would take ~2-3 days and significantly increase credibility. The project demonstrates full pipeline from data (CBECS, NASA POWER) to API to orchestration, which is valuable for solar viability use case. However, do not invest in collecting African SME data unless targeting research role – focus on engineering polish.

6. What type of professional role would this project support as evidence?
Applied AI Engineer, ML Platform Engineer, Backend Engineer (Python/Flask), Data Engineer (ETL for CBECS and NASA POWER), or Junior MLOps (Railway deployment, model caching, API gateway). Supports roles requiring: building ML microservices, Flask API development, input validation and security, model integration and orchestration, and testing. Does not strongly support Frontend, Data Science Research (no novel modelling), or DevOps with containers/K8s (no Docker).

7. What claims should I NOT make publicly based on the current repository?
- Do not claim Model1 accuracy ±20% for African SMEs – no African validation data, trained on US CBECS.
- Do not claim XGBoost for Model1 – it's GradientBoostingRegressor.
- Do not claim 3 ML microservices – Model3 is deterministic formula.
- Do not claim production deployment with users – no evidence of live URL, no user metrics.
- Do not claim R² 0.9830 / MAPE 9.38% as final without noting discrepancy and inability to reproduce due to sklearn version mismatch.
- Do not claim Model2 works globally – it hard errors outside lat [-34,16] lon [-18,45] and has 25% MAPE for Cape Town.
- Do not claim Model4 viability scoring is ML-learned – it's heuristic with manual fudge factors.
- Do not claim solo ownership – team project with 3 active members, authorship unclear from shallow git.
- Do not claim CI/CD or Docker – none present.
- Do not claim frontend integration – no frontend code in repo.
