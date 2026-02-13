# Model 3 ROI Calculation API

## Overview
This Flask API calculates Return on Investment (ROI) for energy systems.  
It accepts input data (generation, consumption, cost, price) and returns ROI calculations.  

## Installation
```bash
# Clone repo
git clone <repo-url>
cd model3_api

# Activate virtual environment (Windows CMD)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the API
python app/app.py

Endpoints
POST /calculate-roi

Calculates ROI based on input data.

Request Example
{
  "generation_kwh": 500,
  "consumption_kwh": 300,
  "installation_cost": 4000,
  "electricity_price": 0.18
}

Response Example
{
  "status": "success",
  "message": "ROI calculation not implemented yet",
  "input_received": {
    "generation_kwh": 500,
    "consumption_kwh": 300,
    "installation_cost": 4000,
    "electricity_price": 0.18
  }
}

Error Codes
Code	Meaning
200	Success
400	Invalid input
500	Server error
Notes

ROI formulas will be added later.

Use the JSON files in the tests folder for mock input scenarios.