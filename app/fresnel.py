"""Fresnel-Kirchhoff diffraction parameter and first Fresnel zone radius.

Pure functions of geometry and wavelength; no state, no I/O.
"""
from __future__ import annotations

import math


def fresnel_parameter(
    h_m: float, d1_m: float, d2_m: float, wavelength_m: float
) -> float:
    """Fresnel-Kirchhoff parameter v.

        v = h * sqrt( 2 (d1 + d2) / (lambda * d1 * d2) )

    The sign of v follows the sign of h: v > 0 for an obstructing
    obstacle, v < 0 when the line of sight clears it, v = 0 exactly
    when the obstacle grazes the sight line.
    """
    return h_m * math.sqrt(
        2.0 * (d1_m + d2_m) / (wavelength_m * d1_m * d2_m)
    )


def first_fresnel_radius_m(
    d1_m: float, d2_m: float, wavelength_m: float
) -> float:
    """Radius of the first Fresnel zone at the obstacle plane [m].

        r1 = sqrt( lambda * d1 * d2 / (d1 + d2) )
    """
    return math.sqrt(wavelength_m * d1_m * d2_m / (d1_m + d2_m))


def clearance_ratio(clearance_m: float, first_radius_m: float) -> float:
    """Clearance expressed as a fraction of the first Fresnel zone radius.

    Values >= ~0.6 correspond to free-space-like propagation; negative
    values mean the obstacle cuts into the first Fresnel zone.
    """
    return clearance_m / first_radius_m
