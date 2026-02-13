## SolarSense AI — Model 3: Financial Viability & ROI

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/) 
[![Flask](https://img.shields.io/badge/Flask-3.x-orange)](https://flask.palletsprojects.com/) 

---

## Project Overview
Model 3 of the **SolarSense AI capstone project** evaluates whether installing a solar energy system is financially viable for a customer.  

It calculates:

- **Monthly savings** from solar energy  
- **Return on Investment (ROI %)**  

The service is exposed as a **REST API** built with **Flask**, allowing integration with other models in the system.

---

## Tech Stack

- Python 3.10+  
- Flask  
- flask-cors  
- flask-limiter  
- REST API  
- JSON input/output  

---

## Repository Structure (Relevant Parts)

```text
Model-1-branch/
├── models/
│   ├── roi_calculation/
│   │   ├── src/
│   │   │   └── app.py          # Flask application and ROI logic
│   │   ├── README.md           # Model 3 (ROI) documentation
│   │   ├── requirements.txt    # Model 3 dependencies
│   │   └── examples.http       # Example HTTP requests
│   └── ...                     # Other models (consumption, generation, etc.)
├── tests/
│   └── roi_calculation/
│       └── test_app.py         # Automated tests for ROI API
└── README.md                   # This file
```

For detailed Model 3 API usage, see `models/roi_calculation/README.md`.

---

## Python & Virtual Environment

- **Required Python version**: **3.10+**

It is strongly recommended to use a virtual environment at the project root.

### Create and Activate Virtual Environment

From the project root:

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

To deactivate the virtual environment:

```bash
deactivate
```

---

## Installing Dependencies

From the project root, install Model 3 dependencies:

```bash
pip install -r models/roi_calculation/requirements.txt
```

If you have a global/shared requirements file for the whole project, install that as usual in addition.

---

## Running the ROI API (Model 3)

From the project root:

```bash
cd models/roi_calculation/src
python app.py
```

The API will start on:

```text
http://0.0.0.0:5000/
```

You can verify it’s running by opening:

```text
GET http://localhost:5000/
```

Expected response:

```json
{
  "message": "Model 3 ROI API running"
}
```

---

## ROI API Endpoint (Current Implementation)

- **Base URL (local)**: `http://localhost:5000`
- **Version prefix**: `/api/v1`

### Endpoint

```text
POST /api/v1/calculate-roi
Content-Type: application/json
```

### Request Body

All fields are **required** and must be **numbers greater than 0**.

```json
{
  "consumption_kwh": 450.0,
  "generation_kwh": 500.0,
  "tariff_per_kwh": 0.20,
  "system_cost_usd": 6000.0
}
```

- `consumption_kwh` > 0 and ≤ 100000  
- `generation_kwh` > 0 and ≤ 100000  
- `tariff_per_kwh` > 0 and ≤ 100  
- `system_cost_usd` > 0 and ≤ 1,000,000  
- Request body size is limited to **100 KB**.

### Successful Response (200)

```json
{
  "monthly_savings_usd": 90.0,
  "roi_percentage": 18.0,
  "system_cost_usd": 6000.0
}
```

> Note: Model 3 **does not compute or return any payback period**. It is purely ROI and savings based.

### Error Responses (Examples)

- **400 – Bad Request**

```json
{ "error": "Request body must be a JSON object" }
```

```json
{ "error": "consumption_kwh must be greater than 0.0" }
```

```json
{ "error": "tariff_per_kwh must be less than or equal to 100.0" }
```

- **413 – Payload Too Large**

```json
{ "error": "Request payload too large" }
```

- **429 – Rate Limit Exceeded**

```json
{ "error": "Rate limit exceeded" }
```

- **500 – Internal Server Error**

```json
{ "error": "Internal server error" }
```

---

## Running Tests

From the project root (`Model-1-branch`), with the virtual environment activated:

```bash
pytest
```

This will discover and run tests under `tests/`, including the comprehensive suite for the ROI API in `tests/roi_calculation/test_app.py`.

---

## Environment Variables

The current ROI service implementation does **not** require any mandatory environment variables for basic local development.  
If you introduce configuration (e.g., for deployment environments, logging, or external services), document them here.

---

## Authors

- Zainabu Mohamed (Model 3 ROI logic & initial API)

Model 3 — Financial Viability & ROI
