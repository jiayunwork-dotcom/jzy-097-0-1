"""Batch scheduling: evaluate a set of links in one pass.

Each job is dispatched through the evaluation pipeline independently:
a failure on one link is captured on that item's outcome and never
aborts or contaminates the others. Results come back in submission
order, keyed by index and caller-supplied id, so entries cannot
overwrite each other.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from .evaluator import LossEvaluation, evaluate_loss
from .geometry import GeometryError, LinkGeometry


@dataclass(frozen=True)
class BatchJob:
    """One link to evaluate, with an optional caller-supplied id."""

    id: Optional[str]
    h_m: float
    d1_m: float
    d2_m: float
    frequency_hz: float


@dataclass(frozen=True)
class BatchItemOutcome:
    """Per-link outcome: either an evaluation or the reason it failed."""

    index: int
    id: Optional[str]
    ok: bool
    evaluation: Optional[LossEvaluation]
    error: Optional[str]


def evaluate_batch(jobs: Iterable[BatchJob]) -> list[BatchItemOutcome]:
    """Evaluate every job independently, preserving submission order."""
    outcomes: list[BatchItemOutcome] = []
    for index, job in enumerate(jobs):
        try:
            geometry = LinkGeometry(
                h_m=job.h_m,
                d1_m=job.d1_m,
                d2_m=job.d2_m,
                frequency_hz=job.frequency_hz,
            )
            evaluation = evaluate_loss(geometry)
        except GeometryError as exc:
            outcomes.append(
                BatchItemOutcome(
                    index=index,
                    id=job.id,
                    ok=False,
                    evaluation=None,
                    error=str(exc),
                )
            )
        else:
            outcomes.append(
                BatchItemOutcome(
                    index=index,
                    id=job.id,
                    ok=True,
                    evaluation=evaluation,
                    error=None,
                )
            )
    return outcomes
