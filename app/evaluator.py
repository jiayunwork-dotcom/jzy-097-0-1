"""Composition layer: turn a LinkGeometry into evaluation results.

Bridges geometry / fresnel / loss without letting any of them know
about each other or about HTTP.
"""
from __future__ import annotations

from dataclasses import dataclass

from .fresnel import (
    clearance_ratio,
    first_fresnel_radius_m,
    fresnel_parameter,
)
from .geometry import LinkGeometry
from .loss import diffraction_loss_db


@dataclass(frozen=True)
class ParameterEvaluation:
    """Fresnel parameter view of a link (no loss, no LOS verdict)."""

    v: float
    clearance_m: float
    clearance_ratio: float
    first_fresnel_radius_m: float
    wavelength_m: float


@dataclass(frozen=True)
class LossEvaluation(ParameterEvaluation):
    """Full view: parameters plus additional loss and LOS verdict."""

    loss_db: float
    los: bool


def evaluate_parameters(geometry: LinkGeometry) -> ParameterEvaluation:
    """Compute v, clearance and first Fresnel zone radius for a link."""
    wavelength = geometry.wavelength_m
    radius = first_fresnel_radius_m(geometry.d1_m, geometry.d2_m, wavelength)
    clearance = geometry.clearance_m
    return ParameterEvaluation(
        v=fresnel_parameter(geometry.h_m, geometry.d1_m, geometry.d2_m, wavelength),
        clearance_m=clearance,
        clearance_ratio=clearance_ratio(clearance, radius),
        first_fresnel_radius_m=radius,
        wavelength_m=wavelength,
    )


def evaluate_loss(geometry: LinkGeometry) -> LossEvaluation:
    """Compute parameters plus additional diffraction loss and LOS verdict."""
    params = evaluate_parameters(geometry)
    return LossEvaluation(
        v=params.v,
        clearance_m=params.clearance_m,
        clearance_ratio=params.clearance_ratio,
        first_fresnel_radius_m=params.first_fresnel_radius_m,
        wavelength_m=params.wavelength_m,
        loss_db=diffraction_loss_db(params.v),
        los=not geometry.obstructs_line_of_sight,
    )
