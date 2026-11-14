"""What one cycle of a PRODUCT sells for (T-018): price source by quality tier, harvest months, sale channels, and
the per-year quantities the UI needs to recompute margins with the farmer's OWN price (decision Enrique 2026-11-14).

Price tiers for the default price (the first that has data wins, and the card says which one):
  1  CARM yearbook monthly quotes of this product's variety (and quality), months of this cycle's harvest
  2  CARM quotes of the same crop, any variety with the same unit (crop-level Murcia price)
  3  Eurostat national annual first-stage price (EUR/kg products only)
CARM quotes are nominal and orientative (yearbooks' own words); they are deflated to `base_year` with Spain HICP.
A quote more than 5x above or below its series median is treated as a printing error and excluded (reported).

Quantities sold: per kg = coste_total / coste_unitario (IMIDA's unit cost is per kg of NET marketable product);
per unit (lettuce, EUR/ud) = coste_total / coste_unitario_ud. Fallback: gross produccion_media (flagged).
"""
import datetime as dt
import statistics

from . import price as pr

OUTLIER_X = 5.0
# Licence gate (decision Enrique 2026-11-14). esam.carm.es/legal: reproduction with citation allowed, but "sólo está
# autorizado el uso personal no-comercial" and "no está permitida la modificación" -> NOT an open licence. Until CARM
# grants written permission (request to agri-estadistica@carm.es), anything PUBLISHED uses open data only
# (Eurostat CC BY 4.0); CARM quotes are used for internal runs only (allow_restricted=True).
RESTRICTED_SOURCES = {"CARM-ANUARIO": "esam.carm.es/legal: uso personal no comercial, sin modificación; permiso solicitado"}


def harvest_months(start, lengths, window):
    """{(year, month)} of the days in the harvest window ('late', 'mid+late', 'all', ...) of a cycle from start."""
    names, out, day = [], set(), start
    for name, n in zip(("ini", "dev", "mid", "late"), lengths):
        names += [name] * n
    wanted = None if window in ("all", "", None) else set(window.split("+"))
    for name in names:
        if wanted is None or name in wanted:
            out.add((day.year, day.month))
        day += dt.timedelta(days=1)
    return out


def _clean(series):
    """Drop printing errors: quotes > OUTLIER_X away from the series median. Returns (series, dropped list)."""
    vals = [v for months in series.values() for v, _ in months.values()]
    if not vals:
        return series, []
    med = statistics.median(vals)
    keep, dropped = {}, []
    for y, months in series.items():
        for m, (v, u) in months.items():
            if med > 0 and (v > OUTLIER_X * med or v < med / OUTLIER_X):
                dropped.append((y, m, v))
            else:
                keep.setdefault(y, {})[m] = (v, u)
    return keep, dropped


class Market:
    def __init__(self, carm, eurostat, hicp, base_year, allow_restricted=False):
        self.carm = carm if allow_restricted else {}  # CARM quotes only for internal runs until permission arrives
        self.eurostat, self.hicp, self.base = eurostat, hicp, base_year
        self.restricted_used = bool(allow_restricted and carm)

    def _real(self, v, year):
        return v * self.hicp[self.base] / self.hicp[year] if year in self.hicp else None

    def series_for(self, crop_id, variety, quality, unit):
        """Tiered default series: (tier, label, {year: {month: (value, unit)}}, keys used, dropped outliers)."""
        variants = [v for v in (variety or "").split("|") if v] or [""]
        keys = [(crop_id, v, quality or "") for v in variants if (crop_id, v, quality or "") in self.carm]
        if keys:
            merged = {}
            for k in keys:
                for y, ms in self.carm[k].items():
                    for m, vu in ms.items():
                        if vu[1] == unit:
                            merged.setdefault(y, {})[m] = vu
            if merged:
                s, drop = _clean(merged)
                return 1, f"CARM anuarios, {crop_id} {'/'.join(variants)} {quality}".strip(), s, keys, drop
        same = [k for k in self.carm if k[0] == crop_id and k[2] == "" and any(
            vu[1] == unit for ms in self.carm[k].values() for vu in ms.values())]
        if same:
            merged = {}
            for k in same:
                for y, ms in self.carm[k].items():
                    for m, (v, u) in ms.items():
                        if u == unit:
                            merged.setdefault(y, {}).setdefault(m, []).append(v)
            merged = {y: {m: (sum(v) / len(v), unit) for m, v in ms.items()} for y, ms in merged.items()}
            s, drop = _clean(merged)
            return 2, f"CARM anuarios, {crop_id} (media de todas las variedades)", s, same, drop
        return 3, "Eurostat, media nacional anual", None, [], []

    def cycle_price(self, series, months):
        """Mean real price over the quotes in this cycle's harvest months; else mean of that harvest year's quotes."""
        vals = [self._real(series[y][m][0], y) for (y, m) in months if y in series and m in series[y]]
        vals = [v for v in vals if v is not None]
        if vals:
            return sum(vals) / len(vals), "meses de cosecha"
        last_year = max(y for y, _ in months)
        if last_year in series:
            vals = [self._real(v, last_year) for v, _ in series[last_year].values()]
            return sum(vals) / len(vals), "media del año (sin cotización en los meses de cosecha)"
        return None, "sin cotización ese año"

    def channels(self, crop_id, unit, default_keys):
        """Other CARM series of the same crop and unit = alternative ways of selling (export, industry, one cut...)."""
        out = []
        for k in sorted(self.carm):
            if k[0] != crop_id or k in default_keys:
                continue
            if not any(vu[1] == unit for ms in self.carm[k].values() for vu in ms.values()):
                continue
            s, drop = _clean({y: {m: vu for m, vu in ms.items() if vu[1] == unit} for y, ms in self.carm[k].items()})
            out.append({"id": "_".join(x for x in k[1:] if x) or "general", "variedad": k[1], "calidad": k[2],
                        "serie": s, "excluidos": drop})
        return out

    def eurostat_series(self, crop_id):
        """{harvest_year: real EUR/kg in base_year}, trend-checked exactly like before (price.py)."""
        s = self.eurostat.get(crop_id)
        if not s:
            return None, None
        adj, info = pr.scenarios(s, self.base)
        return {y: v * self.hicp[self.base] / 100 for y, v in adj.items()}, info


# Ways the farmer can set their own price in the UI (exported as-is; the UI recomputes margen = cantidad x precio - coste
# per historical year). Default when nothing is set: the tiered official price above.
USER_PRICE_OPTIONS = [
    {"id": "oficial", "nombre": "Precio de referencia (por defecto)",
     "explica": "Cotización de Murcia de tu tipo de cultivo en los meses en que cosecharías, año a año (CARM, "
                "orientativa); si no existe, la de Murcia del cultivo; si no, la media nacional (Eurostat)."},
    {"id": "canal", "nombre": "Otra forma de venta oficial",
     "explica": "La cotización de Murcia de otro canal del mismo cultivo: exportación, industria, un corte, "
                "plaza... (solo los que publica la CARM para tu cultivo)."},
    {"id": "fijo", "nombre": "Precio cerrado / contrato",
     "explica": "Vendes a un precio fijo pactado (por kg o por pieza): se usa el mismo precio en todos los años; "
                "el riesgo que queda es el del clima y el de los costes."},
    {"id": "ajuste", "nombre": "Referencia ± un porcentaje",
     "explica": "Tu cooperativa o comprador paga la referencia menos su comisión (p. ej. −8 %) o más una prima de "
                "calidad (p. ej. +10 %): se aplica el porcentaje a cada año."},
    {"id": "recoleccion", "nombre": "¿Quién paga la recolección?",
     "explica": "Por defecto la pagas tú (coste IMIDA de recolección incluido). Si vendes 'en el árbol' o 'en la "
                "finca' y el comprador cosecha con su cuadrilla, quita ese coste: la web resta coste_recoleccion_eur_ha. "
                "Las cotizaciones CARM se publican 's/finca' (lechuga, melón) o 's/árbol' (limón); el anuario no "
                "define si la recolección va incluida."},
    {"id": "mis_anios", "nombre": "Mis precios de años pasados",
     "explica": "Escribes lo que cobraste en los años que recuerdes; en los demás años se usa la referencia."},
]
