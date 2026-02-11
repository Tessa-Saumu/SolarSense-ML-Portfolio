"""
Simple test script for the solar_climatology_api Flask service.

This script exercises:
- Valid coordinates (e.g., Mombasa)
- Edge-of-coverage coordinates
- Invalid coordinates (outside SSA bounds)
- All 12 months for a given site

Results are written to outputs/api_test_results.json.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import requests


BASE_URL = "http://localhost:8000"
OUTPUTS_DIR = Path("outputs")
OUTPUTS_DIR.mkdir(exist_ok=True)
RESULTS_PATH = OUTPUTS_DIR / "api_test_results.json"


def call_predict(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Helper to call the /api/v1/predict-generation endpoint."""
    resp = requests.post(f"{BASE_URL}/api/v1/predict-generation", json=payload, timeout=30)
    return {"status_code": resp.status_code, "payload": payload, "response": resp.json()}


def main() -> None:
    results: List[Dict[str, Any]] = []

    # 1. Valid coordinates (Mombasa: -4.0435, 39.6682)
    results.append(
        call_predict({"latitude": -4.0435, "longitude": 39.6682, "include_lifetime": True})
    )

    # 2. Edge case (far south: -25, 28)
    results.append(
        call_predict({"latitude": -25.0, "longitude": 28.0, "include_lifetime": True})
    )

    # 3. Invalid coordinates (outside SSA)
    results.append(
        call_predict({"latitude": -40.0, "longitude": 60.0, "include_lifetime": False})
    )

    # 4. All 12 months for a valid location (e.g., Nairobi)
    for m in range(1, 13):
        results.append(
            call_predict(
                {
                    "latitude": -1.2921,
                    "longitude": 36.8219,
                    "month": m,
                    "include_lifetime": False,
                }
            )
        )

    RESULTS_PATH.write_text(json.dumps(results, indent=2))
    print(f"Saved API test results to {RESULTS_PATH}")


if __name__ == "__main__":
    main()




