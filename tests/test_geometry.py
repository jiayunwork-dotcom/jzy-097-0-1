"""Geometry validation, wavelength and clearance tests."""
import math

import pytest

from app.geometry import GeometryError, LinkGeometry


def make_geometry(**overrides) -> LinkGeometry:
    kwargs = dict(h_m=10.0, d1_m=2000.0, d2_m=3000.0, frequency_hz=900e6)
    kwargs.update(overrides)
    return LinkGeometry(**kwargs)


def test_wavelength_from_frequency():
    geometry = make_geometry(frequency_hz=1e9)
    assert geometry.wavelength_m == pytest.approx(0.299792458, rel=1e-9)


def test_clearance_is_negative_of_h():
    assert make_geometry(h_m=10.0).clearance_m == -10.0
    assert make_geometry(h_m=-4.0).clearance_m == 4.0


def test_obstruction_flag_follows_h_sign():
    assert make_geometry(h_m=0.1).obstructs_line_of_sight is True
    assert make_geometry(h_m=0.0).obstructs_line_of_sight is False
    assert make_geometry(h_m=-0.1).obstructs_line_of_sight is False


@pytest.mark.parametrize("d1_m", [0.0, -1.0, -2000.0])
def test_non_positive_d1_rejected_with_reason(d1_m):
    with pytest.raises(GeometryError, match="d1_m must be positive"):
        make_geometry(d1_m=d1_m)


@pytest.mark.parametrize("d2_m", [0.0, -1.0, -3000.0])
def test_non_positive_d2_rejected_with_reason(d2_m):
    with pytest.raises(GeometryError, match="d2_m must be positive"):
        make_geometry(d2_m=d2_m)


@pytest.mark.parametrize("frequency_hz", [0.0, -900e6])
def test_non_positive_frequency_rejected_with_reason(frequency_hz):
    with pytest.raises(GeometryError, match="frequency_hz must be positive"):
        make_geometry(frequency_hz=frequency_hz)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -float("inf")])
def test_non_finite_values_rejected(bad):
    with pytest.raises(GeometryError, match="must be finite"):
        make_geometry(h_m=bad)
    with pytest.raises(GeometryError, match="must be finite"):
        make_geometry(d1_m=bad)


def test_error_message_reports_all_problems():
    with pytest.raises(GeometryError) as excinfo:
        make_geometry(d1_m=-1.0, frequency_hz=0.0)
    message = str(excinfo.value)
    assert "d1_m" in message and "frequency_hz" in message
