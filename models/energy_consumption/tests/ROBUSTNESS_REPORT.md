# Model 1 Energy Consumption ML API — Robustness Report

This document is generated from the test suite in `test_robustness.py` and serves as **living documentation** of failure modes, acceptable input ranges, behavioral sensitivity, and output safety rails.

---

## 1. Acceptable Input Ranges (from boundary tests)

| Field | Type | Acceptable range | Boundary behaviour |
|-------|------|------------------|---------------------|
| **sqft_m2** | number | **(0, 10_000]** | Rejected: `≤ 0` or `> 10_000`. Just above zero (e.g. `0.001`) accepted; `10_000` accepted; `10_001` rejected. |
| **operating_hours_weekly** | number | **(0, 168]** | Rejected: `≤ 0` or `> 168`. Zero rejected; `168` (24/7) accepted; `168.1` rejected. |
| **num_refrigeration_units** | integer | **[0, 500]** | Zero accepted; `500` accepted; `501` or negative rejected. |
| **num_workers** (optional) | integer | **Effective: (0, 1000]** | If `≤ 0` or invalid, defaults to `5`. If `> 1000`, rejected with `INVALID_FIELD_VALUE`. |
| **months_per_year** (optional) | integer | **Effective: 12** | If `≤ 0` or `> 12` or invalid, reset to `12` (no error). |
| **location** | string | **Length ≤ 200** | Exactly 200 characters accepted; 201 characters rejected with `INVALID_FIELD_VALUE`. Non-string (e.g. integer) rejected with `INVALID_FIELD_TYPE`. |
| **business_type** | string | **One of: `butchery`, `grocery`, `mini_supermarket`** | Case-insensitive. Empty string or invalid value (e.g. `restaurant`) → `INVALID_BUSINESS_TYPE`. |

---

## 2. Known Failure Modes and Error Codes

| HTTP | Error code | When it occurs |
|------|------------|----------------|
| **401** | `UNAUTHORIZED` | Missing or wrong `X-API-KEY` header on `/api/v1/estimate-consumption`. |
| **400** | `MISSING_FIELD` | One of the required fields is missing: `business_type`, `sqft_m2`, `operating_hours_weekly`, `num_refrigeration_units`, `location`. |
| **400** | `INVALID_JSON` | Request body is not valid JSON, or body is empty with `Content-Type: application/json`. |
| **400** | `INVALID_FIELD_TYPE` | Wrong type for a field (e.g. `sqft_m2` string `"abc"`, `operating_hours_weekly` string, `num_refrigeration_units` float string `"3.5"` or non-integer, `location` integer, `business_type` integer). |
| **400** | `INVALID_FIELD_VALUE` | Value out of range: `sqft_m2` ≤ 0 or > 10_000; `operating_hours_weekly` ≤ 0 or > 168; `num_refrigeration_units` < 0 or > 500; `num_workers` > 1000; `location` length > 200. |
| **400** | `INVALID_BUSINESS_TYPE` | `business_type` not one of `butchery`, `grocery`, `mini_supermarket` (e.g. `restaurant` or empty string). |
| **415** | `UNSUPPORTED_MEDIA_TYPE` | Request without `Content-Type: application/json` (e.g. no Content-Type header). |
| **500** | `PREDICTION_ERROR` | Model not loaded (`best_model` is `None`) or internal prediction/scaling/encoding failure. Response message is generic (“Internal Server Error”); no stack trace or internal details leaked. |

### Type behaviour (documented)

- **num_refrigeration_units**: Must be an integer. Float string such as `"3.5"` is **rejected** with `INVALID_FIELD_TYPE` (API uses `int(...)`).

---

## 3. Behavioral Summary (how output changes with inputs)

Derived from GROUP 8 single-variable sweeps and GROUP 7 climate tests.

| Input varied | Direction of `estimated_consumption_kwh_monthly` | Notes |
|--------------|--------------------------------------------------|--------|
| **sqft_m2** | Increases (monotonic in tests) | Sweep [20, 60, 150, 500, 2000]: output increases as floor area increases. |
| **operating_hours_weekly** | Increases (monotonic in tests) | Sweep [10, 40, 80, 120, 168]: more hours → higher consumption. |
| **num_refrigeration_units** | Refrigeration share in **50–70%** of total; refrigeration component increases with unit count | Share is clamped; at high unit count the refrigeration share reaches the cap (0.7). |
| **num_workers** | Effect documented; output remains in plausible range | Sweep [1, 5, 20, 100]: all responses 200; monthly kWh in [0, 1_000_000]. Not necessarily strictly monotonic. |
| **business_type** | All valid types return 200 with plausible kWh | At fixed inputs, `butchery`, `grocery`, `mini_supermarket` all return 200 and monthly kWh in [0, 1_000_000]. |
| **location** (climate) | Higher climate factor → higher monthly kWh | Lagos (1.35) > Johannesburg (1.18). Monthly kWh scales with `climate_adjustment_factor`. |

### Climate adjustment factors (GROUP 7)

| Location | Factor |
|----------|--------|
| Lagos, Nigeria | 1.35 |
| Accra, Ghana | 1.30 |
| Dar es Salaam, Tanzania | 1.35 |
| Kampala, Uganda | 1.25 |
| Nairobi, Kenya | 1.20 |
| Unknown City, Country (default) | 1.20 |
| Johannesburg, South Africa | 1.18 |

---

## 4. Output Safety Rails and Capping

| Behaviour | Implementation |
|-----------|----------------|
| **Monthly kWh cap** | If model output (after climate adjustment) would exceed **1,000,000** kWh/month, `estimated_consumption_kwh_monthly` is set to **1,000,000.0**. Response remains **200**. |
| **Negative prediction** | If monthly kWh is negative (e.g. very negative log-space prediction), it is reset to **0.0**. Response remains **200**. |
| **Breakdown non-negative** | `breakdown.refrigeration` and `breakdown.other` are both **≥ 0** (enforced with `max(0, ...)`). |
| **Confidence score range** | `confidence_score` is clamped to **[0, 1]** before rounding. |

---

## 5. Confidence Score Conditions

| Condition | Confidence score |
|-----------|-------------------|
| `num_refrigeration_units == 0` | **0.75** |
| `num_refrigeration_units > 0` and `sqft_m2 > 0` and `operating_hours_weekly > 0` | **0.85** |
| All responses | Score is always in **[0, 1]** (validated in tests). |

---

## Test Suite Reference

- **File**: `models/energy_consumption/tests/test_robustness.py`
- **Fixture app**: `create_app(test_mode=True, api_key="test-key-123")` with mock model (log-space prediction `log1p(50000)`), identity scaler, and label encoders returning `[0]`.
- **Protected requests**: Use header `X-API-KEY: test-key-123`.
- **Groups**: Authentication (1), Content-Type/JSON (2), Missing fields (3), Invalid types (4), Boundary/range (5), Business type (6), Climate sensitivity (7), Input sensitivity (8), Confidence (9), Output capping (10), Model not loaded (11).

Run all robustness tests:

```bash
cd models/energy_consumption/tests
python -m pytest test_robustness.py -v
```
