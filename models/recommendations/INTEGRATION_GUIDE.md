# INTEGRATION GUIDE & BACKEND REQUIREMENTS
## Model 4: AI Recommendation Engine — v1.2.0-mvp-diesel

**Owner:** Bella
**For:** Backend Developers & System Integrators
**Last Updated:** February 15, 2026

---

## TABLE OF CONTENTS

1. [Backend Requirements](#backend-requirements)
2. [Integration Steps](#integration-steps)
3. [API Contract](#api-contract)
4. [System Sizing Algorithm](#system-sizing-algorithm)
5. [Diesel Economics Model](#diesel-economics-model)
6. [Database Schema](#database-schema)
7. [Error Handling](#error-handling)
8. [Performance Considerations](#performance-considerations)
9. [Security Requirements](#security-requirements)
10. [Deployment to Railway](#deployment-to-railway)
11. [Integration Checklist](#integration-checklist)

---

## BACKEND REQUIREMENTS

### System Requirements

| Component | Requirement | Notes |
|-----------|-------------|-------|
| **Python** | 3.8+ | Tested on 3.11 |
| **RAM** | 512MB minimum | 1GB recommended |
| **CPU** | 1 vCPU | 2+ for production |
| **Storage** | 100MB | App + logs |
| **Network** | Outbound HTTPS | To call Models 1–3 on Railway |

### Python Dependencies

```
Flask==3.0.0
Flask-CORS==4.0.0
Flask-Limiter==3.5.0
python-dotenv==1.0.0
requests==2.31.0
gunicorn==21.2.0
```

### Environment Variables

```bash
# Required — app will not start without these
API_KEY=<your_generated_key>           # Model 4's own API key (for incoming requests)
MODELS_API_KEY=<shared_railway_key>    # Key for calling Models 1-3 on Railway

# Required for production
MODELS_BASE_URL=https://dse-models-production.up.railway.app/api/v1

# Optional
PORT=5000
```

### External Service Dependencies

| Service | Endpoint | Timeout | Required |
|---------|----------|---------|----------|
| Model 1 | `{MODELS_BASE_URL}/estimate-consumption` | 30s | Yes |
| Model 2 | `{MODELS_BASE_URL}/predict-generation` | 30s | Yes |
| Model 3 | `{MODELS_BASE_URL}/calculate-roi` | 30s | Yes |

**Geographic constraint:** Model 2 only covers Sub-Saharan Africa (lat: -26 to 6, lon: -18 to 44). Requests outside this range cause Model 2 to return 400, which triggers a 503 from Model 4.

---

## INTEGRATION STEPS

### Step 1 — Verify Models 1–3 are Running

```bash
API_KEY=QfBmvo3htYQPSJWYYLcChxXvZonTuC2U
BASE=https://dse-models-production.up.railway.app/api/v1

# Gateway health
curl "$BASE/health"

# Model 1
curl -X POST "$BASE/estimate-consumption" \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"business_type":"grocery","sqft_m2":60,"operating_hours_weekly":98,"num_refrigeration_units":2,"location":"Nairobi","num_workers":3,"months_per_year":12}'

# Model 2
curl -X POST "$BASE/predict-generation" \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"latitude":-1.2921,"longitude":36.8219}'

# Model 3
curl -X POST "$BASE/calculate-roi" \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"consumption_kwh":220,"generation_kwh":198,"tariff_per_kwh":0.15,"system_cost_usd":14707}'
```

All should return `200 OK`.

### Step 2 — Set Up Model 4

```bash
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements_model4.txt
cp .env_model4 .env
```

### Step 3 — Configure `.env`

```bash
API_KEY=<generate with: python -c "import secrets; print(secrets.token_urlsafe(32))">
MODELS_API_KEY=QfBmvo3htYQPSJWYYLcChxXvZonTuC2U
MODELS_BASE_URL=https://dse-models-production.up.railway.app/api/v1
PORT=5000
```

### Step 4 — Run and Test Locally

```bash
python model4_app.py

# In another terminal:
curl http://127.0.0.1:5000/health
python test_diesel_mvp.py
```

---

## API CONTRACT

### POST /api/v1/analyze

**Auth:** `X-API-KEY` header required

#### Request Schema (TypeScript)

```typescript
interface AnalysisRequest {
  // ── Required ──────────────────────────────────────────────
  business_name: string;          // 1–200 chars
  business_type: BusinessType;    // See enum below
  location: string;               // Human-readable e.g. "Nairobi, Kenya"
  latitude: number;               // -90 to 90 (Model 2 accepts -26 to 6 only)
  longitude: number;              // -180 to 180 (Model 2 accepts -18 to 44 only)

  // ── Input mode: provide ONE of these two options ──────────
  equipment_list?: Equipment[];   // Option A: equipment-based input
  sqft_m2?: number;               // Option B: direct metrics
  operating_hours_weekly?: number;
  num_refrigeration_units?: number;

  // ── Optional: base settings ───────────────────────────────
  tariff?: number;                // Grid electricity $/kWh. Default: 0.15
  num_workers?: number;           // Default: 5
  months_per_year?: number;       // Default: 12

  // ── Optional: diesel replacement mode ────────────────────
  uses_diesel?: boolean;          // Default: false
  diesel_hours_per_day?: number;  // 0–24. Default: 12 (only used if uses_diesel=true)
  diesel_price_per_liter?: number;// USD. Default: 1.20 (only used if uses_diesel=true)
}

interface Equipment {
  equipment_type: string;         // See supported types list in README
  quantity: number;               // 0–100
  hours_per_day?: number;         // 0–24. Default: 12
}

type BusinessType =
  | "Restaurant" | "Retail" | "Office" | "Hotel"
  | "Healthcare" | "Education" | "Manufacturing"
  | "Food & Beverage" | "Cafe" | "Gym" | "Bakery"
  | "Entertainment" | "Workshop";
```

#### Response Schema (TypeScript)

```typescript
interface AnalysisResponse {
  // ── Input echo ────────────────────────────────────────────
  business_name: string;
  business_type: string;
  location: string;
  analyzed_at: string;              // ISO 8601

  // ── Energy analysis ───────────────────────────────────────
  estimated_consumption_kwh: number;   // Monthly kWh from Model 1
  predicted_generation_kwh: number;    // Monthly kWh (scaled to system size)
  recommended_panel_area_m2: number;   // Recommended system size (max 50m²)
  system_cost: number;                 // USD. Scales at $600/m² (max ~$20,000)

  // ── Financial analysis ────────────────────────────────────
  roi_percentage: number;           // Annual ROI %
  monthly_savings: number;          // USD/month

  // ── Recommendation ────────────────────────────────────────
  recommendation: "High" | "Medium" | "Low";
  viability_score: number;          // 0–100
  status: "HIGHLY VIABLE" | "MODERATELY VIABLE" | "NOT VIABLE";
  explanation: string;              // Human-readable reasoning
  confidence: number;               // 0–100

  // ── Energy scenario ───────────────────────────────────────
  energy_scenario: "grid_only" | "diesel_replacement";
  current_energy_cost: {
    total_monthly: number;          // USD. Sum of grid + diesel costs
    diesel_monthly: number;         // USD. 0 if grid_only
    grid_monthly: number;           // USD
  };

  // ── Diesel details (only present if uses_diesel=true) ─────
  diesel_details?: {
    hours_per_day: number;
    price_per_liter: number;
    monthly_liters: number;
    effective_tariff: number;       // Effective $/kWh for diesel power
    diesel_kwh_monthly: number;     // kWh covered by generator
  };
}
```

#### Error Response Schema

```typescript
interface ErrorResponse {
  error: string;       // Category: "Bad Request", "Unauthorized", etc.
  message: string;     // Human-readable
  // 503 only:
  business_name?: string;
  status?: "INCOMPLETE";
}

// HTTP status codes:
// 400 — Validation failure (missing fields, out-of-range values)
// 401 — Missing or invalid X-API-KEY
// 429 — Rate limit exceeded (100 req/min per IP)
// 500 — Internal error (no internal details exposed)
// 503 — One or more upstream models failed
```

#### Viability Score Reference

| Score | Recommendation | Status | Typical Scenario |
|-------|---------------|--------|-----------------|
| ≥ 65 | High | HIGHLY VIABLE | Heavy diesel user (18h/day), ROI 35%+ |
| 40–64 | Medium | MODERATELY VIABLE | Moderate diesel (12h/day) + high tariff |
| < 40 | Low | NOT VIABLE | Grid-only at African tariffs ($0.12–0.18/kWh) |

> Grid-only "Low" ratings are economically accurate, not a bug. Solar ROI at $0.15/kWh is 2–5%. The product should surface diesel replacement as a value proposition for businesses with generators.

---

## SYSTEM SIZING ALGORITHM

Model 4 automatically scales the recommended solar system based on consumption:

```
target_generation = consumption_kwh * 0.90          # 90% coverage target
scaling_factor    = target_generation / base_10m2_generation
scaling_factor    = clamp(scaling_factor, 1.0, 5.0) # max 50m² for SME realism
recommended_m2    = 10 * scaling_factor
system_cost_usd   = 6000 * scaling_factor           # $600/m² African market rate
```

**Cap rationale:** 50m² (~$20,000) is the realistic upper bound for African SME solar deployment. Beyond this, financing becomes the limiting factor, not ROI.

---

## DIESEL ECONOMICS MODEL

When `uses_diesel: true`, Model 4 calculates a blended tariff used in ROI:

```
diesel_fraction       = diesel_hours_per_day / 24
diesel_kwh_monthly    = consumption_kwh * diesel_fraction
diesel_liters_monthly = diesel_kwh_monthly * 0.40   # 0.40 L/kWh (partial load rate)
diesel_fuel_cost      = diesel_liters_monthly * diesel_price_per_liter
diesel_maintenance    = diesel_hours_per_day * 30 * 0.50  # $0.50/hr
diesel_cost_monthly   = diesel_fuel_cost + diesel_maintenance

grid_kwh_monthly      = consumption_kwh * (1 - diesel_fraction)
grid_cost_monthly     = grid_kwh_monthly * tariff

total_cost            = diesel_cost_monthly + grid_cost_monthly
blended_tariff        = total_cost / consumption_kwh  # Passed to Model 3
```

**Note:** 0.40 L/kWh reflects small generator partial-load efficiency. The industry-quoted 0.25 L/kWh is full-load rated output only.

---

## DATABASE SCHEMA

Optional — for storing analysis results.

```sql
CREATE TABLE businesses (
    id SERIAL PRIMARY KEY,
    business_name VARCHAR(200) NOT NULL,
    business_type VARCHAR(100) NOT NULL,
    location VARCHAR(200),
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE analysis_results (
    id SERIAL PRIMARY KEY,
    business_id INTEGER REFERENCES businesses(id) ON DELETE CASCADE,
    estimated_consumption_kwh DECIMAL(10, 2),
    predicted_generation_kwh DECIMAL(10, 2),
    recommended_panel_area_m2 DECIMAL(6, 2),
    system_cost_usd DECIMAL(10, 2),
    roi_percentage DECIMAL(5, 2),
    monthly_savings_usd DECIMAL(10, 2),
    recommendation VARCHAR(20) CHECK (recommendation IN ('High', 'Medium', 'Low')),
    viability_score DECIMAL(5, 2) CHECK (viability_score >= 0 AND viability_score <= 100),
    status VARCHAR(50),
    explanation TEXT,
    confidence DECIMAL(5, 2),
    energy_scenario VARCHAR(30),
    uses_diesel BOOLEAN DEFAULT FALSE,
    diesel_hours_per_day DECIMAL(4, 2),
    diesel_cost_monthly DECIMAL(10, 2),
    blended_tariff DECIMAL(6, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE api_logs (
    id SERIAL PRIMARY KEY,
    endpoint VARCHAR(200),
    method VARCHAR(10),
    status_code INTEGER,
    execution_time_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_analysis_business ON analysis_results(business_id);
CREATE INDEX idx_analysis_recommendation ON analysis_results(recommendation);
CREATE INDEX idx_analysis_created ON analysis_results(created_at);
```

---

## ERROR HANDLING

### Upstream Model Failure Strategy

If any of Models 1–3 returns a non-200 response or times out:
1. Error is logged with full detail server-side
2. Client receives `503 Service Unavailable`
3. No internal error details are exposed
4. No automatic retries (client should retry after confirming upstream health)

### Common 400 Validation Errors

| Error | Cause |
|-------|-------|
| `Missing required fields: latitude` | Field omitted from request |
| `latitude must be between -90 and 90` | Out-of-range coordinate |
| `uses_diesel must be true or false` | Wrong type (e.g. string "true") |
| `diesel_hours_per_day must be between 0 and 24` | Invalid range |
| `Must provide either equipment_list OR business metrics` | Neither input mode provided |

---

## PERFORMANCE CONSIDERATIONS

### Expected Latencies

| Step | Time |
|------|------|
| Model 1 call | 1–3s |
| Model 2 call | 1–3s |
| Model 3 call | 0.5–1s |
| Model 4 logic | <100ms |
| **Total** | **3–7s** |

### Future Optimisation Options

Model 1 and Model 2 calls are independent and could be parallelised with `concurrent.futures`:
```python
with ThreadPoolExecutor() as executor:
    f1 = executor.submit(call_model1_consumption, data)
    f2 = executor.submit(call_model2_generation, lat, lon)
    consumption_data = f1.result()
    generation_data = f2.result()
```
This would cut total latency to ~3–4s.

Model 2 results can be cached by lat/lon + month (solar data doesn't change), with a 24h TTL.

---

## SECURITY REQUIREMENTS

- API key must be minimum 32 characters, URL-safe base64
- Never commit `.env` to version control
- Use different keys for development and production
- Production must use HTTPS (Railway provides this automatically)
- Rate limit storage should use Redis in production (not in-memory)

---

## DEPLOYMENT TO RAILWAY

```bash
# Procfile
echo "web: gunicorn model4_app:app" > Procfile

# runtime.txt
echo "python-3.11.0" > runtime.txt

# Deploy
railway login
railway init
railway variables set API_KEY=<your_model4_key>
railway variables set MODELS_API_KEY=QfBmvo3htYQPSJWYYLcChxXvZonTuC2U
railway variables set MODELS_BASE_URL=https://dse-models-production.up.railway.app/api/v1
railway up
```

---

## INTEGRATION CHECKLIST

### Setup
- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements_model4.txt`)
- [ ] `.env` created with all three required variables
- [ ] API key generated (32+ characters)

### Configuration
- [ ] `MODELS_BASE_URL` set to Railway URL
- [ ] `MODELS_API_KEY` set to shared key
- [ ] `.env` added to `.gitignore`

### Testing
- [ ] `/health` returns 200
- [ ] Models 1–3 reachable (verify with curl commands in Step 1)
- [ ] 401 returned without API key
- [ ] 429 returned after 100 requests/minute
- [ ] Valid grid-only request returns 200
- [ ] Valid diesel request returns 200 with `diesel_details` field
- [ ] Out-of-SSA coordinates return 503 (Model 2 rejects them)
- [ ] `test_diesel_mvp.py` passes all 3 tests

### Production
- [ ] Deployed to Railway
- [ ] Environment variables set in Railway dashboard
- [ ] HTTPS endpoint verified
- [ ] Health check URL confirmed working

---

**Owner:** Bella | **Updates:** Tessa
**Version:** 1.2.0-mvp-diesel | February 15, 2026