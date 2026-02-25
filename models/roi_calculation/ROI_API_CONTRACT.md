## API Contract – SolarSense Model 3 ROI Service

This document reflects the **current, actual implementation** of the ROI API in
`models/roi_calculation/src/app.py`.

---

### 1. Base URL & Versioning

- **Local base URL (default)**: `http://localhost:5000`
- **API version prefix**: `/api/v1`

All versioned endpoints are prefixed with `/api/v1`.

---

### 2. Endpoints Overview

- `/api/v1/health`  
  - **Method**: `GET`  
  - **Description**: Health check endpoint.

- `/api/v1/calculate-roi`  
  - **Method**: `POST`  
  - **Description**: Calculates ROI metrics for a solar installation using a deterministic formula.

---

### 3. Required Headers

For all `/api/v1/*` endpoints:

- **Content-Type**: `application/json` (for JSON requests)
- **X-API-KEY**: your API key

The API key value is read from the `API_KEY` environment variable.

---

### 4. Authentication & Security

- **Authentication mechanism**:  
  - API key header enforced via `@app.before_request` on all paths starting with `/api/`.

- **Behavior when API key is missing or invalid**:  
  - Returns **401 Unauthorized** with JSON body:

```json
{ "error": "Unauthorized" }
```

- **Behavior when `API_KEY` is not configured on the server**:  
  - Returns **500 Internal Server Error** with JSON body:

```json
{ "error": "Internal server error" }
```

- **Transport security**:  
  - Local development uses HTTP (`http://localhost:5000`).  
  - For production deployments, front the service with an HTTPS-terminating proxy or load balancer.

---

### 5. Rate Limiting

Rate limiting is enforced using **Flask-Limiter**.

- **Global default**:  
  - `100 requests per minute` per client IP.

- **ROI endpoint** (`/api/v1/calculate-roi`):  
  - Explicitly decorated with `@limiter.limit("100 per minute")`.  
  - Effective rate limit: **100 requests per minute per IP**.

On limit breach, responses use:

```json
{ "error": "Rate limit exceeded" }
```

with HTTP status **429**.

---

### 6. Request Schema – `POST /api/v1/calculate-roi`

**URL**

```text
POST /api/v1/calculate-roi
```

**Body (JSON, required)**:

```json
{
  "consumption_kwh": 450.0,
  "generation_kwh": 500.0,
  "tariff_per_kwh": 0.20,
  "system_cost_usd": 6000.0
}
```

**Fields**

| Field             | Type    | Required | Description                                | Constraints                      |
|-------------------|---------|----------|--------------------------------------------|----------------------------------|
| `consumption_kwh` | number  | yes      | Monthly energy consumption in kWh          | `> 0` and `≤ 100000`             |
| `generation_kwh`  | number  | yes      | Monthly solar generation in kWh            | `> 0` and `≤ 100000`             |
| `tariff_per_kwh`  | number  | yes      | Electricity tariff in USD per kWh          | `> 0` and `≤ 100`                |
| `system_cost_usd` | number  | yes      | Total solar system cost (USD)              | `> 0` and `≤ 1,000,000`          |

**Request size limit**

- The raw request body size is limited by:

```python
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024  # 100 KB
```

If the payload exceeds this size, the server returns **413** (see error section).

---

### 7. Response Schema – Success (200)

On a valid request, the API responds with HTTP **200 OK** and JSON:

```json
{
  "monthly_savings_usd": 90.0,
  "roi_percentage": 18.0,
  "system_cost_usd": 6000.0
}
```

**Fields**

| Field                | Type   | Description                                              |
|----------------------|--------|----------------------------------------------------------|
| `monthly_savings_usd`| number | Estimated monthly savings in USD                         |
| `roi_percentage`     | number | Annual ROI as a percentage of the system cost           |
| `system_cost_usd`    | number | Echo of the input system cost for traceability          |

> **Note**: The implementation **does not** compute or return a payback period.

---

### 8. Error Responses

All error responses are JSON objects with a single `error` field.

#### 8.1 400 – Bad Request

Returned when:

- Request body is missing, not JSON, or not a JSON object.
- Required fields are missing.
- Fields cannot be parsed as numbers.
- Fields violate numeric constraints (≤ 0, or above configured caps).

**Shapes (examples):**

- Invalid or missing JSON body:

```json
{ "error": "Request body must be a JSON object" }
```

- Missing required field:

```json
{ "error": "Missing field: system_cost_usd" }
```

- Field has non-numeric type:

```json
{ "error": "tariff_per_kwh must be a number" }
```

- Field violates lower bound:

```json
{ "error": "consumption_kwh must be greater than 0.0" }
```

- Field violates upper bound:

```json
{ "error": "tariff_per_kwh must be less than or equal to 100.0" }
```

#### 8.2 413 – Payload Too Large

When the request body exceeds `MAX_CONTENT_LENGTH`:

```json
{ "error": "Request payload too large" }
```

HTTP status **413**.

#### 8.3 429 – Rate Limit Exceeded

When the configured rate limits are exceeded:

```json
{ "error": "Rate limit exceeded" }
```

HTTP status **429**.

#### 8.4 401 – Unauthorized

When the `X-API-KEY` header is missing or does not match the configured `API_KEY`:

```json
{ "error": "Unauthorized" }
```

HTTP status **401**.

#### 8.5 500 – Internal Server Error

For unexpected server errors (including exceptions inside the ROI calculation),
the API returns:

```json
{ "error": "Internal server error" }
```

HTTP status **500**.

Stack traces are **not** included in the JSON body.

---

### 9. Sample `curl` Request

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

Example response:

```json
{
  "monthly_savings_usd": 90.0,
  "roi_percentage": 18.0,
  "system_cost_usd": 6000.0
}
```

---

### 10. Response Schema Table

| Field                | Type   | Present On | Description                                |
|----------------------|--------|-----------:|--------------------------------------------|
| `monthly_savings_usd`| number |      200   | Monthly cost savings in USD                |
| `roi_percentage`     | number |      200   | Annual ROI percentage                      |
| `system_cost_usd`    | number |      200   | Echo of input system cost                  |
| `error`              | string | 4xx / 5xx  | Human‑readable error message               |

---

### 11. Error Codes Summary

| HTTP Status | When Returned                                                 | Example Body                                      |
|-------------|---------------------------------------------------------------|---------------------------------------------------|
| 200         | Successful ROI calculation                                    | `{ "monthly_savings_usd": ..., "roi_percentage": ..., "system_cost_usd": ... }` |
| 400         | Invalid/missing JSON, missing fields, type/validation errors  | `{ "error": "Request body must be a JSON object" }` |
| 401         | Missing or invalid `X-API-KEY`                                | `{ "error": "Unauthorized" }`                     |
| 413         | Request payload exceeds 100 KB                                | `{ "error": "Request payload too large" }`        |
| 429         | Rate limit exceeded                                           | `{ "error": "Rate limit exceeded" }`              |
| 500         | Unexpected server error or missing `API_KEY` configuration    | `{ "error": "Internal server error" }`            |

---

### 12. Security Notes

- Input is strictly validated for type and range to avoid obvious abuse (very
  large numbers, non‑numeric types).
- Request size is capped at 100 KB to prevent oversized payload attacks.
- Rate limiting (100 requests/minute/IP) mitigates brute‑force and abuse.
- Error responses are generic and do not leak stack traces or internal details.

---

### 13. Versioning Notes

- Current version prefix: **`/api/v1`**.
- Any future breaking changes should be introduced under `/api/v2/...` while
  keeping `/api/v1/...` stable for existing consumers.


