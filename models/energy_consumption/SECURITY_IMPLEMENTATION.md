# Security Implementation Guide

## Overview

This document outlines the security features implemented in the ML-based Energy Consumption API (`app_ml.py`) to meet Cybersecurity Team requirements.

## Security Features Implemented

### 1. ✅ API Key Authentication

**Implementation:**
- Requires `X-API-KEY` header in all requests to `/api/v1/estimate-consumption`
- API key is loaded from environment variable using `python-dotenv`
- Health endpoint (`/api/v1/health`) does NOT require authentication

**Code Location:**
- `require_api_key()` decorator function (lines ~97-120)
- Applied to `estimate_consumption()` endpoint

**Configuration:**
- API key stored in `.env` file as `API_KEY`
- See `.env.example` for template

**Error Response:**
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or missing API key",
    "status": 401
  }
}
```

### 2. ✅ Rate Limiting

**Implementation:**
- Using `Flask-Limiter` library
- Limit: **100 requests per minute** per IP address
- Applied to `/api/v1/estimate-consumption` endpoint
- Uses in-memory storage (can be upgraded to Redis for production)

**Code Location:**
- Limiter initialization (lines ~50-60)
- Decorator on `estimate_consumption()` endpoint (line ~123)

**Configuration:**
- Rate limit: `"100 per minute"`
- Key function: `get_remote_address` (IP-based)

### 3. ✅ Enhanced Input Validation

**Implemented Validations:**

#### Numeric Range Validation:
- `sqft_m2`: Must be > 0 and ≤ 10,000 m²
- `operating_hours_weekly`: Must be 0-168 (hours in a week)
- `num_refrigeration_units`: Must be ≥ 0 and ≤ 500
- `num_workers`: Must be > 0 and ≤ 1,000 (if provided)

#### String Format Validation:
- `business_type`: Must match expected values (`butchery`, `grocery`, `mini_supermarket`)
- `location`: Must be non-empty string, max 200 characters

**Code Location:**
- Input validation section (lines ~138-250)

**Error Responses:**
- `400 INVALID_FIELD_VALUE` - Value out of range
- `400 INVALID_FIELD_TYPE` - Wrong data type
- `400 INVALID_BUSINESS_TYPE` - Invalid business type

### 4. ✅ Output Validation & Consistency

**Implemented Validations:**

#### Output Value Validation:
- `estimated_consumption_kwh_monthly`: Capped at 1,000,000 kWh/month
- `confidence_score`: Enforced range [0, 1]
- `breakdown.refrigeration`: Non-negative
- `breakdown.other`: Non-negative
- `climate_adjustment_factor`: Validated to be positive

**Code Location:**
- Output validation section (lines ~300-320)

**Response Format:**
- All responses are strictly JSON
- All numeric values are validated before returning

### 5. ✅ Error Handling & Protection

**Implemented Features:**

#### Error Code Mapping:
- `400` - Bad Request (validation errors, missing fields)
- `401` - Unauthorized (missing/invalid API key)
- `500` - Internal Server Error (model/prediction errors)

#### Stack Trace Hiding:
- All 500 errors return generic "Internal Server Error" message
- Internal error details logged but not exposed to client
- No stack traces in error responses

**Code Location:**
- Exception handling (lines ~318-340)

**Error Response Format:**
```json
{
  "error": {
    "code": "PREDICTION_ERROR",
    "message": "Internal Server Error",
    "status": 500
  }
}
```

### 6. ✅ Configuration Management

**Implementation:**
- Uses `python-dotenv` to load environment variables
- API key loaded from `.env` file
- No hardcoded secrets in code

**Code Location:**
- Environment loading (lines ~10-12)
- API key configuration (lines ~50-55)

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

New dependencies added:
- `flask-limiter>=3.5.0`
- `python-dotenv>=1.0.0`

### 2. Create `.env` File

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and set your API key:

```env
API_KEY=your-secure-api-key-here
```

**Generate a secure API key:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Run the API

```bash
cd src
python app_ml.py
```

## API Usage with Security

### Authenticated Request Example

```bash
curl -X POST "http://localhost:8001/api/v1/estimate-consumption" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: your-secure-api-key-here" \
  -d '{
    "business_type": "butchery",
    "sqft_m2": 60.0,
    "operating_hours_weekly": 98.0,
    "num_refrigeration_units": 3,
    "location": "Lagos, Nigeria"
  }'
```

### Health Check (No Auth Required)

```bash
curl "http://localhost:8001/api/v1/health"
```

## Testing

### Run Security Tests

```bash
# Run all security tests
pytest tests/test_security_ml.py -v

# Run all tests (including security)
pytest tests/ -v
```

### Test Coverage

Security tests cover:
- ✅ API key authentication (missing, invalid, valid)
- ✅ Enhanced input validation (max values, string length)
- ✅ Output validation (positive values, realistic ranges)
- ✅ Error handling (hidden stack traces)

## Security Checklist Compliance

| Requirement | Status | Implementation |
|------------|--------|---------------|
| API Key Authentication | ✅ | `X-API-KEY` header, env var |
| Rate Limiting (100/min) | ✅ | Flask-Limiter |
| Input Validation (ranges) | ✅ | All numeric fields validated |
| Reject Wrong Data (>500 units) | ✅ | Max 500 refrigeration units |
| Format Validation | ✅ | business_type, location |
| JSON-only Responses | ✅ | All responses use `jsonify()` |
| Realistic Output Values | ✅ | Capped at 1M kWh, confidence [0,1] |
| Specific Error Codes | ✅ | 400, 401, 500 |
| Hide Stack Traces | ✅ | Generic "Internal Server Error" |
| Environment Variables | ✅ | python-dotenv, .env file |

## Production Recommendations

1. **API Key Management:**
   - Use a secrets management service (AWS Secrets Manager, HashiCorp Vault)
   - Rotate API keys regularly
   - Use different keys for different environments

2. **Rate Limiting:**
   - Upgrade to Redis-backed rate limiting for distributed systems
   - Implement per-user rate limits (if user authentication added)

3. **Logging:**
   - Set up structured logging (JSON format)
   - Log authentication failures and rate limit violations
   - Monitor for suspicious patterns

4. **HTTPS:**
   - Always use HTTPS in production
   - API keys should never be sent over HTTP

5. **Input Validation:**
   - Consider adding request size limits
   - Implement request signing for additional security

6. **Error Handling:**
   - Set up error monitoring (Sentry, Rollbar)
   - Log detailed errors server-side only

## Notes

- **Payback Period:** As requested, no validation for payback period (feature removed)
- **Health Endpoint:** Does not require authentication (standard practice)
- **Test Mode:** Tests use `disable_auth=True` to bypass authentication
- **Rate Limiting:** Uses in-memory storage (suitable for single-instance deployments)

## Support

For security concerns or questions, contact the Cybersecurity Team.

