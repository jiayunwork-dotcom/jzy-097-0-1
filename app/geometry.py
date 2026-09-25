"""Link geometry, wavelength and clearance.

Sign convention (pinned, do not flip): ``h_m`` is the obstacle height
*above* the transmitter-receiver line of sight. Positive means the
obstacle obstructs the direct ray, negative means the ray clears the
obstacle. Swapping this sign would turn obstruction into clearance.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

SPEED_OF_LIGHT_M_PER_S = 299_792_458.0


class GeometryError(ValueError):
    """Raised when a link geometry is physically invalid."""


@dataclass(frozen=True)
class LinkGeometry:
    """Geometry of a single knife-edge obstacle on a radio link.

    Attributes:
        h_m: obstacle height above the Tx-Rx line of sight [m].
             Positive = obstruction, negative = clearance below the line.
        d1_m: horizontal distance transmitter -> obstacle [m], must be > 0.
        d2_m: horizontal distance obstacle -> receiver [m], must be > 0.
        frequency_hz: carrier frequency [Hz], must be > 0.
    """

    h_m: float
    d1_m: float
    d2_m: float
    frequency_hz: float

    def __post_init__(self) -> None:
        problems: list[str] = []
        for name in ("h_m", "d1_m", "d2_m", "frequency_hz"):
            value = getattr(self, name)
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                problems.append(f"{name} must be a number, got {value!r}")
            elif not math.isfinite(value):
                problems.append(f"{name} must be finite, got {value!r}")
        if not problems:
            if self.d1_m <= 0:
                problems.append(f"d1_m must be positive, got {self.d1_m}")
            if self.d2_m <= 0:
                problems.append(f"d2_m must be positive, got {self.d2_m}")
            if self.frequency_hz <= 0:
                problems.append(
                    f"frequency_hz must be positive, got {self.frequency_hz}"
                )
        if problems:
            raise GeometryError("; ".join(problems))

    @property
    def wavelength_m(self) -> float:
        """Wavelength [m] derived from the carrier frequency."""
        return SPEED_OF_LIGHT_M_PER_S / self.frequency_hz

    @property
    def clearance_m(self) -> float:
        """Gap between the line of sight and the obstacle top [m].

        Positive = the direct ray clears the obstacle; negative = the
        obstacle protrudes into the ray path by that many metres.
        """
        return -self.h_m

    @property
    def obstructs_line_of_sight(self) -> bool:
        """True when the obstacle top is strictly above the sight line."""
        return self.h_m > 0.0
