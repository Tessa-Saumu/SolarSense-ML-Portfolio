from flask import Flask, request, jsonify

app = Flask(__name__)

def calculate_roi(system_cost,
                  monthly_consumption,
                  monthly_generation,
                  tariff):

    energy_offset = min(monthly_consumption, monthly_generation)

    monthly_savings = energy_offset * tariff
    annual_savings = monthly_savings * 12

    roi = (annual_savings / system_cost) * 100
    payback = system_cost / annual_savings

    if roi > 20:
        viability = "Highly Viable"
    elif roi >= 10:
        viability = "Moderately Viable"
    else:
        viability = "Not Viable"

    return {
        "monthly_savings_usd": round(monthly_savings, 2),
        "annual_savings_usd": round(annual_savings, 2),
        "roi_percentage": round(roi, 2),
        "payback_years": round(payback, 2),
        "viability": viability
    }


@app.route("/calculate-roi", methods=["POST"])
def roi_endpoint():

    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    required_fields = [
        "system_cost",
        "monthly_consumption",
        "monthly_generation",
        "tariff"
    ]

    values = {}

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

        try:
            values[field] = float(data[field])
        except:
            return jsonify({"error": f"{field} must be a number"}), 400

    if values["system_cost"] <= 0:
        return jsonify({"error": "system_cost must be greater than 0"}), 400

    if values["tariff"] <= 0:
        return jsonify({"error": "tariff must be greater than 0"}), 400

    if values["monthly_consumption"] < 0 or values["monthly_generation"] < 0:
        return jsonify({
            "error": "monthly_consumption and monthly_generation cannot be negative"
        }), 400

    result = calculate_roi(
        values["system_cost"],
        values["monthly_consumption"],
        values["monthly_generation"],
        values["tariff"]
    )

    return jsonify(result)


@app.route("/")
def home():
    return jsonify({"message": "Model 3 ROI API running"})


if __name__ == "__main__":
    app.run(debug=True)
