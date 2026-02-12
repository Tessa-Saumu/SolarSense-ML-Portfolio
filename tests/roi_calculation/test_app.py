import math

import pytest

from models.roi_calculation.src.app import create_app, calculate_roi


@pytest.fixture
def app():
    """Create a Flask app instance configured for testing."""
    app = create_app({"TESTING": True})
    return app


@pytest.fixture
def client(app):
    """Flask test client fixture."""
    return app.test_client()


@pytest.fixture
def valid_payload():
    """A valid, representative request payload."""
    return {
        "consumption_kwh": 450.0,
        "generation_kwh": 500.0,
        "tariff_per_kwh": 0.20,
        "system_cost_usd": 6000.0,
    }


def test_home_endpoint_ok(client):
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, dict)
    assert data.get("message") == "Model 3 ROI API running"


def test_calculate_roi_success(client, valid_payload):
    resp = client.post("/api/v1/calculate-roi", json=valid_payload)
    assert resp.status_code == 200
    data = resp.get_json()

    # Response schema
    assert set(data.keys()) == {
        "monthly_savings_usd",
        "roi_percentage",
        "system_cost_usd",
    }

    # Types
    assert isinstance(data["monthly_savings_usd"], (int, float))
    assert isinstance(data["roi_percentage"], (int, float))
    assert isinstance(data["system_cost_usd"], (int, float))

    # Logical consistency with calculation function
    expected = calculate_roi(**valid_payload)
    assert math.isclose(
        data["monthly_savings_usd"],
        expected["monthly_savings_usd"],
        rel_tol=1e-6,
    )
    assert math.isclose(
        data["roi_percentage"],
        expected["roi_percentage"],
        rel_tol=1e-6,
    )
    assert math.isclose(
        data["system_cost_usd"],
        expected["system_cost_usd"],
        rel_tol=1e-6,
    )


def test_malformed_json(client):
    resp = client.post(
        "/api/v1/calculate-roi",
        data="{bad-json",
        content_type="application/json",
    )
    assert resp.status_code == 400
    data = resp.get_json()
    assert data == {"error": "Request body must be a JSON object"}


def test_empty_body(client):
    # No body and no JSON header
    resp = client.post("/api/v1/calculate-roi")
    assert resp.status_code == 400
    assert resp.get_json() == {
        "error": "Request body must be a JSON object"
    }


def test_missing_required_field(client, valid_payload):
    payload = valid_payload.copy()
    payload.pop("system_cost_usd")

    resp = client.post("/api/v1/calculate-roi", json=payload)
    assert resp.status_code == 400
    assert resp.get_json() == {"error": "Missing field: system_cost_usd"}


def test_invalid_type_for_field(client, valid_payload):
    payload = valid_payload.copy()
    payload["tariff_per_kwh"] = "not-a-number"

    resp = client.post("/api/v1/calculate-roi", json=payload)
    assert resp.status_code == 400
    assert resp.get_json() == {"error": "tariff_per_kwh must be a number"}


@pytest.mark.parametrize(
    "field, value, expected_error",
    [
        ("consumption_kwh", 0, "consumption_kwh must be greater than 0.0"),
        ("consumption_kwh", -1, "consumption_kwh must be greater than 0.0"),
        ("generation_kwh", 0, "generation_kwh must be greater than 0.0"),
        ("generation_kwh", -10, "generation_kwh must be greater than 0.0"),
        ("tariff_per_kwh", 0, "tariff_per_kwh must be greater than 0.0"),
        ("tariff_per_kwh", -0.1, "tariff_per_kwh must be greater than 0.0"),
        ("system_cost_usd", 0, "system_cost_usd must be greater than 0.0"),
        ("system_cost_usd", -1000, "system_cost_usd must be greater than 0.0"),
    ],
)
def test_invalid_numeric_ranges_negative_or_zero(
    client, valid_payload, field, value, expected_error
):
    payload = valid_payload.copy()
    payload[field] = value

    resp = client.post("/api/v1/calculate-roi", json=payload)
    assert resp.status_code == 400
    assert resp.get_json() == {"error": expected_error}


@pytest.mark.parametrize(
    "field, value",
    [
        ("consumption_kwh", 100001),
        ("generation_kwh", 100001),
        ("tariff_per_kwh", 101),
        ("system_cost_usd", 1_000_001),
    ],
)
def test_above_max_value_caps(client, valid_payload, field, value):
    payload = valid_payload.copy()
    payload[field] = value

    resp = client.post("/api/v1/calculate-roi", json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "must be less than or equal to" in data["error"]
    assert field in data["error"]


def test_extra_fields_are_ignored(client, valid_payload):
    payload = valid_payload.copy()
    payload["unexpected_field"] = "ignored"

    resp = client.post("/api/v1/calculate-roi", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()

    assert set(data.keys()) == {
        "monthly_savings_usd",
        "roi_percentage",
        "system_cost_usd",
    }


def test_large_but_valid_boundary_values(client):
    payload = {
        "consumption_kwh": 100000.0,
        "generation_kwh": 100000.0,
        "tariff_per_kwh": 100.0,
        "system_cost_usd": 1_000_000.0,
    }

    resp = client.post("/api/v1/calculate-roi", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()

    # Sanity checks for extreme but valid inputs
    assert data["monthly_savings_usd"] > 0
    assert data["roi_percentage"] > 0
    assert data["system_cost_usd"] == pytest.approx(1_000_000.0)


def test_payload_too_large_triggers_413(client):
    # Build a payload significantly larger than 100 KB
    big_string = "x" * (120 * 1024)
    resp = client.post(
        "/api/v1/calculate-roi",
        data=big_string,
        content_type="application/json",
    )
    assert resp.status_code == 413
    assert resp.get_json() == {"error": "Request payload too large"}


def test_rate_limit_exceeded_results_in_429(client, valid_payload):
    # Default limit is 100 per minute; send 101 requests
    last_response = None
    for _ in range(101):
        last_response = client.post("/api/v1/calculate-roi", json=valid_payload)

    assert last_response is not None
    assert last_response.status_code in {200, 429}

    # Ensure at least one 429 occurred
    # (client.history isn't available, so re-send until we hit the limit again)
    resp = client.post("/api/v1/calculate-roi", json=valid_payload)
    assert resp.status_code == 429
    assert resp.get_json() == {"error": "Rate limit exceeded"}


def test_internal_error_returns_generic_500(monkeypatch, client, valid_payload):
    # Force calculate_roi to raise an exception inside the endpoint
    import models.roi_calculation.src.app as app_module

    def boom(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(app_module, "calculate_roi", boom)

    resp = client.post("/api/v1/calculate-roi", json=valid_payload)
    assert resp.status_code == 500
    assert resp.get_json() == {"error": "Internal server error"}


