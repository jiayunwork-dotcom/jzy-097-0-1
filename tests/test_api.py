"""HTTP interface tests (run inside the container with FastAPI installed)."""
import math

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

PAYLOAD = {"h_m": 10.0, "d1_m": 2000.0, "d2_m": 3000.0, "frequency_hz": 900e6}


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_parameters_endpoint_returns_v_clearance_radius_only():
    response = client.post("/api/v1/diffraction/parameters", json=PAYLOAD)
    assert response.status_code == 200
    body = response.json()
    assert body["v"] == pytest.approx(0.7074, rel=1e-3)
    assert body["clearance_m"] == -10.0
    assert body["first_fresnel_radius_m"] == pytest.approx(19.99, rel=1e-3)
    assert body["clearance_ratio"] == pytest.approx(-0.5, abs=0.01)
    assert "loss_db" not in body
    assert "los" not in body


def test_loss_endpoint_adds_loss_and_los():
    response = client.post("/api/v1/diffraction/loss", json=PAYLOAD)
    assert response.status_code == 200
    body = response.json()
    assert body["v"] == pytest.approx(0.7074, rel=1e-3)
    assert body["loss_db"] == pytest.approx(11.89, abs=0.05)
    assert body["los"] is False


def test_grazing_obstacle_over_http_costs_about_6db():
    response = client.post("/api/v1/diffraction/loss", json={**PAYLOAD, "h_m": 0.0})
    body = response.json()
    assert body["v"] == 0.0
    assert body["loss_db"] == pytest.approx(6.03, abs=0.05)


def test_clear_link_over_http_is_not_charged_6db():
    payload = {**PAYLOAD, "h_m": -50.0, "d1_m": 1000.0, "d2_m": 1000.0,
               "frequency_hz": 1e9}
    body = client.post("/api/v1/diffraction/loss", json=payload).json()
    assert body["loss_db"] == 0.0
    assert body["los"] is True


def test_frequency_doubling_over_http_scales_v_by_sqrt2():
    v1 = client.post("/api/v1/diffraction/parameters", json=PAYLOAD).json()["v"]
    v2 = client.post(
        "/api/v1/diffraction/parameters",
        json={**PAYLOAD, "frequency_hz": 1800e6},
    ).json()["v"]
    assert v2 / v1 == pytest.approx(math.sqrt(2.0), rel=1e-9)


@pytest.mark.parametrize("field,value", [("d1_m", -5.0), ("d1_m", 0.0),
                                         ("d2_m", -1.0), ("frequency_hz", 0.0),
                                         ("frequency_hz", -900e6)])
def test_non_positive_inputs_rejected_with_reason(field, value):
    response = client.post("/api/v1/diffraction/loss", json={**PAYLOAD, field: value})
    assert response.status_code == 400
    body = response.json()
    assert body["error"] == "invalid_geometry"
    assert field in body["reason"]


def test_malformed_payload_rejected_with_reasons():
    response = client.post("/api/v1/diffraction/loss", json={"h_m": "abc"})
    assert response.status_code == 422
    body = response.json()
    assert body["error"] == "invalid_request"
    assert body["reasons"]


def test_batch_endpoint_results_independent():
    payload = {
        "links": [
            {"id": "ridge", **PAYLOAD},
            {"id": "clear", **PAYLOAD, "h_m": -50.0, "d1_m": 1000.0,
             "d2_m": 1000.0, "frequency_hz": 1e9},
            {"id": "broken", **PAYLOAD, "d2_m": 0.0},
        ]
    }
    response = client.post("/api/v1/diffraction/batch", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 3
    results = body["results"]
    assert [r["id"] for r in results] == ["ridge", "clear", "broken"]
    assert [r["ok"] for r in results] == [True, True, False]
    assert results[0]["result"]["loss_db"] == pytest.approx(11.89, abs=0.05)
    assert results[1]["result"]["loss_db"] == 0.0
    assert results[1]["result"]["los"] is True
    assert "d2_m must be positive" in results[2]["error"]


def test_preset_ridge_loss_above_6db():
    response = client.get("/api/v1/presets/ridge")
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "ridge_slight_obstruction"
    assert body["evaluation"]["loss_db"] > 6.0
    assert body["evaluation"]["v"] > 0.0
