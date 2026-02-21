-- =============================================
-- Solar Irradiance Database Schema
-- Model 2: Solar Generation Prediction
-- Database: PostgreSQL (for pgAdmin)
-- =============================================

-- Instructions for pgAdmin:
-- 1. Create a new database called 'solar_irradiance'
-- 2. Right-click on the database → Query Tool
-- 3. Copy and paste this entire script
-- 4. Click Execute (F5)

-- Drop existing tables if needed (uncomment to reset database)
-- DROP TABLE IF EXISTS solar_irradiance_monthly CASCADE;
-- DROP TABLE IF EXISTS solar_irradiance_daily CASCADE;
-- DROP TABLE IF EXISTS locations CASCADE;

-- =============================================
-- LOCATIONS TABLE
-- =============================================
CREATE TABLE IF NOT EXISTS locations (
    location_id SERIAL PRIMARY KEY,
    location_name VARCHAR(100) UNIQUE NOT NULL,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    country VARCHAR(50),
    region VARCHAR(50),
    city VARCHAR(50),
    -- SME context fields
    typical_retail_type VARCHAR(50),  -- 'butchery', 'grocery', 'mini_supermarket', 'cold_chain'
    estimated_cold_storage_kw DECIMAL(8, 2),  -- Optional: if known
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CHECK (latitude BETWEEN -90 AND 90),
    CHECK (longitude BETWEEN -180 AND 180)
);

-- Create indexes for faster queries
CREATE INDEX idx_locations_country ON locations(country);
CREATE INDEX idx_locations_coordinates ON locations(latitude, longitude);

-- =============================================
-- DAILY SOLAR IRRADIANCE DATA
-- =============================================
CREATE TABLE IF NOT EXISTS solar_irradiance_daily (
    id SERIAL PRIMARY KEY,
    location_id INTEGER NOT NULL REFERENCES locations(location_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    
    -- Solar irradiance parameters (from NASA POWER)
    ghi_kwh_m2 DECIMAL(8, 4),  -- Global Horizontal Irradiance (All Sky)
    clear_sky_ghi_kwh_m2 DECIMAL(8, 4),  -- Clear Sky GHI
    dni_kwh_m2 DECIMAL(8, 4),  -- Direct Normal Irradiance (optional)
    dhi_kwh_m2 DECIMAL(8, 4),  -- Diffuse Horizontal Irradiance (optional)
    
    -- Environmental factors affecting solar performance
    temperature_c DECIMAL(6, 2),  -- Temperature at 2m
    wind_speed_ms DECIMAL(6, 2),  -- Wind speed at 10m
    relative_humidity_pct DECIMAL(5, 2),  -- Relative humidity
    
    -- Derived/calculated fields
    solar_potential_kwh DECIMAL(10, 4),  -- Calculated solar generation potential
    
    -- Metadata
    data_source VARCHAR(50) DEFAULT 'NASA_POWER',
    data_quality_flag VARCHAR(20),  -- 'good', 'suspect', 'missing'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    UNIQUE(location_id, date),
    CHECK (ghi_kwh_m2 >= 0),
    CHECK (temperature_c BETWEEN -50 AND 60),
    CHECK (wind_speed_ms >= 0),
    CHECK (relative_humidity_pct BETWEEN 0 AND 100)
);

-- Create indexes for faster time-series queries
CREATE INDEX idx_daily_location_date ON solar_irradiance_daily(location_id, date DESC);
CREATE INDEX idx_daily_date ON solar_irradiance_daily(date);

-- =============================================
-- MONTHLY AGGREGATED DATA
-- =============================================
CREATE TABLE IF NOT EXISTS solar_irradiance_monthly (
    id SERIAL PRIMARY KEY,
    location_id INTEGER NOT NULL REFERENCES locations(location_id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    
    -- Aggregated solar metrics
    avg_ghi_kwh_m2 DECIMAL(8, 4),
    min_ghi_kwh_m2 DECIMAL(8, 4),
    max_ghi_kwh_m2 DECIMAL(8, 4),
    std_ghi_kwh_m2 DECIMAL(8, 4),  -- Standard deviation for variability
    
    -- Aggregated environmental metrics
    avg_temperature_c DECIMAL(6, 2),
    avg_wind_speed_ms DECIMAL(6, 2),
    avg_relative_humidity_pct DECIMAL(5, 2),
    
    -- Summary statistics
    total_days_with_data INTEGER,
    avg_solar_potential_kwh DECIMAL(10, 4),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    UNIQUE(location_id, year, month),
    CHECK (month BETWEEN 1 AND 12),
    CHECK (year BETWEEN 2000 AND 2100)
);

-- Create indexes
CREATE INDEX idx_monthly_location_time ON solar_irradiance_monthly(location_id, year, month);

-- =============================================
-- USEFUL VIEWS
-- =============================================

-- View: Latest solar data for each location
CREATE OR REPLACE VIEW v_latest_solar_data AS
SELECT 
    l.location_name,
    l.latitude,
    l.longitude,
    l.country,
    s.date,
    s.ghi_kwh_m2,
    s.temperature_c,
    s.wind_speed_ms
FROM locations l
JOIN solar_irradiance_daily s ON l.location_id = s.location_id
WHERE s.date = (
    SELECT MAX(date) 
    FROM solar_irradiance_daily 
    WHERE location_id = l.location_id
);

-- View: Average solar irradiance by location
CREATE OR REPLACE VIEW v_location_solar_summary AS
SELECT 
    l.location_name,
    l.country,
    l.latitude,
    l.longitude,
    COUNT(s.id) as total_records,
    AVG(s.ghi_kwh_m2) as avg_ghi,
    MIN(s.ghi_kwh_m2) as min_ghi,
    MAX(s.ghi_kwh_m2) as max_ghi,
    AVG(s.temperature_c) as avg_temp
FROM locations l
LEFT JOIN solar_irradiance_daily s ON l.location_id = s.location_id
GROUP BY l.location_id, l.location_name, l.country, l.latitude, l.longitude;

SELECT * FROM v_location_solar_summary;

-- =============================================
-- SAMPLE QUERIES
-- =============================================

-- Insert sample location
-- INSERT INTO locations (location_name, latitude, longitude, country, region)
-- VALUES ('Nairobi_Kenya', -1.2921, 36.8219, 'Kenya', 'East Africa');

-- Get all data for a specific location
 SELECT * FROM solar_irradiance_daily 
 WHERE location_id = (SELECT location_id FROM locations WHERE location_name = 'Nairobi_Kenya')
 ORDER BY date DESC
 LIMIT 30;

-- Calculate monthly averages for a location
 SELECT 
    EXTRACT(YEAR FROM date) as year,
    EXTRACT(MONTH FROM date) as month,
     AVG(ghi_kwh_m2) as avg_ghi,
     AVG(temperature_c) as avg_temp
 FROM solar_irradiance_daily
 WHERE location_id = 1
 GROUP BY year, month
 ORDER BY year, month;

-- =============================================
-- HELPER FUNCTION: Populate monthly table
-- =============================================
CREATE OR REPLACE FUNCTION refresh_monthly_aggregates()
RETURNS void AS $$
BEGIN
    INSERT INTO solar_irradiance_monthly (
        location_id, year, month,
        avg_ghi_kwh_m2, min_ghi_kwh_m2, max_ghi_kwh_m2, std_ghi_kwh_m2,
        avg_temperature_c, avg_wind_speed_ms, avg_relative_humidity_pct,
        total_days_with_data, avg_solar_potential_kwh
    )
    SELECT 
        location_id,
        EXTRACT(YEAR FROM date)::INTEGER as year,
        EXTRACT(MONTH FROM date)::INTEGER as month,
        AVG(ghi_kwh_m2),
        MIN(ghi_kwh_m2),
        MAX(ghi_kwh_m2),
        STDDEV(ghi_kwh_m2),
        AVG(temperature_c),
        AVG(wind_speed_ms),
        AVG(relative_humidity_pct),
        COUNT(*),
        AVG(solar_potential_kwh)
    FROM solar_irradiance_daily
    GROUP BY location_id, year, month
    ON CONFLICT (location_id, year, month) 
    DO UPDATE SET
        avg_ghi_kwh_m2 = EXCLUDED.avg_ghi_kwh_m2,
        min_ghi_kwh_m2 = EXCLUDED.min_ghi_kwh_m2,
        max_ghi_kwh_m2 = EXCLUDED.max_ghi_kwh_m2,
        std_ghi_kwh_m2 = EXCLUDED.std_ghi_kwh_m2,
        avg_temperature_c = EXCLUDED.avg_temperature_c,
        total_days_with_data = EXCLUDED.total_days_with_data;
END;
$$ LANGUAGE plpgsql;

-- 1. Remove the old version entirely
DROP VIEW IF EXISTS v_solar_data_complete;

-- 2. Create it fresh
CREATE VIEW v_solar_data_complete AS
SELECT
    l.location_name,
    COALESCE(l.country, 'Unknown') AS country,
    l.latitude,
    l.longitude,
    s.date,
    EXTRACT(YEAR FROM s.date)::int  AS year,
    EXTRACT(MONTH FROM s.date)::int AS month,
    EXTRACT(DAY FROM s.date)::int   AS day,
    TRIM(TO_CHAR(s.date, 'Day'))   AS day_of_week,
    s.ghi_kwh_m2,
    s.clear_sky_ghi_kwh_m2,
    s.temperature_c,
    s.wind_speed_ms,
    s.relative_humidity_pct,
    s.solar_potential_kwh AS estimated_daily_generation_kwh,
    COALESCE(s.data_quality_flag, 'good') AS data_quality
FROM solar_irradiance_daily s
JOIN locations l
  ON s.location_id = l.location_id;

-- To refresh monthly aggregates, run:
SELECT refresh_monthly_aggregates();

SELECT COUNT(*) FROM solar_irradiance_daily;

-- This should tell us exactly what's in the database
SELECT 
    'Locations' as table_name, 
    COUNT(*) as record_count 
FROM locations
UNION ALL
SELECT 
    'Daily Data', 
    COUNT(*) 
FROM solar_irradiance_daily;

--Checking out our data in our table

SELECT* FROM locations;

SELECT* FROM public.solar_irradiance_daily;

SELECT* FROM public.solar_irradiance_monthly;
