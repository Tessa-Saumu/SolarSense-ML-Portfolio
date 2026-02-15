 # SolarSense AI — Model 3: Financial Viability & ROI

[![Python](https://img.shields.io/badge/Python-3.x-blue)](https://www.python.org/) 
[![Flask](https://img.shields.io/badge/Flask-2.x-orange)](https://flask.palletsprojects.com/) 

---

## Project Overview
Model 3 of the **SolarSense AI capstone project** evaluates whether installing a solar energy system is financially viable for a customer.  

It calculates:

- **Monthly savings** from solar energy  
- **Annual savings**  
- **Return on Investment (ROI %)**  
- **Payback period** in years  
- **Financial viability classification**

The service is exposed as a **REST API** built with **Flask**, allowing integration with other models in the system.

---

## What This Service Does
Given:

- Cost of installing the solar system  
- Monthly electricity consumption  
- Monthly solar energy generation  
- Electricity tariff per kWh  

The API returns:

- Monthly savings (USD)  
- Annual savings (USD)  
- ROI percentage  
- Payback period (years)  
- Viability label:  
  - **Highly Viable**  
  - **Moderately Viable**  
  - **Not Viable**

---

## Tech Stack

- Python 3  
- Flask  
- flask-cors  
- REST API  
- JSON input/output  

---

## Project Structure


    model_roi_api/
    │
    ├── app.py          # Flask application and ROI logic
    ├── README.md       # Project documentation


---

## How to Run the Project

1. Clone or download the repository

2. Install dependencies
   
   **pip install flask flask-cors**
#### OR
   **python -m pip install flask flask-cors**
  
3. Start the server
 - **python app.py**
 - You should see:- *Running on http://127.0.0.1:5000*

4. Test the API
    - Open your browser and go to:-
          http://127.0.0.1:5000/
   - You should see:- 
        *{"message":"Model 3 ROI API running"}*
---

## API ENDPOINT
This endpoint calculates the financial metrics:-
POST /calculate-roi

    1. Request Format(JSON)
                {
        "system_cost": 12000,
        "monthly_consumption": 1200,
        "monthly_generation": 1800,
        "tariff": 0.2
                }
    2. Field Description
  | Field             | Description                              |
| ------------------- | ---------------------------------------- |
| system_cost         | Total installation cost (USD)            |
| monthly_consumption | Energy used per month (kWh)              |
| monthly_generation  | Energy produced by solar per month (kWh) |
| tariff              | Electricity price per kWh (USD)          |

    3. Successful Response Sample
         {
        "monthly_savings_usd": 240.0,
        "annual_savings_usd": 2880.0,
        "roi_percentage": 24.0,
        "payback_years": 4.17,
        "viability": "Highly Viable"
        }

    4. Error Handling
        Missing Field:- 
        {"error": "Missing field: system_cost"}
        Invalid Inputs:- 
        {"error": "system_cost must be greater than 0"}
        # OR
        {"error": "monthly_consumption and monthly_generation cannot be negative"}

## CALCULATION LOGIC
- Energy offset = min(consumption, generation)
- Monthly savings = energy offset × tariff
- Annual savings = monthly savings × 12
- ROI (%) = (annual savings ÷ system cost) × 100
- Payback years = system cost ÷ annual savings


## VIABILITY RULES:-
- ROI > 20% → Highly Viable
- ROI ≥ 10% → Moderately Viable
- ROI < 10% → Not Viable
---

## INTEGRATION GUIDE FOR OTHER MODELS
    1. Endpoint
    **POST /calculate-roi**

    2. Expected Input
         {
    "system_cost": 12000,
    "monthly_consumption": 1200,
    "monthly_generation": 1800,
    "tariff": 0.2
           }

    3. Expected Output
        {
    "monthly_savings_usd": 240.0,
    "annual_savings_usd": 2880.0,
    "roi_percentage": 24.0,
    "payback_years": 4.17,
    "viability": "Highly Viable"
        }


    4.Output Interpretation

|   Field             | Meaning                      |
| ------------------- | ------------------------------ |
| monthly_savings_usd | Estimated monthly cost savings |
| annual_savings_usd  | Estimated yearly savings       |
| roi_percentage      | Annual ROI percentage          |
| payback_years       | Years to recover system cost   |
| viability           | Financial classification       |


    5. Status Code
        200 OK – Calculation successful
        400 Bad Request – Missing or invalid inputs

---

## AUTHOR
Zainabu Mohamed
---
Model 3 — Financial Viability & ROI
