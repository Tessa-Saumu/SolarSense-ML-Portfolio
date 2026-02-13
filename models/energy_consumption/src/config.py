from typing import Dict

# Allowed business types
ALLOWED_BUSINESS_TYPES = [
    "butchery",
    "grocery",
    "mini-supermarket",
    "cold_storage",
    "food_retail",
]

# Allowed equipment types
ALLOWED_EQUIPMENT_TYPES = [
    "refrigerator",
    "freezer",
    "cold_room",
    "lights",
    "pos",
    "hvac",
]

# Days per month to use for monthly estimate
DAYS_PER_MONTH = 30

# Equipment power ratings in Watts.
# These are approximate MVP values and can be refined with better data.
EQUIPMENT_POWER_WATTS: Dict[str, int] = {
    # Refrigeration (refrigeration-first focus)
    "refrigerator_500L": 150,
    "refrigerator_1000L": 250,
    "refrigerator_2000L": 350,
    "freezer_500L": 200,
    "freezer_1000L": 350,
    "freezer_2000L": 450,
    "cold_room_50m2": 5000,
    "cold_room_100m2": 8000,
    # Lighting
    "lights_small": 40,
    "lights_medium": 80,
    "lights_large": 150,
    # POS and small electronics
    "pos": 30,
    # HVAC
    "hvac_small": 1500,
    "hvac_medium": 2500,
    "hvac_large": 3500,
}

# Default fallback ratings for equipment types if size/capacity is unknown
DEFAULT_TYPE_POWER_WATTS: Dict[str, int] = {
    "refrigerator": 200,
    "freezer": 300,
    "cold_room": 6000,
    "lights": 60,
    "pos": 30,
    "hvac": 2000,
}

# Climate adjustment factors based on representative African cities.
# Values reflect increased cooling loads in hot/humid regions.
CLIMATE_ZONES: Dict[str, float] = {
    # Hot / humid (25–40% increase)
    "Lagos": 1.35,
    "Accra": 1.30,
    "Dar es Salaam": 1.35,
    "Kinshasa": 1.35,
    "Abidjan": 1.30,
    "Douala": 1.30,
    "Luanda": 1.30,
    "Maputo": 1.28,
    # Moderate (15–25% increase)
    "Nairobi": 1.20,
    "Johannesburg": 1.18,
    "Kigali": 1.18,
    "Addis Ababa": 1.20,
    "Cape Town": 1.18,
    "Gaborone": 1.18,
}

# Default climate factor when we cannot infer city from the location string
DEFAULT_CLIMATE_FACTOR = 1.20


