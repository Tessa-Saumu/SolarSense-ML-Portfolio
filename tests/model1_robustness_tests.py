"""
Model 1 robustness tests: Energy Consumption ML API.

Runs a suite of edge-case requests against:
POST /api/v1/estimate-consumption

Outputs:
- Console summary table
- model1_robustness_report.json

Usage (API running on production or override with env var):
    python model1_robustness_tests.py
    python model1_robustness_tests.py --base-url https://dse-models-production.up.railway.app --out my_report.json
    
    # For local testing:
    export MODEL1_BASE_URL=http://localhost:8000
    python model1_robustness_tests.py
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import requests


# -----------------------------
# Config (edit these if needed)
# -----------------------------

BASE_URL = os.getenv("MODEL1_BASE_URL", "https://dse-models-production.up.railway.app")
ENDPOINT_PATH = "/api/v1/estimate-consumption"
TIMEOUT_SECONDS = 10

# Auth is required by the Model 1 service.
# Set API_KEY in your environment, or it falls back to the default test key.
API_KEY = os.getenv("API_KEY") or "QfBmvo3htYQPSJWYYLcChxXvZonTuC2U"

# "Acceptable" definition for successful responses:
# - HTTP 200
# - plausible monthly kWh value in [0, 1_000_000]
KWH_LOWER_INCLUSIVE = 0.0
KWH_UPPER_INCLUSIVE = 1_000_000.0


_NO_JSON_BODY = object()


@dataclass(frozen=True)
class TestCase:
    id: str
    category: str
    name: str
    payload: Union[Dict[str, Any], object]
    expected_status: Optional[int]          # None means "don't assert exact code"
    expected_error_code: Optional[str]      # e.g. "UNAUTHORIZED", "MISSING_FIELD"
    expectation: str                        # "accept" | "reject"
    tags: Tuple[str, ...] = ()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _join_url(base_url: str, path: str) -> str:
    return base_url.rstrip("/") + path


def _build_headers(include_auth: bool = True) -> Dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if include_auth and API_KEY:
        headers["X-API-KEY"] = API_KEY
    return headers


def _safe_json(response: requests.Response) -> Tuple[Optional[Any], Optional[str]]:
    try:
        return response.json(), None
    except Exception as e:
        text = None
        try:
            text = response.text
        except Exception:
            text = None
        err = f"invalid_json_response: {type(e).__name__}: {e}"
        if text:
            err += f" | body_prefix={text[:400]!r}"
        return None, err


def _extract_kwh(resp_json: Any) -> Optional[float]:
    if not isinstance(resp_json, dict):
        return None
    v = resp_json.get("estimated_consumption_kwh_monthly")
    if isinstance(v, (int, float)):
        return float(v)
    return None


def _is_plausible_kwh(kwh: float) -> bool:
    return KWH_LOWER_INCLUSIVE <= kwh <= KWH_UPPER_INCLUSIVE


def _evaluate(
    test: TestCase,
    status_code: Optional[int],
    resp_json: Any,
    request_error: Optional[str],
    json_error: Optional[str],
) -> Tuple[bool, Optional[str]]:
    """Return (passed, failure_mode)."""
    if request_error:
        return False, request_error
    if json_error and test.expectation == "accept":
        return False, json_error

    if test.expectation == "reject":
        # Pass if we got a non-200 HTTP status
        if status_code is not None and status_code != 200:
            # Optionally check expected_status and expected_error_code
            if test.expected_status is not None and status_code != test.expected_status:
                return False, f"wrong_status_code(expected={test.expected_status},got={status_code})"
            if test.expected_error_code is not None:
                actual_code = None
                if isinstance(resp_json, dict):
                    actual_code = (resp_json.get("error") or {}).get("code")
                if actual_code != test.expected_error_code:
                    return False, f"wrong_error_code(expected={test.expected_error_code},got={actual_code})"
            return True, None
        return False, "expected_rejection_but_got_200"

    # expectation == "accept"
    if status_code != 200:
        return False, f"status_not_200(got={status_code})"
    if resp_json is None:
        return False, "missing_json_body"
    kwh = _extract_kwh(resp_json)
    if kwh is None:
        return False, "missing_kwh_field"
    if not _is_plausible_kwh(kwh):
        return False, f"kwh_out_of_range({kwh})"
    return True, None


def _run_test_case(test: TestCase, base_url: str) -> Dict[str, Any]:
    url = _join_url(base_url, ENDPOINT_PATH)

    # Some auth tests deliberately omit or send wrong key
    if test.tags and "no_auth" in test.tags:
        headers = {"Content-Type": "application/json"}
    elif test.tags and "wrong_auth" in test.tags:
        headers = {"Content-Type": "application/json", "X-API-KEY": "wrong-key"}
    elif test.tags and "no_content_type" in test.tags:
        headers = {"X-API-KEY": API_KEY} if API_KEY else {}
    else:
        headers = _build_headers(include_auth=True)

    started = time.time()
    status_code: Optional[int] = None
    resp_text: Optional[str] = None
    resp_json: Any = None
    request_error: Optional[str] = None
    json_error: Optional[str] = None

    try:
        if test.payload is _NO_JSON_BODY:
            resp = requests.post(url, headers=headers, timeout=TIMEOUT_SECONDS)
        elif test.tags and "no_content_type" in test.tags:
            # Send as raw data without Content-Type: application/json
            resp = requests.post(
                url,
                data=json.dumps(test.payload),
                headers=headers,
                timeout=TIMEOUT_SECONDS,
            )
        elif test.tags and "malformed_json" in test.tags:
            resp = requests.post(
                url,
                data="{ invalid json }",
                headers=headers,
                timeout=TIMEOUT_SECONDS,
            )
        elif test.tags and "empty_body" in test.tags:
            resp = requests.post(
                url,
                data="",
                headers=headers,
                timeout=TIMEOUT_SECONDS,
            )
        else:
            resp = requests.post(url, headers=headers, json=test.payload, timeout=TIMEOUT_SECONDS)
        status_code = resp.status_code
        try:
            resp_text = resp.text
        except Exception:
            resp_text = None
        resp_json, json_error = _safe_json(resp)
    except requests.exceptions.Timeout:
        request_error = f"timeout_after_{TIMEOUT_SECONDS}s"
    except requests.exceptions.ConnectionError as e:
        request_error = f"connection_error: {e}"
    except requests.exceptions.RequestException as e:
        request_error = f"request_exception: {type(e).__name__}: {e}"

    elapsed_ms = int((time.time() - started) * 1000)

    passed, failure_mode = _evaluate(test, status_code, resp_json, request_error, json_error)

    extracted_kwh = _extract_kwh(resp_json) if resp_json is not None else None

    resp_text_capped = None
    if resp_text is not None:
        resp_text_capped = resp_text if len(resp_text) <= 20_000 else (resp_text[:20_000] + "\n...<truncated>...")

    return {
        "id": test.id,
        "category": test.category,
        "name": test.name,
        "tags": list(test.tags),
        "request": {
            "url": url,
            "headers_sent": {
                "Content-Type": "application/json",
                **({"X-API-KEY": "***set***"} if API_KEY and "no_auth" not in (test.tags or ()) and "wrong_auth" not in (test.tags or ()) else {}),
            },
            "payload_sent": None if test.payload is _NO_JSON_BODY else test.payload,
            "timeout_seconds": TIMEOUT_SECONDS,
        },
        "response": {
            "status_code": status_code,
            "json": resp_json,
            "text": resp_text_capped,
        },
        "evaluation": {
            "expectation": test.expectation,
            "expected_status": test.expected_status,
            "expected_error_code": test.expected_error_code,
            "extracted_kwh_monthly": extracted_kwh,
            "passed": passed,
            "failure_mode": failure_mode,
        },
        "timing": {"elapsed_ms": elapsed_ms, "started_at": _now_iso()},
    }


def _fmt_bool(v: bool) -> str:
    return "PASS" if v else "FAIL"


def _print_summary_table(results: List[Dict[str, Any]]) -> None:
    rows: List[List[str]] = []
    for i, r in enumerate(results, start=1):
        status = r["response"]["status_code"]
        status_s = str(status) if status is not None else "-"
        passed = bool(r["evaluation"]["passed"])
        failure = r["evaluation"]["failure_mode"] or ""
        rows.append([str(i), r["category"], r["name"], status_s, _fmt_bool(passed), failure])

    headers = ["#", "Category", "Test", "HTTP", "Result", "Failure mode"]
    widths = [len(h) for h in headers]
    for row in rows:
        for j, cell in enumerate(row):
            widths[j] = max(widths[j], len(cell))

    def fmt_row(row: List[str]) -> str:
        return " | ".join(cell.ljust(widths[j]) for j, cell in enumerate(row))

    def line() -> str:
        return "-+-".join("-" * (w + 0) for w in widths)

    print(fmt_row(headers))
    print(line())
    for row in rows:
        print(fmt_row(row))

    total = len(results)
    passed_n = sum(1 for r in results if r["evaluation"]["passed"])
    print()
    print(f"Total: {total} | Passed: {passed_n} | Failed: {total - passed_n}")


# ---------------------------------------------------------------------------
# Valid base payload used as baseline for many tests
# ---------------------------------------------------------------------------
VALID_PAYLOAD: Dict[str, Any] = {
    "business_type": "butchery",
    "sqft_m2": 60,
    "operating_hours_weekly": 98,
    "num_refrigeration_units": 3,
    "location": "Lagos, Nigeria",
}

BASELINE_PAYLOAD: Dict[str, Any] = {
    "business_type": "butchery",
    "sqft_m2": 60,
    "operating_hours_weekly": 98,
    "num_refrigeration_units": 3,
    "location": "Lagos, Nigeria",
}


def _make_test_cases() -> List[TestCase]:
    cases: List[TestCase] = []

    def add(
        *,
        category: str,
        name: str,
        payload: Union[Dict[str, Any], object],
        expectation: str,
        expected_status: Optional[int] = None,
        expected_error_code: Optional[str] = None,
        tags: Tuple[str, ...] = (),
    ) -> None:
        cases.append(
            TestCase(
                id=f"{len(cases) + 1:03d}",
                category=category,
                name=name,
                payload=payload,
                expectation=expectation,
                expected_status=expected_status,
                expected_error_code=expected_error_code,
                tags=tags,
            )
        )

    # =========================================================================
    # GROUP 1 — Authentication & Security
    # =========================================================================

    add(
        category="Authentication & Security",
        name="missing API key → 401 UNAUTHORIZED",
        payload=VALID_PAYLOAD,
        expectation="reject",
        expected_status=401,
        expected_error_code="UNAUTHORIZED",
        tags=("auth", "no_auth"),
    )
    add(
        category="Authentication & Security",
        name="wrong API key → 401 UNAUTHORIZED",
        payload=VALID_PAYLOAD,
        expectation="reject",
        expected_status=401,
        expected_error_code="UNAUTHORIZED",
        tags=("auth", "wrong_auth"),
    )
    add(
        category="Authentication & Security",
        name="correct API key → not 401",
        payload=VALID_PAYLOAD,
        expectation="accept",
        tags=("auth",),
    )
    add(
        category="Authentication & Security",
        name="health endpoint requires no auth → 200",
        # Health endpoint is GET; we handle it specially in _run_test_case by skipping the normal POST
        # We mark it with a special tag and handle below in the runner override
        payload=_NO_JSON_BODY,
        expectation="accept",
        tags=("health_check",),
    )

    # =========================================================================
    # GROUP 2 — Content Type & JSON Validation
    # =========================================================================

    add(
        category="Content Type & JSON Validation",
        name="no Content-Type header → 415 INVALID_CONTENT_TYPE",
        payload=VALID_PAYLOAD,
        expectation="reject",
        expected_status=415,
        expected_error_code="INVALID_CONTENT_TYPE",
        tags=("content_type", "no_content_type"),
    )
    add(
        category="Content Type & JSON Validation",
        name="malformed JSON body → 500 PREDICTION_ERROR",
        payload=VALID_PAYLOAD,
        expectation="reject",
        expected_status=500,
        expected_error_code="PREDICTION_ERROR",
        tags=("json_validation", "malformed_json"),
    )
    add(
        category="Content Type & JSON Validation",
        name="empty body with correct Content-Type → 500 PREDICTION_ERROR",
        payload=VALID_PAYLOAD,
        expectation="reject",
        expected_status=500,
        expected_error_code="PREDICTION_ERROR",
        tags=("json_validation", "empty_body"),
    )

    # =========================================================================
    # GROUP 3 — Missing Required Fields
    # =========================================================================

    for missing_field, partial in [
        ("business_type", {"sqft_m2": 60, "operating_hours_weekly": 98, "num_refrigeration_units": 3, "location": "Lagos, Nigeria"}),
        ("sqft_m2", {"business_type": "butchery", "operating_hours_weekly": 98, "num_refrigeration_units": 3, "location": "Lagos, Nigeria"}),
        ("operating_hours_weekly", {"business_type": "butchery", "sqft_m2": 60, "num_refrigeration_units": 3, "location": "Lagos, Nigeria"}),
        ("num_refrigeration_units", {"business_type": "butchery", "sqft_m2": 60, "operating_hours_weekly": 98, "location": "Lagos, Nigeria"}),
        ("location", {"business_type": "butchery", "sqft_m2": 60, "operating_hours_weekly": 98, "num_refrigeration_units": 3}),
    ]:
        add(
            category="Missing Required Fields",
            name=f"missing {missing_field} → 400 MISSING_REQUIRED_FIELDS",
            payload=partial,
            expectation="reject",
            expected_status=400,
            expected_error_code="MISSING_REQUIRED_FIELDS",
            tags=("missing_field",),
        )

    # =========================================================================
    # GROUP 4 — Invalid Field Types
    # =========================================================================

    add(
        category="Invalid Field Types",
        name="sqft_m2 as numeric string '100' → accepted (coercion)",
        payload={**VALID_PAYLOAD, "sqft_m2": "100"},
        expectation="accept",
        expected_status=200,
        expected_error_code=None,
        tags=("type_coercion",),
    )
    add(
        category="Invalid Field Types",
        name="operating_hours_weekly as numeric string '80' → accepted (coercion)",
        payload={**VALID_PAYLOAD, "operating_hours_weekly": "80"},
        expectation="accept",
        expected_status=200,
        expected_error_code=None,
        tags=("type_coercion",),
    )
    add(
        category="Invalid Field Types",
        name="num_refrigeration_units as numeric string '3' → accepted (coercion)",
        payload={**VALID_PAYLOAD, "num_refrigeration_units": "3"},
        expectation="accept",
        expected_status=200,
        expected_error_code=None,
        tags=("type_coercion",),
    )
    add(
        category="Invalid Field Types",
        name="location as integer → accepted (coerced to string)",
        payload={**VALID_PAYLOAD, "location": 12345},
        expectation="accept",
        expected_status=200,
        expected_error_code=None,
        tags=("type_coercion",),
    )
    add(
        category="Invalid Field Types",
        name="business_type as integer → 400 INVALID_BUSINESS_TYPE",
        payload={**VALID_PAYLOAD, "business_type": 123},
        expectation="reject",
        expected_status=400,
        expected_error_code="INVALID_BUSINESS_TYPE",
        tags=("type_error",),
    )

    # =========================================================================
    # GROUP 5 — Boundary / Range Validation
    # =========================================================================

    add(
        category="Boundary / Range Validation",
        name="sqft_m2 = 0 → 400 INVALID_FIELD_VALUE",
        payload={**VALID_PAYLOAD, "sqft_m2": 0},
        expectation="reject",
        expected_status=400,
        expected_error_code="INVALID_FIELD_VALUE",
        tags=("boundary",),
    )
    add(
        category="Boundary / Range Validation",
        name="sqft_m2 = -1 → 400 INVALID_FIELD_VALUE",
        payload={**VALID_PAYLOAD, "sqft_m2": -1},
        expectation="reject",
        expected_status=400,
        expected_error_code="INVALID_FIELD_VALUE",
        tags=("boundary",),
    )
    add(
        category="Boundary / Range Validation",
        name="sqft_m2 = 0.001 → 200 (just above zero)",
        payload={**VALID_PAYLOAD, "sqft_m2": 0.001},
        expectation="accept",
        tags=("boundary",),
    )
    add(
        category="Boundary / Range Validation",
        name="sqft_m2 = 10000 → 200 (at max)",
        payload={**VALID_PAYLOAD, "sqft_m2": 10000},
        expectation="accept",
        tags=("boundary",),
    )
    add(
        category="Boundary / Range Validation",
        name="sqft_m2 = 10001 → 400 INVALID_FIELD_VALUE",
        payload={**VALID_PAYLOAD, "sqft_m2": 10001},
        expectation="reject",
        expected_status=400,
        expected_error_code="INVALID_FIELD_VALUE",
        tags=("boundary",),
    )
    add(
        category="Boundary / Range Validation",
        name="operating_hours_weekly = 0 → 400",
        payload={**VALID_PAYLOAD, "operating_hours_weekly": 0},
        expectation="reject",
        expected_status=400,
        tags=("boundary",),
    )
    add(
        category="Boundary / Range Validation",
        name="operating_hours_weekly = 168 → 200 (at max)",
        payload={**VALID_PAYLOAD, "operating_hours_weekly": 168},
        expectation="accept",
        tags=("boundary",),
    )
    add(
        category="Boundary / Range Validation",
        name="operating_hours_weekly = 168.1 → 400",
        payload={**VALID_PAYLOAD, "operating_hours_weekly": 168.1},
        expectation="reject",
        expected_status=400,
        tags=("boundary",),
    )
    add(
        category="Boundary / Range Validation",
        name="num_refrigeration_units = 0 → 200 (valid)",
        payload={**VALID_PAYLOAD, "num_refrigeration_units": 0},
        expectation="accept",
        tags=("boundary",),
    )
    add(
        category="Boundary / Range Validation",
        name="num_refrigeration_units = 500 → 200 (at max)",
        payload={**VALID_PAYLOAD, "num_refrigeration_units": 500},
        expectation="accept",
        tags=("boundary",),
    )
    add(
        category="Boundary / Range Validation",
        name="num_refrigeration_units = 501 → 400",
        payload={**VALID_PAYLOAD, "num_refrigeration_units": 501},
        expectation="reject",
        expected_status=400,
        tags=("boundary",),
    )
    add(
        category="Boundary / Range Validation",
        name="num_refrigeration_units = -1 → 400",
        payload={**VALID_PAYLOAD, "num_refrigeration_units": -1},
        expectation="reject",
        expected_status=400,
        tags=("boundary",),
    )
    add(
        category="Boundary / Range Validation",
        name="num_workers = 0 → 400 INVALID_FIELD_VALUE",
        payload={**VALID_PAYLOAD, "num_workers": 0},
        expectation="reject",
        expected_status=400,
        expected_error_code="INVALID_FIELD_VALUE",
        tags=("boundary",),
    )
    add(
        category="Boundary / Range Validation",
        name="num_workers = 1000 → 200 (at max)",
        payload={**VALID_PAYLOAD, "num_workers": 1000},
        expectation="accept",
        tags=("boundary", "optional"),
    )
    add(
        category="Boundary / Range Validation",
        name="num_workers = 1001 → 400",
        payload={**VALID_PAYLOAD, "num_workers": 1001},
        expectation="reject",
        expected_status=400,
        tags=("boundary", "optional"),
    )
    add(
        category="Boundary / Range Validation",
        name="months_per_year = 0 → 200 (resets to 12)",
        payload={**VALID_PAYLOAD, "months_per_year": 0},
        expectation="accept",
        tags=("boundary", "optional"),
    )
    add(
        category="Boundary / Range Validation",
        name="months_per_year = 13 → 200 (resets to 12)",
        payload={**VALID_PAYLOAD, "months_per_year": 13},
        expectation="accept",
        tags=("boundary", "optional"),
    )
    add(
        category="Boundary / Range Validation",
        name="location string 200 chars → 200 (at max)",
        payload={**VALID_PAYLOAD, "location": "A" * 200},
        expectation="accept",
        tags=("boundary",),
    )
    add(
        category="Boundary / Range Validation",
        name="location string 201 chars → 400 INVALID_FIELD_VALUE",
        payload={**VALID_PAYLOAD, "location": "A" * 201},
        expectation="reject",
        expected_status=400,
        expected_error_code="INVALID_FIELD_VALUE",
        tags=("boundary",),
    )

    # =========================================================================
    # GROUP 6 — Business Type Validation
    # =========================================================================

    for bt, exp in [
        ("butchery", "accept"),
        ("grocery", "accept"),
        ("mini_supermarket", "accept"),
        ("BUTCHERY", "accept"),   # case-insensitive
        ("restaurant", "reject"),
        ("", "reject"),
    ]:
        add(
            category="Business Type Validation",
            name=f"business_type='{bt}' → {'200' if exp == 'accept' else '400 INVALID_BUSINESS_TYPE'}",
            payload={**VALID_PAYLOAD, "business_type": bt},
            expectation=exp,
            expected_status=None if exp == "accept" else 400,
            expected_error_code=None if exp == "accept" else "INVALID_BUSINESS_TYPE",
            tags=("business_type",),
        )

    # =========================================================================
    # GROUP 7 — Climate Factor Sensitivity
    # =========================================================================

    climate_cases = [
        ("Lagos, Nigeria", 1.35),
        ("Accra, Ghana", 1.30),
        ("Nairobi, Kenya", 1.20),
        ("Kampala, Uganda", 1.25),
        ("Johannesburg, South Africa", 1.18),
        ("Dar es Salaam, Tanzania", 1.35),
        ("Unknown City, Country", 1.20),
    ]
    for location, factor in climate_cases:
        add(
            category="Climate Factor Sensitivity",
            name=f"climate_factor {location} → {factor}",
            payload={**VALID_PAYLOAD, "location": location},
            expectation="accept",
            tags=("climate",),
        )

    # Lagos vs Johannesburg: Lagos kWh should be higher
    add(
        category="Climate Factor Sensitivity",
        name="Lagos kWh > Johannesburg kWh (highest vs lowest factor)",
        payload={**VALID_PAYLOAD, "location": "Lagos, Nigeria"},
        expectation="accept",
        tags=("climate", "comparative_lagos"),
    )
    add(
        category="Climate Factor Sensitivity",
        name="Johannesburg kWh reference (for comparison with Lagos)",
        payload={**VALID_PAYLOAD, "location": "Johannesburg, South Africa"},
        expectation="accept",
        tags=("climate", "comparative_joburg"),
    )

    # =========================================================================
    # GROUP 8 — Input Sensitivity / Behavioral Scenarios
    # =========================================================================

    for sqft in [20, 60, 150, 500, 2000]:
        add(
            category="Input Sensitivity - sqft_m2 sweep",
            name=f"sqft_m2={sqft}",
            payload={**BASELINE_PAYLOAD, "sqft_m2": sqft},
            expectation="accept",
            tags=("sweep", "sqft_sweep"),
        )

    for hrs in [10, 40, 80, 120, 168]:
        add(
            category="Input Sensitivity - operating_hours sweep",
            name=f"operating_hours_weekly={hrs}",
            payload={**BASELINE_PAYLOAD, "operating_hours_weekly": hrs},
            expectation="accept",
            tags=("sweep", "hours_sweep"),
        )

    for units in [0, 1, 3, 10, 50]:
        add(
            category="Input Sensitivity - refrigeration sweep",
            name=f"num_refrigeration_units={units}",
            payload={**BASELINE_PAYLOAD, "num_refrigeration_units": units},
            expectation="accept",
            tags=("sweep", "refrigeration_sweep"),
        )

    for workers in [1, 5, 20, 100]:
        add(
            category="Input Sensitivity - num_workers sweep",
            name=f"num_workers={workers}",
            payload={**BASELINE_PAYLOAD, "num_workers": workers},
            expectation="accept",
            tags=("sweep", "workers_sweep"),
        )

    for bt in ["butchery", "grocery", "mini_supermarket"]:
        add(
            category="Input Sensitivity - business type comparison",
            name=f"business_type={bt} kWh in [0, 1_000_000]",
            payload={**BASELINE_PAYLOAD, "business_type": bt},
            expectation="accept",
            tags=("sweep", "business_type_sweep"),
        )

    # =========================================================================
    # GROUP 9 — Confidence Score Logic
    # =========================================================================

    add(
        category="Confidence Score Logic",
        name="num_refrigeration_units=0 → confidence_score=0.75",
        payload={**VALID_PAYLOAD, "num_refrigeration_units": 0},
        expectation="accept",
        tags=("confidence",),
    )
    add(
        category="Confidence Score Logic",
        name="positive inputs → confidence_score=0.85",
        payload=VALID_PAYLOAD,
        expectation="accept",
        tags=("confidence",),
    )
    add(
        category="Confidence Score Logic",
        name="extreme low inputs → confidence_score in [0,1]",
        payload={**VALID_PAYLOAD, "num_refrigeration_units": 0, "sqft_m2": 0.001, "operating_hours_weekly": 1},
        expectation="accept",
        tags=("confidence",),
    )
    add(
        category="Confidence Score Logic",
        name="extreme high inputs → confidence_score in [0,1]",
        payload={**VALID_PAYLOAD, "num_refrigeration_units": 500, "sqft_m2": 10000, "operating_hours_weekly": 168},
        expectation="accept",
        tags=("confidence",),
    )

    return cases


# ---------------------------------------------------------------------------
# Post-run checks that require comparing results across multiple test cases
# ---------------------------------------------------------------------------

def _run_cross_case_checks(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    After all individual test cases run, run cross-case assertions
    (monotonicity sweeps, comparative checks, confidence values).
    Returns a list of check result dicts.
    """
    checks = []

    def _kwh_from(r: Dict[str, Any]) -> Optional[float]:
        return r["evaluation"].get("extracted_kwh_monthly")

    def _passed(r: Dict[str, Any]) -> bool:
        return bool(r["evaluation"]["passed"])

    # Helper: get results by tag
    def _by_tag(tag: str) -> List[Dict[str, Any]]:
        return [r for r in results if tag in r.get("tags", [])]

    # --- sqft_m2 sweep: monotonically increasing ---
    sqft_results = _by_tag("sqft_sweep")
    if len(sqft_results) == 5 and all(_passed(r) for r in sqft_results):
        kwh_vals = [_kwh_from(r) for r in sqft_results]
        is_mono = all(
            kwh_vals[i + 1] >= kwh_vals[i]  # type: ignore[operator]
            for i in range(len(kwh_vals) - 1)
            if kwh_vals[i] is not None and kwh_vals[i + 1] is not None
        )
        checks.append({
            "check": "sqft_m2 sweep monotonically increasing",
            "passed": is_mono,
            "values": kwh_vals,
            "failure_mode": None if is_mono else f"not_monotonic: {kwh_vals}",
        })
    else:
        checks.append({
            "check": "sqft_m2 sweep monotonically increasing",
            "passed": False,
            "failure_mode": "prerequisite_test_cases_failed_or_missing",
        })

    # --- operating_hours_weekly sweep: monotonically increasing ---
    hrs_results = _by_tag("hours_sweep")
    if len(hrs_results) == 5 and all(_passed(r) for r in hrs_results):
        kwh_vals = [_kwh_from(r) for r in hrs_results]
        is_mono = all(
            kwh_vals[i + 1] >= kwh_vals[i]  # type: ignore[operator]
            for i in range(len(kwh_vals) - 1)
            if kwh_vals[i] is not None and kwh_vals[i + 1] is not None
        )
        checks.append({
            "check": "operating_hours_weekly sweep monotonically increasing",
            "passed": is_mono,
            "values": kwh_vals,
            "failure_mode": None if is_mono else f"not_monotonic: {kwh_vals}",
        })
    else:
        checks.append({
            "check": "operating_hours_weekly sweep monotonically increasing",
            "passed": False,
            "failure_mode": "prerequisite_test_cases_failed_or_missing",
        })

    # --- refrigeration sweep: refrigeration share 50-70% and increases ---
    refrig_results = _by_tag("refrigeration_sweep")
    if len(refrig_results) == 5 and all(_passed(r) for r in refrig_results):
        refrig_share_ok = True
        refrig_kwh_vals = []
        for r in refrig_results:
            rj = r["response"]["json"] or {}
            total = rj.get("estimated_consumption_kwh_monthly")
            breakdown = rj.get("breakdown") or {}
            ref = breakdown.get("refrigeration")
            if total and ref is not None and total > 0:
                units = (r["request"]["payload_sent"] or {}).get("num_refrigeration_units", -1)
                if units > 0:
                    share = ref / total
                    if not (0.50 <= share <= 0.70):
                        refrig_share_ok = False
            refrig_kwh_vals.append(ref)
        refrig_increasing = (
            refrig_kwh_vals[-1] is not None
            and refrig_kwh_vals[0] is not None
            and refrig_kwh_vals[-1] >= refrig_kwh_vals[0]
        )
        passed = refrig_share_ok and refrig_increasing
        checks.append({
            "check": "refrigeration sweep: share 50-70% and increases with units",
            "passed": passed,
            "refrigeration_kwh_values": refrig_kwh_vals,
            "failure_mode": None if passed else "refrigeration_share_or_direction_wrong",
        })
    else:
        checks.append({
            "check": "refrigeration sweep: share 50-70% and increases with units",
            "passed": False,
            "failure_mode": "prerequisite_test_cases_failed_or_missing",
        })

    # --- Lagos kWh > Johannesburg kWh ---
    lagos_r = next((r for r in results if "comparative_lagos" in r.get("tags", [])), None)
    joburg_r = next((r for r in results if "comparative_joburg" in r.get("tags", [])), None)
    if lagos_r and joburg_r and _passed(lagos_r) and _passed(joburg_r):
        kwh_lagos = _kwh_from(lagos_r)
        kwh_joburg = _kwh_from(joburg_r)
        passed = kwh_lagos is not None and kwh_joburg is not None and kwh_lagos > kwh_joburg
        checks.append({
            "check": "Lagos monthly kWh > Johannesburg monthly kWh",
            "passed": passed,
            "kwh_lagos": kwh_lagos,
            "kwh_johannesburg": kwh_joburg,
            "failure_mode": None if passed else f"lagos={kwh_lagos} not > joburg={kwh_joburg}",
        })
    else:
        checks.append({
            "check": "Lagos monthly kWh > Johannesburg monthly kWh",
            "passed": False,
            "failure_mode": "prerequisite_test_cases_failed_or_missing",
        })

    # --- Climate factor values ---
    climate_expected = {
        "Lagos, Nigeria": 1.35,
        "Accra, Ghana": 1.30,
        "Nairobi, Kenya": 1.20,
        "Kampala, Uganda": 1.25,
        "Johannesburg, South Africa": 1.18,
        "Dar es Salaam, Tanzania": 1.35,
        "Unknown City, Country": 1.20,
    }
    climate_results = _by_tag("climate")
    for r in climate_results:
        if "comparative_lagos" in r["tags"] or "comparative_joburg" in r["tags"]:
            continue
        payload = r["request"].get("payload_sent") or {}
        location = payload.get("location", "")
        expected_factor = climate_expected.get(location)
        if expected_factor is None:
            continue
        actual_factor = None
        rj = r["response"]["json"] or {}
        if isinstance(rj, dict):
            actual_factor = rj.get("climate_adjustment_factor")
        passed = _passed(r) and actual_factor == expected_factor
        checks.append({
            "check": f"climate_adjustment_factor for '{location}'",
            "passed": passed,
            "expected": expected_factor,
            "actual": actual_factor,
            "failure_mode": None if passed else f"expected={expected_factor},got={actual_factor}",
        })

    # --- Confidence score checks ---
    conf_results = _by_tag("confidence")
    for r in conf_results:
        if not _passed(r):
            continue
        rj = r["response"]["json"] or {}
        score = rj.get("confidence_score") if isinstance(rj, dict) else None
        payload = r["request"].get("payload_sent") or {}
        name = r["name"]
        if "0.75" in name:
            passed = score == 0.75
            checks.append({
                "check": f"confidence_score == 0.75 for '{name}'",
                "passed": passed,
                "actual": score,
                "failure_mode": None if passed else f"expected=0.75,got={score}",
            })
        elif "0.85" in name:
            passed = score == 0.85
            checks.append({
                "check": f"confidence_score == 0.85 for '{name}'",
                "passed": passed,
                "actual": score,
                "failure_mode": None if passed else f"expected=0.85,got={score}",
            })
        elif "in [0,1]" in name:
            if score is not None:
                passed = 0 <= score <= 1
                checks.append({
                    "check": f"confidence_score in [0,1] for '{name}'",
                    "passed": passed,
                    "actual": score,
                    "failure_mode": None if passed else f"score={score} out of [0,1]",
                })

    return checks


# ---------------------------------------------------------------------------
# Health check override
# ---------------------------------------------------------------------------

def _run_health_check(base_url: str) -> Dict[str, Any]:
    """GET /api/v1/health — no auth required, expect 200 with status=healthy."""
    url = _join_url(base_url, "/api/v1/health")
    started = time.time()
    status_code: Optional[int] = None
    resp_json: Any = None
    request_error: Optional[str] = None

    try:
        resp = requests.get(url, timeout=TIMEOUT_SECONDS)
        status_code = resp.status_code
        resp_json, _ = _safe_json(resp)
    except requests.exceptions.Timeout:
        request_error = f"timeout_after_{TIMEOUT_SECONDS}s"
    except requests.exceptions.ConnectionError as e:
        request_error = f"connection_error: {e}"
    except requests.exceptions.RequestException as e:
        request_error = f"request_exception: {type(e).__name__}: {e}"

    elapsed_ms = int((time.time() - started) * 1000)
    passed = (
        request_error is None
        and status_code == 200
        and isinstance(resp_json, dict)
        and resp_json.get("status") in ("healthy", "ok")
    )
    return {
        "id": "HEALTH",
        "category": "Authentication & Security",
        "name": "health endpoint requires no auth → 200",
        "tags": ["health_check"],
        "request": {"url": url, "method": "GET", "headers_sent": {}, "timeout_seconds": TIMEOUT_SECONDS},
        "response": {"status_code": status_code, "json": resp_json},
        "evaluation": {
            "expectation": "accept",
            "expected_status": 200,
            "expected_error_code": None,
            "extracted_kwh_monthly": None,
            "passed": passed,
            "failure_mode": request_error or (None if passed else f"status={status_code},body={resp_json}"),
        },
        "timing": {"elapsed_ms": elapsed_ms, "started_at": _now_iso()},
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Stress-test Model 1 /api/v1/estimate-consumption robustness."
    )
    parser.add_argument(
        "--base-url",
        default=BASE_URL,
        help="Base URL for the API gateway (default: env MODEL1_BASE_URL or http://localhost:8000).",
    )
    parser.add_argument(
        "--out",
        default="model1_robustness_report.json",
        help="Output report filename (default: model1_robustness_report.json).",
    )
    args = parser.parse_args(argv)

    base_url = args.base_url
    out_path = Path(args.out)

    cases = _make_test_cases()

    print(f"Running {len(cases)} test cases against {_join_url(base_url, ENDPOINT_PATH)} ...")
    print()

    started = time.time()
    results: List[Dict[str, Any]] = []

    for case in cases:
        if "health_check" in case.tags:
            results.append(_run_health_check(base_url))
        else:
            results.append(_run_test_case(case, base_url))

    elapsed_ms = int((time.time() - started) * 1000)

    # Cross-case checks
    cross_checks = _run_cross_case_checks(results)

    # Summary counts by category
    by_category: Dict[str, Dict[str, int]] = {}
    for r in results:
        cat = r["category"]
        by_category.setdefault(cat, {"total": 0, "passed": 0, "failed": 0})
        by_category[cat]["total"] += 1
        if r["evaluation"]["passed"]:
            by_category[cat]["passed"] += 1
        else:
            by_category[cat]["failed"] += 1

    cross_passed = sum(1 for c in cross_checks if c["passed"])
    cross_failed = len(cross_checks) - cross_passed

    report = {
        "meta": {
            "model": "Model 1 - Energy Consumption ML API",
            "endpoint": ENDPOINT_PATH,
            "base_url": base_url,
            "timeout_seconds": TIMEOUT_SECONDS,
            "auth_header_used": bool(API_KEY),
            "generated_at": _now_iso(),
            "duration_ms": elapsed_ms,
            "acceptable_definition": {
                "status_code": 200,
                "plausible_kwh_range": {
                    "gte": KWH_LOWER_INCLUSIVE,
                    "lte": KWH_UPPER_INCLUSIVE,
                },
            },
        },
        "summary": {
            "individual_tests": {
                "total": len(results),
                "passed": sum(1 for r in results if r["evaluation"]["passed"]),
                "failed": sum(1 for r in results if not r["evaluation"]["passed"]),
                "by_category": by_category,
            },
            "cross_case_checks": {
                "total": len(cross_checks),
                "passed": cross_passed,
                "failed": cross_failed,
            },
            "overall_passed": (
                sum(1 for r in results if not r["evaluation"]["passed"]) == 0
                and cross_failed == 0
            ),
        },
        "tests": results,
        "cross_case_checks": cross_checks,
    }

    _print_summary_table(results)

    if cross_checks:
        print()
        print("Cross-case checks:")
        print("-" * 60)
        for c in cross_checks:
            status = "PASS" if c["passed"] else "FAIL"
            fm = c.get("failure_mode") or ""
            print(f"  [{status}] {c['check']}" + (f" — {fm}" if fm else ""))

    print()
    ind_passed = sum(1 for r in results if r["evaluation"]["passed"])
    ind_total = len(results)
    print(f"Individual tests: {ind_total} total | {ind_passed} passed | {ind_total - ind_passed} failed")
    print(f"Cross-case checks: {len(cross_checks)} total | {cross_passed} passed | {cross_failed} failed")

    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print()
    print(f"Wrote report: {out_path.resolve()}")

    return 0 if report["summary"]["overall_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())