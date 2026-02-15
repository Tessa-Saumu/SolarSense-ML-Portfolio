# Cursor AI Analysis Prompt: Model 3 ROI Calculation Review

## Task
Analyze the contents of the `roi_calculation` folder (Zainabu's Model 3 implementation) and verify it meets ALL requirements from the DSE Team Alignment Document V2.1.

## What to Check

### 1. Required Files
Based on Definition of Done (V2.1, page 7-8), the folder MUST contain:

- [ ] `app.py` (Flask API endpoint)
- [ ] `README.md` (setup instructions)
- [ ] `requirements.txt` (dependencies)
- [ ] API documentation (request/response schemas, examples)
- [ ] Test file or test examples

### 2. Core Functionality Requirements (V2.1, page 3)

**Model 3: Financial Viability & ROI Calculation**

#### Required Inputs (app.py must accept):
```python
{
  "consumption_kwh": float,        # Monthly consumption from Model 1
  "generation_kwh": float,          # Monthly generation from Model 2
  "tariff_per_kwh": float,         # Electricity tariff ($/kWh)
  "system_cost_usd": float         # Solar system cost
}
```

#### Required Outputs (app.py must return):
```python
{
  "roi_percentage": float,
  "monthly_savings_usd": float,
  "system_cost_usd": float,
  # NO payback_period - this was explicitly descoped
}
```

#### Critical Requirements:
- [ ] **NO PAYBACK PERIOD** in calculations or response (descoped per V2.1)
- [ ] Uses `/api/v1/calculate-roi` endpoint (API versioning requirement)
- [ ] Mathematically accurate calculations (formula-based, not ML)
- [ ] Input validation (all values must be > 0)
- [ ] Error handling (400 for bad input, 500 for server errors)

### 3. API Endpoint Structure (V2.1, page 8)

**Required endpoint:**
```
POST /api/v1/calculate-roi
```

**NOT acceptable:**
- `POST /calculate-roi` (missing /api/v1/ prefix)
- Any other endpoint name

### 4. Division of Labor Check (V2.1, page 3)

Model 3 was assigned to:
- **Zainabu:** ROI calculation formulas, tariff data collection, cost benchmarks
- **Evelyn:** Flask API structure, error handling, testing, documentation

Check if code shows:
- [ ] Clear ROI calculation formulas
- [ ] Proper Flask API structure
- [ ] Input validation
- [ ] Error handling (generic error messages, no stack traces)
- [ ] Request size limits
- [ ] Rate limiting (optional but recommended)

### 5. ROI Calculation Formula (Expected)

The code should implement something like:
```python
# Monthly savings
monthly_savings = (generation_kwh * tariff_per_kwh) - operational_costs

# Annual savings
annual_savings = monthly_savings * 12

# ROI percentage
roi_percentage = (annual_savings / system_cost_usd) * 100

# System recommendation (if included)
if roi_percentage > 20:
    recommendation = "Highly Viable"
elif roi_percentage >= 10:
    recommendation = "Moderately Viable"
else:
    recommendation = "Not Viable"
```

### 6. Security Requirements (Added Feb 11)

Check for:
- [ ] Input validation (type checking, range validation)
- [ ] Numeric validation (all inputs > 0)
- [ ] Max value caps (e.g., consumption < 100,000 kWh)
- [ ] Safe division (zero checks to prevent division by zero)
- [ ] Generic error responses (no stack traces exposed)
- [ ] Request size limit (`app.config['MAX_CONTENT_LENGTH']`)
- [ ] Rate limiting (Flask-Limiter - 100 requests/minute)

### 7. Dependencies Check (requirements.txt)

Expected libraries:
```
flask
flask-cors
flask-limiter  # For rate limiting
pandas  # If using for data handling
numpy   # If using for calculations
```

### 8. README.md Completeness

Must include:
- [ ] Setup instructions
- [ ] How to run the API
- [ ] API endpoint documentation
- [ ] Request/response examples
- [ ] Dependencies installation
- [ ] Known limitations

### 9. Definition of Done Checklist (V2.1, page 7-8)

- [ ] 1. Functional API endpoint (local Flask running)
- [ ] 2. Tested with sample inputs, returns reasonable outputs
- [ ] 3. API documentation (request schema, response format, example calls, error codes)
- [ ] 4. Code pushed to GitHub with clear README
- [ ] 5. Handoff doc for Sarah (integration steps, dependencies, known limitations)
- [ ] 6. AI usage documented (which tools used, prompts that worked, time saved)
- [ ] 7. API endpoints use `/api/v1/` prefix (versioning requirement)
- [ ] 8. **NO payback period** in Model 3 outputs or Model 4 decision logic

### 10. Red Flags to Report

**CRITICAL ISSUES (Must be fixed before handoff):**
- Missing `/api/v1/` prefix in endpoint
- Payback period calculation present
- No input validation
- No error handling
- Incorrect formula implementation
- Missing dependencies in requirements.txt
- No API documentation

**MAJOR ISSUES (Should be fixed):**
- No rate limiting
- No request size limits
- No test cases
- Incomplete README
- No example requests/responses

**MINOR ISSUES (Nice to have):**
- No AI usage documentation
- Limited error messages
- No logging

---

## Analysis Instructions for Cursor

**Step 1:** List all files in the `roi_calculation` folder

**Step 2:** Read and analyze `app.py`:
- Identify the endpoint route(s)
- Check if `/api/v1/calculate-roi` is present
- Verify input validation exists
- Check for payback period calculations (MUST NOT exist)
- Verify ROI calculation formula
- Check error handling implementation
- Verify Flask-Limiter usage (rate limiting)

**Step 3:** Read and analyze `README.md`:
- Check for setup instructions
- Check for API documentation
- Check for example requests/responses

**Step 4:** Read `requirements.txt` (if exists):
- Verify Flask is listed
- Check for flask-cors
- Check for flask-limiter
- Note any missing dependencies

**Step 5:** Check for test files or examples

**Step 6:** Generate a report in this format:

```markdown
# Model 3 ROI Calculation - Code Review Report

## Files Found
- [ ] app.py
- [ ] README.md
- [ ] requirements.txt
- [ ] Tests/Examples
- [ ] Other: [list]

## Critical Requirements Status

### ✅ PASSED
[List requirements that are met]

### ❌ FAILED
[List requirements that are NOT met]

### ⚠️ PARTIAL/UNCLEAR
[List requirements that are partially met or unclear]

## Detailed Findings

### Endpoint Configuration
- Endpoint route: [actual route found]
- Expected route: POST /api/v1/calculate-roi
- Status: [PASS/FAIL]

### Input Validation
- Validates consumption_kwh: [YES/NO/PARTIAL]
- Validates generation_kwh: [YES/NO/PARTIAL]
- Validates tariff_per_kwh: [YES/NO/PARTIAL]
- Validates system_cost_usd: [YES/NO/PARTIAL]
- Type checking: [YES/NO]
- Range checking (> 0): [YES/NO]

### Payback Period Check
- Payback period calculation found: [YES/NO]
- If YES: **CRITICAL ISSUE - MUST REMOVE**

### ROI Calculation
- Formula present: [YES/NO]
- Formula appears correct: [YES/NO/UNCLEAR]
- Code snippet: [paste relevant code]

### Error Handling
- 400 errors for bad input: [YES/NO]
- 500 errors for server errors: [YES/NO]
- Generic error messages (no stack traces): [YES/NO]

### Security Features
- Input validation: [YES/NO/PARTIAL]
- Rate limiting: [YES/NO]
- Request size limits: [YES/NO]

### Dependencies
- Flask: [YES/NO]
- flask-cors: [YES/NO]
- flask-limiter: [YES/NO]
- Other: [list]

### Documentation
- README has setup instructions: [YES/NO]
- README has API docs: [YES/NO]
- README has examples: [YES/NO]

## Definition of Done Score: [X/9]

1. Functional API endpoint: [PASS/FAIL/UNKNOWN]
2. Returns reasonable outputs: [PASS/FAIL/UNKNOWN]
3. API documentation: [PASS/FAIL/PARTIAL]
4. README present: [PASS/FAIL]
5. Handoff doc: [PASS/FAIL/NOT FOUND]
6. AI usage documented: [PASS/FAIL/NOT FOUND]
7. Uses /api/v1/ prefix: [PASS/FAIL]
8. NO payback period: [PASS/FAIL]
9. Code quality: [PASS/FAIL/PARTIAL]

## Recommended Actions

### Must Fix (Before Handoff):
[List critical issues]

### Should Fix (Before Handoff):
[List major issues]

### Nice to Have:
[List minor improvements]

## Overall Assessment
[READY FOR HANDOFF / NEEDS WORK / MAJOR ISSUES]

**Confidence Level:** [HIGH/MEDIUM/LOW]
**Estimated Time to Fix Issues:** [X hours]
```

