## Model 1 – Change Log (Since DSE Lead Takeover)

This document summarizes the key changes and fixes made to **Model 1 – Energy Consumption Estimation**
from the point when the DSE lead took over ownership.

---

### API & Core Logic

- Implemented a **versioned Flask API** at `POST /api/v1/estimate-consumption` with:
  - JSON input handling and CORS enabled.
  - Structured error responses using a consistent `{ "error": { code, message, status } }` shape.
- Added a dedicated **validation layer** (`src/validation.py`) that:
  - Validates `business_type`, `operating_hours`, `equipment`, and `location`.
  - Enforces presence of at least one refrigeration item (`refrigerator`, `freezer`, `cold_room`),
    with stricter rules for `butchery`, `grocery`, and `mini-supermarket`.
  - Ensures equipment fields (`type`, `quantity`, `size_capacity`, `daily_operating_hours`) are
    within expected ranges.
- Finalized a **formula-based estimator** (`src/estimator.py`) that:
  - Uses equipment power ratings and type+size inference (from `src/config.py`).
  - Computes monthly kWh from power, quantity, and operating hours.
  - Applies **African climate adjustment factors** based on city (hot/humid vs moderate).
  - Enforces a **refrigeration-first** share (≈50–70% for key business types).
  - Produces a `confidence_score` based on equipment data completeness and refrigeration presence.

---

### Configuration & Observability

- Centralized business types, equipment power ratings, and climate zones in `src/config.py`,
  including an expanded set of African cities (e.g. Douala, Luanda, Maputo, Cape Town, Gaborone).
- Externalized the API port via an environment variable:
  - `MODEL1_PORT` (default: `8001`) in `src/app.py`.
- Added **basic logging** in `src/app.py`:
  - Logs validation errors with code and message.
  - Logs successful estimations with business type, location, estimated kWh, and confidence score.

---

### Documentation & Handoff

- Created `models/energy_consumption/README.md` with:
  - Request/response schemas.
  - Error codes and examples.
  - Setup and run instructions.
  - Example `curl` commands and limitations.
- Added `INTEGRATION_GUIDE_MODEL1.md` for backend integration (Sarah), covering:
  - Endpoints, expected latency, and response contracts.
  - Fallback strategy for validation vs availability failures.
  - Example Python integration snippet.
- Documented AI tooling usage and time savings in `AI_USAGE.md`.
- Added `sample_requests.json` with realistic test payloads for:
  - Butchery in Lagos.
  - Grocery in Nairobi.
  - Cold storage in Johannesburg.
- Updated the **root `README.md`** to:
  - Mark the Flask service in `models/energy_consumption` as the **canonical Model 1 implementation**.
  - Note that the older FastAPI + XGBoost service under `api/` is **legacy**.
- Updated `api/README.md` to clearly label the FastAPI/XGBoost endpoint as a **legacy prototype**,
  not part of the official Model 1 implementation.

---

### Testing

- Introduced `models/energy_consumption/tests/test_api.py` with basic pytest coverage:
  - Health-check test for `GET /api/v1/health`.
  - Happy-path test using the `butchery_lagos` sample payload, asserting:
    - Presence of all required response fields.
    - Refrigeration share ≥ 50% of total estimated consumption.
  - Negative test to ensure requests **without refrigeration equipment** are rejected with
    `400` and `error.code == "INVALID_EQUIPMENT"`.

---

### Legacy / Unused Components

- Confirmed that:
  - The FastAPI app in `api/app.py` and `xgboost_energy_model.pkl` are **legacy artefacts**
    and are not used by the current Model 1 microservice.
  - The Jupyter notebook `notebooks/energy_consumption_Solar.ipynb` is kept for exploration /
    R&D but is not required for the live API.





