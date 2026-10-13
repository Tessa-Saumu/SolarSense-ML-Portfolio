"""Country hints select bounded assumptions; overlapping boxes never guess tariffs."""
import pytest

from models.recommendations.model4_app import resolve_country_and_tariff


@pytest.mark.parametrize("lat,lon,country,tariff", [
    (-1.2921, 36.8219, "Kenya", 0.17),
    (-1.9706, 30.1044, "Rwanda", 0.115),
    (0.3476, 32.5825, "Uganda", 0.45),
    (-6.7924, 39.2083, "Tanzania", 0.10),
    (5.6037, -0.1870, "Ghana", 0.085),
])
def test_explicit_supported_country(lat, lon, country, tariff):
    """Known city inputs retain the asserted country's configured assumption."""
    assert resolve_country_and_tariff(lat, lon, country) == {"country": country, "tariff": tariff}


@pytest.mark.parametrize("lat,lon", [(-1.2921, 36.8219), (-1.9706, 30.1044), (0.3476, 32.5825), (5, 2)])
def test_overlapping_boxes_without_hint_reject(lat, lon):
    """Nairobi, Kigali, Kampala and a shared boundary must not pick first match."""
    assert resolve_country_and_tariff(lat, lon) is None


@pytest.mark.parametrize("hint", ["Ghana", "Unknown", "", 123])
def test_unsupported_or_mismatched_hint_reject(hint):
    """Hints cannot select a country's assumptions outside its existing bounds."""
    assert resolve_country_and_tariff(-1.2921, 36.8219, hint) is None


def test_unique_box_and_unsupported_coordinates():
    """Single matches preserve existing heuristic behavior; no match rejects."""
    assert resolve_country_and_tariff(-6.7924, 39.2083)["country"] == "Tanzania"
    assert resolve_country_and_tariff(80, 80, "Kenya") is None
