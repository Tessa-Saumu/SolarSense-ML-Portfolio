from config import EQUIPMENT_POWER_RATINGS, HOT_CLIMATE_CITIES

def estimate_consumption(data):
    total_kwh = 0

    for item in data["equipment"]:
        power = EQUIPMENT_POWER_RATINGS.get(item["type"], 0.1)
        total_kwh += power * item["quantity"] * item.get("daily_operating_hours", 8) * 30

    city = data.get("location")

    if city in HOT_CLIMATE_CITIES:
        total_kwh *= 1.15

    confidence = 0.7 if total_kwh > 0 else 0.3

    return {
        "estimated_kwh": round(total_kwh, 2),
        "confidence_score": confidence
    }
