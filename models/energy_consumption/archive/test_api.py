import json
from pathlib import Path

from flask.testing import FlaskClient

import sys


def _create_app():
    """
    Helper to import and create the Flask app.

    Assumes tests are run from the repo root or from within models/energy_consumption.
    """
    # Ensure src directory is on sys.path
    base_dir = Path(__file__).resolve().parents[1]
    src_dir = base_dir / "src"
    sys.path.insert(0, str(src_dir))

    from app import create_app  # type: ignore

    return create_app()


def _load_sample_payload(key: str) -> dict:
    base_dir = Path(__file__).resolve().parents[1]
    sample_path = base_dir / "sample_requests.json"
    data = json.loads(sample_path.read_text(encoding="utf-8"))
    return data[key]


def test_health_endpoint():
    app = _create_app()
    client: FlaskClient = app.test_client()

    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body == {"status": "healthy"}


def test_estimate_consumption_butchery_lagos():
    app = _create_app()
    client: FlaskClient = app.test_client()

    payload = _load_sample_payload("butchery_lagos")
    resp = client.post("/api/v1/estimate-consumption", json=payload)

    assert resp.status_code == 200
    body = resp.get_json()

    assert "estimated_consumption_kwh_monthly" in body
    assert "confidence_score" in body
    assert "breakdown" in body
    assert "climate_adjustment_factor" in body
    assert "equipment_summary" in body

    # Refrigeration-heavy heuristic: refrigeration should be at least 50% of total
    total = body["estimated_consumption_kwh_monthly"]
    refrigeration = body["breakdown"]["refrigeration"]
    assert total > 0
    assert refrigeration / total >= 0.5


def test_estimate_consumption_requires_refrigeration():
    app = _create_app()
    client: FlaskClient = app.test_client()

    # Clone a valid payload but strip refrigeration items
    payload = _load_sample_payload("grocery_nairobi")
    payload["equipment"] = [
            e for e in payload["equipment"] if e["type"] not in ["refrigerator", "freezer", "cold_room"]
    ]

    resp = client.post("/api/v1/estimate-consumption", json=payload)
    assert resp.status_code == 400

    body = resp.get_json()
    assert "error" in body
    assert body["error"]["code"] == "INVALID_EQUIPMENT"






