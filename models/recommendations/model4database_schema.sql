-- Solar Viability Database Schema
-- Simple and clean structure for MVP

-- ============================================
-- 1. BUSINESS INFO TABLE
-- ============================================
CREATE TABLE business (
    id SERIAL PRIMARY KEY,
    business_name VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    monthly_energy_usage_kwh DECIMAL(10, 2),
    monthly_energy_cost DECIMAL(10, 2),
    roof_area_sqm DECIMAL(10, 2),
    business_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 2. SOLAR ANALYSIS (Model 1 - Sunshine)
-- ============================================
CREATE TABLE solar_analysis (
    id SERIAL PRIMARY KEY,
    business_id INTEGER REFERENCES business(id),
    solar_irradiance_kwh_m2_day DECIMAL(10, 2),
    annual_sunshine_hours DECIMAL(10, 2),
    optimal_panel_angle DECIMAL(5, 2),
    shading_factor DECIMAL(3, 2),
    solar_potential_score DECIMAL(3, 2), -- 0-10 scale
    model_confidence DECIMAL(3, 2), -- percentage
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 3. COST ANALYSIS (Model 2 - Money)
-- ============================================
CREATE TABLE cost_analysis (
    id SERIAL PRIMARY KEY,
    business_id INTEGER REFERENCES business(id),
    system_size_kw DECIMAL(10, 2),
    installation_cost DECIMAL(12, 2),
    annual_energy_production_kwh DECIMAL(10, 2),
    annual_savings DECIMAL(10, 2),
    roi_years DECIMAL(5, 2),
    payback_period_years DECIMAL(5, 2),
    net_present_value DECIMAL(12, 2),
    incentives_available DECIMAL(10, 2),
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 4. BUSINESS SUITABILITY (Model 3 - Fit)
-- ============================================
CREATE TABLE business_suitability (
    id SERIAL PRIMARY KEY,
    business_id INTEGER REFERENCES business(id),
    business_hours_match_score DECIMAL(3, 2), -- 0-10
    energy_pattern_compatibility DECIMAL(3, 2), -- 0-10
    roof_suitability_score DECIMAL(3, 2), -- 0-10
    maintenance_capacity_score DECIMAL(3, 2), -- 0-10
    overall_suitability_score DECIMAL(3, 2), -- 0-10
    risk_factors TEXT,
    opportunities TEXT,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 5. FINAL RECOMMENDATION (Your Brain's Decision)
-- ============================================
CREATE TABLE final_recommendation (
    id SERIAL PRIMARY KEY,
    business_id INTEGER REFERENCES business(id),
    solar_analysis_id INTEGER REFERENCES solar_analysis(id),
    cost_analysis_id INTEGER REFERENCES cost_analysis(id),
    business_suitability_id INTEGER REFERENCES business_suitability(id),
    
    -- Final Decision
    solar_viable BOOLEAN NOT NULL,
    recommended_system_size_kw DECIMAL(10, 2),
    estimated_roi_years DECIMAL(5, 2),
    confidence_score DECIMAL(3, 2), -- 0-100
    
    -- Explanation
    recommendation_summary TEXT NOT NULL,
    key_reasons TEXT[], -- Array of reasons
    warnings TEXT[], -- Any concerns
    next_steps TEXT[], -- What to do next
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 6. AUDIT LOG (Track everything)
-- ============================================
CREATE TABLE analysis_log (
    id SERIAL PRIMARY KEY,
    business_id INTEGER REFERENCES business(id),
    action VARCHAR(100),
    model_name VARCHAR(50),
    status VARCHAR(50),
    error_message TEXT,
    execution_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- SAMPLE DATA (for testing)
-- ============================================

-- Sample Business
INSERT INTO business (
    business_name, 
    location, 
    latitude, 
    longitude,
    monthly_energy_usage_kwh,
    monthly_energy_cost,
    roof_area_sqm,
    business_type
) VALUES (
    'Joe''s Coffee Shop',
    'Nairobi, Kenya',
    -1.2921,
    36.8219,
    2500,
    45000,
    150,
    'Food & Beverage'
);

-- ============================================
-- INDEXES (for performance)
-- ============================================
CREATE INDEX idx_business_location ON business(location);
CREATE INDEX idx_final_recommendation_business ON final_recommendation(business_id);
CREATE INDEX idx_analysis_log_business ON analysis_log(business_id);

INSERT INTO business (
    business_name,
    location,
    latitude,
    longitude,
    monthly_energy_usage_kwh,
    monthly_energy_cost,
    roof_area_sqm,
    business_type
)
SELECT
    'Business ' || gs,
    'Nairobi, Kenya',
    -1.2921 + (random() - 0.5) * 0.1,
    36.8219 + (random() - 0.5) * 0.1,
    (random() * 5000 + 500)::DECIMAL(10,2),
    (random() * 100000 + 10000)::DECIMAL(10,2),
    (random() * 500 + 50)::DECIMAL(10,2),
    (ARRAY['Retail', 'Manufacturing', 'Food & Beverage', 'Office'])[floor(random()*4)+1]
FROM generate_series(1,1000) gs;

INSERT INTO solar_analysis (
    business_id,
    solar_irradiance_kwh_m2_day,
    annual_sunshine_hours,
    optimal_panel_angle,
    shading_factor,
    solar_potential_score,
    model_confidence
)
SELECT
    id,
    (random()*2 + 4)::DECIMAL(10,2),
    (random()*1000 + 2000)::DECIMAL(10,2),
    (random()*15 + 10)::DECIMAL(5,2),
    (random()*0.3)::DECIMAL(5,2),
    (random()*10)::DECIMAL(5,2),
    (random()*9.99)::DECIMAL(5,2)
FROM business;

INSERT INTO solar_analysis (
    business_id,
    solar_irradiance_kwh_m2_day,
    annual_sunshine_hours,
    optimal_panel_angle,
    shading_factor,
    solar_potential_score,
    model_confidence
)
SELECT
    id,
    (random()*2 + 4)::DECIMAL(10,2),
    (random()*1000 + 2000)::DECIMAL(10,2),
    (random()*15 + 10)::DECIMAL(5,2),
    (random()*0.3)::DECIMAL(3,2),
    (random()*10)::DECIMAL(3,2),
    (random()*9.99)::DECIMAL(3,2)
FROM business;

INSERT INTO cost_analysis (
    business_id,
    system_size_kw,
    installation_cost,
    annual_energy_production_kwh,
    annual_savings,
    roi_years,
    payback_period_years,
    net_present_value,
    incentives_available
)
SELECT
    id,
    (random()*100 + 10)::DECIMAL(10,2),
    (random()*1000000 + 500000)::DECIMAL(12,2),
    (random()*100000 + 20000)::DECIMAL(10,2),
    (random()*500000 + 50000)::DECIMAL(10,2),
    (random()*10 + 2)::DECIMAL(5,2),
    (random()*8 + 2)::DECIMAL(5,2),
    (random()*2000000 - 500000)::DECIMAL(12,2),
    (random()*100000)::DECIMAL(10,2)
FROM business;

INSERT INTO business_suitability (
    business_id,
    business_hours_match_score,
    energy_pattern_compatibility,
    roof_suitability_score,
    maintenance_capacity_score,
    overall_suitability_score,
    risk_factors,
    opportunities
)
SELECT
    id,
    (random()*9.99)::DECIMAL(3,2),
    (random()*9.99)::DECIMAL(3,2),
    (random()*9.99)::DECIMAL(3,2),
    (random()*9.99)::DECIMAL(3,2),
    (random()*9.99)::DECIMAL(3,2),
    'Minimal shading issues',
    'High solar exposure'
FROM business;

INSERT INTO final_recommendation (
    business_id,
    solar_analysis_id,
    cost_analysis_id,
    business_suitability_id,
    solar_viable,
    recommended_system_size_kw,
    estimated_roi_years,
    confidence_score,
    recommendation_summary,
    key_reasons,
    warnings,
    next_steps
)
SELECT
    b.id,
    sa.id,
    ca.id,
    bs.id,
    (random() > 0.3),
    (random()*100 + 10)::DECIMAL(10,2),
    (random()*10 + 2)::DECIMAL(5,2),
    (random()*9.99)::DECIMAL(3,2),
    'Solar installation recommended based on strong ROI and sunlight exposure.',
    ARRAY['High sunlight','Good roof area'],
    ARRAY['Seasonal variability'],
    ARRAY['Conduct site inspection','Apply for incentives']
FROM business b
JOIN solar_analysis sa ON sa.business_id = b.id
JOIN cost_analysis ca ON ca.business_id = b.id
JOIN business_suitability bs ON bs.business_id = b.id;

SELECT * FROM business;

SELECT 
    b.business_name,
    fr.solar_viable,
    fr.estimated_roi_years,
    fr.confidence_score
FROM final_recommendation fr
JOIN business b ON b.id = fr.business_id
LIMIT 10;


