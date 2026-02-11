## Model 1 – Energy Consumption Estimation (Refrigeration-Heavy SMEs)

This microservice estimates monthly electricity consumption (kWh) for **refrigeration-heavy food retail SMEs** (butcheries, groceries, mini‑supermarkets, cold storage, food retail) in Sub‑Saharan Africa when smart meter data is unavailable.

It uses a **formula-based, equipment-driven approach** with explicit **climate adjustments** for African cities and a **refrigeration-first focus**.

---

### How It Works

- **Framework**: Flask (+ CORS)
- **Endpoint**: `POST /api/v1/estimate-consumption`
- **Port (default)**: `8001`
- **Approach**: Deterministic formulas using equipment power ratings rather than a black-box ML model.

Core calculation:

- Look up or infer **equipment power rating (W)** from type + size (e.g. `refrigerator_500L` → 150 W)
- Compute per-equipment energy:
  - $kWh_{monthly} = \\frac{power\_W \\times quantity \\times daily\_hours \\times 30}{1000}$
- Apply **climate adjustment factor** based on location (city string)
- Enforce **refrigeration share** between **50–70%** for key business types

---

### API – Request Schema

`POST /api/v1/estimate-consumption`

```json
{
  "business_type": "butchery",
  "operating_hours": 12,
  "equipment": [
    {
      "type": "refrigerator",
      "quantity": 3,
      "size_capacity": "500L",
      "daily_operating_hours": 24
    },
    {
      "type": "freezer",
      "quantity": 2,
      "size_capacity": "1000L",
      "daily_operating_hours": 20
    },
    {
      "type": "lights",
      "quantity": 10,
      "size_capacity": "medium",
      "daily_operating_hours": 12
    }
  ],
  "location": "Lagos, Nigeria"
}
```

**Fields**

- **business_type**: one of
  - `"butchery"`, `"grocery"`, `"mini-supermarket"`, `"cold_storage"`, `"food_retail"`
- **operating_hours**: integer `1–24` (typical business operating hours)
- **equipment**: non-empty array of equipment objects:
  - **type**: `"refrigerator" | "freezer" | "cold_room" | "lights" | "pos" | "hvac"`
  - **quantity**: integer `1–50`
  - **size_capacity**: string like `"500L"`, `"1000L"`, `"2000L"`, `"50m2"`, `"small"`, `"medium"`, `"large"`
  - **daily_operating_hours**: integer `1–24` (optional – falls back to `operating_hours` if omitted)
- **location**: string like `"Lagos, Nigeria"` or `"Nairobi, Kenya"`

**Refrigeration requirement**

- At least **one** equipment item must be refrigeration:
  - `"refrigerator"`, `"freezer"`, or `"cold_room"`
- For `"butchery"`, `"grocery"`, `"mini-supermarket"` this is treated as **mandatory**.

---

### API – Response Schema

```json
{
  "estimated_consumption_kwh_monthly": 1200.5,
  "confidence_score": 0.85,
  "breakdown": {
    "refrigeration": 720.3,
    "lighting": 180.0,
    "hvac": 200.2,
    "other": 100.0
  },
  "climate_adjustment_factor": 1.25,
  "equipment_summary": {
    "total_refrigeration_units": 6,
    "total_other_equipment": 4
  }
}
```

**Interpretation**

- **estimated_consumption_kwh_monthly**: total monthly energy use (kWh)
- **confidence_score**: `0.0–1.0` heuristic based on:
  - completeness of equipment data (size, hours, quantity)
  - presence of refrigeration equipment
- **breakdown**: allocation of total kWh into:
  - `refrigeration`, `lighting`, `hvac`, `other`
- **climate_adjustment_factor**:
  - 1.30–1.40 for hot/humid cities (e.g. Lagos, Accra, Dar es Salaam)
  - 1.15–1.25 for moderate cities (e.g. Nairobi, Johannesburg)
  - default `1.20` if location is unknown
- **equipment_summary**: counts refrigeration vs other equipment units.

---

### Error Handling

Errors are returned in structured form:

```json
{
  "error": {
    "code": "INVALID_EQUIPMENT",
    "message": "At least one refrigeration equipment item required",
    "status": 400
  }
}
```

Possible error codes:

- **INVALID_JSON** – body is not valid JSON
- **INVALID_PAYLOAD** – body is not a JSON object
- **MISSING_FIELD** – a required field is missing
- **INVALID_FIELD_TYPE** – a field has the wrong type
- **INVALID_BUSINESS_TYPE** – business_type not in allowed list
- **INVALID_OPERATING_HOURS** – outside `1–24`
- **INVALID_EQUIPMENT** – equipment list invalid or missing refrigeration
- **INVALID_LOCATION** – location is not a string

All validation errors return **HTTP 400**.

---

### How to Run Locally

From the project root:

```bash
cd models/energy_consumption
pip install -r requirements.txt

# Run the Flask app
cd src
python app.py
```

The service will start on:

- `http://0.0.0.0:8001`
- Health checks:
  - `GET /api/v1/health`
  - `GET /health` (legacy/unversioned)

---

### Example curl Commands

```bash
curl -X POST "http://localhost:8001/api/v1/estimate-consumption" \
  -H "Content-Type: application/json" \
  -d '{
    "business_type": "butchery",
    "operating_hours": 12,
    "equipment": [
      {
        "type": "refrigerator",
        "quantity": 3,
        "size_capacity": "500L",
        "daily_operating_hours": 24
      },
      {
        "type": "freezer",
        "quantity": 2,
        "size_capacity": "1000L",
        "daily_operating_hours": 20
      },
      {
        "type": "lights",
        "quantity": 10,
        "size_capacity": "medium",
        "daily_operating_hours": 12
      }
    ],
    "location": "Lagos, Nigeria"
  }'
```

---

### Notes & Limitations (MVP)

- **±20% error margin** expected – values are approximate but consistent.
- Equipment power ratings are **heuristic** and can be refined with field data.
- Climate factor uses a **city substring match** on the location string.
- Legacy `xgboost_energy_model.pkl` is currently **not used**; this microservice is fully formula-based for transparency and speed.


