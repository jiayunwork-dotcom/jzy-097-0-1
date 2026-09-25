"""Batch scheduling tests: independence, isolation, ordering."""
import pytest

from app.batch import BatchJob, evaluate_batch
from app.evaluator import evaluate_loss
from app.geometry import LinkGeometry


def job(id_, h_m=10.0, d1_m=2000.0, d2_m=3000.0, frequency_hz=900e6):
    return BatchJob(
        id=id_, h_m=h_m, d1_m=d1_m, d2_m=d2_m, frequency_hz=frequency_hz
    )


def test_invalid_item_does_not_abort_batch():
    outcomes = evaluate_batch(
        [
            job("ok-1"),
            job("bad", d1_m=-5.0),
            job("ok-2", h_m=-50.0, d1_m=1000.0, d2_m=1000.0, frequency_hz=1e9),
        ]
    )
    assert [o.ok for o in outcomes] == [True, False, True]
    assert "d1_m must be positive" in outcomes[1].error
    assert outcomes[1].evaluation is None


def test_results_are_independent_and_do_not_overwrite():
    outcomes = evaluate_batch([job("a"), job("b"), job("a")])
    assert [o.id for o in outcomes] == ["a", "b", "a"]
    assert [o.index for o in outcomes] == [0, 1, 2]
    assert all(o.ok for o in outcomes)
    # identical geometry -> identical numbers, but three distinct entries
    vs = [o.evaluation.v for o in outcomes]
    assert vs[0] == pytest.approx(vs[1])
    assert vs[1] == pytest.approx(vs[2])


def test_batch_matches_individual_evaluation():
    geometry = LinkGeometry(h_m=7.5, d1_m=1500.0, d2_m=2500.0, frequency_hz=2.4e9)
    solo = evaluate_loss(geometry)
    (outcome,) = evaluate_batch(
        [job("x", h_m=7.5, d1_m=1500.0, d2_m=2500.0, frequency_hz=2.4e9)]
    )
    assert outcome.evaluation == solo


def test_empty_batch_yields_empty_results():
    assert evaluate_batch([]) == []
