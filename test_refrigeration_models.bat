@echo off
setlocal

REM ============================================================
REM  SolarSense LOCAL Refrigeration Test Suite
REM  Tests Model 1 & Model 4 specific refrigeration scenarios
REM
REM  Before running:
REM    1. venv\Scripts\activate
REM    2. python api/main.py
REM    3. Run this script in a second terminal
REM ============================================================

set BASE_URL=http://127.0.0.1:8000/api/v1
set API_KEY=QfBmvo3htYQPSJWYYLcChxXvZonTuC2U

echo ============================================================
echo  SolarSense Refrigeration Tests
echo  Base URL: %BASE_URL%
echo ============================================================
echo.

REM ── 1. Model 1 - Single Freezer ─────────────────────────────
echo [1/3] Model 1 - Single Freezer (Butchery, Lagos)...
curl.exe -s -w "\nHTTP Status: %%{http_code}\n" ^
  -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" ^
  -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\": \"butchery\", \"sqft_m2\": 60, \"operating_hours_weekly\": 98, \"num_refrigeration_units\": 1, \"location\": \"Lagos, Nigeria\", \"num_workers\": 3, \"months_per_year\": 12}"
echo.
echo ------------------------------------------------------------

REM Expected:
REM estimated_consumption_kwh_monthly ≈ 1500-1700
REM refrigeration ≈ 1000-1100
REM other ≈ 400-600


REM ── 2. Model 1 - Three Freezers ─────────────────────────────
echo [2/3] Model 1 - Three Freezers (Butchery, Lagos)...
curl.exe -s -w "\nHTTP Status: %%{http_code}\n" ^
  -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" ^
  -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\": \"butchery\", \"sqft_m2\": 60, \"operating_hours_weekly\": 98, \"num_refrigeration_units\": 3, \"location\": \"Lagos, Nigeria\", \"num_workers\": 3, \"months_per_year\": 12}"
echo.
echo ------------------------------------------------------------

REM Expected:
REM estimated_consumption_kwh_monthly ≈ 3500-3800
REM refrigeration ≈ 3000-3300
REM other ≈ 400-600


REM ── 3. Model 4 - Cold Storage (Kampala) ─────────────────────
echo [3/3] Model 4 - Cold Storage (Kampala, Uganda)...
curl.exe -s -w "\nHTTP Status: %%{http_code}\n" ^
  -X POST "%BASE_URL%/analyze" ^
  -H "Content-Type: application/json" ^
  -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_name\": \"Kampala Cold Storage\", \"business_type\": \"Cold storage\", \"location\": \"Kampala, Uganda\", \"latitude\": 0.3476, \"longitude\": 32.5825, \"equipment_list\": [{\"equipment_type\": \"cold_room\", \"quantity\": 2, \"hours_per_day\": 24}, {\"equipment_type\": \"freezer\", \"quantity\": 3, \"hours_per_day\": 24}], \"grid_tariff\": 0.08}"
echo.
echo ------------------------------------------------------------

REM Expected:
REM consumption_kwh_monthly ≈ 4000-5000
REM Breakdown:
REM   2 cold rooms (~1600)
REM   3 freezers (~2700)
REM   Total ≈ 4300 kWh/month

echo ============================================================
echo  Refrigeration tests complete! (3/3)
echo ============================================================

endlocal
pause