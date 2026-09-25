"""Fresnel parameter and first Fresnel zone radius tests."""
import math

import pytest

from app.fresnel import (
    clearance_ratio,
    first_fresnel_radius_m,
    fresnel_parameter,
)
from app.geometry import LinkGeometry

WAVELENGTH_900MHZ = 299_792_458.0 / 900e6


def test_grazing_obstacle_gives_v_zero():
    assert fresnel_parameter(0.0, 2000.0, 3000.0, WAVELENGTH_900MHZ) == 0.0


def test_v_sign_follows_h_sign():
    v_obstructed = fresnel_parameter(10.0, 2000.0, 3000.0, WAVELENGTH_900MHZ)
    v_clear = fresnel_parameter(-10.0, 2000.0, 3000.0, WAVELENGTH_900MHZ)
    assert v_obstructed > 0.0
    assert v_clear < 0.0
    assert v_obstructed == pytest.approx(-v_clear, rel=1e-12)


def test_v_matches_pinned_formula():
    # v = h * sqrt(2 (d1 + d2) / (lambda d1 d2))
    v = fresnel_parameter(10.0, 2000.0, 3000.0, WAVELENGTH_900MHZ)
    expected = 10.0 * math.sqrt(
        2.0 * 5000.0 / (WAVELENGTH_900MHZ * 2000.0 * 3000.0)
    )
    assert v == pytest.approx(expected, rel=1e-12)
    assert v == pytest.approx(0.7074, rel=1e-3)


def test_doubling_frequency_scales_v_by_sqrt2():
    base = LinkGeometry(h_m=10.0, d1_m=2000.0, d2_m=3000.0, frequency_hz=900e6)
    doubled = LinkGeometry(h_m=10.0, d1_m=2000.0, d2_m=3000.0, frequency_hz=1800e6)
    v1 = fresnel_parameter(base.h_m, base.d1_m, base.d2_m, base.wavelength_m)
    v2 = fresnel_parameter(
        doubled.h_m, doubled.d1_m, doubled.d2_m, doubled.wavelength_m
    )
    assert v2 / v1 == pytest.approx(math.sqrt(2.0), rel=1e-12)


def test_first_fresnel_radius_value():
    # d1 = d2 = 500 m, f = 1 GHz -> r1 = sqrt(250 * lambda) ~= 8.657 m
    radius = first_fresnel_radius_m(500.0, 500.0, 0.299792458)
    assert radius == pytest.approx(8.6573, rel=1e-3)


def test_first_fresnel_radius_shrinks_with_frequency():
    low = first_fresnel_radius_m(2000.0, 3000.0, 299_792_458.0 / 900e6)
    high = first_fresnel_radius_m(2000.0, 3000.0, 299_792_458.0 / 1800e6)
    assert high == pytest.approx(low / math.sqrt(2.0), rel=1e-12)


def test_clearance_ratio_normalises_by_first_zone():
    assert clearance_ratio(-10.0, 20.0) == pytest.approx(-0.5)
    assert clearance_ratio(12.0, 20.0) == pytest.approx(0.6)
