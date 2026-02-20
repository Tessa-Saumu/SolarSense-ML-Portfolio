# ROI Model 3 – Stress Test Report

## Overview
This document presents the stress testing, validation rules, identified failure modes, and acceptable input ranges for the **ROI Calculation API**. The goal of this testing was to ensure the model behaves reliably under normal, boundary, and extreme input conditions while maintaining secure and predictable outputs.

---

## Test Environment
- **Language:** Python 3.14
- **Framework:** Flask
- **Testing Tool:** Pytest
- **Total Automated Tests:** 65
- **Execution Time:** 0.40 seconds

All tests passed successfully.

---

## Test Coverage
The automated stress tests covered the following areas:

### 1. Happy Path Scenarios
- Correct ROI computation
- Output structure validation
- Rounding to two decimal places
- ROI = 100% boundary case
- Equal generation and consumption

### 2. Boundary Value Testing
- Maximum and minimum acceptable numeric inputs
- Near-zero system cost
- Maximum tariff
- Maximum equipment units
- 24-hour operational limit

### 3. ROI Clamping Logic
- ROI capped at 100%
- ROI forced to 0 when savings are negative
- Behaviour when savings are extremely high

### 4. Non-Negativity Guards
- Monthly savings never negative in final output
- Annual savings never negative

### 5. Input Type Validation
- Rejection of:
  - Non-numeric strings
  - Lists
  - None values
  - Infinity
- Acceptance of numeric strings through coercion

### 6. Optional Field Validation
#### Hours per Day
- Accepted: 0–24
- Rejected: negative values and values above 24

#### Equipment Units
- Accepted: 0–500
- Rejected: negative and >500
- Float values truncated to integer

#### String Fields
- Maximum length enforcement
- Unicode support for location
- SQL injection rejection
- XSS attempt rejection
- Whitespace trimming

### 7. Floating Point Precision
- Consistent rounding behaviour
- Stability for very small positive numbers
- NaN input handling

---

## Identified Failure Modes
No runtime crashes occurred. However, the following design limitations were identified:

| Scenario | Behaviour | Impact |
|----------|-----------|--------|
Boolean values used as numeric input | Coerced to 1 or 0 | Silent data corruption risk |
Float provided for integer field | Value truncated | Hidden precision loss |
ROI capped at 100% | Real ROI above 100% not visible | Analytical ambiguity |
No payback period calculation | ROI only reflects percentage return | Limited financial insight |
Unicode business type rejected | Validation failure without guidance | User experience limitation |

These are documented as **known design gaps**, not system failures.

---

## Acceptable Input Ranges

### Numeric Fields
| Field | Valid Range |
|-------|-------------|
system_cost | 0 < value ≤ 1,000,000 |
tariff | 0 < value ≤ 100 |
monthly_generation | 0 ≤ value ≤ defined kWh max |
monthly_consumption | 0 ≤ value ≤ defined kWh max |
hours_per_day | 0 – 24 |
equipment_units | 0 – 500 |

### Categorical Fields
| Field | Constraint |
|-------|------------|
business_type | Predefined controlled list |
location | ≤ 128 characters, Unicode allowed |

---

## Model Assumptions
The ROI model currently assumes:

- Constant tariff over time
- Constant monthly generation
- Constant monthly consumption
- No maintenance or operational costs
- No system degradation
- No inflation or discount rate

These assumptions simplify the calculation but limit long-term financial accuracy.

---

## Security Validation
The API successfully:

- Enforces API key authentication
- Applies rate limiting
- Rejects SQL injection attempts
- Rejects XSS payloads
- Hides internal server errors

---

## Conclusion
The ROI Calculation API demonstrates stable and secure behaviour under extensive stress testing. All 65 automated test scenarios passed, confirming:

- Strong input validation
- Controlled handling of extreme values
- Deterministic financial outputs
- Protection against malformed and malicious inputs

The remaining issues are documented as known design limitations and do not affect runtime stability.

---

## Future Improvements
- Add payback period calculation
- Prevent boolean-to-float coercion
- Enforce strict integer validation for unit fields
- Distinguish between actual ROI and capped ROI
- Provide user-friendly validation feedback for rejected categorical inputs

---

## How to Run the Tests
```bash
pytest test_roi_stress.py -v
```

---

## Author
Capstone Project – ROI Model 3 Validation- Zainab Mohamed

