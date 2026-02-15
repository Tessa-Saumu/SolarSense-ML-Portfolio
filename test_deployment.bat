@echo off
setlocal

set BASE_URL=https://dse-models-production.up.railway.app/api/v1
set API_KEY=QfBmvo3htYQPSJWYYLcChxXvZonTuC2U

echo ============================================================
echo  SolarSense Deployment Tests (Models 1-4)
echo  Base URL: %BASE_URL%
echo ============================================================
echo.

REM ── 1. General Health Check (no auth) ───────────────────────
echo [1/8] General Health Check...
curl.exe -s -w "\nHTTP Status: %%{http_code}\n" "%BASE_URL%/health"
echo.
echo ------------------------------------------------------------

REM ── 2. Model 2 Health Check (auth required) ─────────────────
echo [2/8] Model 2 Health Check (with API key)...
curl.exe -s -w "\nHTTP Status: %%{http_code}\n" ^
  -H "X-API-KEY: %API_KEY%" ^
  "%BASE_URL%/health"
echo.
echo ------------------------------------------------------------

REM ── 3. Model 2 Model Info ────────────────────────────────────
echo [3/8] Model 2 - Model Info...
curl.exe -s -w "\nHTTP Status: %%{http_code}\n" ^
  -H "X-API-KEY: %API_KEY%" ^
  "%BASE_URL%/model-info"
echo.
echo ------------------------------------------------------------

REM ── 4. Model 1 - Estimate Consumption ───────────────────────
echo [4/8] Model 1 - Estimate Energy Consumption...
curl.exe -s -w "\nHTTP Status: %%{http_code}\n" ^
  -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" ^
  -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\": \"butchery\", \"sqft_m2\": 60.0, \"operating_hours_weekly\": 98.0, \"num_refrigeration_units\": 3, \"location\": \"Lagos, Nigeria\", \"num_workers\": 3, \"months_per_year\": 12}"
echo.
echo ------------------------------------------------------------

REM ── 5. Model 2 - Predict Solar Generation ───────────────────
echo [5/8] Model 2 - Predict Solar Generation...
curl.exe -s -w "\nHTTP Status: %%{http_code}\n" ^
  -X POST "%BASE_URL%/predict-generation" ^
  -H "Content-Type: application/json" ^
  -H "X-API-KEY: %API_KEY%" ^
  -d "{\"latitude\": -1.2921, \"longitude\": 36.8219, \"month\": 6, \"include_lifetime\": true}"
echo.
echo ------------------------------------------------------------

REM ── 6. Model 3 - Calculate ROI ───────────────────────────────
echo [6/8] Model 3 - Calculate ROI...
curl.exe -s -w "\nHTTP Status: %%{http_code}\n" ^
  -X POST "%BASE_URL%/calculate-roi" ^
  -H "Content-Type: application/json" ^
  -H "X-API-KEY: %API_KEY%" ^
  -d "{\"consumption_kwh\": 450.0, \"generation_kwh\": 500.0, \"tariff_per_kwh\": 0.20, \"system_cost_usd\": 6000.0}"
echo.
echo ------------------------------------------------------------

REM ── 7. Model 4 - Analyze (Grid-Only) ────────────────────────
echo [7/8] Model 4 - Solar Viability Analysis (Grid-Only)...
curl.exe -s -w "\nHTTP Status: %%{http_code}\n" ^
  -X POST "%BASE_URL%/analyze" ^
  -H "Content-Type: application/json" ^
  -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_name\": \"Joe's Coffee Shop\", \"business_type\": \"Cafe\", \"location\": \"Nairobi, Kenya\", \"latitude\": -1.2921, \"longitude\": 36.8219, \"equipment_list\": [{\"equipment_type\": \"refrigerator\", \"quantity\": 2, \"hours_per_day\": 24}, {\"equipment_type\": \"espresso_machine\", \"quantity\": 1, \"hours_per_day\": 10}, {\"equipment_type\": \"lights\", \"quantity\": 15, \"hours_per_day\": 12}], \"tariff\": 0.15, \"uses_diesel\": false}"
echo.
echo ------------------------------------------------------------

REM ── 8. Model 4 - Analyze (Diesel Replacement) ───────────────
echo [8/8] Model 4 - Solar Viability Analysis (Diesel Replacement)...
curl.exe -s -w "\nHTTP Status: %%{http_code}\n" ^
  -X POST "%BASE_URL%/analyze" ^
  -H "Content-Type: application/json" ^
  -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_name\": \"Mombasa Cold Storage\", \"business_type\": \"Retail\", \"location\": \"Mombasa, Kenya\", \"latitude\": -4.0435, \"longitude\": 39.6682, \"equipment_list\": [{\"equipment_type\": \"cold_room\", \"quantity\": 1, \"hours_per_day\": 24}, {\"equipment_type\": \"refrigerator\", \"quantity\": 4, \"hours_per_day\": 24}, {\"equipment_type\": \"lights\", \"quantity\": 8, \"hours_per_day\": 12}], \"tariff\": 0.18, \"uses_diesel\": true, \"diesel_hours_per_day\": 18, \"diesel_price_per_liter\": 1.35}"
echo.
echo ============================================================
echo  All deployment tests complete! (8/8)
echo  Expected: HTTP 200 on all tests
echo ============================================================

endlocal
pause