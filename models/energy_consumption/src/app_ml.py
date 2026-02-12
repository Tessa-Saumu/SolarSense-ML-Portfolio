
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import joblib
import os

app = Flask(__name__)
CORS(app)

# Load model and scaler
MODEL_PATH = "models/energy_consumption_model_v1.joblib"
SCALER_PATH = "models/energy_scaler_v1.joblib"
FEATURE_COLS_PATH = "models/feature_columns_v1.joblib"
MAPPINGS_PATH = "models/sme_mappings_v1.joblib"

model_data = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
feature_columns = joblib.load(FEATURE_COLS_PATH)
sme_mappings = joblib.load(MAPPINGS_PATH)

best_model = model_data['best_model']
use_log_target = model_data.get('use_log_target', False)
le_pba = sme_mappings['le_pba']
le_cendiv = sme_mappings['le_cendiv']
le_size = sme_mappings['le_size']

# Climate zones
CLIMATE_ZONES = {
    'lagos': 1.35, 'accra': 1.30, 'nairobi': 1.20, 'kampala': 1.25,
    'johannesburg': 1.18, 'dar es salaam': 1.35, 'kinshasa': 1.35, 'abidjan': 1.30
}

def get_climate_factor(location: str) -> float:
    """Get climate adjustment factor from location string."""
    location_lower = location.lower()
    for city, factor in CLIMATE_ZONES.items():
        if city in location_lower:
            return factor
    return 1.20  # default

@app.route('/api/v1/estimate-consumption', methods=['POST'])
def estimate_consumption():
    """Estimate energy consumption for African SME."""
    try:
        data = request.get_json()

        # Input validation
        required_fields = ['business_type', 'sqft_m2', 'operating_hours_weekly', 
                          'num_refrigeration_units', 'location']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': {
                        'code': 'MISSING_FIELD',
                        'message': f'Missing required field: {field}',
                        'status': 400
                    }
                }), 400

        # Extract inputs
        business_type = data['business_type'].lower()
        sqft_m2 = float(data['sqft_m2'])
        sqft = sqft_m2 * 10.764  # Convert m² to sqft
        operating_hours_weekly = float(data['operating_hours_weekly'])
        num_refrigeration_units = int(data['num_refrigeration_units'])
        num_workers = int(data.get('num_workers', 5))
        months_per_year = int(data.get('months_per_year', 12))
        location = data['location']

        # Validate business type
        valid_business_types = ['butchery', 'grocery', 'mini_supermarket']
        if business_type not in valid_business_types:
            return jsonify({
                'error': {
                    'code': 'INVALID_BUSINESS_TYPE',
                    'message': f'Invalid business_type. Must be one of: {valid_business_types}',
                    'status': 400
                }
            }), 400

        # Map business type to PBA
        pba_code = 11  # Food Sales

        # Get climate factor
        climate_factor = get_climate_factor(location)

        # Create features
        sqft_per_worker = sqft / max(num_workers, 1)
        wkhrs_per_week_normalized = operating_hours_weekly / 168
        annual_operating_hours = operating_hours_weekly * months_per_year * (52/12)
        refrigeration_density = (num_refrigeration_units / max(sqft, 1)) * 1000
        is_high_refrigeration = 1 if num_refrigeration_units > 3 else 0
        is_extended_hours = 1 if operating_hours_weekly > 60 else 0

        # Size category
        if sqft < 2000:
            size_category = 'small'
        elif sqft < 10000:
            size_category = 'medium'
        else:
            size_category = 'large'

        # Encode categoricals
        pba_encoded = le_pba.transform([str(pba_code)])[0]
        cendiv_encoded = le_cendiv.transform(['5'])[0]  # Default
        size_category_encoded = le_size.transform([size_category])[0]

        # Build feature vector
        feature_vector = np.array([[
            sqft, operating_hours_weekly, num_refrigeration_units, 1,  # NFLOOR=1
            num_workers, months_per_year, 5,  # YRCONC=5
            0,  # kwh_per_sqft (will be predicted)
            sqft_per_worker, wkhrs_per_week_normalized, annual_operating_hours,
            refrigeration_density, is_high_refrigeration, is_extended_hours,
            pba_encoded, cendiv_encoded, size_category_encoded
        ]])

        # Scale and predict
        feature_vector_scaled = scaler.transform(feature_vector)

        if use_log_target:
            log_prediction = best_model.predict(feature_vector_scaled)[0]
            base_prediction = np.expm1(log_prediction)
        else:
            base_prediction = best_model.predict(feature_vector_scaled)[0]

        # Apply climate adjustment
        adjusted_prediction = base_prediction * climate_factor
        monthly_kwh = adjusted_prediction / 12

        # Breakdown
        refrigeration_share = min(0.70, max(0.50, num_refrigeration_units / max(num_workers * 2, 1)))
        refrigeration_kwh = monthly_kwh * refrigeration_share
        other_kwh = monthly_kwh * (1 - refrigeration_share)

        # Confidence score (based on data completeness)
        confidence_score = 0.75
        if all([sqft_m2 > 0, operating_hours_weekly > 0, num_refrigeration_units > 0]):
            confidence_score = 0.85

        return jsonify({
            'estimated_consumption_kwh_monthly': round(monthly_kwh, 2),
            'confidence_score': round(confidence_score, 2),
            'breakdown': {
                'refrigeration': round(refrigeration_kwh, 2),
                'other': round(other_kwh, 2)
            },
            'climate_adjustment_factor': round(climate_factor, 2),
            'equipment_summary': {
                'total_refrigeration_units': num_refrigeration_units,
                'total_other_equipment': 0  # Not tracked in this version
            }
        }), 200

    except Exception as e:
        return jsonify({
            'error': {
                'code': 'PREDICTION_ERROR',
                'message': str(e),
                'status': 500
            }
        }), 500

@app.route('/api/v1/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    port = int(os.getenv('MODEL1_PORT', 8001))
    app.run(host='0.0.0.0', port=port, debug=True)
