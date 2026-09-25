"""End-to-end relations through the evaluation pipeline."""
import math

import pytest

from app.evaluator import evaluate_loss, evaluate_parameters
from app.geometry import LinkGeometry


def make_geometry(h_m=10.0, d1_m=2000.0, d2_m=3000.0, frequency_hz=900e6):
    return LinkGeometry(h_m=h_m, d1_m=d1_m, d2_m=d2_m, frequency_hz=frequency_hz)


def test_grazing_obstacle_v_zero_and_loss_about_6db():
    result = evaluate_loss(make_geometry(h_m=0.0))
    assert result.v == 0.0
    assert result.loss_db == pytest.approx(6.03, abs=0.05)


def test_raising_obstacle_raises_loss():
    losses = [
        evaluate_loss(make_geometry(h_m=h)).loss_db for h in (2.0, 5.0, 10.0, 20.0)
    ]
    assert all(b > a for a, b in zip(losses, losses[1:]))


def test_doubling_frequency_scales_v_by_sqrt2_same_geometry():
    v1 = evaluate_parameters(make_geometry(frequency_hz=900e6)).v
    v2 = evaluate_parameters(make_geometry(frequency_hz=1800e6)).v
    assert v2 / v1 == pytest.approx(math.sqrt(2.0), rel=1e-12)


def test_symmetric_path_deep_clearance_loss_tends_to_zero():
    result = evaluate_loss(
        make_geometry(h_m=-50.0, d1_m=1000.0, d2_m=1000.0, frequency_hz=1e9)
    )
    assert result.v < -0.78
    assert result.loss_db == 0.0
    assert result.los is True


def test_clear_link_is_not_charged_6db():
    # Ample clearance: h well below the sight line -> loss must be ~0 dB,
    # never a hard-coded 6 dB.
    result = evaluate_loss(
        make_geometry(h_m=-30.0, d1_m=1000.0, d2_m=1000.0, frequency_hz=3e9)
    )
    assert result.loss_db == 0.0


def test_los_verdict_follows_obstruction():
    assert evaluate_loss(make_geometry(h_m=10.0)).los is False
    assert evaluate_loss(make_geometry(h_m=-10.0)).los is True
    assert evaluate_loss(make_geometry(h_m=0.0)).los is True


def test_parameters_view_carries_clearance_and_radius():
    result = evaluate_parameters(make_geometry(h_m=10.0))
    assert result.clearance_m == -10.0
    assert result.first_fresnel_radius_m == pytest.approx(19.99, rel=1e-3)
    assert result.clearance_ratio == pytest.approx(-0.5, abs=0.01)
    assert result.wavelength_m == pytest.approx(0.3331, rel=1e-3)
