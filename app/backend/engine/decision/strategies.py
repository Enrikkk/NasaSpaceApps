"""Strategies (S0-S3), the rotation DP and the scenario sampler (T-020).

DP (research/predictive-model-research.md, "Rotaciones"): V_t(o) = score(o) + max over o' with allowed(last(o), first(o'))
of V_{t+1}(o'), for t = HORIZON-1 .. 0. score = weighted sum of the four plan-year criteria normalised to 0-1
(1 = best in all four: more margin, LESS water, more soil-N benefit, LESS risk = higher CVaR80 of the margin).
Strategies differ only by weights and a "not ruinous" filter:
  S0 the current rotation (marked, never filtered)      S1 maximum expected margin
  S2 soil and water first (margin >= 0)                  S3 low risk (margin >= 0)

Scenario samples: N_SAMPLES draws; each draw picks, for every plan-year of the horizon, one historical year (climate
and price of the SAME year stay paired) with random numbers shared by all rotations, and a cost multiplier U(0.85, 1.15).
This is resampling of 19 real years, not new information: it spreads the sequence over different year orders.
"""
import random

from ..core import stats
from . import rotations as rt, rules

N_SAMPLES = 200
COST_BAND = (0.85, 1.15)
STRATEGIES = {
    "S1": {"nombre": "Más margen esperado dentro de las reglas", "w": {"margen": 1.0, "agua": 0, "suelo_n": 0, "riesgo": 0},
           "ruinosa": False},
    "S2": {"nombre": "Suelo y agua primero", "w": {"margen": 0.15, "agua": 0.40, "suelo_n": 0.40, "riesgo": 0.05},
           "ruinosa": True},
    "S3": {"nombre": "Riesgo bajo", "w": {"margen": 0.20, "agua": 0.10, "suelo_n": 0.10, "riesgo": 0.60}, "ruinosa": True},
}


def norm(vals, higher_better=True):
    lo, hi = min(vals), max(vals)
    if hi == lo:
        return [0.5] * len(vals)
    return [((v - lo) / (hi - lo)) if higher_better else ((hi - v) / (hi - lo)) for v in vals]


def option_scores(opts, static, runs):
    """{option: dict(raw metrics, crit{margen, agua, suelo_n, riesgo})} for options with at least one money year."""
    raw = {o: rt.option_metrics(o, static, runs) for o in opts}
    raw = {o: m for o, m in raw.items() if m}
    keys = list(raw)
    cols = {"margen": norm([raw[o]["margen"] for o in keys]), "agua": norm([raw[o]["agua"] for o in keys], False),
            "suelo_n": norm([raw[o]["suelo_n"] for o in keys]), "riesgo": norm([raw[o]["cvar"] for o in keys])}
    for i, o in enumerate(keys):
        raw[o]["crit"] = {c: cols[c][i] for c in cols}
    return raw


def _first_last(o, static):
    seq = [static[k]["crop"] for k in o.keys]
    return (seq[0], seq[-1]) if seq else (None, None)


def dp(scores, static, crops, weights, ruinous_filter, prev_crop=None, horizon=rt.HORIZON):
    """Best path of `horizon` year options. Returns list of Option or None."""
    opts = [o for o, m in scores.items() if not (ruinous_filter and m["margen"] < 0)]
    if not opts:
        return None
    sc = {o: sum(weights[c] * scores[o]["crit"][c] for c in weights) for o in opts}
    fl = {o: _first_last(o, static) for o in opts}
    nxt = {i: [j for j in opts if rules.allowed(crops, fl[i][1], fl[j][0])] for i in opts}
    V = [dict() for _ in range(horizon)]
    arg = [dict() for _ in range(horizon)]
    for i in opts:
        V[horizon - 1][i] = sc[i]
    for t in range(horizon - 2, -1, -1):
        for i in opts:
            cands = nxt[i]
            if not cands:
                V[t][i] = float("-inf")
                continue
            j = max(cands, key=lambda c: V[t + 1][c])
            V[t][i], arg[t][i] = sc[i] + V[t + 1][j], j
    starts = [i for i in opts if rules.allowed(crops, prev_crop, fl[i][0])]
    best = max(starts, key=lambda i: V[0][i])
    if V[0][best] == float("-inf"):
        return None
    path = [best]
    for t in range(horizon - 1):
        path.append(arg[t][path[-1]])
    return path


def draws(n=N_SAMPLES, horizon=rt.HORIZON, seed=2026):
    """Shared random numbers: [(u_t..., cost_multiplier)] per draw."""
    rng = random.Random(seed)
    return [([rng.random() for _ in range(horizon)], rng.uniform(*COST_BAND)) for _ in range(n)]


def simulate(path, runs, shared):
    """Per-draw annual margin and water for a path, plus pooled bad-year counts. None if any plan-year has no money year."""
    yv = [rt.year_values(o, runs) for o in path]
    pools = [sorted(y for y, v in d.items() if v["money"]) for d in yv]
    if any(not p for p in pools):
        return None
    margins, waters = [], []
    for us, mult in shared:
        tot_m = tot_w = 0.0
        for t, u in enumerate(us):
            y = pools[t][int(u * len(pools[t]))]
            v = yv[t][y]
            tot_m += v["rev"] - v["cost"] * mult
            tot_w += v["agua"]
        margins.append(tot_m / len(path))
        waters.append(tot_w / len(path))
    k = n = 0
    for t, d in enumerate(yv):
        for y in pools[t]:
            n += 1
            k += bool(d[y]["clima_malo"] or d[y]["margen"] < 0)
    first = sorted(pools[0], key=lambda y: yv[0][y]["margen"])[:3]
    return {"margen": margins, "agua": waters, "k_malos": k, "n": n, "peores_anios": first,
            "margen_medio": sum(sum(d[y]["margen"] for y in pools[t]) / len(pools[t]) for t, d in enumerate(yv)) / len(path)}


def raw_criteria(path, static, runs, sim, scores):
    """Rotation-level raw values (before the 0-1 normalisation across the exported rotations)."""
    sts = [rt.option_static(o, static) for o in path]
    suelo = sum(0.5 * min(1.0, s["n_credit"] / rules.N_CREDIT[rt.COVER_PRODUCT]) + 0.5 * (1 - s["bare_days"] / 365)
                for s in sts) / len(sts)
    water = sum(sum(v["agua"] for v in rt.year_values(o, runs).values()) / len(rt.year_values(o, runs)) for o in path) / len(path)
    if sim is None:
        return {"margen": None, "agua": water, "suelo_n": suelo, "riesgo": None}
    return {"margen": sim["margen_medio"], "agua": water, "suelo_n": suelo, "riesgo": stats.cvar(sim["margen"], 0.8)}


def normalise_rotations(raws):
    """0-1 criteria across the given rotations (1 = best). None where the raw value is missing."""
    out = [{} for _ in raws]
    for c, better in (("margen", True), ("agua", False), ("suelo_n", True), ("riesgo", True)):
        idx = [i for i, r in enumerate(raws) if r[c] is not None]
        vals = norm([raws[i][c] for i in idx], better) if idx else []
        for i in range(len(raws)):
            out[i][c] = None
        for i, v in zip(idx, vals):
            out[i][c] = round(v, 3)
    return out
