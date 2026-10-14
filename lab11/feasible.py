"""Part B: physics check. TODO 3."""
from __future__ import annotations

import math

G = 9.81


def is_feasible(p: dict) -> bool:
    a_lat = (math.pi / p["cutDur"]) ** 2 * 3.5 / 2.0
    grip = p["mu"] * G
    return bool(
        a_lat <= grip
        and p["cutBrake"] <= grip
        and p["pedV"] <= 2.5
        and 0.0 < p["cutV"] <= 22.0
    )
