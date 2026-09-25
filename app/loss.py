"""Knife-edge diffraction loss approximation J(v), ITU-R P.526 style.

Standard-library math only; no signal-processing dependencies. This is
the *additional* loss caused by the obstacle on top of whatever the
path would have without it -- it is NOT a free-space path loss and is
never substituted by one.
"""
from __future__ import annotations

import math

#: Below this v the knife-edge contribution is negligible (~0 dB).
V_ZERO_LOSS_THRESHOLD = -0.78


def diffraction_loss_db(v: float) -> float:
    """Additional diffraction loss in dB for Fresnel parameter v.

        J(v) = 6.9 + 20 * log10( sqrt((v - 0.1)^2 + 1) + v - 0.1 )   v > -0.78
        J(v) = 0                                                      v <= -0.78

    Properties worth testing:
      * J(0) ~= 6.0 dB  (obstacle grazing the sight line)
      * J is strictly increasing for v > -0.78
      * J -> 0 dB as v -> -inf (deep clearance, ample Fresnel clearance)
    """
    if v <= V_ZERO_LOSS_THRESHOLD:
        return 0.0
    return 6.9 + 20.0 * math.log10(math.sqrt((v - 0.1) ** 2 + 1.0) + v - 0.1)
