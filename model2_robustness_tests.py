"""
Model 2 robustness tests: XGBoost Climatological Solar Generation.

Runs a suite of edge-case requests against:
POST /api/v1/predict-generation

Outputs:
- Console summary table
- model2_robustness_report.json
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

BASE_URL = os.getenv("MODEL2_BASE_URL", "http://localhost:8000")
ENDPOINT_PATH = "/api/v1/predict-generation"
TIMEOUT_SECONDS = 3

# Auth is required by the Model 2 service per integration guide.
# Set SOLAR_API_KEY (preferred) or API_KEY in your environment.
API_KEY = os.getenv("SOLAR_API_KEY") or os.getenv("API_KEY") or ""

DRY_SEASON_MONTHS = {12, 1, 2, 6, 7, 8}

# "Acceptable" definition requested by user:
# - HTTP 200
# - plausible kWh value > 0 and < 50 (we use daily_kwh / average_daily_kwh)
KWH_LOWER_EXCLUSIVE = 0.0
KWH_UPPER_EXCLUSIVE = 50.0


_NO_JSON_BODY = object()


@dataclass(frozen=True)
class TestCase:
    id: str
    category: str
    name: str
    payload: Union[Dict[str, Any], object]
    expectation: str  # "accept" | "reject_or_degrade"
    tags: Tuple[str, ...] = ()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _join_url(base_url: str, path: str) -> str:
    return base_url.rstrip("/") + path


def _build_headers() -> Dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["X-API-KEY"] = API_KEY
    return headers


def _safe_json(response: requests.Response) -> Tuple[Optional[Any], Optional[str]]:
    try:
        return response.json(), None
    except Exception as e:  # noqa: BLE001 - we want any JSON parsing issue
        text = None
        try:
            text = response.text
        except Exception:
            text = None
        err = f"invalid_json_response: {type(e).__name__}: {e}"
        if text:
            err += f" | body_prefix={text[:400]!r}"
        return None, err


def _get_nested(obj: Any, path: List[Union[str, int]]) -> Any:
    cur = obj
    for p in path:
        if isinstance(p, int):
            if not isinstance(cur, list) or p >= len(cur):
                return None
            cur = cur[p]
        else:
            if not isinstance(cur, dict) or p not in cur:
                return None
            cur = cur[p]
    return cur


def _extract_daily_kwh(resp_json: Any) -> Tuple[Optional[float], Optional[str]]:
    """
    Prefer the single-month response field:
    - monthly_generation[0].daily_kwh

    Fallbacks:
    - annual_summary.average_daily_kwh
    - any numeric-looking field named generation_kwh (less likely for this API)
    """
    candidates: List[Tuple[str, List[Union[str, int]]]] = [
        ("monthly_generation[0].daily_kwh", ["monthly_generation", 0, "daily_kwh"]),
        ("annual_summary.average_daily_kwh", ["annual_summary", "average_daily_kwh"]),
    ]

    for label, path in candidates:
        val = _get_nested(resp_json, path)
        if isinstance(val, (int, float)):
            return float(val), label

    # As a last resort, scan a few known keys shallowly.
    if isinstance(resp_json, dict):
        for k in ("generation_kwh", "daily_kwh", "average_daily_kwh"):
            v = resp_json.get(k)
            if isinstance(v, (int, float)):
                return float(v), k
    return None, None


def _is_plausible_kwh(kwh: float) -> bool:
    return (kwh > KWH_LOWER_EXCLUSIVE) and (kwh < KWH_UPPER_EXCLUSIVE)


def _evaluate_acceptability(status_code: Optional[int], resp_json: Any) -> Tuple[bool, Optional[str], Optional[float], Optional[str]]:
    if status_code != 200:
        return False, "status_not_200", None, None

    if resp_json is None:
        return False, "missing_json_body", None, None

    kwh, field_path = _extract_daily_kwh(resp_json)
    if kwh is None:
        return False, "missing_kwh_field", None, None

    if not _is_plausible_kwh(kwh):
        return False, f"kwh_out_of_range({kwh})", kwh, field_path

    return True, None, kwh, field_path


def _classify_failure_mode(
    *,
    request_error: Optional[str],
    json_error: Optional[str],
    acceptable: bool,
    acceptable_failure: Optional[str],
    expectation: str,
    status_code: Optional[int],
) -> Optional[str]:
    if request_error:
        return request_error
    if json_error:
        return json_error

    if expectation == "accept":
        if acceptable:
            return None
        return acceptable_failure or "unacceptable_response"

    # reject_or_degrade
    if status_code is None:
        return "no_status_code"
    if status_code != 200:
        return None  # rejection is acceptable for this expectation
    if acceptable:
        return "unexpected_acceptance"
    return None  # degraded output (200 but unacceptable) is acceptable here


def _run_test_case(test: TestCase, base_url: str) -> Dict[str, Any]:
    url = _join_url(base_url, ENDPOINT_PATH)
    headers = _build_headers()
    started = time.time()

    status_code: Optional[int] = None
    resp_text: Optional[str] = None
    resp_json: Any = None
    request_error: Optional[str] = None
    json_error: Optional[str] = None

    try:
        if test.payload is _NO_JSON_BODY:
            resp = requests.post(url, headers=headers, timeout=TIMEOUT_SECONDS)
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

    acceptable, acceptable_failure, extracted_kwh, extracted_kwh_path = _evaluate_acceptability(status_code, resp_json)

    if test.expectation == "accept":
        passed = acceptable
    else:
        # Outside range / invalid types: "pass" if rejected (non-200) OR degraded (200 but unacceptable).
        passed = (status_code is not None and status_code != 200) or (status_code == 200 and not acceptable)

    failure_mode = _classify_failure_mode(
        request_error=request_error,
        json_error=json_error,
        acceptable=acceptable,
        acceptable_failure=acceptable_failure,
        expectation=test.expectation,
        status_code=status_code,
    )

    # Keep response body in the report, but guard against extremely large output.
    # Lifetime responses can be sizable; cap text to 20k for readability.
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
            "headers_sent": {"Content-Type": "application/json", **({"X-API-KEY": "***set***"} if API_KEY else {})},
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
            "acceptable_definition": {
                "status_code": 200,
                "kwh_field_preference": ["monthly_generation[0].daily_kwh", "annual_summary.average_daily_kwh"],
                "plausible_kwh_range": {"gt": KWH_LOWER_EXCLUSIVE, "lt": KWH_UPPER_EXCLUSIVE},
            },
            "extracted_kwh": extracted_kwh,
            "extracted_kwh_field": extracted_kwh_path,
            "acceptable": acceptable,
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
        cat = r["category"]
        name = r["name"]
        rows.append([str(i), cat, name, status_s, _fmt_bool(passed), failure])

    headers = ["#", "Category", "Test", "HTTP", "Result", "Failure mode"]
    widths = [len(h) for h in headers]
    for row in rows:
        for j, cell in enumerate(row):
            widths[j] = max(widths[j], len(cell))

    def line(sep: str = "-") -> str:
        return sep.join(sep * (w + 2) for w in widths)

    def fmt_row(row: List[str]) -> str:
        return " | ".join(cell.ljust(widths[i]) for i, cell in enumerate(row))

    print(fmt_row(headers))
    print(line("-"))
    for row in rows:
        print(fmt_row(row))

    total = len(results)
    passed_n = sum(1 for r in results if r["evaluation"]["passed"])
    print()
    print(f"Total: {total} | Passed: {passed_n} | Failed: {total - passed_n}")


def _make_test_cases() -> List[TestCase]:
    cases: List[TestCase] = []

    def add(
        *,
        category: str,
        name: str,
        payload: Union[Dict[str, Any], object],
        expectation: str,
        tags: Tuple[str, ...] = (),
    ) -> None:
        cases.append(
            TestCase(
                id=f"{len(cases)+1:03d}",
                category=category,
                name=name,
                payload=payload,
                expectation=expectation,
                tags=tags,
            )
        )

    # Common "in-range" baseline location/month (Nairobi-like, per docs)
    base_lat = -1.2921
    base_lon = 36.8219
    base_month = 6

    # 1) Boundary coordinates — exact boundary values and combinations
    boundary_lats = [-26.0, 6.0]
    boundary_lons = [-18.0, 44.0]
    mid_lat = -10.0
    mid_lon = 10.0

    for lat, lon in [(-26.0, mid_lon), (6.0, mid_lon), (mid_lat, -18.0), (mid_lat, 44.0)]:
        add(
            category="Boundary coordinates",
            name=f"edge(lat={lat}, lon={lon})",
            payload={"latitude": lat, "longitude": lon, "month": base_month, "include_lifetime": False},
            expectation="accept",
            tags=("boundary",),
        )
    for lat in boundary_lats:
        for lon in boundary_lons:
            add(
                category="Boundary coordinates",
                name=f"corner(lat={lat}, lon={lon})",
                payload={"latitude": lat, "longitude": lon, "month": base_month, "include_lifetime": False},
                expectation="accept",
                tags=("boundary", "corner"),
            )

    # 2) Just outside boundaries — expect rejection or degraded output
    outside_lats = [-27.0, 7.0]
    outside_lons = [-19.0, 45.0]
    for lat in outside_lats:
        add(
            category="Just outside boundaries",
            name=f"outside_lat(lat={lat}, lon={mid_lon})",
            payload={"latitude": lat, "longitude": mid_lon, "month": base_month, "include_lifetime": False},
            expectation="reject_or_degrade",
            tags=("outside",),
        )
    for lon in outside_lons:
        add(
            category="Just outside boundaries",
            name=f"outside_lon(lat={mid_lat}, lon={lon})",
            payload={"latitude": mid_lat, "longitude": lon, "month": base_month, "include_lifetime": False},
            expectation="reject_or_degrade",
            tags=("outside",),
        )
    for lat, lon in [(-27.0, -19.0), (7.0, 45.0), (-27.0, 45.0), (7.0, -19.0)]:
        add(
            category="Just outside boundaries",
            name=f"outside_corner(lat={lat}, lon={lon})",
            payload={"latitude": lat, "longitude": lon, "month": base_month, "include_lifetime": False},
            expectation="reject_or_degrade",
            tags=("outside", "corner"),
        )

    # 3) Equator and extreme south
    for lat in [0.0, -25.9]:
        add(
            category="Equator and extreme south",
            name=f"lat_focus(lat={lat})",
            payload={"latitude": lat, "longitude": base_lon, "month": base_month, "include_lifetime": False},
            expectation="accept",
            tags=("lat_focus",),
        )

    # 4) Dry season vs wet season months — test all 12 months, flag dry season months
    for m in range(1, 13):
        dry = m in DRY_SEASON_MONTHS
        add(
            category="Dry vs wet season months",
            name=f"month={m} ({'dry' if dry else 'wet'})",
            payload={"latitude": base_lat, "longitude": base_lon, "month": m, "include_lifetime": False},
            expectation="accept",
            tags=("dry_season" if dry else "wet_season",),
        )

    # 5) Month boundaries — valid boundaries and invalid values
    for m, exp in [(1, "accept"), (12, "accept"), (0, "reject_or_degrade"), (13, "reject_or_degrade")]:
        add(
            category="Month boundaries",
            name=f"month={m}",
            payload={"latitude": base_lat, "longitude": base_lon, "month": m, "include_lifetime": False},
            expectation=exp,
            tags=("month_boundary",),
        )

    # 6) Missing optional fields — send request without include_lifetime
    add(
        category="Missing optional fields",
        name="omit include_lifetime",
        payload={"latitude": base_lat, "longitude": base_lon, "month": base_month},
        expectation="accept",
        tags=("optional_missing",),
    )

    # 7) Null and wrong types — latitude as string, month as null, empty body
    add(
        category="Null and wrong types",
        name="latitude as string",
        payload={"latitude": "0", "longitude": base_lon, "month": base_month, "include_lifetime": False},
        expectation="reject_or_degrade",
        tags=("type_error",),
    )
    add(
        category="Null and wrong types",
        name="month as null",
        payload={"latitude": base_lat, "longitude": base_lon, "month": None, "include_lifetime": False},
        expectation="reject_or_degrade",
        tags=("null_value",),
    )
    add(
        category="Null and wrong types",
        name="empty json object body",
        payload={},
        expectation="reject_or_degrade",
        tags=("empty_body",),
    )
    add(
        category="Null and wrong types",
        name="no json body",
        payload=_NO_JSON_BODY,
        expectation="reject_or_degrade",
        tags=("empty_body", "no_json"),
    )

    # 8) Coordinate precision — many decimals, zero longitude, zero latitude
    add(
        category="Coordinate precision",
        name="many decimals",
        payload={
            "latitude": -10.1234567890123,
            "longitude": 10.9876543210987,
            "month": 3,
            "include_lifetime": False,
        },
        expectation="accept",
        tags=("precision",),
    )
    for lat, lon, label in [
        (0.0, base_lon, "zero latitude"),
        (base_lat, 0.0, "zero longitude"),
        (0.0, 0.0, "zero lat & lon"),
    ]:
        add(
            category="Coordinate precision",
            name=label,
            payload={"latitude": lat, "longitude": lon, "month": base_month, "include_lifetime": False},
            expectation="accept",
            tags=("zero_coord",),
        )

    return cases


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Stress-test Model 2 /api/v1/predict-generation robustness.")
    parser.add_argument("--base-url", default=BASE_URL, help="Base URL for the Model 2 service (default: env MODEL2_BASE_URL or http://localhost:8000).")
    parser.add_argument(
        "--out",
        default="model2_robustness_report.json",
        help="Output report filename (default: model2_robustness_report.json).",
    )
    args = parser.parse_args(argv)

    base_url = args.base_url
    out_path = Path(args.out)

    cases = _make_test_cases()

    started = time.time()
    results: List[Dict[str, Any]] = []
    for case in cases:
        results.append(_run_test_case(case, base_url))

    elapsed_ms = int((time.time() - started) * 1000)

    # Summary counts
    by_category: Dict[str, Dict[str, int]] = {}
    for r in results:
        cat = r["category"]
        by_category.setdefault(cat, {"total": 0, "passed": 0, "failed": 0})
        by_category[cat]["total"] += 1
        if r["evaluation"]["passed"]:
            by_category[cat]["passed"] += 1
        else:
            by_category[cat]["failed"] += 1

    report = {
        "meta": {
            "model": "Model 2 - XGBoost Climatological Solar Generation",
            "endpoint": ENDPOINT_PATH,
            "base_url": base_url,
            "timeout_seconds": TIMEOUT_SECONDS,
            "auth_header_used": bool(API_KEY),
            "generated_at": _now_iso(),
            "duration_ms": elapsed_ms,
            "acceptable_definition": {"status_code": 200, "plausible_kwh_range": {"gt": KWH_LOWER_EXCLUSIVE, "lt": KWH_UPPER_EXCLUSIVE}},
            "dry_season_months": sorted(DRY_SEASON_MONTHS),
        },
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r["evaluation"]["passed"]),
            "failed": sum(1 for r in results if not r["evaluation"]["passed"]),
            "by_category": by_category,
        },
        "tests": results,
    }

    _print_summary_table(results)

    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print()
    print(f"Wrote report: {out_path.resolve()}")

    # Exit code indicates whether all tests passed per expectations.
    return 0 if report["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

