"""Part C: estimate a rare probability honestly. TODO 4, 6 and 7."""
from __future__ import annotations

import math

import numpy as np

from avsim import space
from .search import proposal_logpdf


def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return 0.0, 1.0
    phat = k / n
    z2 = z * z
    denom = 1.0 + z2 / n
    centre = (phat + z2 / (2.0 * n)) / denom
    radius = z * math.sqrt(phat * (1.0 - phat) / n + z2 / (4.0 * n * n)) / denom
    return max(0.0, centre - radius), min(1.0, centre + radius)


def log_weights(Z, Bn, nat: space.Natural, prop: dict, beta: float = 0.2) -> np.ndarray:
    logp = nat.logpdf(Z, Bn)
    logprop = proposal_logpdf(prop, Z, Bn)
    logq = np.logaddexp(math.log1p(-beta) + logprop, math.log(beta) + logp)
    return logp - logq


def is_estimate(logw: np.ndarray, y: np.ndarray, z: float = 1.96) -> dict:
    logw = np.asarray(logw, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(y)
    if n == 0:
        return dict(p=0.0, lo=0.0, hi=1.0, se=0.0, ess=0.0, n=0)
    w = np.exp(logw)
    wy = w * y
    p = float(np.mean(wy))
    se = float(np.std(wy, ddof=1) / math.sqrt(n)) if n > 1 else 0.0
    sum_w = float(np.sum(w))
    sum_w2 = float(np.sum(w * w))
    ess = sum_w * sum_w / sum_w2 if sum_w2 > 0.0 else 0.0
    return dict(p=p, lo=max(0.0, p - z * se), hi=min(1.0, p + z * se), se=se, ess=ess, n=n)


def rule_of_three(n_eff: float) -> float:
    return 3.0 / max(n_eff, 1.0)
