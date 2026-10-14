"""Part A: read a rollout. TODO 1, 2 and 9 live here; the helpers below them are given."""
from __future__ import annotations

import numpy as np

from avsim import core

G = 9.81
HALF_EGO = core.CAR[0] / 2


def ego_events(R: core.Rollout, k: int) -> list[dict]:
    return [e for e in R.events[k] if e["a"] == "ego" or e["b"] == "ego"]


def min_ttc(R: core.Rollout, cap: float = 10.0) -> np.ndarray:
    F = R.F
    ego = F[:, :, core.IX["ego"]]
    leaders = R.EGO[:, :, 3].astype(int)
    valid = leaders >= 0
    safe_leaders = np.where(valid, leaders, 0)
    leader = np.take_along_axis(F, safe_leaders[..., None, None], axis=2).squeeze(2)

    rx = leader[..., 0] - ego[..., 0]
    rz = leader[..., 1] - ego[..., 1]
    lon = rx * ego[..., 2] + rz * ego[..., 3]
    half_len = np.where(safe_leaders == core.IX["P1"], 0.3, core.LEN[safe_leaders] / 2.0)
    gap = np.maximum(lon - HALF_EGO - half_len, 0.0)
    closing = ego[..., 4] - leader[..., 4]
    ttc = np.where(valid & (closing > 0.1), gap / np.maximum(closing, 1e-6), np.inf)
    result = np.minimum(cap, np.min(ttc, axis=1))
    crashed = np.array([bool(ego_events(R, k)) for k in range(F.shape[0])])
    result[crashed] = 0.0
    return result


def contact_type(R: core.Rollout, k: int, event: dict) -> str:
    f = event["f"]
    other_name = event["b"] if event["a"] == "ego" else event["a"]
    ego = R.F[k, f, core.IX["ego"]]
    other = R.F[k, f, core.IX[other_name]]
    rx, rz = other[0] - ego[0], other[1] - ego[1]
    lon = rx * ego[2] + rz * ego[3]
    lat = -rx * ego[3] + rz * ego[2]
    if lon > HALF_EGO and abs(lat) < 1.6:
        return "front"
    if lon < -HALF_EGO and abs(lat) < 1.6:
        return "rear"
    return "side"


def progress_metrics(R: core.Rollout) -> tuple[np.ndarray, np.ndarray]:
    ego = R.F[:, :, core.IX["ego"]]
    steps = np.diff(ego[..., :2], axis=1)
    distance = np.linalg.norm(steps, axis=-1).sum(axis=1)
    harsh = (ego[..., 5] < -3.0).sum(axis=1)
    return distance, harsh


def pair_min_ttc(R, follower, leader, cap=10.0, lat_max=2.2, leader_vmin=-1.0):
    F = R.F
    a, b = F[:, :, core.IX[follower]], F[:, :, core.IX[leader]]
    rx, rz = b[..., 0] - a[..., 0], b[..., 1] - a[..., 1]
    lon = rx * a[..., 2] + rz * a[..., 3]
    lat = -rx * a[..., 3] + rz * a[..., 2]
    gap = np.maximum(lon - core.LEN[core.IX[follower]] / 2 - core.LEN[core.IX[leader]] / 2, 0.0)
    dv = a[..., 4] - b[..., 4]
    ok = (lon > 0) & (np.abs(lat) < lat_max) & (dv > 0.1) & (b[..., 4] >= leader_vmin)
    ttc = np.where(ok, gap / np.maximum(dv, 1e-6), np.inf)
    return np.minimum(cap, ttc.min(1))


def ped_room(R, cap=30.0):
    e, p = R.F[:, :, core.IX["ego"]], R.F[:, :, core.IX["P1"]]
    mu = np.asarray(R.params["mu"])[:, None]
    inlane = np.abs(p[..., 1] - e[..., 1]) < 1.9
    ahead = p[..., 0] - e[..., 0] - HALF_EGO
    room = np.where(inlane & (ahead > -1.0), ahead - e[..., 4] ** 2 / (2 * mu * G), cap)
    return np.clip(room.min(1), -cap, cap)
