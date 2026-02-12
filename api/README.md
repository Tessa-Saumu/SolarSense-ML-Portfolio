# Legacy FastAPI Energy Consumption API (Not Model 1)

> ⚠️ Note: This is a legacy prototype; the official Model 1 implementation is the Flask service under `models/energy_consumption` exposing `POST /api/v1/estimate-consumption`. The content below describes this older FastAPI/XGBoost endpoint.

# Energy Consumption Estimation API

## Overview
This project provides an AI-powered API that estimates daily energy consumption (kWh)
based on power input parameters.

The model uses an XGBoost regression algorithm trained on solar energy generation data.

---

## Input Parameters
- **dc_power** (float): DC power input
- **ac_power** (float): AC power input

---

## Output
- **estimated_daily_kwh**: Estimated daily energy consumption in kilowatt-hours (kWh)

---

## Tech Stack
- Python
- XGBoost
- FastAPI
- Scikit-learn
- NumPy

---

## How to Run the API

1. Install dependencies:
```bash
pip install -r requirements.txt
