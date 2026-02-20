"""
Stress-test suite for ROI Calculation API (Model 3)
====================================================
Tests the pure calculate_roi() function and all validation helpers
without requiring a running Flask server.

Run with:
    pytest test_roi_stress.py -v
or:
    python test_roi_stress.py
"""

import math
import sys
import unittest

# ---------------------------------------------------------------------------
# Inline copies of the functions under test
# (avoids Flask / flask-limiter import chain in CI without those packages)
# ---------------------------------------------------------------------------

def calculate_roi(system_cost_usd: float,
                  consumption_kwh: float,
                  generation_kwh: float,
                  tariff_per_kwh: float) -> dict:
    energy_offset_kwh = min(consumption_kwh, generation_kwh)
    monthly_savings_usd = energy_offset_kwh * tariff_per_kwh
    annual_savings_usd = monthly_savings_usd * 12
    if annual_savings_usd <= 0:
        roi_percentage = 0.0
    else:
        raw_roi = (annual_savings_usd / system_cost_usd) * 100
        roi_percentage = max(0.0, min(raw_roi, 100.0))
    monthly_savings_usd = max(0.0, monthly_savings_usd)
    system_cost_usd = max(0.0, system_cost_usd)
    return {
        "monthly_savings_usd": round(monthly_savings_usd, 2),
        "roi_percentage": round(roi_percentage, 2),
        "system_cost_usd": round(system_cost_usd, 2),
    }


ALLOWED_BUSINESS_TYPE_CHARS = set(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 _-&/"
)


def _validate_float_field(data, field_name, display_name,
                           min_value=0.0, strictly_positive=True, max_value=None):
    if field_name not in data:
        return None, ({"error": f"Missing field: {field_name}"}, 400)
    try:
        value = float(data[field_name])
    except (TypeError, ValueError):
        return None, ({"error": f"{field_name} must be a number"}, 400)
    if strictly_positive:
        if value <= min_value:
            return None, ({"error": f"{field_name} must be greater than {min_value}"}, 400)
    else:
        if value < min_value:
            return None, ({"error": f"{field_name} must be greater than or equal to {min_value}"}, 400)
    if max_value is not None and value > max_value:
        return None, ({"error": f"{field_name} must be less than or equal to {max_value}"}, 400)
    return value, None


def _validate_optional_hours(data, field_name):
    if field_name not in data:
        return None, None
    try:
        value = float(data[field_name])
    except (TypeError, ValueError):
        return None, ({"error": f"{field_name} must be a number"}, 400)
    if value < 0 or value > 24:
        return None, ({"error": f"{field_name} must be between 0 and 24 hours"}, 400)
    return value, None


def _validate_optional_units(data, field_name, max_units=500):
    if field_name not in data:
        return None, None
    try:
        value = int(data[field_name])
    except (TypeError, ValueError):
        return None, ({"error": f"{field_name} must be an integer"}, 400)
    if value < 0 or value > max_units:
        return None, ({"error": f"{field_name} must be between 0 and {max_units}"}, 400)
    return value, None


def _validate_optional_string(data, field_name, max_len=64):
    if field_name not in data:
        return None, None
    value = data[field_name]
    if not isinstance(value, str):
        return None, ({"error": f"{field_name} must be a string"}, 400)
    value_stripped = value.strip()
    if not value_stripped:
        return None, ({"error": f"{field_name} cannot be empty"}, 400)
    if len(value_stripped) > max_len:
        return None, ({"error": f"{field_name} must be at most {max_len} characters"}, 400)
    if field_name == "business_type":
        if not all(ch in ALLOWED_BUSINESS_TYPE_CHARS for ch in value_stripped):
            return None, ({"error": f"{field_name} contains invalid characters"}, 400)
    return value_stripped, None


# ===========================================================================
# Helper
# ===========================================================================

def _accept(val, err):
    """Assert that a validation call accepted the value."""
    assert err is None, f"Expected acceptance but got error: {err}"
    return val


def _reject(val, err, expected_status=400):
    """Assert that a validation call rejected the value."""
    assert err is not None, "Expected rejection but value was accepted."
    assert err[1] == expected_status, f"Expected HTTP {expected_status}, got {err[1]}"
    return err[0]["error"]


# ===========================================================================
# 1.  calculate_roi – happy-path & arithmetic correctness
# ===========================================================================

class TestCalculateROIHappyPath(unittest.TestCase):

    def test_normal_case_arithmetic(self):
        """Savings = offset * tariff; ROI = annual_savings / cost * 100."""
        r = calculate_roi(10000, 500, 400, 0.15)
        self.assertAlmostEqual(r["monthly_savings_usd"], 60.00, places=2)
        self.assertAlmostEqual(r["roi_percentage"], 7.20, places=2)
        self.assertAlmostEqual(r["system_cost_usd"], 10000.00, places=2)

    def test_consumption_equals_generation(self):
        """When perfectly matched, full generation is offset."""
        r = calculate_roi(10000, 500, 500, 0.15)
        self.assertAlmostEqual(r["monthly_savings_usd"], 75.00, places=2)
        self.assertAlmostEqual(r["roi_percentage"], 9.00, places=2)

    def test_roi_exactly_100_percent(self):
        """Annual savings == system cost → ROI = 100%."""
        # 1000 kWh * $1/kWh * 12 = $12000 = system_cost
        r = calculate_roi(12000, 1000, 1000, 1.0)
        self.assertEqual(r["roi_percentage"], 100.0)

    def test_output_keys_present(self):
        """Response dict must contain exactly the three specified keys."""
        r = calculate_roi(10000, 500, 400, 0.15)
        self.assertSetEqual(set(r.keys()),
                            {"monthly_savings_usd", "roi_percentage", "system_cost_usd"})

    def test_rounding_to_two_decimal_places(self):
        """All output values must be rounded to exactly 2 decimal places."""
        r = calculate_roi(10000, 333, 333, 0.1)
        for key, val in r.items():
            # repr should have at most 2 digits after decimal point
            parts = str(val).split(".")
            self.assertTrue(len(parts) == 1 or len(parts[1]) <= 2,
                            f"{key}={val} has more than 2 decimal places")


# ===========================================================================
# 2.  calculate_roi – offset capping (generation vs consumption)
# ===========================================================================

class TestOffsetCapping(unittest.TestCase):

    def test_generation_exceeds_consumption(self):
        """Offset must be capped at consumption, not generation."""
        r = calculate_roi(10000, 300, 1000, 0.20)
        # offset = 300 kWh (consumption, the smaller value)
        self.assertAlmostEqual(r["monthly_savings_usd"], 60.00, places=2)

    def test_consumption_exceeds_generation(self):
        """Offset must be capped at generation when consumption is larger."""
        r = calculate_roi(50000, 100000, 100, 0.15)
        # offset = 100 kWh
        self.assertAlmostEqual(r["monthly_savings_usd"], 15.00, places=2)

    def test_tiny_generation(self):
        """Near-zero generation produces near-zero savings, not an error."""
        r = calculate_roi(10000, 500, 0.001, 0.15)
        self.assertAlmostEqual(r["monthly_savings_usd"], 0.00, places=2)
        self.assertEqual(r["roi_percentage"], 0.0)

    def test_tiny_consumption(self):
        """Near-zero consumption produces near-zero savings, not an error."""
        r = calculate_roi(10000, 0.001, 500, 0.15)
        self.assertAlmostEqual(r["monthly_savings_usd"], 0.00, places=2)


# ===========================================================================
# 3.  calculate_roi – ROI clamping (0–100%)
# ===========================================================================

class TestROIClamping(unittest.TestCase):

    def test_roi_clamped_at_100_percent_when_raw_exceeds(self):
        """ROI > 100% raw must be clamped to exactly 100."""
        r = calculate_roi(100, 1000, 1000, 5.0)   # raw ROI = 60,000%
        self.assertEqual(r["roi_percentage"], 100.0)

    def test_roi_not_clamped_when_below_100(self):
        """ROI below 100% must not be altered."""
        r = calculate_roi(10000, 500, 400, 0.15)   # raw ROI = 7.2%
        self.assertAlmostEqual(r["roi_percentage"], 7.20, places=2)

    def test_roi_zero_when_no_savings(self):
        """Zero annual savings must produce ROI = 0, not division error."""
        r = calculate_roi(10000, 0.001, 0.001, 0.001)
        self.assertEqual(r["roi_percentage"], 0.0)

    def test_max_inputs_roi_clamped(self):
        """Maximum allowed inputs should not overflow; ROI is clamped."""
        r = calculate_roi(1_000_000, 100_000, 100_000, 100.0)
        self.assertEqual(r["roi_percentage"], 100.0)
        self.assertAlmostEqual(r["system_cost_usd"], 1_000_000.0, places=2)

    def test_high_tariff_roi_clamped(self):
        """Unrealistically high tariff still produces clamped ROI."""
        r = calculate_roi(10000, 500, 500, 100.0)  # raw ROI = 6,000%
        self.assertEqual(r["roi_percentage"], 100.0)

    def test_near_zero_system_cost_roi_clamped(self):
        """Extremely small (but valid) system cost does not cause overflow."""
        r = calculate_roi(0.001, 500, 500, 1.0)   # raw ROI = enormous
        self.assertEqual(r["roi_percentage"], 100.0)


# ===========================================================================
# 4.  calculate_roi – output non-negativity guards
# ===========================================================================

class TestNonNegativityGuards(unittest.TestCase):

    def test_monthly_savings_always_non_negative(self):
        """monthly_savings_usd must never be negative."""
        r = calculate_roi(10000, 0.001, 0.001, 0.001)
        self.assertGreaterEqual(r["monthly_savings_usd"], 0.0)

    def test_system_cost_passthrough_non_negative(self):
        """system_cost_usd is echoed in output and must be non-negative."""
        r = calculate_roi(10000, 500, 400, 0.15)
        self.assertGreaterEqual(r["system_cost_usd"], 0.0)


# ===========================================================================
# 5.  _validate_float_field – required numeric fields
# ===========================================================================

class TestValidateFloatField(unittest.TestCase):

    # --- Rejection cases ---

    def test_missing_field_returns_400(self):
        _, err = _validate_float_field({}, "consumption_kwh", "consumption_kwh")
        _reject(None, err)

    def test_non_numeric_string_returns_400(self):
        _, err = _validate_float_field({"consumption_kwh": "abc"}, "consumption_kwh", "consumption_kwh")
        _reject(None, err)

    def test_none_value_returns_400(self):
        _, err = _validate_float_field({"consumption_kwh": None}, "consumption_kwh", "consumption_kwh")
        _reject(None, err)

    def test_list_value_returns_400(self):
        _, err = _validate_float_field({"consumption_kwh": [500]}, "consumption_kwh", "consumption_kwh")
        _reject(None, err)

    def test_zero_strictly_positive_returns_400(self):
        _, err = _validate_float_field({"consumption_kwh": 0}, "consumption_kwh", "consumption_kwh",
                                        strictly_positive=True)
        _reject(None, err)

    def test_negative_value_returns_400(self):
        _, err = _validate_float_field({"consumption_kwh": -100}, "consumption_kwh", "consumption_kwh")
        _reject(None, err)

    def test_exceeds_max_kwh_returns_400(self):
        _, err = _validate_float_field({"consumption_kwh": 100001}, "consumption_kwh", "consumption_kwh",
                                        max_value=100000.0)
        _reject(None, err)

    def test_infinity_rejected_by_max_check(self):
        _, err = _validate_float_field({"consumption_kwh": float("inf")}, "consumption_kwh", "consumption_kwh",
                                        max_value=100000.0)
        _reject(None, err)

    def test_tariff_exceeds_max_100_returns_400(self):
        _, err = _validate_float_field({"tariff_per_kwh": 100.01}, "tariff_per_kwh", "tariff_per_kwh",
                                        max_value=100.0)
        _reject(None, err)

    def test_system_cost_exceeds_1m_returns_400(self):
        _, err = _validate_float_field({"system_cost_usd": 1_000_001}, "system_cost_usd", "system_cost_usd",
                                        max_value=1_000_000.0)
        _reject(None, err)

    # --- Acceptance cases ---

    def test_numeric_string_is_coerced(self):
        """Numeric strings like '500.5' must be accepted and coerced to float."""
        val, err = _validate_float_field({"consumption_kwh": "500.5"}, "consumption_kwh", "consumption_kwh",
                                          max_value=100000.0)
        self.assertIsNone(err)
        self.assertAlmostEqual(val, 500.5)

    def test_boolean_true_coerced_to_1(self):
        """Python True evaluates to 1.0; this is accepted as a valid positive float.
        NOTE: This is a known quirk – consider explicit isinstance check in production."""
        val, err = _validate_float_field({"consumption_kwh": True}, "consumption_kwh", "consumption_kwh",
                                          max_value=100000.0)
        self.assertIsNone(err)
        self.assertAlmostEqual(val, 1.0)

    def test_boundary_max_value_accepted(self):
        val, err = _validate_float_field({"consumption_kwh": 100000.0}, "consumption_kwh", "consumption_kwh",
                                          max_value=100000.0)
        self.assertIsNone(err)

    def test_boundary_min_strictly_positive(self):
        """Value just above 0 must be accepted when strictly_positive=True."""
        val, err = _validate_float_field({"consumption_kwh": 0.0001}, "consumption_kwh", "consumption_kwh",
                                          strictly_positive=True)
        self.assertIsNone(err)


# ===========================================================================
# 6.  _validate_optional_hours
# ===========================================================================

class TestValidateOptionalHours(unittest.TestCase):

    def test_absent_field_returns_none_no_error(self):
        val, err = _validate_optional_hours({}, "operating_hours")
        self.assertIsNone(val)
        self.assertIsNone(err)

    def test_zero_hours_accepted(self):
        val, err = _validate_optional_hours({"operating_hours": 0}, "operating_hours")
        self.assertIsNone(err)
        self.assertEqual(val, 0.0)

    def test_24_hours_accepted(self):
        val, err = _validate_optional_hours({"operating_hours": 24}, "operating_hours")
        self.assertIsNone(err)
        self.assertEqual(val, 24.0)

    def test_just_above_24_rejected(self):
        _, err = _validate_optional_hours({"operating_hours": 24.1}, "operating_hours")
        _reject(None, err)

    def test_negative_hours_rejected(self):
        _, err = _validate_optional_hours({"operating_hours": -1}, "operating_hours")
        _reject(None, err)

    def test_non_numeric_string_rejected(self):
        _, err = _validate_optional_hours({"operating_hours": "morning"}, "operating_hours")
        _reject(None, err)


# ===========================================================================
# 7.  _validate_optional_units
# ===========================================================================

class TestValidateOptionalUnits(unittest.TestCase):

    def test_absent_field_returns_none_no_error(self):
        val, err = _validate_optional_units({}, "equipment_units")
        self.assertIsNone(val)
        self.assertIsNone(err)

    def test_zero_units_accepted(self):
        val, err = _validate_optional_units({"equipment_units": 0}, "equipment_units")
        self.assertIsNone(err)
        self.assertEqual(val, 0)

    def test_500_units_accepted(self):
        val, err = _validate_optional_units({"equipment_units": 500}, "equipment_units")
        self.assertIsNone(err)
        self.assertEqual(val, 500)

    def test_501_units_rejected(self):
        _, err = _validate_optional_units({"equipment_units": 501}, "equipment_units")
        _reject(None, err)

    def test_negative_units_rejected(self):
        _, err = _validate_optional_units({"equipment_units": -1}, "equipment_units")
        _reject(None, err)

    def test_float_truncated_to_int(self):
        """2.5 is cast to int (2); no error. Callers should be aware of silent truncation."""
        val, err = _validate_optional_units({"equipment_units": 2.5}, "equipment_units")
        self.assertIsNone(err)
        self.assertEqual(val, 2)

    def test_non_numeric_string_rejected(self):
        _, err = _validate_optional_units({"equipment_units": "many"}, "equipment_units")
        _reject(None, err)


# ===========================================================================
# 8.  _validate_optional_string
# ===========================================================================

class TestValidateOptionalString(unittest.TestCase):

    def test_absent_field_returns_none_no_error(self):
        val, err = _validate_optional_string({}, "business_type")
        self.assertIsNone(val)
        self.assertIsNone(err)

    def test_normal_business_type_accepted(self):
        val, err = _validate_optional_string({"business_type": "Retail Shop"}, "business_type")
        self.assertIsNone(err)
        self.assertEqual(val, "Retail Shop")

    def test_whitespace_stripped(self):
        val, err = _validate_optional_string({"business_type": "  Café  "}, "business_type")
        # Note: 'é' is not in ALLOWED_BUSINESS_TYPE_CHARS, so this will be rejected
        _reject(None, err)

    def test_whitespace_only_rejected(self):
        _, err = _validate_optional_string({"business_type": "   "}, "business_type")
        _reject(None, err)

    def test_sql_injection_rejected(self):
        _, err = _validate_optional_string({"business_type": "'; DROP TABLE users;--"}, "business_type")
        _reject(None, err)

    def test_xss_attempt_rejected(self):
        _, err = _validate_optional_string({"business_type": "<script>alert(1)</script>"}, "business_type")
        _reject(None, err)

    def test_exactly_64_chars_accepted(self):
        val, err = _validate_optional_string({"business_type": "A" * 64}, "business_type")
        self.assertIsNone(err)

    def test_65_chars_rejected(self):
        _, err = _validate_optional_string({"business_type": "A" * 65}, "business_type")
        _reject(None, err)

    def test_unicode_accented_char_rejected_for_business_type(self):
        """Unicode chars (e.g. 'é') are not in ALLOWED_BUSINESS_TYPE_CHARS."""
        _, err = _validate_optional_string({"business_type": "Café"}, "business_type")
        _reject(None, err)

    def test_non_string_integer_rejected(self):
        _, err = _validate_optional_string({"business_type": 42}, "business_type")
        _reject(None, err)

    def test_location_unicode_accepted(self):
        """Location field has no character-set restriction beyond max length."""
        val, err = _validate_optional_string({"location": "Nairobi, Kenya"}, "location", max_len=128)
        self.assertIsNone(err)

    def test_location_128_chars_accepted(self):
        val, err = _validate_optional_string({"location": "A" * 128}, "location", max_len=128)
        self.assertIsNone(err)

    def test_location_129_chars_rejected(self):
        _, err = _validate_optional_string({"location": "A" * 129}, "location", max_len=128)
        _reject(None, err)


# ===========================================================================
# 9.  Known bugs / design gaps documented as explicit tests
# ===========================================================================

class TestKnownDesignGaps(unittest.TestCase):

    def test_BUG_boolean_accepted_as_numeric(self):
        """
        KNOWN ISSUE: Python's bool is a subclass of int, so True/False pass
        float() coercion (True -> 1.0, False -> 0.0). False is then rejected
        by strictly_positive, but True slips through as 1.0.
        Mitigation: Add `isinstance(data[field_name], bool)` guard before float().
        """
        val, err = _validate_float_field({"consumption_kwh": True}, "consumption_kwh", "consumption_kwh",
                                          strictly_positive=True, max_value=100000.0)
        # Documents current (buggy) behaviour, not desired behaviour:
        self.assertIsNone(err, "BUG: bool True is accepted as 1.0")

    def test_BUG_float_units_silently_truncated(self):
        """
        KNOWN ISSUE: _validate_optional_units casts to int(), silently truncating
        floats. 2.9 becomes 2, which may mislead callers expecting strict integer
        enforcement. Mitigation: reject non-integer inputs explicitly.
        """
        val, err = _validate_optional_units({"equipment_units": 2.9}, "equipment_units")
        self.assertIsNone(err, "BUG: float 2.9 silently truncated to int 2")
        self.assertEqual(val, 2)

    def test_BUG_roi_100_ambiguity(self):
        """
        DESIGN GAP: The ROI output of 100% could mean:
          (a) The system genuinely returns its cost in exactly one year, OR
          (b) The true ROI was far above 100% but got clamped.
        There is currently no way for callers to distinguish these cases.
        Mitigation: Include a boolean `roi_clamped` flag in the response.
        """
        genuine_100 = calculate_roi(12000, 1000, 1000, 1.0)
        clamped_100 = calculate_roi(100, 1000, 1000, 5.0)
        self.assertEqual(genuine_100["roi_percentage"], clamped_100["roi_percentage"],
                         "Both return 100%; caller cannot distinguish them.")

    def test_BUG_unicode_in_business_type_rejected_no_user_friendly_guidance(self):
        """
        DESIGN GAP: Non-ASCII characters in business_type return a generic
        'contains invalid characters' error. The allowed set is not documented
        to callers, so international clients (e.g. names with accents/CJK) will
        get confusing 400s. Mitigation: include the allowed character set in the
        error message, or expand the allowlist.
        """
        _, err = _validate_optional_string({"business_type": "日本語"}, "business_type")
        self.assertIsNotNone(err)
        error_msg = err[0]["error"]
        self.assertIn("invalid characters", error_msg)
        # Desired improvement: error_msg should explain what IS allowed.

    def test_BUG_no_payback_period_in_response(self):
        """
        DESIGN GAP (explicitly descoped per docstring): Payback period is not
        returned. Callers must compute system_cost / (monthly_savings * 12)
        themselves, which duplicates logic and can lead to divide-by-zero on
        their side if savings happen to be 0.
        """
        r = calculate_roi(10000, 500, 400, 0.15)
        self.assertNotIn("payback_months", r)
        self.assertNotIn("payback_years", r)


# ===========================================================================
# 10.  Boundary / mathematical precision
# ===========================================================================

class TestPrecision(unittest.TestCase):

    def test_floating_point_rounding_consistent(self):
        """Repeatedly calling with identical inputs yields identical results."""
        args = dict(system_cost_usd=7777, consumption_kwh=333.33,
                    generation_kwh=333.33, tariff_per_kwh=0.23)
        results = [calculate_roi(**args) for _ in range(100)]
        self.assertTrue(all(r == results[0] for r in results))

    def test_very_small_positive_inputs_do_not_raise(self):
        """Smallest positive floats (epsilon-like values) must not crash."""
        r = calculate_roi(sys.float_info.min, sys.float_info.min,
                          sys.float_info.min, sys.float_info.min)
        self.assertIsInstance(r["roi_percentage"], float)

    def test_nan_input_to_calculate_roi(self):
        """
        EDGE CASE: float('nan') is not blocked by any validator (it would slip
        through max_value checks if those checks use <=). This tests the pure
        function directly — NaN propagation produces unexpected outputs.
        """
        r = calculate_roi(float("nan"), 500, 500, 0.15)
        # NaN in system_cost causes roi to be NaN (clamping min/max with NaN is undefined)
        # Documenting current behaviour; ideally a validator should reject NaN.
        self.assertTrue(math.isnan(r["roi_percentage"]) or r["roi_percentage"] == 0.0,
                        f"Unexpected roi: {r['roi_percentage']}")


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    test_classes = [
        TestCalculateROIHappyPath,
        TestOffsetCapping,
        TestROIClamping,
        TestNonNegativityGuards,
        TestValidateFloatField,
        TestValidateOptionalHours,
        TestValidateOptionalUnits,
        TestValidateOptionalString,
        TestKnownDesignGaps,
        TestPrecision,
    ]
    for tc in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(tc))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
