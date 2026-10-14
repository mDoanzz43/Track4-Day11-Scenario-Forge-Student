"""Part C/D: search for failures with the cross-entropy method. TODO 5; the sampling helpers are given."""
from __future__ import annotations

import math

import numpy as np

from avsim import space


def cem_update(Z, Bn, score, prev: dict, rho: float = 0.1, smooth: float = 0.7, min_std: float = 0.25,
               p_clip=(0.03, 0.97)) -> dict:
    n_elite = max(2, int(math.ceil(rho * len(score))))
    elite_idx = np.argsort(-np.asarray(score), kind="stable")[:n_elite]
    elite_z = np.asarray(Z)[elite_idx]
    elite_b = np.asarray(Bn)[elite_idx]
    mean = smooth * elite_z.mean(axis=0) + (1.0 - smooth) * np.asarray(prev["mean"])
    std = smooth * elite_z.std(axis=0) + (1.0 - smooth) * np.asarray(prev["std"])
    p_bin = smooth * elite_b.mean(axis=0) + (1.0 - smooth) * np.asarray(prev["p_bin"])
    return dict(
        mean=mean,
        std=np.maximum(min_std, std),
        p_bin=np.clip(p_bin, p_clip[0], p_clip[1]),
        level=float(np.min(np.asarray(score)[elite_idx])),
    )


def natural_proposal(nat: space.Natural) -> dict:
    return dict(mean=np.zeros(space.D), std=np.ones(space.D), p_bin=nat.p_bin.copy(), level=-math.inf)


def proposal_sample(prop, n, rng):
    Z = prop["mean"] + prop["std"] * rng.standard_normal((n, space.D))
    Bn = (rng.random((n, space.B)) < prop["p_bin"]).astype(int)
    return Z, Bn


def proposal_logpdf(prop, Z, Bn):
    lz = (-0.5 * np.sum(((Z - prop["mean"]) / prop["std"]) ** 2, 1) - np.sum(np.log(prop["std"]))
          - 0.5 * space.D * math.log(2 * math.pi))
    lb = np.sum(Bn * np.log(prop["p_bin"]) + (1 - Bn) * np.log1p(-prop["p_bin"]), 1)
    return lz + lb


def mixture_sample(prop, nat: space.Natural, n, rng, beta=0.2):
    Z, Bn = proposal_sample(prop, n, rng)
    m = rng.random(n) < beta
    Zn, Bnn = nat.sample(int(m.sum()), rng)
    Z[m], Bn[m] = Zn, Bnn
    return Z, Bn
