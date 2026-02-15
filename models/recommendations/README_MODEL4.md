#  MODEL 4: AI RECOMMENDATION ENGINE & ORCHESTRATION

**Solar Viability Assessment System**  
**Owner:** Bella  
**Version:** 1.0.0  
**Last Updated:** February 14, 2026

---

##  TABLE OF CONTENTS

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Quick Start](#quick-start)
4. [API Documentation](#api-documentation)
5. [Security Features](#security-features)
6. [Integration with Models 1-3](#integration-with-models-1-3)
7. [Testing](#testing)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)

---

##  OVERVIEW

Model 4 is the **master orchestration layer** that coordinates Models 1-3 and generates final solar viability recommendations.

### **What It Does:**

1.  Calls Model 1 (Energy Consumption Estimation)
2.  Calls Model 2 (Solar Generation Prediction)
3.  Calls Model 3 (Financial Viability & ROI)
4.  Applies intelligent recommendation logic
5.  Returns viability score (High/Medium/Low) with explanation

### **Key Features:**

-  **Secure** - API key authentication, rate limiting
-  **Validated** - Input/output validation, realistic ranges
-  **Protected** - Error handling, no leaked information
-  **Resilient** - Graceful degradation if models unavailable
-  **Explainable** - Clear reasoning for recommendations

---

## 🏗️ ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT                              │
│            (Web App / Mobile / API Consumer)                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ POST /api/v1/analyze
                         │ (with X-API-KEY header)
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                       MODEL 4                               │
│            AI Recommendation Engine                         │
│               (This Application)                            │
│                                                             │
│  1. Validate Input                                          │
│  2. Call Model 1 → Consumption                              │
│  3. Call Model 2 → Generation                               │
│  4. Call Model 3 → ROI                                      │
│  5. Generate Recommendation                                 │
│  6. Return Result                                           │
└─────────┬──────────┬──────────┬────────────────────────────┘
          │          │          │
          │          │          │ (All via Railway API)
          ▼          ▼          ▼
    ┌─────────┐ ┌─────────┐ ┌─────────┐
    │ Model 1 │ │ Model 2 │ │ Model 3 │
    │ Energy  │ │ Solar   │ │   ROI   │
    │ Consump.│ │ Gener.  │ │  Calc.  │
    └─────────┘ └─────────┘ └─────────┘
```

---

##  QUICK START

### **Prerequisites:**

- Python 3.8+
- pip
- Models 1-3 deployed on Railway (already done!)

### **Installation:**

```bash
# 1. Clone repository
git clone <your-repo-url>
cd model4

# 2. Install dependencies
pip install -r requirements_model4.txt

# 3. Create .env file
cp .env_model4 .env

# 4. Generate your API key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 5. Edit .env file
# Add your generated API key to API_KEY
# MODELS_API_KEY should be: API_KEY (as provided by your team)

# 6. Run the application
python model4_app.py
```

### **Verify It's Working:**

```bash
# Health check (no auth needed)
curl http://127.0.0.1:5000/health

# Expected: {"status": "healthy", ...}
```

---

##  API DOCUMENTATION

### **Base URL:**
```
Local: http://127.0.0.1:5000
Production: https://your-deployment-url.com
```

### **Authentication:**
All `/api/v1/*` endpoints require API key:
```
Header: X-API-KEY: your_api_key_here
```

---

### **ENDPOINT 1: Health Check**

**No authentication required**

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Model 4 Orchestration",
  "timestamp": "2024-02-14T10:30:00.000000",
  "version": "1.0.0"
}
```

---

### **ENDPOINT 2: API Information**

**No authentication required**

```http
GET /
```

**Response:**
```json
{
  "service": "Solar Viability Assessment - Model 4",
  "description": "AI Recommendation Engine & Orchestration",
  "version": "1.0.0",
  "owner": "Bella",
  "endpoints": {
    "health": "GET /health",
    "analyze": "POST /api/v1/analyze",
    "models_status": "GET /api/v1/models/status"
  },
  "security": "API key required (X-API-KEY header)",
  "integrated_models": {
    "model_1": "Energy Consumption Estimation",
    "model_2": "Solar Generation Prediction",
    "model_3": "Financial Viability & ROI"
  }
}
```

---

### **ENDPOINT 3: Solar Viability Analysis** 

**Requires authentication**

```http
POST /api/v1/analyze
Content-Type: application/json
X-API-KEY: your_api_key_here
```

**Request Body:**
```json
{
  "business_name": "Joe's Coffee Shop",
  "business_type": "Cafe",
  "location": "Nairobi, Kenya",
  "latitude": -1.2921,
  "longitude": 36.8219,
  "equipment_list": [
    {
      "equipment_type": "refrigerator",
      "quantity": 2,
      "hours_per_day": 24
    },
    {
      "equipment_type": "espresso_machine",
      "quantity": 1,
      "hours_per_day": 10
    },
    {
      "equipment_type": "lights",
      "quantity": 15,
      "hours_per_day": 12
    }
  ],
  "tariff": 0.15
}
```

**Required Fields:**
- `business_name` (string, 1-200 chars)
- `business_type` (string, one of: Restaurant, Retail, Office, Hotel, Healthcare, Education, Manufacturing, Food & Beverage, Cafe, Gym, Bakery, Entertainment, Workshop)
- `location` (string)
- `latitude` (float, -90 to 90)
- `longitude` (float, -180 to 180)
- `equipment_list` (array, max 500 items)
  - Each item must have:
    - `equipment_type` (string)
    - `quantity` (integer, 0-100)
    - `hours_per_day` (float, 0-24) - optional

**Optional Fields:**
- `tariff` (float, default 0.15) - electricity cost in $/kWh

**Success Response (200 OK):**
```json
{
  "business_name": "Joe's Coffee Shop",
  "business_type": "Cafe",
  "location": "Nairobi, Kenya",
  "estimated_consumption_kwh": 2500.5,
  "predicted_generation_kwh": 3200.8,
  "roi_percentage": 18.5,
  "monthly_savings": 125.75,
  "system_cost": 15000,
  "recommendation": "High",
  "viability_score": 85.3,
  "status": "HIGHLY VIABLE",
  "explanation": "Solar is highly viable because: Strong ROI of 18.5%; Excellent solar coverage (128% of consumption); Significant monthly savings ($125.75).",
  "confidence": 92.5,
  "analyzed_at": "2024-02-14T10:30:00.000000"
}
```

**Recommendation Levels:**
- `High` (score ≥ 70) - Highly recommended
- `Medium` (score 50-69) - Moderately recommended
- `Low` (score < 50) - Not recommended

**Error Responses:**

```json
// 400 Bad Request - Invalid input
{
  "error": "Bad Request",
  "message": "latitude must be between -90 and 90"
}

// 401 Unauthorized - Missing/invalid API key
{
  "error": "Unauthorized",
  "message": "API key is required. Include X-API-KEY header."
}

// 503 Service Unavailable - Models 1-3 down
{
  "error": "Service Unavailable",
  "message": "Unable to complete analysis. One or more required services are unavailable.",
  "business_name": "Joe's Coffee Shop",
  "status": "INCOMPLETE"
}

// 500 Internal Server Error
{
  "error": "Internal Server Error",
  "message": "An error occurred processing your request. Please contact support."
}
```

---

### **ENDPOINT 4: Models Status** 

**Requires authentication**

```http
GET /api/v1/models/status
X-API-KEY: your_api_key_here
```

**Response:**
```json
{
  "model_4": "operational",
  "integrated_models": {
    "base_url": "https://dse-models-production.up.railway.app/api/v1",
    "status": "healthy",
    "model_1": "Energy Consumption Estimation",
    "model_2": "Solar Generation Prediction",
    "model_3": "Financial Viability & ROI"
  },
  "timestamp": "2024-02-14T10:30:00.000000"
}
```

---

##  SECURITY FEATURES

### **1. API Key Authentication**

All `/api/v1/*` endpoints require valid API key in header:

```bash
X-API-KEY: your_api_key_here
```

**Enforced by:** `@require_api_key` decorator

---

### **2. Rate Limiting**

Limits: **100 requests per minute** per IP address

**Enforced by:** Flask-Limiter

**Response if exceeded:**
```json
{
  "error": "Too Many Requests",
  "message": "Rate limit exceeded"
}
```
Status: `429 Too Many Requests`

---

### **3. Input Validation**

All inputs are validated for:

- ✅ **Required fields** - Missing fields rejected
- ✅ **Data types** - Must match expected types
- ✅ **Realistic ranges:**
  - Latitude: -90 to 90
  - Longitude: -180 to 180
  - Quantity: 0 to 100 per item
  - Hours: 0 to 24 per day
  - Equipment list: Max 500 items
- ✅ **Allowed values** - business_type must be from approved list

**Enforced by:** `validate_business_input()` function

---

### **4. Output Validation**

All outputs are sanitized:

- ✅ Viability score: 0-100
- ✅ ROI: Non-negative
- ✅ Energy values: Non-negative
- ✅ No payback period (removed from project)

**Enforced by:** `validate_output()` function

---

### **5. Error Handling**

- ✅ **400** - Bad Request (validation errors)
- ✅ **401** - Unauthorized (missing/invalid API key)
- ✅ **404** - Not Found (invalid endpoint)
- ✅ **429** - Too Many Requests (rate limit exceeded)
- ✅ **500** - Internal Server Error (no details leaked)
- ✅ **503** - Service Unavailable (models down)

**No stack traces or internal details exposed in errors!**

---

## 🔗 INTEGRATION WITH MODELS 1-3

Model 4 integrates with deployed Models 1-3 on Railway:

**Base URL:** `https://dse-models-production.up.railway.app/api/v1`  
**API Key:** `API_KEY` (sent as `X-API-KEY` header)

### **Integration Points:**

1. **Model 1 - Energy Consumption**
   ```
   POST /api/v1/estimate-consumption
   ```
   - Sends: equipment_list, business_type
   - Receives: estimated_consumption_kwh, confidence

2. **Model 2 - Solar Generation**
   ```
   POST /api/v1/predict-generation
   ```
   - Sends: latitude, longitude
   - Receives: predicted_generation_kwh, confidence

3. **Model 3 - ROI Calculation**
   ```
   POST /api/v1/calculate-roi
   ```
   - Sends: consumption_kwh, generation_kwh, tariff
   - Receives: roi_percentage, monthly_savings, system_cost

### **Resilience:**

If any model fails:
- ✅ Error is logged
- ✅ User receives 503 Service Unavailable
- ✅ No internal details exposed
- ✅ Graceful degradation

---

## 🧪 TESTING

### **Automated Tests:**

```bash
# Run comprehensive test suite
python test.py

# Expected output:
# ✅ All tests passed
# Success rate: 100%
```

### **Manual Tests:**

```bash
# 1. Health check
curl http://127.0.0.1:5000/health

# 2. Valid analysis (replace with your API key)
curl -X POST http://127.0.0.1:5000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: your_api_key_here" \
  -d '{
    "business_name": "Test Cafe",
    "business_type": "Cafe",
    "location": "Nairobi, Kenya",
    "latitude": -1.2921,
    "longitude": 36.8219,
    "equipment_list": [
      {"equipment_type": "refrigerator", "quantity": 2, "hours_per_day": 24}
    ]
  }'

# 3. Test without API key (should fail with 401)
curl -X POST http://127.0.0.1:5000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{...}'
```

---

##  DEPLOYMENT

### **Deploy to Railway:**

1. **Prepare for deployment:**
   ```bash
   # Create Procfile
   echo "web: gunicorn model4_app:app" > Procfile
   
   # Create runtime.txt
   echo "python-3.11.0" > runtime.txt
   ```

2. **Deploy to Railway:**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login
   railway login
   
   # Initialize project
   railway init
   
   # Deploy
   railway up
   ```

3. **Set environment variables in Railway:**
   ```
   API_KEY=your_generated_api_key
   MODELS_API_KEY=API_KEY
   MODELS_BASE_URL=https://dse-models-production.up.railway.app/api/v1
   ```

4. **Test deployed API:**
   ```bash
   curl https://your-railway-url.railway.app/health
   ```

---

## 🔧 TROUBLESHOOTING

### **Problem: 401 Unauthorized**

**Solution:** Check API key in `.env` file and request header match

```bash
# Verify .env
cat .env | grep API_KEY

# Test with correct key
curl -H "X-API-KEY: $(grep API_KEY .env | cut -d'=' -f2)" http://localhost:5000/api/v1/models/status
```

---

### **Problem: 503 Service Unavailable**

**Solution:** Models 1-3 may be down. Check their status:

```bash
curl -H "X-API-KEY: API_KEY" https://dse-models-production.up.railway.app/api/v1/health
```

---

### **Problem: Invalid input errors**

**Solution:** Check request format matches API documentation exactly

Common issues:
- Missing required fields
- business_type not in allowed list
- latitude/longitude out of range
- hours_per_day > 24

---

### **Problem: Flask app won't start**

**Solution:**

```bash
# Check dependencies
pip install -r requirements_model4.txt

# Check .env file exists
ls -la .env

# Check API_KEY is set
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('API_KEY'))"

# Run with verbose logging
python model4_app.py
```

---

## 📞 SUPPORT

**Owner:** Bella  
**Project:** Solar Viability Assessment System  
**Model:** Model 4 - AI Recommendation Engine & Orchestration

For issues or questions:
1. Check this README
2. Run `python test.py` to diagnose
3. Check logs for error details
4. Contact team lead

---


