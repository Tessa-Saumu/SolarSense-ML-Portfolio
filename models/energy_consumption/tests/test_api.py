import requests

url = "http://127.0.0.1:8001/api/v1/estimate-consumption"

headers = {
    "X-API-KEY": "supersecret123",
    "Content-Type": "application/json"
}

payload = {
    "business_type": "butchery",
    "location": "Lusaka",
    "equipment": [
        {"type": "freezer", "quantity": 2, "daily_operating_hours": 20}
    ]
}

response = requests.post(url, json=payload, headers=headers)

print("Status Code:", response.status_code)
print("Response:", response.json())
