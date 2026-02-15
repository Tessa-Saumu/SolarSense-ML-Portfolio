# 🔗 INTEGRATION GUIDE & BACKEND REQUIREMENTS
## Model 4: AI Recommendation Engine

**Owner:** Bella  
**For:** Backend Developers & System Integrators

---

## 📋 TABLE OF CONTENTS

1. [Backend Requirements](#backend-requirements)
2. [Integration Steps](#integration-steps)
3. [API Contract](#api-contract)
4. [Database Schema](#database-schema)
5. [Error Handling](#error-handling)
6. [Performance Considerations](#performance-considerations)
7. [Security Requirements](#security-requirements)

---

## 💻 BACKEND REQUIREMENTS

### **System Requirements:**

| Component | Requirement | Notes |
|-----------|-------------|-------|
| **Python** | 3.8+ | Tested on 3.11 |
| **RAM** | Minimum 512MB | 1GB recommended |
| **CPU** | 1 vCPU | 2+ for production |
| **Storage** | 100MB | For app + logs |
| **Network** | Outbound HTTPS | To call Models 1-3 |

### **Python Dependencies:**

```
Flask==3.0.0          # Web framework
Flask-CORS==4.0.0     # CORS support
Flask-Limiter==3.5.0  # Rate limiting
python-dotenv==1.0.0  # Environment variables
requests==2.31.0      # HTTP client
gunicorn==21.2.0      # Production server
```

**Install all:**
```bash
pip install -r requirements_model4.txt
```

### **Environment Variables Required:**

```bash
# Required
API_KEY=<your_generated_key>
MODELS_API_KEY=API_KEY
MODELS_BASE_URL=https://dse-models-production.up.railway.app/api/v1

# Optional
PORT=5000
FLASK_ENV=production
DATABASE_URL=postgresql://...  # If using database
```

### **External Services:**

Model 4 depends on:

1. **Model 1 API** (Railway)
   - URL: `{MODELS_BASE_URL}/estimate-consumption`
   - Timeout: 30s
   - Required: Yes

2. **Model 2 API** (Railway)
   - URL: `{MODELS_BASE_URL}/predict-generation`
   - Timeout: 30s
   - Required: Yes

3. **Model 3 API** (Railway)
   - URL: `{MODELS_BASE_URL}/calculate-roi`
   - Timeout: 30s
   - Required: Yes

4. **Database** (Optional)
   - PostgreSQL 13+
   - For storing analysis results
   - Not required for MVP

---

## 🔄 INTEGRATION STEPS

### **Step 1: Verify Models 1-3 are Running**

```bash
# Test Model 1
curl -X POST "https://dse-models-production.up.railway.app/api/v1/estimate-consumption" \
  -H "X-API-KEY: API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "equipment_list": [{"equipment_type": "refrigerator", "quantity": 1, "hours_per_day": 24}],
    "business_type": "Cafe"
  }'

# Test Model 2
curl -X POST "https://dse-models-production.up.railway.app/api/v1/predict-generation" \
  -H "X-API-KEY: API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"latitude": -1.2921, "longitude": 36.8219}'

# Test Model 3
curl -X POST "https://dse-models-production.up.railway.app/api/v1/calculate-roi" \
  -H "X-API-KEY: API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"consumption_kwh": 2500, "generation_kwh": 3000, "tariff": 0.15}'
```

**All should return 200 OK with JSON data**

---

### **Step 2: Setup Model 4 Environment**

```bash
# Clone/download Model 4 code
cd model4

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements_model4.txt

# Create .env file
cp .env_model4 .env

# Generate API key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Edit .env file with your API key
nano .env
```

---

### **Step 3: Configure Integration**

Edit `.env` file:

```bash
# Your Model 4 API key (generated in Step 2)
API_KEY=kR7vN3mP9xQ2wL5yT8aF6bH4cJ1dE0gK9sM3nR7pL2

# Models 1-3 configuration (from team)
MODELS_API_KEY=API_KEY
MODELS_BASE_URL=https://dse-models-production.up.railway.app/api/v1

# Optional
PORT=5000
FLASK_ENV=production
```

---

### **Step 4: Test Locally**

```bash
# Start Model 4
python model4_app.py

# In another terminal, test
curl http://127.0.0.1:5000/health

# Should see:
# {"status": "healthy", "service": "Model 4 Orchestration", ...}
```

---

### **Step 5: Run Integration Tests**

```bash
# Run comprehensive test suite
python test.py

# Should see:
# ✅ ALL TESTS PASSED
# Success rate: 100%
```

---

### **Step 6: Deploy to Production**

See [Deployment](#deployment-to-railway) section

---

## 📡 API CONTRACT

### **Request Format (POST /api/v1/analyze):**

```typescript
interface AnalysisRequest {
  // Required fields
  business_name: string;        // 1-200 characters
  business_type: BusinessType;  // See allowed values below
  location: string;             // Human-readable location
  latitude: number;             // -90 to 90
  longitude: number;            // -180 to 180
  equipment_list: Equipment[];  // Max 500 items
  
  // Optional fields
  tariff?: number;              // Default: 0.15 ($/kWh)
}

interface Equipment {
  equipment_type: string;       // e.g., "refrigerator"
  quantity: number;             // 0-100
  hours_per_day?: number;       // 0-24, optional
}

type BusinessType = 
  | "Restaurant"
  | "Retail"
  | "Office"
  | "Hotel"
  | "Healthcare"
  | "Education"
  | "Manufacturing"
  | "Food & Beverage"
  | "Cafe"
  | "Gym"
  | "Bakery"
  | "Entertainment"
  | "Workshop";
```

### **Response Format (200 OK):**

```typescript
interface AnalysisResponse {
  // Input echo
  business_name: string;
  business_type: string;
  location: string;
  
  // Model 1 outputs
  estimated_consumption_kwh: number;  // Non-negative
  
  // Model 2 outputs
  predicted_generation_kwh: number;   // Non-negative
  
  // Model 3 outputs
  roi_percentage: number;             // Non-negative
  monthly_savings: number;            // In dollars
  system_cost: number;                // In dollars
  
  // Model 4 outputs
  recommendation: "High" | "Medium" | "Low";
  viability_score: number;            // 0-100
  status: "HIGHLY VIABLE" | "MODERATELY VIABLE" | "NOT VIABLE";
  explanation: string;                // Human-readable
  confidence: number;                 // 0-100
  
  // Metadata
  analyzed_at: string;                // ISO 8601 timestamp
}
```

### **Error Responses:**

```typescript
interface ErrorResponse {
  error: string;        // Error category
  message: string;      // Human-readable message
}

// Status codes:
// 400 - Bad Request (validation error)
// 401 - Unauthorized (missing/invalid API key)
// 404 - Not Found (invalid endpoint)
// 429 - Too Many Requests (rate limit)
// 500 - Internal Server Error
// 503 - Service Unavailable (models down)
```

---

## 🗄️ DATABASE SCHEMA

**Optional: For storing analysis results**

```sql
-- Table 1: Businesses
CREATE TABLE businesses (
    id SERIAL PRIMARY KEY,
    business_name VARCHAR(200) NOT NULL,
    business_type VARCHAR(100) NOT NULL,
    location VARCHAR(200),
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 2: Equipment
CREATE TABLE equipment (
    id SERIAL PRIMARY KEY,
    business_id INTEGER REFERENCES businesses(id) ON DELETE CASCADE,
    equipment_type VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity >= 0 AND quantity <= 100),
    hours_per_day DECIMAL(4, 2) CHECK (hours_per_day >= 0 AND hours_per_day <= 24),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 3: Analysis Results
CREATE TABLE analysis_results (
    id SERIAL PRIMARY KEY,
    business_id INTEGER REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Model outputs
    estimated_consumption_kwh DECIMAL(10, 2),
    predicted_generation_kwh DECIMAL(10, 2),
    roi_percentage DECIMAL(5, 2),
    monthly_savings DECIMAL(10, 2),
    system_cost DECIMAL(10, 2),
    
    -- Recommendation
    recommendation VARCHAR(20) CHECK (recommendation IN ('High', 'Medium', 'Low')),
    viability_score DECIMAL(5, 2) CHECK (viability_score >= 0 AND viability_score <= 100),
    status VARCHAR(50),
    explanation TEXT,
    confidence DECIMAL(5, 2),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_business_id (business_id),
    INDEX idx_recommendation (recommendation),
    INDEX idx_created_at (created_at)
);

-- Table 4: API Logs (for monitoring)
CREATE TABLE api_logs (
    id SERIAL PRIMARY KEY,
    endpoint VARCHAR(200),
    method VARCHAR(10),
    status_code INTEGER,
    request_data JSONB,
    response_data JSONB,
    error_message TEXT,
    execution_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_endpoint (endpoint),
    INDEX idx_status_code (status_code),
    INDEX idx_created_at (created_at)
);
```

**To use database:**

1. Create database:
   ```bash
   createdb solar_viability
   ```

2. Run schema:
   ```bash
   psql -d solar_viability -f database_schema.sql
   ```

3. Add to `.env`:
   ```bash
   DATABASE_URL=postgresql://user:pass@localhost:5432/solar_viability
   ```

4. Uncomment database code in `model4_app.py`

---

## ⚠️ ERROR HANDLING

### **Error Handling Strategy:**

```python
try:
    # Call Model 1
    model1_data = call_model1(...)
except requests.Timeout:
    # Model took too long
    return 503, "Model 1 timeout"
except requests.ConnectionError:
    # Model is down
    return 503, "Model 1 unavailable"
except Exception as e:
    # Unexpected error - DON'T expose details
    logger.error(f"Model 1 error: {str(e)}")
    return 500, "Internal server error"
```

### **Graceful Degradation:**

If any Model (1, 2, or 3) fails:
1. ✅ Error is logged internally
2. ✅ Return 503 Service Unavailable
3. ✅ Include partial info if available
4. ❌ Do NOT expose internal errors
5. ❌ Do NOT return stack traces

### **Retry Strategy:**

Models 1-3 calls:
- ✅ Timeout: 30 seconds
- ❌ No automatic retries (to respect rate limits)
- ✅ Client can retry on 503

---

## ⚡ PERFORMANCE CONSIDERATIONS

### **Expected Latencies:**

| Operation | Time | Notes |
|-----------|------|-------|
| Model 1 call | 1-3s | Energy consumption |
| Model 2 call | 1-3s | Solar generation |
| Model 3 call | 0.5-1s | ROI calculation |
| Model 4 logic | <100ms | Recommendation |
| **Total** | **3-7s** | End-to-end |

### **Optimization Tips:**

1. **Parallel Model Calls** (future):
   ```python
   # Instead of sequential:
   # model1 → model2 → model3
   
   # Use async/concurrent:
   # model1 + model2 in parallel → model3
   ```

2. **Caching** (future):
   - Cache Model 2 results by lat/long (solar doesn't change)
   - TTL: 24 hours

3. **Database Connection Pooling:**
   ```python
   from sqlalchemy.pool import QueuePool
   engine = create_engine(
       DATABASE_URL,
       poolclass=QueuePool,
       pool_size=10,
       max_overflow=20
   )
   ```

### **Scaling:**

For high traffic:
1. Use Gunicorn with 4+ workers:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 model4_app:app
   ```

2. Add Redis for rate limiting:
   ```python
   limiter = Limiter(
       storage_uri="redis://localhost:6379"
   )
   ```

3. Use load balancer (Railway handles this)

---

## 🔒 SECURITY REQUIREMENTS

### **Authentication:**

**Required:**
- ✅ API key in `X-API-KEY` header
- ✅ Stored in environment variable (not hardcoded)
- ✅ Minimum 32 characters
- ✅ URL-safe base64 encoded

**Generate:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### **Rate Limiting:**

**Implemented:**
- ✅ 100 requests/minute per IP
- ✅ Returns 429 if exceeded
- ✅ Uses in-memory storage (production: use Redis)

**Override (if needed):**
```python
limiter = Limiter(
    default_limits=["200 per minute"]  # Increase limit
)
```

### **Input Validation:**

**Required checks:**
- ✅ All required fields present
- ✅ Data types correct
- ✅ Ranges realistic:
  - Latitude: -90 to 90
  - Longitude: -180 to 180
  - Quantity: 0 to 100
  - Hours: 0 to 24
- ✅ business_type in allowed list
- ✅ equipment_list max 500 items

### **Output Sanitization:**

**Required:**
- ✅ Viability score: 0-100
- ✅ ROI: Non-negative
- ✅ Energy values: Non-negative
- ✅ No stack traces in errors
- ✅ No internal paths/details exposed

### **HTTPS Requirements:**

**Production:**
- ✅ Must use HTTPS
- ✅ Railway provides this automatically
- ✅ Redirect HTTP → HTTPS

**Local Development:**
- ⚠️ HTTP is OK for localhost

---

## 🚀 DEPLOYMENT TO RAILWAY

### **Prerequisites:**

1. Railway account
2. Models 1-3 already deployed
3. Code pushed to Git

### **Deployment Steps:**

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
railway init

# 4. Link to existing project (if applicable)
railway link

# 5. Set environment variables
railway variables set API_KEY=your_generated_key
railway variables set MODELS_API_KEY=API_KEY
railway variables set MODELS_BASE_URL=https://dse-models-production.up.railway.app/api/v1

# 6. Deploy
railway up

# 7. Get deployment URL
railway domain
```

### **Required Files:**

**Procfile:**
```
web: gunicorn model4_app:app
```

**runtime.txt:**
```
python-3.11.0
```

**requirements_model4.txt:**
(Already provided)

### **Verify Deployment:**

```bash
# Get your Railway URL
RAILWAY_URL=$(railway domain)

# Test health
curl https://$RAILWAY_URL/health

# Test with API key
curl -X POST "https://$RAILWAY_URL/api/v1/analyze" \
  -H "X-API-KEY: your_api_key" \
  -H "Content-Type: application/json" \
  -d @test_data.json
```

---

## ✅ INTEGRATION CHECKLIST

Before going live:

### **Setup:**
- [ ] Python 3.8+ installed
- [ ] All dependencies installed
- [ ] .env file created with all variables
- [ ] API key generated (32+ characters)

### **Configuration:**
- [ ] MODELS_BASE_URL correct
- [ ] MODELS_API_KEY = API_KEY
- [ ] Database configured (if using)

### **Testing:**
- [ ] Health endpoint returns 200
- [ ] Models 1-3 accessible
- [ ] Authentication working (401 without key)
- [ ] Rate limiting working (429 after 100 req)
- [ ] Valid requests return 200
- [ ] Invalid inputs return 400
- [ ] Test suite passes (python test.py)

### **Security:**
- [ ] API key in environment variable
- [ ] No hardcoded secrets
- [ ] .env in .gitignore
- [ ] HTTPS enabled (production)
- [ ] Error messages don't leak info

### **Deployment:**
- [ ] Procfile created
- [ ] runtime.txt created
- [ ] Railway variables set
- [ ] Deployed successfully
- [ ] Production URL working

---

## 📞 SUPPORT & CONTACT

**For integration issues:**

1. Check this guide
2. Run `python test.py` for diagnostics
3. Check logs: `tail -f logs/model4.log`
4. Contact: Bella (Model 4 Owner)

**Common Issues:**
- Models timeout → Check Railway status
- 401 errors → Verify API key in .env
- 400 errors → Check request format
- 503 errors → Models 1-3 may be down

---

**Last Updated:** February 14, 2024  
**Version:** 1.0.0  
**Maintained by:** Bella
