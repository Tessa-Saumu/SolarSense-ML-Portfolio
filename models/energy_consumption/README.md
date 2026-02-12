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

### Setup & Installation

#### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- (Optional) ngrok for public URL tunneling

#### Step 1: Create Virtual Environment

```bash
# Navigate to the project directory
cd models/energy_consumption

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### Step 2: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Or install manually:
pip install flask flask-cors numpy scikit-learn xgboost joblib pandas
```

#### Step 3: Verify Installation

```bash
# Check Flask is installed
python -c "import flask; print(flask.__version__)"

# Check other dependencies
python -c "import numpy, sklearn, xgboost, joblib; print('All dependencies installed!')"
```

---

### How to Run Locally

#### Option A: Formula-Based API (Recommended for MVP)

This uses the deterministic formula-based approach (no ML model required):

```bash
# Make sure virtual environment is activated
cd models/energy_consumption/src
python app.py
```

The service will start on:
- `http://0.0.0.0:8001` or `http://localhost:8001`
- Health checks:
  - `GET /api/v1/health`
  - `GET /health` (legacy/unversioned)

#### Option B: ML-Based API (Requires Trained Model)

This uses the trained XGBoost/Gradient Boosting model from the notebook:

```bash
# Make sure virtual environment is activated
# Ensure model files exist in models/ directory:
#   - energy_consumption_model_v1.joblib
#   - energy_scaler_v1.joblib
#   - feature_columns_v1.joblib
#   - sme_mappings_v1.joblib

cd models/energy_consumption/src
python app_ml.py
```

**Note:** The ML-based API requires model files to be generated from `model1_energy_consumption.ipynb` first.

#### Change Port (Optional)

Set the `MODEL1_PORT` environment variable to use a different port:

```bash
# Windows PowerShell:
$env:MODEL1_PORT = "9001"
python app.py

# Windows CMD:
set MODEL1_PORT=9001
python app.py

# macOS/Linux:
export MODEL1_PORT=9001
python app.py
```

---

### Running with ngrok (Public URL)

ngrok creates a public HTTPS URL that tunnels to your local server, useful for:
- Testing with external services
- Frontend development
- API integration testing
- Sharing with team members

#### Step 1: Install ngrok

**Option A: Download from website**
1. Visit https://ngrok.com/download
2. Download for your OS
3. Extract and add to PATH, or use full path

**Option B: Using package manager**
```bash
# macOS (Homebrew):
brew install ngrok

# Windows (Chocolatey):
choco install ngrok

# Linux (snap):
snap install ngrok
```

#### Step 2: Start Your Local API

```bash
# In one terminal, start the API
cd models/energy_consumption/src
python app.py
```

#### Step 3: Start ngrok Tunnel

**In a new terminal window:**

```bash
# Create tunnel to port 8001 (default)
ngrok http 8001

# Or if using custom port:
ngrok http 9001
```

You'll see output like:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:8001
```

#### Step 4: Use the Public URL

Copy the `https://` URL from ngrok and use it in your requests:

```bash
# Example: Using the ngrok URL
curl -X POST "https://abc123.ngrok.io/api/v1/estimate-consumption" \
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
      }
    ],
    "location": "Lagos, Nigeria"
  }'
```

#### ngrok Tips

- **Free tier:** URLs change each time you restart ngrok
- **Paid tier:** Can reserve static domains
- **Web interface:** Visit `http://127.0.0.1:4040` to see request logs
- **Keep both running:** Keep both the Flask app and ngrok running simultaneously

#### Stopping ngrok

Press `Ctrl+C` in the ngrok terminal to stop the tunnel.

---

### Troubleshooting

#### Port Already in Use

If you see `Address already in use` error:

```bash
# Find process using port 8001
# Windows:
netstat -ano | findstr :8001

# macOS/Linux:
lsof -i :8001

# Kill the process or use a different port:
$env:MODEL1_PORT = "9001"  # Windows PowerShell
python app.py
```

#### Module Not Found Errors

If you see `ModuleNotFoundError`:

```bash
# Make sure virtual environment is activated
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

#### Model Files Not Found (ML API)

If using `app_ml.py` and getting model file errors:

1. Ensure you've run `model1_energy_consumption.ipynb` to generate model files
2. Check that these files exist in `models/` directory:
   - `energy_consumption_model_v1.joblib`
   - `energy_scaler_v1.joblib`
   - `feature_columns_v1.joblib`
   - `sme_mappings_v1.joblib`

#### ngrok Connection Issues

- **"tunnel session failed"**: Check that your local API is running first
- **"bind: address already in use"**: Another ngrok instance may be running
- **Slow responses**: Free ngrok tier has rate limits; consider paid tier for production

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


