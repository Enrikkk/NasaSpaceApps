"""Price scenarios per crop (T-018 part 1): which past price levels can happen in the target year.

Decision (Enrique, 2026-11-14): keep the real historical years as scenarios; correct for a trend ONLY where an
honest walk-forward backtest shows the trend line beats the simple median. No ML price regressor: in the same
backtest a gradient-boosting regressor on the 3 previous years lost to the median in 5 of 6 crops (+18 % to +42 %
mean absolute error) and tied on lettuce (research/predictive-model-research.md also rejects price ML).

Backtest: for every year i with >= 8 years of history, predict year i from years < i only, with
  median   = median of the previous years
  trend    = least-squares line through the previous years, evaluated at i
and compare mean absolute errors. Trend is used if its MAE <= TREND_GAIN x median MAE.
Trend correction: P'_y = P_y - line(y) + line(target_year): same year-to-year shocks, today's level.
"""
import numpy as np

TREND_GAIN = 0.8   # trend must cut the median's error by >= 20 % (design value, reported as "supuesto")
MIN_HISTORY = 8


def backtest(series):
    """series {year: price}. Returns {"median_mae", "trend_mae", "n_pred", "usa_tendencia"}."""
    ys = sorted(series)
    x = np.array([series[y] for y in ys], dtype=float)
    t = np.array(ys, dtype=float)
    em, et = [], []
    for i in range(MIN_HISTORY, len(x)):
        em.append(abs(np.median(x[:i]) - x[i]))
        b = np.polyfit(t[:i], x[:i], 1)
        et.append(abs(np.polyval(b, t[i]) - x[i]))
    if not em:
        return {"median_mae": None, "trend_mae": None, "n_pred": 0, "usa_tendencia": False}
    m, tr = float(np.mean(em)), float(np.mean(et))
    return {"median_mae": m, "trend_mae": tr, "n_pred": len(em), "usa_tendencia": tr <= TREND_GAIN * m}


def scenarios(series, target_year):
    """Price per historical year as it would look in `target_year`. Returns ({year: price}, info dict)."""
    bt = backtest(series)
    if not bt["usa_tendencia"]:
        return dict(series), {**bt, "metodo": "años históricos tal cual (la tendencia no mejora a la mediana)"}
    ys = sorted(series)
    b = np.polyfit(ys, [series[y] for y in ys], 1)
    shift = {y: float(np.polyval(b, target_year) - np.polyval(b, y)) for y in ys}
    adj = {y: max(0.0, series[y] + shift[y]) for y in ys}
    return adj, {**bt, "metodo": f"años históricos recolocados al nivel de tendencia de {target_year}",
                 "pendiente_por_anio": float(b[0]), "nivel_tendencia": float(np.polyval(b, target_year))}
