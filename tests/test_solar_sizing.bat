@echo off
setlocal enabledelayedexpansion

set API_KEY=QfBmvo3htYQPSJWYYLcChxXvZonTuC2U

echo.
echo  Where do you want to run tests?
echo    [1] LOCAL   (http://127.0.0.1:8000)
echo    [2] REMOTE  (https://dse-models-production.up.railway.app)
echo.
set /p ENV_CHOICE="  Enter 1 or 2: "
if "%ENV_CHOICE%"=="1" (
    set BASE_URL=http://127.0.0.1:8000/api/v1
    set ENV_LABEL=LOCAL
) else (
    set BASE_URL=https://dse-models-production.up.railway.app/api/v1
    set ENV_LABEL=REMOTE
)
echo.
echo  Running against: %ENV_LABEL% (%BASE_URL%)
echo ============================================================

echo.
echo ============================================================
echo  SECTION 1: CONSUMPTION → PANEL AREA / SOLAR (NAIROBI)
echo  Expectation: higher load → higher generation, larger panel area, higher cost
echo ============================================================

echo.
echo --- S1-A: Tiny kiosk (1 fridge, Nairobi) ---
curl.exe -s -X POST "%BASE_URL%/analyze" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_name\":\"S1-A\",\"business_type\":\"grocery\",\"location\":\"Nairobi, Kenya\",\"latitude\":-1.2921,\"longitude\":36.8219,\"equipment_list\":[{\"equipment_type\":\"refrigerator\",\"quantity\":1,\"hours_per_day\":10}],\"uses_diesel\":false}" ^
  | python tests\parse.py --mode solar

echo.
echo --- S1-B: Small shop (2 fridges + 1 freezer, Nairobi) ---
curl.exe -s -X POST "%BASE_URL%/analyze" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_name\":\"S1-B\",\"business_type\":\"grocery\",\"location\":\"Nairobi, Kenya\",\"latitude\":-1.2921,\"longitude\":36.8219,\"equipment_list\":[{\"equipment_type\":\"refrigerator\",\"quantity\":2,\"hours_per_day\":16},{\"equipment_type\":\"freezer\",\"quantity\":1,\"hours_per_day\":24}],\"uses_diesel\":false}" ^
  | python tests\parse.py --mode solar

echo.
echo --- S1-C: Mid supermarket (4 fridges + 3 freezers + lights, Nairobi) ---
curl.exe -s -X POST "%BASE_URL%/analyze" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_name\":\"S1-C\",\"business_type\":\"mini_supermarket\",\"location\":\"Nairobi, Kenya\",\"latitude\":-1.2921,\"longitude\":36.8219,\"equipment_list\":[{\"equipment_type\":\"refrigerator\",\"quantity\":4,\"hours_per_day\":18},{\"equipment_type\":\"freezer\",\"quantity\":3,\"hours_per_day\":24},{\"equipment_type\":\"lights\",\"quantity\":10,\"hours_per_day\":12}],\"uses_diesel\":false}" ^
  | python tests\parse.py --mode solar

echo.
echo --- S1-D: Cold storage (3 cold rooms + 5 freezers, Nairobi) ---
curl.exe -s -X POST "%BASE_URL%/analyze" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_name\":\"S1-D\",\"business_type\":\"grocery\",\"location\":\"Nairobi, Kenya\",\"latitude\":-1.2921,\"longitude\":36.8219,\"equipment_list\":[{\"equipment_type\":\"cold_room\",\"quantity\":3,\"hours_per_day\":24},{\"equipment_type\":\"freezer\",\"quantity\":5,\"hours_per_day\":24}],\"uses_diesel\":false}" ^
  | python tests\parse.py --mode solar

echo.
echo ============================================================
echo  SECTION 2: SAME LOAD, DIFFERENT CITIES
echo  Expectation: similar consumption, but different solar yield/panel size/cost by location
echo ============================================================

rem Profile: mid grocery - 3 fridges + 2 display coolers + 8 lights

echo.
echo --- S2-A: Mid grocery (Accra) ---
curl.exe -s -X POST "%BASE_URL%/analyze" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_name\":\"S2-A\",\"business_type\":\"grocery\",\"location\":\"Accra, Ghana\",\"latitude\":5.6037,\"longitude\":-0.1870,\"equipment_list\":[{\"equipment_type\":\"refrigerator\",\"quantity\":3,\"hours_per_day\":18},{\"equipment_type\":\"display_cooler\",\"quantity\":2,\"hours_per_day\":12},{\"equipment_type\":\"lights\",\"quantity\":8,\"hours_per_day\":12}],\"uses_diesel\":false}" ^
  | python tests\parse.py --mode solar

echo.
echo --- S2-B: Mid grocery (Nairobi) ---
curl.exe -s -X POST "%BASE_URL%/analyze" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_name\":\"S2-B\",\"business_type\":\"grocery\",\"location\":\"Nairobi, Kenya\",\"latitude\":-1.2921,\"longitude\":36.8219,\"equipment_list\":[{\"equipment_type\":\"refrigerator\",\"quantity\":3,\"hours_per_day\":18},{\"equipment_type\":\"display_cooler\",\"quantity\":2,\"hours_per_day\":12},{\"equipment_type\":\"lights\",\"quantity\":8,\"hours_per_day\":12}],\"uses_diesel\":false}" ^
  | python tests\parse.py --mode solar

echo.
echo --- S2-C: Mid grocery (Lagos) ---
curl.exe -s -X POST "%BASE_URL%/analyze" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_name\":\"S2-C\",\"business_type\":\"grocery\",\"location\":\"Lagos, Nigeria\",\"latitude\":6.5244,\"longitude\":3.3792,\"equipment_list\":[{\"equipment_type\":\"refrigerator\",\"quantity\":3,\"hours_per_day\":18},{\"equipment_type\":\"display_cooler\",\"quantity\":2,\"hours_per_day\":12},{\"equipment_type\":\"lights\",\"quantity\":8,\"hours_per_day\":12}],\"uses_diesel\":false}" ^
  | python tests\parse.py --mode solar

echo.
echo --- S2-D: Mid grocery (Johannesburg) ---
curl.exe -s -X POST "%BASE_URL%/analyze" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_name\":\"S2-D\",\"business_type\":\"grocery\",\"location\":\"Johannesburg, South Africa\",\"latitude\":-26.2041,\"longitude\":28.0473,\"equipment_list\":[{\"equipment_type\":\"refrigerator\",\"quantity\":3,\"hours_per_day\":18},{\"equipment_type\":\"display_cooler\",\"quantity\":2,\"hours_per_day\":12},{\"equipment_type\":\"lights\",\"quantity\":8,\"hours_per_day\":12}],\"uses_diesel\":false}" ^
  | python tests\parse.py --mode solar

echo.
echo ============================================================
echo  SECTION 3: DIESEL VS GRID (SAME EQUIPMENT)
echo  Expectation: diesel changes ROI/tariff, but panel area/generation stay similar
echo ============================================================

echo.
echo --- S3-A: Large supermarket (grid only, Lagos) ---
curl.exe -s -X POST "%BASE_URL%/analyze" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_name\":\"S3-A\",\"business_type\":\"mini_supermarket\",\"location\":\"Lagos, Nigeria\",\"latitude\":6.5244,\"longitude\":3.3792,\"equipment_list\":[{\"equipment_type\":\"refrigerator\",\"quantity\":8,\"hours_per_day\":18},{\"equipment_type\":\"freezer\",\"quantity\":4,\"hours_per_day\":24},{\"equipment_type\":\"lights\",\"quantity\":15,\"hours_per_day\":12}],\"uses_diesel\":false}" ^
  | python tests\parse.py --mode solar

echo.
echo --- S3-B: Large supermarket (18h diesel, Lagos) ---
curl.exe -s -X POST "%BASE_URL%/analyze" ^
  -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" ^
  -d "{\"business_name\":\"S3-B\",\"business_type\":\"mini_supermarket\",\"location\":\"Lagos, Nigeria\",\"latitude\":6.5244,\"longitude\":3.3792,\"equipment_list\":[{\"equipment_type\":\"refrigerator\",\"quantity\":8,\"hours_per_day\":18},{\"equipment_type\":\"freezer\",\"quantity\":4,\"hours_per_day\":24},{\"equipment_type\":\"lights\",\"quantity\":15,\"hours_per_day\":12}],\"uses_diesel\":true,\"diesel_hours_per_day\":18,\"diesel_price_per_liter\":0.90}" ^
  | python tests\parse.py --mode solar

echo.
echo ============================================================
echo  ALL DONE  -  Key checks:
echo    S1: Higher consumption -> higher generation, larger panel area, higher cost
echo    S2: Same equipment across cities -> different area/cost due to solar resource
echo    S3: Diesel toggles ROI/tariff but area/generation stay similar
echo ============================================================
pause
endlocal

