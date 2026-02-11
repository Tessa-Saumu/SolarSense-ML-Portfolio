from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from config import ALLOWED_BUSINESS_TYPES, ALLOWED_EQUIPMENT_TYPES


@dataclass
class ValidationError(Exception):
    code: str
    message: str


def _require_field(data: Dict[str, Any], field: str, field_type: Any) -> Any:
    if field not in data:
        raise ValidationError(
            code="MISSING_FIELD",
            message=f"Missing required field: '{field}'",
        )
    value = data[field]
    if not isinstance(value, field_type):
        raise ValidationError(
            code="INVALID_FIELD_TYPE",
            message=f"Field '{field}' has invalid type",
        )
    return value


def _validate_business_type(value: str) -> str:
    bt = value.strip().lower()
    if bt not in ALLOWED_BUSINESS_TYPES:
        raise ValidationError(
            code="INVALID_BUSINESS_TYPE",
            message=f"Invalid business_type '{value}'. Allowed: {', '.join(ALLOWED_BUSINESS_TYPES)}",
        )
    return bt


def _validate_operating_hours(value: Any) -> int:
    try:
        hours = int(value)
    except (TypeError, ValueError):
        raise ValidationError(
            code="INVALID_OPERATING_HOURS",
            message="operating_hours must be an integer between 1 and 24",
        )
    if hours < 1 or hours > 24:
        raise ValidationError(
            code="INVALID_OPERATING_HOURS",
            message="operating_hours must be between 1 and 24",
        )
    return hours


def _validate_equipment_list(
    equipment: Any, business_type: str
) -> List[Dict[str, Any]]:
    if not isinstance(equipment, list) or len(equipment) == 0:
        raise ValidationError(
            code="INVALID_EQUIPMENT",
            message="Equipment must be a non-empty list",
        )

    sanitized: List[Dict[str, Any]] = []
    has_refrigeration = False

    for idx, item in enumerate(equipment):
        if not isinstance(item, dict):
            raise ValidationError(
                code="INVALID_EQUIPMENT",
                message=f"Equipment item at index {idx} must be an object",
            )

        eq_type_raw = item.get("type")
        if not isinstance(eq_type_raw, str):
            raise ValidationError(
                code="INVALID_EQUIPMENT",
                message=f"Equipment item at index {idx} is missing a valid 'type'",
            )
        eq_type = eq_type_raw.strip().lower()
        if eq_type not in ALLOWED_EQUIPMENT_TYPES:
            raise ValidationError(
                code="INVALID_EQUIPMENT",
                message=f"Unsupported equipment type '{eq_type_raw}' at index {idx}. "
                f"Allowed: {', '.join(ALLOWED_EQUIPMENT_TYPES)}",
            )

        quantity_raw = item.get("quantity", 1)
        try:
            quantity = int(quantity_raw)
        except (TypeError, ValueError):
            raise ValidationError(
                code="INVALID_EQUIPMENT",
                message=f"'quantity' for equipment index {idx} must be an integer between 1 and 50",
            )
        if quantity < 1 or quantity > 50:
            raise ValidationError(
                code="INVALID_EQUIPMENT",
                message=f"'quantity' for equipment index {idx} must be between 1 and 50",
            )

        size_capacity = item.get("size_capacity")
        if size_capacity is not None and not isinstance(size_capacity, str):
            raise ValidationError(
                code="INVALID_EQUIPMENT",
                message=f"'size_capacity' for equipment index {idx} must be a string like '500L' or '50m2'",
            )

        hours_raw = item.get("daily_operating_hours", None)
        if hours_raw is None:
            daily_hours = None  # will fall back to business operating hours
        else:
            try:
                daily_hours = int(hours_raw)
            except (TypeError, ValueError):
                raise ValidationError(
                    code="INVALID_EQUIPMENT",
                    message=f"'daily_operating_hours' for equipment index {idx} must be an integer between 1 and 24",
                )
            if daily_hours < 1 or daily_hours > 24:
                raise ValidationError(
                    code="INVALID_EQUIPMENT",
                    message=f"'daily_operating_hours' for equipment index {idx} must be between 1 and 24",
                )

        if eq_type in ["refrigerator", "freezer", "cold_room"]:
            has_refrigeration = True

        sanitized.append(
            {
                "type": eq_type,
                "quantity": quantity,
                "size_capacity": size_capacity,
                "daily_operating_hours": daily_hours,
            }
        )

    # Refrigeration requirement (refrigerator/freezer/cold_room)
    if not has_refrigeration:
        # Tailored message for refrigeration-first business types
        if business_type in ["butchery", "grocery", "mini-supermarket"]:
            msg = (
                "Refrigeration equipment (refrigerator/freezer/cold_room) "
                "required for this business type"
            )
        else:
            msg = "At least one refrigeration equipment item required"
        raise ValidationError(
            code="INVALID_EQUIPMENT",
            message=msg,
        )

    return sanitized


def validate_request_payload(payload: Any) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValidationError(
            code="INVALID_PAYLOAD",
            message="Request body must be a JSON object",
        )

    business_type_raw = _require_field(payload, "business_type", str)
    business_type = _validate_business_type(business_type_raw)

    operating_hours_raw = _require_field(payload, "operating_hours", (int, float, str))
    operating_hours = _validate_operating_hours(operating_hours_raw)

    equipment_raw = payload.get("equipment")
    equipment = _validate_equipment_list(equipment_raw, business_type)

    location_raw = payload.get("location", "")
    if not isinstance(location_raw, str):
        raise ValidationError(
            code="INVALID_LOCATION",
            message="location must be a string like 'Lagos, Nigeria'",
        )
    location = location_raw.strip()

    return {
        "business_type": business_type,
        "operating_hours": operating_hours,
        "equipment": equipment,
        "location": location,
    }



