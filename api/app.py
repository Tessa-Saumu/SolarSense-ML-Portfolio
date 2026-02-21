from fastapi import FastAPI, HTTPException
import joblib
import numpy as np

# Initialize FastAPI app
app = FastAPI(
    title="Energy Consumption Estimation API",
    description="Estimates daily energy consumption (kWh) from power inputs",
    version="1.0"
)

# Load trained model
model = joblib.load("model/xgboost_energy_model.pkl")

@app.post("/predict")
def predict_energy(dc_power: float, ac_power: float):
    """
    Predict daily energy consumption (kWh)
    """

    # ----- Step A: Input validation -----
    if dc_power is None or ac_power is None:
        raise HTTPException(status_code=400, detail="All input fields are required.")

    if dc_power < 0 or ac_power < 0:
        raise HTTPException(status_code=400, detail="Power values must be non-negative.")

    # Optional: set upper realistic limits
    if dc_power > 10000 or ac_power > 10000:
        raise HTTPException(status_code=400, detail="Power values exceed realistic maximum.")

    # ----- Step B: Handle zero input -----
    if dc_power == 0 and ac_power == 0:
        return {"estimated_daily_kwh": 0.0}

    # Prepare features for prediction
    features = np.array([[dc_power, ac_power]])
    prediction = model.predict(features)[0]

    return {
        "estimated_daily_kwh": round(float(prediction), 2)
    }
