"""FastAPI interface layer.

Two call families plus batch:

- POST /api/v1/diffraction/parameters : v, clearance, first Fresnel radius
- POST /api/v1/diffraction/loss       : the same + additional loss + LOS
- POST /api/v1/diffraction/batch      : a set of links evaluated at once
- GET  /api/v1/presets/ridge          : preset slightly-obstructing ridge

Invalid distances/frequency are rejected with a reason-bearing JSON.
"""
from __future__ import annotations

from dataclasses import asdict

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .batch import BatchJob, evaluate_batch
from .evaluator import evaluate_loss, evaluate_parameters
from .geometry import GeometryError, LinkGeometry
from .presets import RIDGE_PRESET, RIDGE_PRESET_DESCRIPTION, RIDGE_PRESET_NAME
from .schemas import (
    BatchRequest,
    BatchResponse,
    BatchItemResponse,
    LinkInput,
    LossResponse,
    ParametersResponse,
    PresetResponse,
)

app = FastAPI(
    title="Knife-Edge Diffraction Service",
    version="1.0.0",
    description="Single knife-edge obstacle diffraction kernel over HTTP.",
)


def _to_geometry(payload: LinkInput) -> LinkGeometry:
    return LinkGeometry(
        h_m=payload.h_m,
        d1_m=payload.d1_m,
        d2_m=payload.d2_m,
        frequency_hz=payload.frequency_hz,
    )


@app.exception_handler(GeometryError)
async def geometry_error_handler(
    _request: Request, exc: GeometryError
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"error": "invalid_geometry", "reason": str(exc)},
    )


@app.exception_handler(RequestValidationError)
async def request_validation_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    reasons = [
        f"{'.'.join(str(part) for part in err['loc'])}: {err['msg']}"
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={"error": "invalid_request", "reasons": reasons},
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/v1/diffraction/parameters", response_model=ParametersResponse)
def diffraction_parameters(payload: LinkInput) -> ParametersResponse:
    """Return v, clearance and first Fresnel zone radius for a link."""
    evaluation = evaluate_parameters(_to_geometry(payload))
    return ParametersResponse(**asdict(evaluation))


@app.post("/api/v1/diffraction/loss", response_model=LossResponse)
def diffraction_loss(payload: LinkInput) -> LossResponse:
    """Return parameters plus additional diffraction loss and LOS verdict."""
    evaluation = evaluate_loss(_to_geometry(payload))
    return LossResponse(**asdict(evaluation))


@app.post("/api/v1/diffraction/batch", response_model=BatchResponse)
def diffraction_batch(payload: BatchRequest) -> BatchResponse:
    """Evaluate a set of links at once; each result is independent."""
    jobs = [
        BatchJob(
            id=link.id,
            h_m=link.h_m,
            d1_m=link.d1_m,
            d2_m=link.d2_m,
            frequency_hz=link.frequency_hz,
        )
        for link in payload.links
    ]
    outcomes = evaluate_batch(jobs)
    return BatchResponse(
        count=len(outcomes),
        results=[
            BatchItemResponse(
                index=outcome.index,
                id=outcome.id,
                ok=outcome.ok,
                result=(
                    LossResponse(**asdict(outcome.evaluation))
                    if outcome.evaluation is not None
                    else None
                ),
                error=outcome.error,
            )
            for outcome in outcomes
        ],
    )


@app.get("/api/v1/presets/ridge", response_model=PresetResponse)
def preset_ridge() -> PresetResponse:
    """Preset example: ridge slightly obstructing the path (loss > 6 dB)."""
    evaluation = evaluate_loss(RIDGE_PRESET)
    return PresetResponse(
        name=RIDGE_PRESET_NAME,
        description=RIDGE_PRESET_DESCRIPTION,
        input=LinkInput(
            h_m=RIDGE_PRESET.h_m,
            d1_m=RIDGE_PRESET.d1_m,
            d2_m=RIDGE_PRESET.d2_m,
            frequency_hz=RIDGE_PRESET.frequency_hz,
        ),
        evaluation=LossResponse(**asdict(evaluation)),
    )
