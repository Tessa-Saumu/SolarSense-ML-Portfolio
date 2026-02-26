@echo off
setlocal

REM ============================================================
REM  SolarSense LOCAL Test - Small Shop (Tier 1)
REM
REM  Scenario:
REM    - 40 sqm (Tier 1 size band)
REM    - 1 refrigeration unit
REM    - Expected monthly range: 800–1400 kWh
REM
REM  Assumptions:
REM    unit_delta = 1 - 5 = -4
REM    annual adjustment = -4 × 120 × 12 = -5,760 kWh/year
REM
REM  Before running:
REM    1. venv\Scripts\activate
REM    2. python api/main.py
REM    3. Run this script in another terminal
REM ============================================================

set BASE_URL=http://127.0.0.1:8000/api/v1
set API_KEY=QfBmvo3htYQPSJWYYLcChxXvZonTuC2U

echo ============================================================
echo  SolarSense - 40sqm Small Shop Test
echo  Base URL: %BASE_URL%
echo ============================================================
echo.

REM ── Model 1 - 40 sqm, 1 Freezer ────────────────────────────
echo [1/1] Model 1 - 40sqm Food Sales (1 refrigeration unit)...

curl.exe -s -w "\nHTTP Status: %%{http_code}\n" ^
  -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" ^
  -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\": \"butchery\", \"sqft_m2\": 40, \"operating_hours_weekly\": 84, \"num_refrigeration_units\": 1, \"location\": \"Lagos, Nigeria\", \"num_workers\": 2, \"months_per_year\": 12}"

echo.
echo ------------------------------------------------------------

REM EXPECTED RESULT:
REM   estimated_consumption_kwh_monthly ≈ 800–1400
REM
REM Reasoning:
REM   - 40 sqm → Tier 1
REM   - Refrigeration delta: (1 - 5) = -4
REM   - Annual adjustment = -5,760 kWh
REM   - Smaller base load due to reduced floor area
REM   - Realistic single-freezer small shop range

echo ============================================================
echo  Test complete!
echo ============================================================

endlocal
pause