from typing import Any, Dict, List, Tuple

from config import (
    EQUIPMENT_POWER_WATTS,
    DEFAULT_TYPE_POWER_WATTS,
    CLIMATE_ZONES,
    DEFAULT_CLIMATE_FACTOR,
    DAYS_PER_MONTH,
)


def _infer_equipment_key(equipment_type: str, size_capacity: str | None) -> Tuple[str, int]:
    """
    Infer the equipment key and fallback power rating based on type and size/capacity.
    Returns (equipment_key, default_power_for_type).
    """
    equipment_type = equipment_type.lower()
    size_capacity = (size_capacity or "").strip().lower()

    # Normalize simple capacities like "500l" or "50m2"
    normalized_capacity = size_capacity.replace(" ", "")

    if equipment_type in ["refrigerator", "freezer"]:
        if "500l" in normalized_capacity:
            key = f"{equipment_type}_500L"
        elif "1000l" in normalized_capacity or "1,000l" in normalized_capacity:
            key = f"{equipment_type}_1000L"
        elif "2000l" in normalized_capacity or "2,000l" in normalized_capacity:
            key = f"{equipment_type}_2000L"
        else:
            key = f"{equipment_type}_1000L"
    elif equipment_type == "cold_room":
        if "50m2" in normalized_capacity:
            key = "cold_room_50m2"
        elif "100m2" in normalized_capacity:
            key = "cold_room_100m2"
        else:
            key = "cold_room_50m2"
    elif equipment_type == "lights":
        if "small" in normalized_capacity or "low" in normalized_capacity:
            key = "lights_small"
        elif "large" in normalized_capacity or "high" in normalized_capacity:
            key = "lights_large"
        else:
            key = "lights_medium"
    elif equipment_type == "hvac":
        if "small" in normalized_capacity:
            key = "hvac_small"
        elif "large" in normalized_capacity:
            key = "hvac_large"
        else:
            key = "hvac_medium"
    elif equipment_type == "pos":
        key = "pos"
    else:
        # Unknown type: return a generic key and 0 to force fallback
        key = equipment_type

    default_power = DEFAULT_TYPE_POWER_WATTS.get(equipment_type, 100)
    return key, default_power


def _get_climate_factor(location: str) -> float:
    if not location:
        return DEFAULT_CLIMATE_FACTOR

    for city, factor in CLIMATE_ZONES.items():
        if city.lower() in location.lower():
            return factor
    return DEFAULT_CLIMATE_FACTOR


def estimate_energy_consumption(
    business_type: str,
    operating_hours: int,
    equipment: List[Dict[str, Any]],
    location: str,
) -> Dict[str, Any]:
    """
    Core formula-based estimation logic.
    """
    total_kwh = 0.0
    refrigeration_kwh = 0.0
    lighting_kwh = 0.0
    hvac_kwh = 0.0
    other_kwh = 0.0

    total_refrigeration_units = 0
    total_other_units = 0

    # Track how complete the equipment specification is for confidence score
    specified_items = 0
    total_items = len(equipment)

    for item in equipment:
        eq_type = str(item.get("type", "")).lower()
        size_capacity = item.get("size_capacity")
        quantity = int(item.get("quantity", 1))
        hours = int(item.get("daily_operating_hours", operating_hours))

        equipment_key, default_power = _infer_equipment_key(eq_type, size_capacity)
        power_watts = EQUIPMENT_POWER_WATTS.get(equipment_key, default_power)

        monthly_kwh = (power_watts * quantity * hours * DAYS_PER_MONTH) / 1000.0
        total_kwh += monthly_kwh

        if eq_type in ["refrigerator", "freezer", "cold_room"]:
            refrigeration_kwh += monthly_kwh
            total_refrigeration_units += quantity
        elif eq_type == "lights":
            lighting_kwh += monthly_kwh
            total_other_units += quantity
        elif eq_type == "hvac":
            hvac_kwh += monthly_kwh
            total_other_units += quantity
        else:
            other_kwh += monthly_kwh
            total_other_units += quantity

        # Consider item "well specified" if it has quantity and size/hours
        if item.get("quantity") and item.get("daily_operating_hours") and item.get("size_capacity"):
            specified_items += 1

    # Apply climate adjustment for refrigeration-heavy loads
    climate_factor = _get_climate_factor(location)
    total_kwh *= climate_factor
    refrigeration_kwh *= climate_factor
    lighting_kwh *= climate_factor
    hvac_kwh *= climate_factor
    other_kwh *= climate_factor

    # Enforce refrigeration-first share heuristics for key business types
    refrigeration_share = refrigeration_kwh / total_kwh if total_kwh > 0 else 0.0
    if business_type in ["butchery", "grocery", "mini-supermarket"]:
        target_min = 0.5
        target_max = 0.7
        if refrigeration_share < target_min and total_kwh > 0:
            # Boost refrigeration portion up towards target_min while keeping total the same
            boost_factor = target_min / max(refrigeration_share, 0.01)
            boosted_refrigeration = refrigeration_kwh * boost_factor
            scale = (total_kwh - refrigeration_kwh) / max(total_kwh - boosted_refrigeration, 0.01)
            refrigeration_kwh = boosted_refrigeration
            # Scale non-refrigeration categories down proportionally
            lighting_kwh *= scale
            hvac_kwh *= scale
            other_kwh *= scale
            total_kwh = refrigeration_kwh + lighting_kwh + hvac_kwh + other_kwh

    # Simple confidence score heuristic
    base_confidence = 0.7
    if total_items > 0:
        completeness_bonus = 0.2 * (specified_items / total_items)
    else:
        completeness_bonus = 0.0

    # Slight bump for having refrigeration units
    if total_refrigeration_units > 0:
        completeness_bonus += 0.05

    confidence_score = min(0.95, base_confidence + completeness_bonus)

    return {
        "estimated_consumption_kwh_monthly": round(total_kwh, 2),
        "confidence_score": round(confidence_score, 2),
        "breakdown": {
            "refrigeration": round(refrigeration_kwh, 2),
            "lighting": round(lighting_kwh, 2),
            "hvac": round(hvac_kwh, 2),
            "other": round(other_kwh, 2),
        },
        "climate_adjustment_factor": round(climate_factor, 2),
        "equipment_summary": {
            "total_refrigeration_units": total_refrigeration_units,
            "total_other_equipment": total_other_units,
        },
    }


