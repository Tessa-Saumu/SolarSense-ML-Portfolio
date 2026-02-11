from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os


# Load environment variables (.env file)

load_dotenv()

API_KEY = os.getenv("API_KEY")

app = Flask(__name__)


# Rate Limiting: 100 requests per minute per IP

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per minute"]
)


# Helper: API Key Authentication

def require_api_key():
    key = request.headers.get("X-API-KEY")

    if not key or key != API_KEY:
        return False
    return True



# Error Handlers (Hide internal errors)

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad Request"}), 400


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": "Unauthorized"}), 401


@app.errorhandler(500)
def server_error(error):
    # Do NOT expose stack trace
    return jsonify({"error": "Internal Server Error"}), 500



# ROI Calculation Endpoint (SECURED)

@app.route("/calculate-roi", methods=["POST"])
@limiter.limit("100 per minute")  # <-- Rate limit applied here
def calculate_roi():

    # API KEY CHECK 
    if not require_api_key():
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.get_json(force=True)

      
        # INPUT EXTRACTION
        
        system_cost = float(data.get("system_cost", -1))
        monthly_consumption = float(data.get("monthly_consumption", -1))
        monthly_generation = float(data.get("monthly_generation", -1))
        tariff = float(data.get("tariff", -1))

        hours_per_day = int(data.get("hours_per_day", 0))
        equipment_units = int(data.get("equipment_units", 0))

        business_type = data.get("business_type", "")
        location = data.get("location", "")

       
        # INPUT VALIDATION (Ranges + formats)
       
        if system_cost <= 0:
            return jsonify({"error": "system_cost must be greater than 0"}), 400

        if monthly_consumption < 0 or monthly_generation < 0:
            return jsonify({"error": "monthly_consumption and monthly_generation cannot be negative"}), 400

        if tariff <= 0:
            return jsonify({"error": "tariff must be greater than 0"}), 400

        if not (0 <= hours_per_day <= 24):
            return jsonify({"error": "hours_per_day must be between 0 and 24"}), 400

        if equipment_units < 0 or equipment_units > 500:
            return jsonify({"error": "equipment_units must be between 0 and 500"}), 400

        allowed_business_types = ["retail", "factory", "office", "warehouse"]
        if business_type.lower() not in allowed_business_types:
            return jsonify({
                "error": "business_type must be one of: retail, factory, office, warehouse"
            }), 400

        if not location.isalpha():
            return jsonify({"error": "location must contain only letters"}), 400

       
        # ROI CALCULATION (NO PAYBACK PERIOD)
        
        monthly_savings = (monthly_generation - monthly_consumption) * tariff
        annual_savings = monthly_savings * 12

        roi = (annual_savings / system_cost) * 100

        
        # OUTPUT VALIDATION
        
        if roi < 0:
            roi = 0

        if roi > 100:
            roi = 100

        if annual_savings < 0:
            annual_savings = 0
            monthly_savings = 0

        
        # Viability Classification
       
        if roi >= 20:
            viability = "Highly Viable"
        elif roi >= 10:
            viability = "Moderately Viable"
        else:
            viability = "Not Viable"

      
        # JSON RESPONSE ONLY
     
        return jsonify({
            "monthly_savings_usd": round(monthly_savings, 2),
            "annual_savings_usd": round(annual_savings, 2),
            "roi_percentage": round(roi, 2),
            "viability": viability
        }), 200

    except Exception:
        # Generic catch-all to avoid leaking internals
        return jsonify({"error": "Internal Server Error"}), 500



# App Runner

if __name__ == "__main__":
    app.run(debug=False)
