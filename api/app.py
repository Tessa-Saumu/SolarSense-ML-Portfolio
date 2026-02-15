from fastapi import FastAPI
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
    features = np.array([[dc_power, ac_power]])
    prediction = model.predict(features)[0]

    return {
        "estimated_daily_kwh": round(float(prediction), 2)
    }
