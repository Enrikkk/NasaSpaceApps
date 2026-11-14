"""Small-sample statistics for 19-20 historical scenarios (research/predictive-model-research.md)."""
import math

from scipy.stats import beta


def wilson(k, n, z=1.959964):
    """95 % Wilson score interval for a proportion k/n (here: share of bad years)."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    den = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, mid - half), min(1.0, mid + half))


def jeffreys(k, n, a=0.05):
    """95 % Jeffreys interval (Beta(k+1/2, n-k+1/2) quantiles, endpoints clamped at k=0 / k=n as Brown-Cai-DasGupta)."""
    lo = 0.0 if k == 0 else float(beta.ppf(a / 2, k + 0.5, n - k + 0.5))
    hi = 1.0 if k == n else float(beta.ppf(1 - a / 2, k + 0.5, n - k + 0.5))
    return (lo, hi)


def success(k_bad, n, method="wilson"):
    """Success share 1 - k/n with its 95 % interval (the interval on failures, flipped)."""
    lo, hi = (wilson if method == "wilson" else jeffreys)(k_bad, n)
    return {"valor": 1 - k_bad / n if n else None, "horquilla": [1 - hi, 1 - lo], "k_malos": k_bad, "n": n,
            "metodo": f"{method} 95 %"}


def quantile(xs, q):
    """Linear-interpolation quantile (numpy's default), xs non-empty."""
    s = sorted(xs)
    i = (len(s) - 1) * q
    lo = math.floor(i)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (i - lo)


def cvar(xs, alpha=0.8):
    """Mean of the worst (1 - alpha) share of outcomes (lower tail). n=20, alpha=0.8 -> mean of the 4 worst."""
    s = sorted(xs)
    m = max(1, round(len(s) * (1 - alpha)))
    return sum(s[:m]) / m
