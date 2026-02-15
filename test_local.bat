@echo off
setlocal

REM ============================================================
REM  SolarSense LOCAL Test Suite
REM  Tests api/main.py running on localhost
REM
REM  Before running:
REM    1. venv\Scripts\activate
REM    2. python api/main.py
REM    3. Run this script in a second terminal
REM ============================================================

set BASE_URL=http://127.0.0.1:8000/api/v1
set API_KEY=QfBmvo3htYQPSJWYYLcChxXvZonTuC2U

echo ============================================================
echo  SolarSense LOCAL Tests (Models 1-4)
echo  Base URL: %BASE_URL%
echo  Make sure api/main.py is running before proceeding!
echo ============================================================
echo.

REM ── 1. Gateway Root ─────────────────────────────────────────
echo [1/10] Gateway Root...
curl.exe -s -w "\nHTTP Status: %%{http_code}\n" "http://127.0.0.1:8000/"
echo.
echo ------------------------------------------------------------

REM ── 2. Gateway Health Check (no auth) ───────────────────────
echo [2/10] Gateway Health Check (no auth required)...
curl.exe -s -w "\nHTTP Status: %%{http_code}\n" "%BASE_URL%/health"
echo.
echo ------------------------------------------------------------

REM ── 3. Auth check — should return 401 ───────────────────────
echo [3/10] Auth Check - No API key (expect 401)...
curl.exe -s -w "\nHTTP Status: %%{http_code}\n" ^
  -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" ^
  -d "{\"business_type\": \"grocery\"}"
echo.
echo ------------------------------------------------------------

REM ── 4. Model 1 - Estimate Consumption ───────────────────────
echo [4/10] Model 1 - Estimate Energy Consumption...
curl.exe -s -w "\nHTTP Status: %%{http_code}\n" ^
  -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" ^
  -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\": \"butchery\", \"sqft_m2\": 60.0, \"operating_hours_weekly\": 98.0, \"num_refrigeration_units\": 3, \"location\": \"Lagos, Nigeria\", \"num_workers\": 3, \"months_per_year\": 12}"
echo.
echo ------------------------------------------------------------

REM ── 5. Model 2 - Model Info ──────────────────────────────────
echo [5/10] Model 2 - Model Info...
curl.exe -s -w "\nHTTP Status: %%{http_code}\n" ^
  -H "X-API-KEY: %API_KEY%" ^
  "%BASE_URL%/model-info"
echo.
echo ------------------------------------------------------------

REM ── 6. Model 2 - Predict Solar Generation ───────────────────
echo [6/10] Model 2 - Predict Solar Generation...
curl.exe -s -w "\nHTTP Status: %%{http_code}\n" ^
  -X POST "%BASE_URL%/predict-generation" ^
  -H "Content-Type: application/json" ^
  -H "X-API-KEY: %API_KEY%" ^
  -d "{\"latitude\": -1.2921, \"longitude\": 36.8219, \"month\": 6, \"include_lifetime\": true}"
echo.
echo ------------------------------------------------------------

REM ── 7. Model 3 - Calculate ROI ───────────────────────────────
echo [7/10] Model 3 - Calculate ROI...
curl.exe -s -w "\nHTTP Status: %%{http_code}\n" ^
  -X POST "%BASE_URL%/calculate-roi" ^
  -H "Content-Type: application/json" ^
  -H "X-API-KEY: %API_KEY%" ^
  -d "{\"consumption_kwh\": 450.0, \"generation_kwh\": 500.0, \"tariff_per_kwh\": 0.20, \"system_cost_usd\": 6000.0}"
echo.
echo ------------------------------------------------------------

REM ── 8. Model 4 - Analyze (Grid-Only) ────────────────────────
echo [8/10] Model 4 - Solar Viability Analysis (Grid-Only)...
curl.exe -s -w "\nHTTP Status: %%{http_code}\n" ^
  -X POST "%BASE_URL%/analyze" ^
  -H "Content-Type: application/json" ^
  -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_name\": \"Joe's Coffee Shop\", \"business_type\": \"Cafe\", \"location\": \"Nairobi, Kenya\", \"latitude\": -1.2921, \"longitude\": 36.8219, \"equipment_list\": [{\"equipment_type\": \"refrigerator\", \"quantity\": 2, \"hours_per_day\": 24}, {\"equipment_type\": \"espresso_machine\", \"quantity\": 1, \"hours_per_day\": 10}, {\"equipment_type\": \"lights\", \"quantity\": 15, \"hours_per_day\": 12}], \"tariff\": 0.15, \"uses_diesel\": false}"
echo.
echo ------------------------------------------------------------

REM ── 9. Model 4 - Analyze (Diesel Replacement) ───────────────
echo [9/10] Model 4 - Solar Viability Analysis (Diesel Replacement)...
curl.exe -s -w "\nHTTP Status: %%{http_code}\n" ^
  -X POST "%BASE_URL%/analyze" ^
  -H "Content-Type: application/json" ^
  -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_name\": \"Mombasa Cold Storage\", \"business_type\": \"Retail\", \"location\": \"Mombasa, Kenya\", \"latitude\": -4.0435, \"longitude\": 39.6682, \"equipment_list\": [{\"equipment_type\": \"cold_room\", \"quantity\": 1, \"hours_per_day\": 24}, {\"equipment_type\": \"refrigerator\", \"quantity\": 4, \"hours_per_day\": 24}, {\"equipment_type\": \"lights\", \"quantity\": 8, \"hours_per_day\": 12}], \"tariff\": 0.18, \"uses_diesel\": true, \"diesel_hours_per_day\": 18, \"diesel_price_per_liter\": 1.35}"
echo.
echo ------------------------------------------------------------

REM ── 10. Model 4 - Invalid coordinates (expect 503) ──────────
echo [10/10] Model 4 - Out-of-bounds coordinates (expect 503)...
curl.exe -s -w "\nHTTP Status: %%{http_code}\n" ^
  -X POST "%BASE_URL%/analyze" ^
  -H "Content-Type: application/json" ^
  -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_name\": \"Test\", \"business_type\": \"Retail\", \"location\": \"London, UK\", \"latitude\": 51.5074, \"longitude\": -0.1278, \"equipment_list\": [{\"equipment_type\": \"lights\", \"quantity\": 5, \"hours_per_day\": 8}], \"tariff\": 0.30}"
echo.
echo ============================================================
echo  All local tests complete! (10/10)
echo.
echo  Expected results:
echo    [1]  200 - Gateway root
echo    [2]  200 - Gateway health
echo    [3]  401 - No API key (auth check)
echo    [4]  200 - Model 1 consumption
echo    [5]  200 - Model 2 model-info
echo    [6]  200 - Model 2 generation
echo    [7]  200 - Model 3 ROI
echo    [8]  200 - Model 4 grid-only
echo    [9]  200 - Model 4 diesel replacement
echo    [10] 503 - Model 4 out-of-SSA coordinates
echo ============================================================

endlocal
pause