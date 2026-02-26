@echo off
setlocal enabledelayedexpansion
REM ============================================================
REM  SolarSense - CONSUMPTION VALIDATION TEST
REM  Covers every profile from both test files:
REM    - full_integration_tests.py  (direct M1 calls + M4 paths)
REM    - test_model4_system.py      (equipment_list via M4)
REM
REM  Usage:
REM    1. venv\Scripts\activate
REM    2. python api/main.py   (start Model 1 on port 8000)
REM    3. Run this script in another terminal
REM ============================================================

set BASE_URL=http://127.0.0.1:8000/api/v1
set API_KEY=QfBmvo3htYQPSJWYYLcChxXvZonTuC2U
set PASS=0
set FAIL=0

echo.
echo ============================================================
echo  CONSUMPTION VALIDATION — Model 1 Direct Calls
echo  These are the EXACT inputs used by full_integration_tests.py
echo ============================================================

REM ── SUITE 1: On-Grid Chain (M1 direct call) ─────────────────
echo.
echo [INTEGRATION Suite 1] sqft=60, 3 units, Lagos, 98hrs/wk
echo   Expected range: 1,500 - 2,000 kWh/mo
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\":\"butchery\",\"sqft_m2\":60,\"operating_hours_weekly\":98,\"num_refrigeration_units\":3,\"location\":\"Lagos, Nigeria\",\"num_workers\":3,\"months_per_year\":12}" ^
  | python -c "import sys,json; d=json.load(sys.stdin); v=d['estimated_consumption_kwh_monthly']; ok='PASS' if 1500<=v<=2000 else 'FAIL'; print(f'  Result: {v} kWh/mo  [{ok}]  (refrig={d[\"breakdown\"][\"refrigeration\"]:.0f}, other={d[\"breakdown\"][\"other\"]:.0f})')"
echo.

REM ── SUITE 2: Diesel (M4 sends sqft_m2 directly) ─────────────
echo [INTEGRATION Suite 2] sqft=80, 5 units, Nairobi, 112hrs/wk
echo   Expected range: 2,000 - 3,000 kWh/mo
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\":\"mini_supermarket\",\"sqft_m2\":80,\"operating_hours_weekly\":112,\"num_refrigeration_units\":5,\"location\":\"Nairobi, Kenya\",\"num_workers\":4,\"months_per_year\":12}" ^
  | python -c "import sys,json; d=json.load(sys.stdin); v=d['estimated_consumption_kwh_monthly']; ok='PASS' if 2000<=v<=3000 else 'FAIL'; print(f'  Result: {v} kWh/mo  [{ok}]')"
echo.

REM ── SUITE 3: Equipment Scaling (3 direct M1 calls) ───────────
echo [INTEGRATION Suite 3] A=minimal B=moderate C=heavy  (must scale A < B < C)
echo   A: sqft=50,  1 unit,  56hrs  Expected: 500-900 kWh/mo
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\":\"grocery\",\"sqft_m2\":50,\"operating_hours_weekly\":56,\"num_refrigeration_units\":1,\"location\":\"Nairobi, Kenya\",\"num_workers\":2,\"months_per_year\":12}" ^
  | python -c "import sys,json; d=json.load(sys.stdin); v=d['estimated_consumption_kwh_monthly']; ok='PASS' if 500<=v<=900 else 'FAIL'; print(f'  A Result: {v} kWh/mo  [{ok}]')"

echo   B: sqft=200, 5 units, 84hrs  Expected: 2,800-4,200 kWh/mo
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\":\"grocery\",\"sqft_m2\":200,\"operating_hours_weekly\":84,\"num_refrigeration_units\":5,\"location\":\"Nairobi, Kenya\",\"num_workers\":5,\"months_per_year\":12}" ^
  | python -c "import sys,json; d=json.load(sys.stdin); v=d['estimated_consumption_kwh_monthly']; ok='PASS' if 2800<=v<=4200 else 'FAIL'; print(f'  B Result: {v} kWh/mo  [{ok}]')"

echo   C: sqft=500, 10 units, 112hrs  Expected: 8,000-13,000 kWh/mo
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\":\"grocery\",\"sqft_m2\":500,\"operating_hours_weekly\":112,\"num_refrigeration_units\":10,\"location\":\"Nairobi, Kenya\",\"num_workers\":10,\"months_per_year\":12}" ^
  | python -c "import sys,json; d=json.load(sys.stdin); v=d['estimated_consumption_kwh_monthly']; ok='PASS' if 8000<=v<=13000 else 'FAIL'; print(f'  C Result: {v} kWh/mo  [{ok}]')"
echo.

REM ── SUITE 4: Diversity profiles (sqft passed directly via M4) ─
echo [INTEGRATION Suite 4] Diversity — 6 profiles (sqft passed directly)
echo   P1: sqft=20,  1 unit,  Accra,         40hrs  Expected: 300-600 kWh/mo
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\":\"grocery\",\"sqft_m2\":20,\"operating_hours_weekly\":40,\"num_refrigeration_units\":1,\"location\":\"Accra, Ghana\",\"num_workers\":2,\"months_per_year\":12}" ^
  | python -c "import sys,json; d=json.load(sys.stdin); v=d['estimated_consumption_kwh_monthly']; ok='PASS' if 300<=v<=600 else 'FAIL'; print(f'  P1 Result: {v} kWh/mo  [{ok}]')"

echo   P2: sqft=100, 5 units, Lagos,         98hrs  Expected: 2,500-3,500 kWh/mo
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\":\"mini_supermarket\",\"sqft_m2\":100,\"operating_hours_weekly\":98,\"num_refrigeration_units\":5,\"location\":\"Lagos, Nigeria\",\"num_workers\":8,\"months_per_year\":12}" ^
  | python -c "import sys,json; d=json.load(sys.stdin); v=d['estimated_consumption_kwh_monthly']; ok='PASS' if 2500<=v<=3500 else 'FAIL'; print(f'  P2 Result: {v} kWh/mo  [{ok}]')"

echo   P3: sqft=200, 10 units, Nairobi,     126hrs  Expected: 5,000-7,500 kWh/mo
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\":\"grocery\",\"sqft_m2\":200,\"operating_hours_weekly\":126,\"num_refrigeration_units\":10,\"location\":\"Nairobi, Kenya\",\"num_workers\":15,\"months_per_year\":12}" ^
  | python -c "import sys,json; d=json.load(sys.stdin); v=d['estimated_consumption_kwh_monthly']; ok='PASS' if 5000<=v<=7500 else 'FAIL'; print(f'  P3 Result: {v} kWh/mo  [{ok}]')"

echo   P4: sqft=30,  1 unit,  Kampala,       60hrs  Expected: 400-750 kWh/mo
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\":\"butchery\",\"sqft_m2\":30,\"operating_hours_weekly\":60,\"num_refrigeration_units\":1,\"location\":\"Kampala, Uganda\",\"num_workers\":3,\"months_per_year\":12}" ^
  | python -c "import sys,json; d=json.load(sys.stdin); v=d['estimated_consumption_kwh_monthly']; ok='PASS' if 400<=v<=750 else 'FAIL'; print(f'  P4 Result: {v} kWh/mo  [{ok}]')"

echo   P5: sqft=120, 8 units, Dar es Salaam,140hrs  Expected: 4,000-6,000 kWh/mo
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\":\"mini_supermarket\",\"sqft_m2\":120,\"operating_hours_weekly\":140,\"num_refrigeration_units\":8,\"location\":\"Dar es Salaam, Tanzania\",\"num_workers\":10,\"months_per_year\":12}" ^
  | python -c "import sys,json; d=json.load(sys.stdin); v=d['estimated_consumption_kwh_monthly']; ok='PASS' if 4000<=v<=6000 else 'FAIL'; print(f'  P5 Result: {v} kWh/mo  [{ok}]')"

echo   P6: sqft=80,  4 units, Johannesburg,  84hrs  Expected: 1,500-2,500 kWh/mo
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\":\"butchery\",\"sqft_m2\":80,\"operating_hours_weekly\":84,\"num_refrigeration_units\":4,\"location\":\"Johannesburg, South Africa\",\"num_workers\":5,\"months_per_year\":12}" ^
  | python -c "import sys,json; d=json.load(sys.stdin); v=d['estimated_consumption_kwh_monthly']; ok='PASS' if 1500<=v<=2500 else 'FAIL'; print(f'  P6 Result: {v} kWh/mo  [{ok}]')"
echo.

REM ── SUITE 6: Caching detection (sqft passed directly via M4) ──
echo [INTEGRATION Suite 6] Caching detection — 8 profiles (must all differ)
echo   tiny salon:       sqft=10,  0 units, 20hrs
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\":\"grocery\",\"sqft_m2\":10,\"operating_hours_weekly\":20,\"num_refrigeration_units\":0,\"location\":\"Nairobi, Kenya\",\"num_workers\":2,\"months_per_year\":12}" ^
  | python -c "import sys,json; d=json.load(sys.stdin); v=d['estimated_consumption_kwh_monthly']; print(f'  Result: {v} kWh/mo')"

echo   1-fridge shop:    sqft=50,  1 unit,  40hrs
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\":\"grocery\",\"sqft_m2\":50,\"operating_hours_weekly\":40,\"num_refrigeration_units\":1,\"location\":\"Nairobi, Kenya\",\"num_workers\":2,\"months_per_year\":12}" ^
  | python -c "import sys,json; d=json.load(sys.stdin); v=d['estimated_consumption_kwh_monthly']; print(f'  Result: {v} kWh/mo')"

echo   4-fridge super:   sqft=150, 4 units, 84hrs
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\":\"mini_supermarket\",\"sqft_m2\":150,\"operating_hours_weekly\":84,\"num_refrigeration_units\":4,\"location\":\"Nairobi, Kenya\",\"num_workers\":4,\"months_per_year\":12}" ^
  | python -c "import sys,json; d=json.load(sys.stdin); v=d['estimated_consumption_kwh_monthly']; print(f'  Result: {v} kWh/mo')"

echo   8-fridge rest:    sqft=300, 8 units, 112hrs
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\":\"grocery\",\"sqft_m2\":300,\"operating_hours_weekly\":112,\"num_refrigeration_units\":8,\"location\":\"Nairobi, Kenya\",\"num_workers\":4,\"months_per_year\":12}" ^
  | python -c "import sys,json; d=json.load(sys.stdin); v=d['estimated_consumption_kwh_monthly']; print(f'  Result: {v} kWh/mo')"

echo   diesel 2h:        sqft=50,  2 units, 56hrs
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\":\"grocery\",\"sqft_m2\":50,\"operating_hours_weekly\":56,\"num_refrigeration_units\":2,\"location\":\"Nairobi, Kenya\",\"num_workers\":2,\"months_per_year\":12}" ^
  | python -c "import sys,json; d=json.load(sys.stdin); v=d['estimated_consumption_kwh_monthly']; print(f'  Result: {v} kWh/mo')"

echo   diesel 8h:        sqft=150, 4 units, 70hrs
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\":\"mini_supermarket\",\"sqft_m2\":150,\"operating_hours_weekly\":70,\"num_refrigeration_units\":4,\"location\":\"Nairobi, Kenya\",\"num_workers\":4,\"months_per_year\":12}" ^
  | python -c "import sys,json; d=json.load(sys.stdin); v=d['estimated_consumption_kwh_monthly']; print(f'  Result: {v} kWh/mo')"

echo   diesel 16h:       sqft=300, 6 units, 98hrs
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\":\"butchery\",\"sqft_m2\":300,\"operating_hours_weekly\":98,\"num_refrigeration_units\":6,\"location\":\"Nairobi, Kenya\",\"num_workers\":4,\"months_per_year\":12}" ^
  | python -c "import sys,json; d=json.load(sys.stdin); v=d['estimated_consumption_kwh_monthly']; print(f'  Result: {v} kWh/mo')"

echo   diesel 22h:       sqft=500, 8 units, 140hrs
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\":\"mini_supermarket\",\"sqft_m2\":500,\"operating_hours_weekly\":140,\"num_refrigeration_units\":8,\"location\":\"Nairobi, Kenya\",\"num_workers\":4,\"months_per_year\":12}" ^
  | python -c "import sys,json; d=json.load(sys.stdin); v=d['estimated_consumption_kwh_monthly']; print(f'  Result: {v} kWh/mo')"
echo   NOTE: All 8 values above must be DIFFERENT and spread wide
echo.

echo ============================================================
echo  SYSTEM TEST PROFILES (test_model4_system.py inputs)
echo  Equipment converted by Model 4 before hitting Model 1
echo  Model 4 sqft lookup: <=2 units=40sqm, <=5=65, <=10=100
echo  These use sqft_m2 as CONVERTED by Model 4
echo ============================================================

echo.
echo [SYSTEM 1] Lagos Fresh Cuts Butchery
echo   Equipment: 4 freezers + 2 fridges = 6 refrig units -> sqft=100
echo   Expected: 2,720 - 3,680 kWh/mo  (3,200 +/- 15%%)
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\":\"butchery\",\"sqft_m2\":100,\"operating_hours_weekly\":84,\"num_refrigeration_units\":6,\"location\":\"Lagos, Nigeria\",\"num_workers\":5,\"months_per_year\":12}" ^
  | python -c "import sys,json; d=json.load(sys.stdin); v=d['estimated_consumption_kwh_monthly']; ok='PASS' if 2720<=v<=3680 else 'FAIL'; print(f'  Result: {v} kWh/mo  [{ok}]')"
echo.

echo [SYSTEM 2] Accra Daily Grocery
echo   Equipment: 2 freezers + 3 fridges = 5 refrig units -> sqft=65
echo   Expected: 1,870 - 2,530 kWh/mo  (2,200 +/- 15%%)
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\":\"grocery\",\"sqft_m2\":65,\"operating_hours_weekly\":84,\"num_refrigeration_units\":5,\"location\":\"Accra, Ghana\",\"num_workers\":3,\"months_per_year\":12}" ^
  | python -c "import sys,json; d=json.load(sys.stdin); v=d['estimated_consumption_kwh_monthly']; ok='PASS' if 1870<=v<=2530 else 'FAIL'; print(f'  Result: {v} kWh/mo  [{ok}]')"
echo.

echo [SYSTEM 3] Nairobi Bread Haven Bakery
echo   Equipment: 2 freezers + 2 fridges = 4 refrig units -> sqft=65
echo   Expected: 2,380 - 3,220 kWh/mo  (2,800 +/- 15%%)
echo   NOTE: Formula gives ~1,740 - will FAIL unless constants raised
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\":\"butchery\",\"sqft_m2\":65,\"operating_hours_weekly\":84,\"num_refrigeration_units\":4,\"location\":\"Nairobi, Kenya\",\"num_workers\":3,\"months_per_year\":12}" ^
  | python -c "import sys,json; d=json.load(sys.stdin); v=d['estimated_consumption_kwh_monthly']; ok='PASS' if 2380<=v<=3220 else 'FAIL'; print(f'  Result: {v} kWh/mo  [{ok}]')"
echo.

echo [SYSTEM 4] Johannesburg ChillMart Supermarket
echo   Equipment: 4 freezers + 4 fridges = 8 refrig units -> sqft=100
echo   Expected: 3,825 - 5,175 kWh/mo  (4,500 +/- 15%%)
echo   NOTE: Formula gives ~3,068 - will FAIL unless constants raised
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\":\"mini_supermarket\",\"sqft_m2\":100,\"operating_hours_weekly\":84,\"num_refrigeration_units\":8,\"location\":\"Johannesburg, South Africa\",\"num_workers\":5,\"months_per_year\":12}" ^
  | python -c "import sys,json; d=json.load(sys.stdin); v=d['estimated_consumption_kwh_monthly']; ok='PASS' if 3825<=v<=5175 else 'FAIL'; print(f'  Result: {v} kWh/mo  [{ok}]')"
echo.

echo [SYSTEM 5] Addis Ice Foods Frozen Retail
echo   Equipment: 3 freezers + 2 fridges = 5 refrig units -> sqft=65
echo   Expected: 3,230 - 4,370 kWh/mo  (3,800 +/- 15%%)
echo   NOTE: Formula gives ~1,980 - will FAIL (expected is very high for 5 units)
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\":\"butchery\",\"sqft_m2\":65,\"operating_hours_weekly\":84,\"num_refrigeration_units\":5,\"location\":\"Addis Ababa, Ethiopia\",\"num_workers\":3,\"months_per_year\":12}" ^
  | python -c "import sys,json; d=json.load(sys.stdin); v=d['estimated_consumption_kwh_monthly']; ok='PASS' if 3230<=v<=4370 else 'FAIL'; print(f'  Result: {v} kWh/mo  [{ok}]')"
echo.

echo [SYSTEM 6] Kampala Farm Cold Storage
echo   Equipment: 4 freezers + 3 fridges + 1 cold_room = 8 refrig units -> sqft=100+20=120
echo   Expected: 3,485 - 4,715 kWh/mo  (4,100 +/- 15%%)
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\":\"grocery\",\"sqft_m2\":120,\"operating_hours_weekly\":84,\"num_refrigeration_units\":8,\"location\":\"Kampala, Uganda\",\"num_workers\":4,\"months_per_year\":12}" ^
  | python -c "import sys,json; d=json.load(sys.stdin); v=d['estimated_consumption_kwh_monthly']; ok='PASS' if 3485<=v<=4715 else 'FAIL'; print(f'  Result: {v} kWh/mo  [{ok}]')"
echo.

echo [SYSTEM 7] Kigali Quick Freeze Butchery
echo   Equipment: 3 freezers + 2 fridges = 5 refrig units -> sqft=65
echo   Expected: 2,210 - 2,990 kWh/mo  (2,600 +/- 15%%)
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\":\"butchery\",\"sqft_m2\":65,\"operating_hours_weekly\":84,\"num_refrigeration_units\":5,\"location\":\"Kigali, Rwanda\",\"num_workers\":3,\"months_per_year\":12}" ^
  | python -c "import sys,json; d=json.load(sys.stdin); v=d['estimated_consumption_kwh_monthly']; ok='PASS' if 2210<=v<=2990 else 'FAIL'; print(f'  Result: {v} kWh/mo  [{ok}]')"
echo.

echo [SYSTEM 8] Dar Fresh Mart Grocery
echo   Equipment: 2 freezers + 3 fridges = 5 refrig units -> sqft=65
echo   Expected: 2,040 - 2,760 kWh/mo  (2,400 +/- 15%%)
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\":\"grocery\",\"sqft_m2\":65,\"operating_hours_weekly\":84,\"num_refrigeration_units\":5,\"location\":\"Dar es Salaam, Tanzania\",\"num_workers\":3,\"months_per_year\":12}" ^
  | python -c "import sys,json; d=json.load(sys.stdin); v=d['estimated_consumption_kwh_monthly']; ok='PASS' if 2040<=v<=2760 else 'FAIL'; print(f'  Result: {v} kWh/mo  [{ok}]')"
echo.

echo [SYSTEM 9] Cape Meat Locker Cold Storage
echo   Equipment: 3 freezers + 2 fridges = 5 refrig units -> sqft=65
echo   Expected: 4,420 - 5,980 kWh/mo  (5,200 +/- 15%%)
echo   NOTE: Formula gives ~1,947 - expected is high (large cold storage)
echo   May need business_type cold_storage detection or larger sqft
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\":\"butchery\",\"sqft_m2\":65,\"operating_hours_weekly\":84,\"num_refrigeration_units\":5,\"location\":\"Cape Town, South Africa\",\"num_workers\":3,\"months_per_year\":12}" ^
  | python -c "import sys,json; d=json.load(sys.stdin); v=d['estimated_consumption_kwh_monthly']; ok='PASS' if 4420<=v<=5980 else 'FAIL'; print(f'  Result: {v} kWh/mo  [{ok}]')"
echo.

echo [SYSTEM 10] Nairobi Frosty Mini Mart
echo   Equipment: 3 freezers + 4 fridges + 1 display_cooler = 8 refrig units -> sqft=100
echo   Expected: 3,060 - 4,140 kWh/mo  (3,600 +/- 15%%)
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_type\":\"mini_supermarket\",\"sqft_m2\":100,\"operating_hours_weekly\":84,\"num_refrigeration_units\":8,\"location\":\"Nairobi, Kenya\",\"num_workers\":5,\"months_per_year\":12}" ^
  | python -c "import sys,json; d=json.load(sys.stdin); v=d['estimated_consumption_kwh_monthly']; ok='PASS' if 3060<=v<=4140 else 'FAIL'; print(f'  Result: {v} kWh/mo  [{ok}]')"
echo.

echo ============================================================
echo  TEST COMPLETE
echo.
echo  KNOWN GAPS TO WATCH:
echo  System 3 (Bakery 4 units):   formula ~1740, need ~2800  [FAIL expected]
echo  System 4 (ChillMart 8 units):formula ~3068, need ~4500  [FAIL expected]
echo  System 5 (Addis 5 units):    formula ~1980, need ~3800  [FAIL expected]
echo  System 9 (Cape Cold Storage):formula ~1947, need ~5200  [FAIL expected]
echo.
echo  Everything else should PASS.
echo  Report results and we fix the remaining constants.
echo ============================================================
pause
endlocal