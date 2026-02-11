REQUIRED_REFRIGERATION = ["refrigerator", "freezer", "cold_room"]

def validate_request(data):
    if "business_type" not in data:
        raise ValueError("Missing business_type")

    if "equipment" not in data or not data["equipment"]:
        raise ValueError("Equipment list required")

    has_refrigeration = any(
        e["type"] in REQUIRED_REFRIGERATION for e in data["equipment"]
    )

    if not has_refrigeration:
        raise ValueError("INVALID_EQUIPMENT: refrigeration equipment required")

    for e in data["equipment"]:
        if e["quantity"] <= 0:
            raise ValueError("Equipment quantity must be > 0")
