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
echo  SECTION 1: FREEZER SCALING  (Lagos 84hrs/wk)
echo  M1=direct call  M4=via equipment_list  should match
echo ============================================================

echo.
echo --- FREEZER x1 (expect 800-1400 kWh/mo) ---
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_type\":\"butchery\",\"sqft_m2\":50,\"operating_hours_weekly\":84,\"num_refrigeration_units\":1,\"location\":\"Lagos, Nigeria\",\"num_workers\":2,\"months_per_year\":12}" | python parse.py --mode m1
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"butchery\",\"location\":\"Lagos, Nigeria\",\"latitude\":6.5244,\"longitude\":3.3792,\"equipment_list\":[{\"equipment_type\":\"freezer\",\"quantity\":1,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo --- FREEZER x3 (expect 2000-3000 kWh/mo) ---
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_type\":\"butchery\",\"sqft_m2\":85,\"operating_hours_weekly\":84,\"num_refrigeration_units\":3,\"location\":\"Lagos, Nigeria\",\"num_workers\":3,\"months_per_year\":12}" | python parse.py --mode m1
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"butchery\",\"location\":\"Lagos, Nigeria\",\"latitude\":6.5244,\"longitude\":3.3792,\"equipment_list\":[{\"equipment_type\":\"freezer\",\"quantity\":3,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo --- FREEZER x5 (expect 3000-4000 kWh/mo) ---
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_type\":\"butchery\",\"sqft_m2\":85,\"operating_hours_weekly\":84,\"num_refrigeration_units\":5,\"location\":\"Lagos, Nigeria\",\"num_workers\":4,\"months_per_year\":12}" | python parse.py --mode m1
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"butchery\",\"location\":\"Lagos, Nigeria\",\"latitude\":6.5244,\"longitude\":3.3792,\"equipment_list\":[{\"equipment_type\":\"freezer\",\"quantity\":5,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo --- FREEZER x7 (expect 4000-5500 kWh/mo) ---
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_type\":\"butchery\",\"sqft_m2\":130,\"operating_hours_weekly\":84,\"num_refrigeration_units\":7,\"location\":\"Lagos, Nigeria\",\"num_workers\":5,\"months_per_year\":12}" | python parse.py --mode m1
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"butchery\",\"location\":\"Lagos, Nigeria\",\"latitude\":6.5244,\"longitude\":3.3792,\"equipment_list\":[{\"equipment_type\":\"freezer\",\"quantity\":7,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo --- FREEZER x10 (expect 5500-7500 kWh/mo) ---
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_type\":\"butchery\",\"sqft_m2\":130,\"operating_hours_weekly\":84,\"num_refrigeration_units\":10,\"location\":\"Lagos, Nigeria\",\"num_workers\":6,\"months_per_year\":12}" | python parse.py --mode m1
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"butchery\",\"location\":\"Lagos, Nigeria\",\"latitude\":6.5244,\"longitude\":3.3792,\"equipment_list\":[{\"equipment_type\":\"freezer\",\"quantity\":10,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo --- FREEZER x15 (expect 8000-11000 kWh/mo) ---
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_type\":\"butchery\",\"sqft_m2\":190,\"operating_hours_weekly\":84,\"num_refrigeration_units\":15,\"location\":\"Lagos, Nigeria\",\"num_workers\":8,\"months_per_year\":12}" | python parse.py --mode m1
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"butchery\",\"location\":\"Lagos, Nigeria\",\"latitude\":6.5244,\"longitude\":3.3792,\"equipment_list\":[{\"equipment_type\":\"freezer\",\"quantity\":15,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo ============================================================
echo  SECTION 2: REFRIGERATOR SCALING  (Lagos 84hrs/wk)
echo ============================================================

echo.
echo --- REFRIGERATOR x1 ---
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_type\":\"grocery\",\"sqft_m2\":50,\"operating_hours_weekly\":84,\"num_refrigeration_units\":1,\"location\":\"Lagos, Nigeria\",\"num_workers\":2,\"months_per_year\":12}" | python parse.py --mode m1
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"grocery\",\"location\":\"Lagos, Nigeria\",\"latitude\":6.5244,\"longitude\":3.3792,\"equipment_list\":[{\"equipment_type\":\"refrigerator\",\"quantity\":1,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo --- REFRIGERATOR x3 ---
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_type\":\"grocery\",\"sqft_m2\":85,\"operating_hours_weekly\":84,\"num_refrigeration_units\":3,\"location\":\"Lagos, Nigeria\",\"num_workers\":3,\"months_per_year\":12}" | python parse.py --mode m1
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"grocery\",\"location\":\"Lagos, Nigeria\",\"latitude\":6.5244,\"longitude\":3.3792,\"equipment_list\":[{\"equipment_type\":\"refrigerator\",\"quantity\":3,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo --- REFRIGERATOR x5 ---
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_type\":\"grocery\",\"sqft_m2\":85,\"operating_hours_weekly\":84,\"num_refrigeration_units\":5,\"location\":\"Lagos, Nigeria\",\"num_workers\":4,\"months_per_year\":12}" | python parse.py --mode m1
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"grocery\",\"location\":\"Lagos, Nigeria\",\"latitude\":6.5244,\"longitude\":3.3792,\"equipment_list\":[{\"equipment_type\":\"refrigerator\",\"quantity\":5,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo --- REFRIGERATOR x7 ---
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_type\":\"grocery\",\"sqft_m2\":130,\"operating_hours_weekly\":84,\"num_refrigeration_units\":7,\"location\":\"Lagos, Nigeria\",\"num_workers\":5,\"months_per_year\":12}" | python parse.py --mode m1
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"grocery\",\"location\":\"Lagos, Nigeria\",\"latitude\":6.5244,\"longitude\":3.3792,\"equipment_list\":[{\"equipment_type\":\"refrigerator\",\"quantity\":7,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo --- REFRIGERATOR x10 ---
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_type\":\"grocery\",\"sqft_m2\":130,\"operating_hours_weekly\":84,\"num_refrigeration_units\":10,\"location\":\"Lagos, Nigeria\",\"num_workers\":6,\"months_per_year\":12}" | python parse.py --mode m1
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"grocery\",\"location\":\"Lagos, Nigeria\",\"latitude\":6.5244,\"longitude\":3.3792,\"equipment_list\":[{\"equipment_type\":\"refrigerator\",\"quantity\":10,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo --- REFRIGERATOR x15 ---
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_type\":\"grocery\",\"sqft_m2\":190,\"operating_hours_weekly\":84,\"num_refrigeration_units\":15,\"location\":\"Lagos, Nigeria\",\"num_workers\":8,\"months_per_year\":12}" | python parse.py --mode m1
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"grocery\",\"location\":\"Lagos, Nigeria\",\"latitude\":6.5244,\"longitude\":3.3792,\"equipment_list\":[{\"equipment_type\":\"refrigerator\",\"quantity\":15,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo ============================================================
echo  SECTION 3: COLD ROOM SCALING  (Nairobi 84hrs/wk)
echo ============================================================

echo.
echo --- COLD ROOM x1 ---
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_type\":\"grocery\",\"sqft_m2\":70,\"operating_hours_weekly\":84,\"num_refrigeration_units\":1,\"location\":\"Nairobi, Kenya\",\"num_workers\":2,\"months_per_year\":12}" | python parse.py --mode m1
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"grocery\",\"location\":\"Nairobi, Kenya\",\"latitude\":-1.2921,\"longitude\":36.8219,\"equipment_list\":[{\"equipment_type\":\"cold_room\",\"quantity\":1,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo --- COLD ROOM x3 ---
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_type\":\"grocery\",\"sqft_m2\":110,\"operating_hours_weekly\":84,\"num_refrigeration_units\":3,\"location\":\"Nairobi, Kenya\",\"num_workers\":3,\"months_per_year\":12}" | python parse.py --mode m1
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"grocery\",\"location\":\"Nairobi, Kenya\",\"latitude\":-1.2921,\"longitude\":36.8219,\"equipment_list\":[{\"equipment_type\":\"cold_room\",\"quantity\":3,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo --- COLD ROOM x5 ---
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_type\":\"grocery\",\"sqft_m2\":185,\"operating_hours_weekly\":84,\"num_refrigeration_units\":5,\"location\":\"Nairobi, Kenya\",\"num_workers\":4,\"months_per_year\":12}" | python parse.py --mode m1
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"grocery\",\"location\":\"Nairobi, Kenya\",\"latitude\":-1.2921,\"longitude\":36.8219,\"equipment_list\":[{\"equipment_type\":\"cold_room\",\"quantity\":5,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo --- COLD ROOM x7 ---
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_type\":\"grocery\",\"sqft_m2\":250,\"operating_hours_weekly\":84,\"num_refrigeration_units\":7,\"location\":\"Nairobi, Kenya\",\"num_workers\":5,\"months_per_year\":12}" | python parse.py --mode m1
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"grocery\",\"location\":\"Nairobi, Kenya\",\"latitude\":-1.2921,\"longitude\":36.8219,\"equipment_list\":[{\"equipment_type\":\"cold_room\",\"quantity\":7,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo --- COLD ROOM x10 ---
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_type\":\"grocery\",\"sqft_m2\":350,\"operating_hours_weekly\":84,\"num_refrigeration_units\":10,\"location\":\"Nairobi, Kenya\",\"num_workers\":6,\"months_per_year\":12}" | python parse.py --mode m1
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"grocery\",\"location\":\"Nairobi, Kenya\",\"latitude\":-1.2921,\"longitude\":36.8219,\"equipment_list\":[{\"equipment_type\":\"cold_room\",\"quantity\":10,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo --- COLD ROOM x15 ---
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_type\":\"grocery\",\"sqft_m2\":500,\"operating_hours_weekly\":84,\"num_refrigeration_units\":15,\"location\":\"Nairobi, Kenya\",\"num_workers\":8,\"months_per_year\":12}" | python parse.py --mode m1
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"grocery\",\"location\":\"Nairobi, Kenya\",\"latitude\":-1.2921,\"longitude\":36.8219,\"equipment_list\":[{\"equipment_type\":\"cold_room\",\"quantity\":15,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo ============================================================
echo  SECTION 4: DISPLAY COOLER SCALING  (Accra 84hrs/wk)
echo ============================================================

echo.
echo --- DISPLAY COOLER x1 ---
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_type\":\"grocery\",\"sqft_m2\":50,\"operating_hours_weekly\":84,\"num_refrigeration_units\":1,\"location\":\"Accra, Ghana\",\"num_workers\":2,\"months_per_year\":12}" | python parse.py --mode m1
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"grocery\",\"location\":\"Accra, Ghana\",\"latitude\":5.6037,\"longitude\":-0.1870,\"equipment_list\":[{\"equipment_type\":\"display_cooler\",\"quantity\":1,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo --- DISPLAY COOLER x3 ---
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_type\":\"grocery\",\"sqft_m2\":85,\"operating_hours_weekly\":84,\"num_refrigeration_units\":3,\"location\":\"Accra, Ghana\",\"num_workers\":3,\"months_per_year\":12}" | python parse.py --mode m1
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"grocery\",\"location\":\"Accra, Ghana\",\"latitude\":5.6037,\"longitude\":-0.1870,\"equipment_list\":[{\"equipment_type\":\"display_cooler\",\"quantity\":3,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo --- DISPLAY COOLER x5 ---
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_type\":\"grocery\",\"sqft_m2\":85,\"operating_hours_weekly\":84,\"num_refrigeration_units\":5,\"location\":\"Accra, Ghana\",\"num_workers\":4,\"months_per_year\":12}" | python parse.py --mode m1
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"grocery\",\"location\":\"Accra, Ghana\",\"latitude\":5.6037,\"longitude\":-0.1870,\"equipment_list\":[{\"equipment_type\":\"display_cooler\",\"quantity\":5,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo --- DISPLAY COOLER x7 ---
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_type\":\"grocery\",\"sqft_m2\":130,\"operating_hours_weekly\":84,\"num_refrigeration_units\":7,\"location\":\"Accra, Ghana\",\"num_workers\":5,\"months_per_year\":12}" | python parse.py --mode m1
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"grocery\",\"location\":\"Accra, Ghana\",\"latitude\":5.6037,\"longitude\":-0.1870,\"equipment_list\":[{\"equipment_type\":\"display_cooler\",\"quantity\":7,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo --- DISPLAY COOLER x10 ---
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_type\":\"grocery\",\"sqft_m2\":130,\"operating_hours_weekly\":84,\"num_refrigeration_units\":10,\"location\":\"Accra, Ghana\",\"num_workers\":6,\"months_per_year\":12}" | python parse.py --mode m1
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"grocery\",\"location\":\"Accra, Ghana\",\"latitude\":5.6037,\"longitude\":-0.1870,\"equipment_list\":[{\"equipment_type\":\"display_cooler\",\"quantity\":10,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo --- DISPLAY COOLER x15 ---
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_type\":\"grocery\",\"sqft_m2\":190,\"operating_hours_weekly\":84,\"num_refrigeration_units\":15,\"location\":\"Accra, Ghana\",\"num_workers\":8,\"months_per_year\":12}" | python parse.py --mode m1
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"grocery\",\"location\":\"Accra, Ghana\",\"latitude\":5.6037,\"longitude\":-0.1870,\"equipment_list\":[{\"equipment_type\":\"display_cooler\",\"quantity\":15,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo ============================================================
echo  SECTION 5: ICE MACHINE SCALING  (Kampala 84hrs/wk)
echo ============================================================

echo.
echo --- ICE MACHINE x1 ---
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_type\":\"grocery\",\"sqft_m2\":50,\"operating_hours_weekly\":84,\"num_refrigeration_units\":1,\"location\":\"Kampala, Uganda\",\"num_workers\":2,\"months_per_year\":12}" | python parse.py --mode m1
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"grocery\",\"location\":\"Kampala, Uganda\",\"latitude\":0.3476,\"longitude\":32.5825,\"equipment_list\":[{\"equipment_type\":\"ice_maker\",\"quantity\":1,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo --- ICE MACHINE x3 ---
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_type\":\"grocery\",\"sqft_m2\":85,\"operating_hours_weekly\":84,\"num_refrigeration_units\":3,\"location\":\"Kampala, Uganda\",\"num_workers\":3,\"months_per_year\":12}" | python parse.py --mode m1
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"grocery\",\"location\":\"Kampala, Uganda\",\"latitude\":0.3476,\"longitude\":32.5825,\"equipment_list\":[{\"equipment_type\":\"ice_maker\",\"quantity\":3,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo --- ICE MACHINE x5 ---
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_type\":\"grocery\",\"sqft_m2\":85,\"operating_hours_weekly\":84,\"num_refrigeration_units\":5,\"location\":\"Kampala, Uganda\",\"num_workers\":4,\"months_per_year\":12}" | python parse.py --mode m1
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"grocery\",\"location\":\"Kampala, Uganda\",\"latitude\":0.3476,\"longitude\":32.5825,\"equipment_list\":[{\"equipment_type\":\"ice_maker\",\"quantity\":5,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo --- ICE MACHINE x7 ---
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_type\":\"grocery\",\"sqft_m2\":130,\"operating_hours_weekly\":84,\"num_refrigeration_units\":7,\"location\":\"Kampala, Uganda\",\"num_workers\":5,\"months_per_year\":12}" | python parse.py --mode m1
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"grocery\",\"location\":\"Kampala, Uganda\",\"latitude\":0.3476,\"longitude\":32.5825,\"equipment_list\":[{\"equipment_type\":\"ice_maker\",\"quantity\":7,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo --- ICE MACHINE x10 ---
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_type\":\"grocery\",\"sqft_m2\":130,\"operating_hours_weekly\":84,\"num_refrigeration_units\":10,\"location\":\"Kampala, Uganda\",\"num_workers\":6,\"months_per_year\":12}" | python parse.py --mode m1
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"grocery\",\"location\":\"Kampala, Uganda\",\"latitude\":0.3476,\"longitude\":32.5825,\"equipment_list\":[{\"equipment_type\":\"ice_maker\",\"quantity\":10,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo --- ICE MACHINE x15 ---
curl.exe -s -X POST "%BASE_URL%/estimate-consumption" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_type\":\"grocery\",\"sqft_m2\":190,\"operating_hours_weekly\":84,\"num_refrigeration_units\":15,\"location\":\"Kampala, Uganda\",\"num_workers\":8,\"months_per_year\":12}" | python parse.py --mode m1
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"grocery\",\"location\":\"Kampala, Uganda\",\"latitude\":0.3476,\"longitude\":32.5825,\"equipment_list\":[{\"equipment_type\":\"ice_maker\",\"quantity\":15,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo ============================================================
echo  SECTION 6: LIGHTING ONLY  (x1 and x15 MUST be identical)
echo ============================================================

echo.
echo --- LIGHTING x1 ---
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"grocery\",\"location\":\"Nairobi, Kenya\",\"latitude\":-1.2921,\"longitude\":36.8219,\"equipment_list\":[{\"equipment_type\":\"lights\",\"quantity\":1,\"hours_per_day\":12}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo --- LIGHTING x15 (must match x1) ---
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"grocery\",\"location\":\"Nairobi, Kenya\",\"latitude\":-1.2921,\"longitude\":36.8219,\"equipment_list\":[{\"equipment_type\":\"lights\",\"quantity\":15,\"hours_per_day\":12}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo --- LIGHTING x15 + 1 FREEZER (should be only slightly more than freezer x1) ---
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"Test\",\"business_type\":\"grocery\",\"location\":\"Nairobi, Kenya\",\"latitude\":-1.2921,\"longitude\":36.8219,\"equipment_list\":[{\"equipment_type\":\"lights\",\"quantity\":15,\"hours_per_day\":12},{\"equipment_type\":\"freezer\",\"quantity\":1,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode m4

echo.
echo ============================================================
echo  SECTION 7: 30 BLENDED PROFILES
echo ============================================================

echo.
echo [B01] Tiny kiosk - 1 fridge, grid, Lagos:
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"B01\",\"business_type\":\"grocery\",\"location\":\"Lagos, Nigeria\",\"latitude\":6.5244,\"longitude\":3.3792,\"equipment_list\":[{\"equipment_type\":\"refrigerator\",\"quantity\":1,\"hours_per_day\":10}],\"uses_diesel\":false}" | python parse.py --mode blend
echo [B02] Small salon - 1 fridge + 5 lights, Accra:
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"B02\",\"business_type\":\"grocery\",\"location\":\"Accra, Ghana\",\"latitude\":5.6037,\"longitude\":-0.1870,\"equipment_list\":[{\"equipment_type\":\"refrigerator\",\"quantity\":1,\"hours_per_day\":12},{\"equipment_type\":\"lights\",\"quantity\":5,\"hours_per_day\":12}],\"uses_diesel\":false}" | python parse.py --mode blend
echo [B03] Small butchery - 1 freezer + 1 fridge, Nairobi:
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"B03\",\"business_type\":\"butchery\",\"location\":\"Nairobi, Kenya\",\"latitude\":-1.2921,\"longitude\":36.8219,\"equipment_list\":[{\"equipment_type\":\"freezer\",\"quantity\":1,\"hours_per_day\":24},{\"equipment_type\":\"refrigerator\",\"quantity\":1,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode blend
echo [B04] Small butchery diesel - 1 freezer + 1 fridge, 8h diesel, Lagos:
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"B04\",\"business_type\":\"butchery\",\"location\":\"Lagos, Nigeria\",\"latitude\":6.5244,\"longitude\":3.3792,\"equipment_list\":[{\"equipment_type\":\"freezer\",\"quantity\":1,\"hours_per_day\":24},{\"equipment_type\":\"refrigerator\",\"quantity\":1,\"hours_per_day\":24}],\"uses_diesel\":true,\"diesel_hours_per_day\":8,\"diesel_price_per_liter\":0.90}" | python parse.py --mode blend
echo [B05] Small grocery - 2 fridges + 5 lights, Kampala:
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"B05\",\"business_type\":\"grocery\",\"location\":\"Kampala, Uganda\",\"latitude\":0.3476,\"longitude\":32.5825,\"equipment_list\":[{\"equipment_type\":\"refrigerator\",\"quantity\":2,\"hours_per_day\":16},{\"equipment_type\":\"lights\",\"quantity\":5,\"hours_per_day\":12}],\"uses_diesel\":false}" | python parse.py --mode blend
echo [B06] Small grocery - 2 fridges + 1 freezer, Dar es Salaam:
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"B06\",\"business_type\":\"grocery\",\"location\":\"Dar es Salaam, Tanzania\",\"latitude\":-6.7924,\"longitude\":39.2083,\"equipment_list\":[{\"equipment_type\":\"refrigerator\",\"quantity\":2,\"hours_per_day\":18},{\"equipment_type\":\"freezer\",\"quantity\":1,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode blend
echo [B07] Bakery - 2 freezers + 1 display cooler, Kigali:
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"B07\",\"business_type\":\"butchery\",\"location\":\"Kigali, Rwanda\",\"latitude\":-1.9536,\"longitude\":30.0606,\"equipment_list\":[{\"equipment_type\":\"freezer\",\"quantity\":2,\"hours_per_day\":24},{\"equipment_type\":\"display_cooler\",\"quantity\":1,\"hours_per_day\":12}],\"uses_diesel\":false}" | python parse.py --mode blend
echo [B08] Mid butchery - 3 freezers + 2 fridges, Johannesburg:
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"B08\",\"business_type\":\"butchery\",\"location\":\"Johannesburg, South Africa\",\"latitude\":-26.2041,\"longitude\":28.0473,\"equipment_list\":[{\"equipment_type\":\"freezer\",\"quantity\":3,\"hours_per_day\":24},{\"equipment_type\":\"refrigerator\",\"quantity\":2,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode blend
echo [B09] Mid butchery diesel - 3 freezers + 2 fridges, 12h diesel, Lagos:
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"B09\",\"business_type\":\"butchery\",\"location\":\"Lagos, Nigeria\",\"latitude\":6.5244,\"longitude\":3.3792,\"equipment_list\":[{\"equipment_type\":\"freezer\",\"quantity\":3,\"hours_per_day\":24},{\"equipment_type\":\"refrigerator\",\"quantity\":2,\"hours_per_day\":24}],\"uses_diesel\":true,\"diesel_hours_per_day\":12,\"diesel_price_per_liter\":0.90}" | python parse.py --mode blend
echo [B10] Mid grocery - 3 fridges + 2 display coolers + 8 lights, Accra:
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"B10\",\"business_type\":\"grocery\",\"location\":\"Accra, Ghana\",\"latitude\":5.6037,\"longitude\":-0.1870,\"equipment_list\":[{\"equipment_type\":\"refrigerator\",\"quantity\":3,\"hours_per_day\":18},{\"equipment_type\":\"display_cooler\",\"quantity\":2,\"hours_per_day\":12},{\"equipment_type\":\"lights\",\"quantity\":8,\"hours_per_day\":12}],\"uses_diesel\":false}" | python parse.py --mode blend
echo [B11] Mid grocery - 4 fridges + 2 freezers, Nairobi:
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"B11\",\"business_type\":\"grocery\",\"location\":\"Nairobi, Kenya\",\"latitude\":-1.2921,\"longitude\":36.8219,\"equipment_list\":[{\"equipment_type\":\"refrigerator\",\"quantity\":4,\"hours_per_day\":18},{\"equipment_type\":\"freezer\",\"quantity\":2,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode blend
echo [B12] Cold storage small - 1 cold room + 2 freezers, Nairobi:
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"B12\",\"business_type\":\"grocery\",\"location\":\"Nairobi, Kenya\",\"latitude\":-1.2921,\"longitude\":36.8219,\"equipment_list\":[{\"equipment_type\":\"cold_room\",\"quantity\":1,\"hours_per_day\":24},{\"equipment_type\":\"freezer\",\"quantity\":2,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode blend
echo [B13] Mini supermarket - 4 fridges + 3 freezers + 10 lights, Lagos:
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"B13\",\"business_type\":\"mini_supermarket\",\"location\":\"Lagos, Nigeria\",\"latitude\":6.5244,\"longitude\":3.3792,\"equipment_list\":[{\"equipment_type\":\"refrigerator\",\"quantity\":4,\"hours_per_day\":18},{\"equipment_type\":\"freezer\",\"quantity\":3,\"hours_per_day\":24},{\"equipment_type\":\"lights\",\"quantity\":10,\"hours_per_day\":12}],\"uses_diesel\":false}" | python parse.py --mode blend
echo [B14] Mini supermarket diesel - 4 fridges + 3 freezers, 16h diesel, Lagos:
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"B14\",\"business_type\":\"mini_supermarket\",\"location\":\"Lagos, Nigeria\",\"latitude\":6.5244,\"longitude\":3.3792,\"equipment_list\":[{\"equipment_type\":\"refrigerator\",\"quantity\":4,\"hours_per_day\":18},{\"equipment_type\":\"freezer\",\"quantity\":3,\"hours_per_day\":24}],\"uses_diesel\":true,\"diesel_hours_per_day\":16,\"diesel_price_per_liter\":0.90}" | python parse.py --mode blend
echo [B15] Mid supermarket - 5 fridges + 3 display coolers, Johannesburg:
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"B15\",\"business_type\":\"mini_supermarket\",\"location\":\"Johannesburg, South Africa\",\"latitude\":-26.2041,\"longitude\":28.0473,\"equipment_list\":[{\"equipment_type\":\"refrigerator\",\"quantity\":5,\"hours_per_day\":18},{\"equipment_type\":\"display_cooler\",\"quantity\":3,\"hours_per_day\":12}],\"uses_diesel\":false}" | python parse.py --mode blend
echo [B16] Mid supermarket - 5 freezers + 3 fridges + 1 ice maker, Accra:
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"B16\",\"business_type\":\"mini_supermarket\",\"location\":\"Accra, Ghana\",\"latitude\":5.6037,\"longitude\":-0.1870,\"equipment_list\":[{\"equipment_type\":\"freezer\",\"quantity\":5,\"hours_per_day\":24},{\"equipment_type\":\"refrigerator\",\"quantity\":3,\"hours_per_day\":18},{\"equipment_type\":\"ice_maker\",\"quantity\":1,\"hours_per_day\":12}],\"uses_diesel\":false}" | python parse.py --mode blend
echo [B17] Cold storage mid - 2 cold rooms + 3 freezers, Kampala:
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"B17\",\"business_type\":\"grocery\",\"location\":\"Kampala, Uganda\",\"latitude\":0.3476,\"longitude\":32.5825,\"equipment_list\":[{\"equipment_type\":\"cold_room\",\"quantity\":2,\"hours_per_day\":24},{\"equipment_type\":\"freezer\",\"quantity\":3,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode blend
echo [B18] Cold storage diesel - 2 cold rooms + 4 freezers, 20h diesel, Lagos:
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"B18\",\"business_type\":\"grocery\",\"location\":\"Lagos, Nigeria\",\"latitude\":6.5244,\"longitude\":3.3792,\"equipment_list\":[{\"equipment_type\":\"cold_room\",\"quantity\":2,\"hours_per_day\":24},{\"equipment_type\":\"freezer\",\"quantity\":4,\"hours_per_day\":24}],\"uses_diesel\":true,\"diesel_hours_per_day\":20,\"diesel_price_per_liter\":0.90}" | python parse.py --mode blend
echo [B19] Large butchery - 6 freezers + 4 fridges, Dar es Salaam:
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"B19\",\"business_type\":\"butchery\",\"location\":\"Dar es Salaam, Tanzania\",\"latitude\":-6.7924,\"longitude\":39.2083,\"equipment_list\":[{\"equipment_type\":\"freezer\",\"quantity\":6,\"hours_per_day\":24},{\"equipment_type\":\"refrigerator\",\"quantity\":4,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode blend
echo [B20] Large grocery - 6 fridges + 4 display coolers + 1 ice maker, Nairobi:
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"B20\",\"business_type\":\"grocery\",\"location\":\"Nairobi, Kenya\",\"latitude\":-1.2921,\"longitude\":36.8219,\"equipment_list\":[{\"equipment_type\":\"refrigerator\",\"quantity\":6,\"hours_per_day\":18},{\"equipment_type\":\"display_cooler\",\"quantity\":4,\"hours_per_day\":12},{\"equipment_type\":\"ice_maker\",\"quantity\":1,\"hours_per_day\":12}],\"uses_diesel\":false}" | python parse.py --mode blend
echo [B21] Large supermarket - 8 fridges + 4 freezers + 15 lights, Lagos:
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"B21\",\"business_type\":\"mini_supermarket\",\"location\":\"Lagos, Nigeria\",\"latitude\":6.5244,\"longitude\":3.3792,\"equipment_list\":[{\"equipment_type\":\"refrigerator\",\"quantity\":8,\"hours_per_day\":18},{\"equipment_type\":\"freezer\",\"quantity\":4,\"hours_per_day\":24},{\"equipment_type\":\"lights\",\"quantity\":15,\"hours_per_day\":12}],\"uses_diesel\":false}" | python parse.py --mode blend
echo [B22] Large supermarket diesel - 8 fridges + 4 freezers, 18h diesel, Lagos:
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"B22\",\"business_type\":\"mini_supermarket\",\"location\":\"Lagos, Nigeria\",\"latitude\":6.5244,\"longitude\":3.3792,\"equipment_list\":[{\"equipment_type\":\"refrigerator\",\"quantity\":8,\"hours_per_day\":18},{\"equipment_type\":\"freezer\",\"quantity\":4,\"hours_per_day\":24}],\"uses_diesel\":true,\"diesel_hours_per_day\":18,\"diesel_price_per_liter\":0.90}" | python parse.py --mode blend
echo [B23] Cold storage large - 3 cold rooms + 5 freezers, Johannesburg:
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"B23\",\"business_type\":\"grocery\",\"location\":\"Johannesburg, South Africa\",\"latitude\":-26.2041,\"longitude\":28.0473,\"equipment_list\":[{\"equipment_type\":\"cold_room\",\"quantity\":3,\"hours_per_day\":24},{\"equipment_type\":\"freezer\",\"quantity\":5,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode blend
echo [B24] Large cold storage diesel - 4 cold rooms + 6 freezers, 22h diesel, Lagos:
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"B24\",\"business_type\":\"grocery\",\"location\":\"Lagos, Nigeria\",\"latitude\":6.5244,\"longitude\":3.3792,\"equipment_list\":[{\"equipment_type\":\"cold_room\",\"quantity\":4,\"hours_per_day\":24},{\"equipment_type\":\"freezer\",\"quantity\":6,\"hours_per_day\":24}],\"uses_diesel\":true,\"diesel_hours_per_day\":22,\"diesel_price_per_liter\":0.90}" | python parse.py --mode blend
echo [B25] Very large supermarket - 10 fridges + 6 freezers + 3 display coolers, Accra:
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"B25\",\"business_type\":\"mini_supermarket\",\"location\":\"Accra, Ghana\",\"latitude\":5.6037,\"longitude\":-0.1870,\"equipment_list\":[{\"equipment_type\":\"refrigerator\",\"quantity\":10,\"hours_per_day\":18},{\"equipment_type\":\"freezer\",\"quantity\":6,\"hours_per_day\":24},{\"equipment_type\":\"display_cooler\",\"quantity\":3,\"hours_per_day\":12}],\"uses_diesel\":false}" | python parse.py --mode blend
echo [B26] Very large supermarket diesel - 10 fridges + 6 freezers, 20h diesel, Nairobi:
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"B26\",\"business_type\":\"mini_supermarket\",\"location\":\"Nairobi, Kenya\",\"latitude\":-1.2921,\"longitude\":36.8219,\"equipment_list\":[{\"equipment_type\":\"refrigerator\",\"quantity\":10,\"hours_per_day\":18},{\"equipment_type\":\"freezer\",\"quantity\":6,\"hours_per_day\":24}],\"uses_diesel\":true,\"diesel_hours_per_day\":20,\"diesel_price_per_liter\":1.35}" | python parse.py --mode blend
echo [B27] Large cold storage - 5 cold rooms + 8 freezers, Kampala:
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"B27\",\"business_type\":\"grocery\",\"location\":\"Kampala, Uganda\",\"latitude\":0.3476,\"longitude\":32.5825,\"equipment_list\":[{\"equipment_type\":\"cold_room\",\"quantity\":5,\"hours_per_day\":24},{\"equipment_type\":\"freezer\",\"quantity\":8,\"hours_per_day\":24}],\"uses_diesel\":false}" | python parse.py --mode blend
echo [B28] Industrial supermarket - 12 fridges + 8 freezers + 2 ice makers, Lagos:
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"B28\",\"business_type\":\"mini_supermarket\",\"location\":\"Lagos, Nigeria\",\"latitude\":6.5244,\"longitude\":3.3792,\"equipment_list\":[{\"equipment_type\":\"refrigerator\",\"quantity\":12,\"hours_per_day\":18},{\"equipment_type\":\"freezer\",\"quantity\":8,\"hours_per_day\":24},{\"equipment_type\":\"ice_maker\",\"quantity\":2,\"hours_per_day\":12}],\"uses_diesel\":false}" | python parse.py --mode blend
echo [B29] Industrial cold storage - 6 cold rooms + 10 freezers, 24h diesel, Lagos:
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"B29\",\"business_type\":\"grocery\",\"location\":\"Lagos, Nigeria\",\"latitude\":6.5244,\"longitude\":3.3792,\"equipment_list\":[{\"equipment_type\":\"cold_room\",\"quantity\":6,\"hours_per_day\":24},{\"equipment_type\":\"freezer\",\"quantity\":10,\"hours_per_day\":24}],\"uses_diesel\":true,\"diesel_hours_per_day\":24,\"diesel_price_per_liter\":0.90}" | python parse.py --mode blend
echo [B30] Max load - 15 fridges + 10 freezers + 5 cold rooms + 3 ice makers, Lagos:
curl.exe -s -X POST "%BASE_URL%/analyze" -H "Content-Type: application/json" -H "X-API-KEY: %API_KEY%" -d "{\"business_name\":\"B30\",\"business_type\":\"mini_supermarket\",\"location\":\"Lagos, Nigeria\",\"latitude\":6.5244,\"longitude\":3.3792,\"equipment_list\":[{\"equipment_type\":\"refrigerator\",\"quantity\":15,\"hours_per_day\":18},{\"equipment_type\":\"freezer\",\"quantity\":10,\"hours_per_day\":24},{\"equipment_type\":\"cold_room\",\"quantity\":5,\"hours_per_day\":24},{\"equipment_type\":\"ice_maker\",\"quantity\":3,\"hours_per_day\":12}],\"uses_diesel\":false}" | python parse.py --mode blend

echo.
echo ============================================================
echo  ALL DONE  -  Key checks:
echo  S1-S5: M1 and M4 values should be close for same unit count
echo  S6:    Lighting x1 and x15 must print identical M4 value
echo  S7:    Consumption must grow from B01 to B30
echo ============================================================
pause
endlocal
