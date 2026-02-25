## ROI Engine Integration Guide – SolarSense Model 3

This guide explains how to integrate with the **Model 3 ROI engine** used in the
SolarSense project. The engine is implemented as a deterministic Flask API in
`models/roi_calculation/src/app.py`.

---

### 1. What the ROI Engine Does

The ROI engine:

- Takes in **monthly energy consumption**, **monthly solar generation**,
  **electricity tariff**, and **system cost**.
- Computes:
  - **Monthly savings (USD)**.
  - **Annual ROI percentage** relative to system cost.
- Returns a **deterministic, formula‑based result** (no machine learning).

There is **no payback period** calculation in the current implementation, in line
with the alignment document.

---

### 2. Deterministic Calculation Model

The underlying logic is purely arithmetic:

- Let:
  - `consumption_kwh` – monthly consumption.
  - `generation_kwh` – monthly generation.
  - `tariff_per_kwh` – tariff in USD per kWh.
  - `system_cost_usd` – total system cost.

- Energy offset:

```text
energy_offset_kwh = min(consumption_kwh, generation_kwh)
```

- Monthly savings:

```text
monthly_savings_usd = energy_offset_kwh * tariff_per_kwh
```

- Annual savings:

```text
annual_savings_usd = monthly_savings_usd * 12
```

- ROI percentage:

```text
if annual_savings_usd <= 0:
    roi_percentage = 0.0
else:
    roi_percentage = (annual_savings_usd / system_cost_usd) * 100
```

Output is rounded to 2 decimal places.

---

### 3. Inputs & Outputs

#### Inputs (Request Body – JSON)

```json
{
  "consumption_kwh": 450.0,
  "generation_kwh": 500.0,
  "tariff_per_kwh": 0.20,
  "system_cost_usd": 6000.0
}
```

- **All fields are required**.

| Field             | Type   | Description                                | Constraints                      |
|-------------------|--------|--------------------------------------------|----------------------------------|
| `consumption_kwh` | number | Monthly energy consumption in kWh          | `> 0` and `≤ 100000`             |
| `generation_kwh`  | number | Monthly solar generation in kWh            | `> 0` and `≤ 100000`             |
| `tariff_per_kwh`  | number | Tariff in USD per kWh                      | `> 0` and `≤ 100`                |
| `system_cost_usd` | number | Total system cost in USD                   | `> 0` and `≤ 1,000,000`          |

#### Outputs (Response Body – JSON, 200)

```json
{
  "monthly_savings_usd": 90.0,
  "roi_percentage": 18.0,
  "system_cost_usd": 6000.0
}
```

| Field                | Type   | Description                                 |
|----------------------|--------|---------------------------------------------|
| `monthly_savings_usd`| number | Estimated monthly savings in USD            |
| `roi_percentage`     | number | Annual ROI as a percentage of system cost   |
| `system_cost_usd`    | number | Echo of input system cost for traceability  |

---

### 4. Endpoint Usage

- **Base URL (local)**: `http://localhost:5000`
- **Version prefix**: `/api/v1`

#### Health Check

```text
GET /api/v1/health
X-API-KEY: <your-api-key>
```

Response:

```json
{
  "status": "ok",
  "service": "roi-calculation"
}
```

#### ROI Calculation Endpoint

```text
POST /api/v1/calculate-roi
Content-Type: application/json
X-API-KEY: <your-api-key>
```

Body: see inputs above.

---

### 5. Example Requests & Responses

#### Example `curl` Call

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

Sample response:

```json
{
  "monthly_savings_usd": 90.0,
  "roi_percentage": 18.0,
  "system_cost_usd": 6000.0
}
```

---

### 6. Integration Flow With Other Services

The ROI engine is designed to be composed with other SolarSense models:

1. **Model 1 (Energy Consumption)**  
   - Produces monthly `consumption_kwh`.

2. **Model 2 (Solar Generation)**  
   - Produces monthly `generation_kwh`.

3. **Tariff & Cost Source**  
   - Backend config or external tariff service provides `tariff_per_kwh`.  
   - Quoting or design system provides `system_cost_usd`.

4. **Model 3 (ROI Engine)**  
   - Consumes these four values and returns `monthly_savings_usd` and `roi_percentage`.

Typical backend flow:

- Collect inputs from upstream services / DB.
- Build the ROI request JSON.
- Call `POST /api/v1/calculate-roi`.
- Use the response to:
  - Populate dashboards.
  - Drive recommendation logic in downstream models (e.g., Model 4).

---

### 7. Validation, Authentication & Error Handling

The engine performs:

- Type checks (all numeric fields must be parseable as floats).
- Range checks:
  - Values must be strictly greater than 0.
  - Values must not exceed configured caps.
- JSON structure check:
  - Request body must be a JSON object.

**Client responsibilities**:

- Ensure all four fields are present and non‑null.
- Ensure numeric values are in realistic ranges before sending to the ROI API.
- Always send a valid `X-API-KEY` header that matches the server-side `API_KEY` environment variable.
- Handle 4xx/5xx responses gracefully (see below).

**Error Responses** (JSON):

- 400 – Bad Request:

```json
{ "error": "Request body must be a JSON object" }
```

```json
{ "error": "consumption_kwh must be greater than 0.0" }
```

```json
{ "error": "tariff_per_kwh must be less than or equal to 100.0" }
```

- 413 – Payload Too Large:

```json
{ "error": "Request payload too large" }
```

- 429 – Rate Limit Exceeded:

```json
{ "error": "Rate limit exceeded" }
```

- 401 – Unauthorized (invalid or missing API key):

```json
{ "error": "Unauthorized" }
```

- 500 – Internal Server Error:

```json
{ "error": "Internal server error" }
```

---

### 8. Security Considerations

- **Rate limiting**:  
  - 100 requests per minute per IP to protect against abuse.

- **Request size limiting**:  
  - Maximum body size of 100 KB.

- **Input validation**:  
  - Strict numeric and range checks to mitigate obvious malformed or malicious input.

- **Error messages**:  
  - Generic 500 responses; no stack traces or internal details are exposed.

For production:

- Run behind HTTPS.
- Consider adding authentication (e.g., API keys, OAuth2) at the gateway or service layer.

---

### 9. Testing Guidance

The repository includes automated tests for the ROI engine:

- Location: `tests/roi_calculation/test_app.py`
- Test framework: **pytest**

Tests cover:

- Successful ROI calculation.
- All validation paths for 400 errors (missing fields, bad types, out‑of‑range).
- Malformed and empty JSON bodies.
- Request size limit (413).
- Rate limiting behavior (429).
- Generic 500 error handling via mocked internal exceptions.
- Response schema and logical consistency of outputs.

To run tests from the project root:

```bash
pytest
```

---

### 10. Known Limitations

- No payback period:
  - Payback years are intentionally **not** computed or returned.
- No persistence:
  - The service is stateless; it does not store any history or inputs.
- No built‑in authentication:
  - Access control must be handled by upstream components if required.
- Simplified financial model:
  - Operational and maintenance costs are not explicitly modeled.

---

### 11. Integration Steps for Backend Teams

1. Ensure connectivity to the ROI API host/port.
2. Map your domain model to the required request fields:
   - `consumption_kwh`
   - `generation_kwh`
   - `tariff_per_kwh`
   - `system_cost_usd`
3. Implement a client call (e.g., using `requests` in Python, `fetch` in Node).
4. On 200 responses:
   - Parse `monthly_savings_usd`, `roi_percentage`, and `system_cost_usd`.
   - Store or forward these values as needed.
5. On 4xx/5xx responses:
   - Log the error and surface a user‑friendly message.
   - Implement retries only for transient errors if appropriate (e.g., 500s).

---

### 12. Integration Steps for Frontend Teams

1. Coordinate with backend to confirm the base URL exposed to the frontend
   (do **not** call the raw Flask service directly from browsers in production).
2. Use the documented request schema to build forms or payloads.
3. Validate inputs client‑side where practical (basic numeric/range checks).
4. Display ROI outputs from the response:
   - `monthly_savings_usd`
   - `roi_percentage`
5. Handle and display error messages from the `error` field when non‑200.

---

For low‑level protocol details (status codes, error formats, etc.), see
`API_CONTRACT.md`, which is kept in sync with the current implementation.


