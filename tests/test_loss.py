"""Diffraction loss approximation tests.

The two load-bearing behaviours: grazing incidence (v = 0) costs about
6 dB, and deep clearance (v well below -0.8) costs nothing.
"""
import pytest

from app.loss import V_ZERO_LOSS_THRESHOLD, diffraction_loss_db


def test_grazing_v_zero_costs_about_6db():
    loss = diffraction_loss_db(0.0)
    assert loss == pytest.approx(6.03, abs=0.05)
    assert 5.8 < loss < 6.3


def test_deep_clearance_costs_nothing():
    assert diffraction_loss_db(-0.78) == 0.0
    assert diffraction_loss_db(-0.8) == 0.0
    assert diffraction_loss_db(-5.0) == 0.0
    assert diffraction_loss_db(-50.0) == 0.0


def test_loss_never_negative():
    for v in (-0.78, -0.5, -0.1, 0.0, 0.5, 1.0, 3.0, 10.0):
        assert diffraction_loss_db(v) >= 0.0


def test_loss_strictly_increasing_above_threshold():
    vs = [-0.7, -0.4, 0.0, 0.5, 1.0, 2.0, 4.0, 8.0]
    losses = [diffraction_loss_db(v) for v in vs]
    assert all(b > a for a, b in zip(losses, losses[1:]))


def test_just_above_threshold_loss_is_small():
    assert 0.0 < diffraction_loss_db(-0.7) < 1.0


def test_threshold_constant_is_about_minus_0_8():
    assert V_ZERO_LOSS_THRESHOLD == pytest.approx(-0.8, abs=0.05)
