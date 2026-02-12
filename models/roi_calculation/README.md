## Model 3 – Financial Viability & ROI Calculation API

This folder contains the **Model 3 ROI Calculation microservice** for the SolarSense project.
It exposes a single HTTP endpoint that computes the **ROI percentage** and **monthly savings**
for a solar installation, based purely on formulas (no ML).

---

### 1. Setup Instructions

- **Prerequisites**
  - Python 3.10+ recommended.
  - `pip` or another Python package manager.

- **Install dependencies**

```bash
cd models/roi_calculation
pip install -r requirements.txt
```

- **Run the API locally**

```bash
cd src
python app.py
```

The API will start on `http://0.0.0.0:5000/`.

You can verify it’s running by opening:

```text
GET http://localhost:5000/
```

Expected response:

```json
{
  "message": "Model 3 ROI API running"
}
```

---

### 2. API Endpoint Documentation

- **Endpoint**

```text
POST /api/v1/calculate-roi
Content-Type: application/json
```

- **Description**

Computes the **ROI percentage** and **monthly savings (USD)** for a solar system based on:
monthly consumption, monthly generation, tariff per kWh, and system cost.

---

#### 2.1 Request Schema

All fields are **required** and must be **numbers greater than 0**.

```json
{
  "consumption_kwh": 450.0,      // Monthly energy consumption in kWh
  "generation_kwh": 500.0,       // Monthly solar generation in kWh
  "tariff_per_kwh": 0.20,        // Electricity tariff in USD per kWh
  "system_cost_usd": 6000.0      // Total solar system cost in USD
}
```

- **Constraints**
  - `consumption_kwh` > 0 and ≤ 100000
  - `generation_kwh` > 0 and ≤ 100000
  - `tariff_per_kwh` > 0 and ≤ 100
  - `system_cost_usd` > 0 and ≤ 1,000,000
  - Request body size is limited to **100 KB**.

---

#### 2.2 Response Schema (Success – 200)

```json
{
  "monthly_savings_usd": 90.0,
  "roi_percentage": 18.0,
  "system_cost_usd": 6000.0
}
```

- **Fields**
  - `monthly_savings_usd` – Estimated savings per month (USD).
  - `roi_percentage` – Annual ROI as a percentage of system cost.
  - `system_cost_usd` – Echoes the input system cost for traceability.

- **Notes**
  - The Model 3 implementation **does not compute or return any payback period**
    (explicitly descoped per Alignment Document v2.1).

---

#### 2.3 Error Responses

- **400 – Bad Request**

Returned when the request body is missing, invalid JSON, missing fields, wrong types,
or out-of-range values.

Examples:

```json
{
  "error": "Request body must be a JSON object"
}
```

```json
{
  "error": "consumption_kwh must be greater than 0.0"
}
```

```json
{
  "error": "tariff_per_kwh must be less than or equal to 100.0"
}
```

- **413 – Payload Too Large**

```json
{
  "error": "Request payload too large"
}
```

- **429 – Rate Limit Exceeded**

```json
{
  "error": "Rate limit exceeded"
}
```

- **500 – Internal Server Error**

```json
{
  "error": "Internal server error"
}
```

The service uses generic messages for 500s and does **not** expose stack traces in responses.

---

### 3. Security & Reliability Features

- **Input validation**
  - Type checking (all numeric fields are parsed as floats).
  - Range validation with meaningful error messages.
  - Max value caps to guard against unrealistic or malicious inputs.

- **Request size limiting**
  - `MAX_CONTENT_LENGTH` set to 100 KB.

- **Rate limiting**
  - Flask-Limiter configured with a default of **100 requests per minute per IP**.
  - ROI endpoint additionally decorated with `@limiter.limit("100 per minute")`.

- **Error handling**
  - Custom handlers for `413`, `429`, and `500`.
  - No stack traces in JSON responses when running the default configuration.

- **CORS**
  - Flask-CORS enabled to allow integration with frontends (can be restricted).

---

### 4. Example Requests

#### 4.1 `curl` Example

```bash
curl -X POST http://localhost:5000/api/v1/calculate-roi \
  -H "Content-Type: application/json" \
  -d '{
    "consumption_kwh": 450,
    "generation_kwh": 500,
    "tariff_per_kwh": 0.20,
    "system_cost_usd": 6000
  }'
```

Expected (sample) response:

```json
{
  "monthly_savings_usd": 90.0,
  "roi_percentage": 18.0,
  "system_cost_usd": 6000.0
}
```

---

### 5. Known Limitations

- Operational costs (e.g., maintenance) are not explicitly modeled; the ROI formula
  follows the simplified approach described in the alignment document.
- No persistent storage or authentication; this is a stateless microservice intended
  to be composed with other models in the SolarSense pipeline.

---

### 6. Alignment Notes (Model 3 – Alignment Doc v2.1)

- Uses the required versioned endpoint: `POST /api/v1/calculate-roi`.
- Accepts the specified inputs:
  `consumption_kwh`, `generation_kwh`, `tariff_per_kwh`, `system_cost_usd`.
- Returns the specified outputs:
  `roi_percentage`, `monthly_savings_usd`, `system_cost_usd`.
- Implements robust input validation, error handling, request size limits,
  and rate limiting as recommended in the alignment document.
- **No payback period** is calculated or returned in the response.


