"""Preset example links shipped with the service."""
from __future__ import annotations

from .geometry import LinkGeometry

#: Ridge slightly obstructing the path: the crest sticks 10 m above the
#: sight line on a 2 km + 3 km path at 900 MHz. v ~= 0.71, so the
#: additional diffraction loss comes out around 11.9 dB (> 6 dB).
RIDGE_PRESET = LinkGeometry(
    h_m=10.0,
    d1_m=2000.0,
    d2_m=3000.0,
    frequency_hz=900e6,
)

RIDGE_PRESET_NAME = "ridge_slight_obstruction"
RIDGE_PRESET_DESCRIPTION = (
    "山脊略微遮挡：900 MHz 链路，障碍距发射端 2000 m、距接收端 3000 m，"
    "脊顶高出直视线 10 m，附加绕射损耗约 11.9 dB（大于 6 dB）。"
)
