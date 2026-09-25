"""HTTP input/output validation models (interface layer only).

Physical validity (positive distances/frequency, finite values) is
enforced by :class:`app.geometry.LinkGeometry` so the core stays
usable without FastAPI; these models only guarantee well-typed JSON.
"""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class LinkInput(BaseModel):
    """Geometry + frequency for one link."""

    h_m: float = Field(
        ...,
        description="Obstacle height above the Tx-Rx line of sight [m]; "
        "positive obstructs, negative clears.",
    )
    d1_m: float = Field(..., description="Distance transmitter -> obstacle [m]")
    d2_m: float = Field(..., description="Distance obstacle -> receiver [m]")
    frequency_hz: float = Field(..., description="Carrier frequency [Hz]")


class BatchLinkInput(LinkInput):
    """One link inside a batch request, with an optional caller id."""

    id: Optional[str] = Field(default=None, description="Caller-supplied label")


class BatchRequest(BaseModel):
    links: List[BatchLinkInput] = Field(..., min_length=1)


class ParametersResponse(BaseModel):
    """Fresnel parameter view: v, clearance, first Fresnel zone radius."""

    v: float
    clearance_m: float
    clearance_ratio: float
    first_fresnel_radius_m: float
    wavelength_m: float


class LossResponse(ParametersResponse):
    """Parameter view plus additional loss and LOS verdict."""

    loss_db: float
    los: bool


class BatchItemResponse(BaseModel):
    index: int
    id: Optional[str]
    ok: bool
    result: Optional[LossResponse] = None
    error: Optional[str] = None


class BatchResponse(BaseModel):
    count: int
    results: List[BatchItemResponse]


class PresetResponse(BaseModel):
    name: str
    description: str
    input: LinkInput
    evaluation: LossResponse
