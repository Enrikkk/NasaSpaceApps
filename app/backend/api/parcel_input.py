"""Entrada del motor POR PARCELA (H-002 de enrique): `ParcelInput` construido con lo que la API ya sabe de un clic.

Cada campo puede ser None = "sin dato" (el motor no lo inventa: factor 1 y "sin dato de X" en la tarjeta). El clima NO va aqui: es la
estacion SIAM unica del motor. Lo que SoilGrids/SIGPAC no dan (salinidad CE, profundidad, drenaje) va a None, nunca se estima.
"""
from typing import Optional


def _num(x) -> Optional[float]:
    return x if isinstance(x, (int, float)) and not isinstance(x, bool) else None


def construir(ctx) -> dict:
    """ctx = engine_adapter.EngineInput -> dict ParcelInput + `sin_dato` (lista de campos vacios)."""
    p = ctx.parcela or {}
    s = ctx.suelo or {}
    regadio = p.get("regadio")
    if regadio is None and _num(p.get("coef_regadio")) is not None:
        regadio = p["coef_regadio"] > 0
    declarados = []
    for item in (ctx.historia or []):
        for d in item.get("declaraciones", []) or []:
            declarados.append({k: d.get(k) for k in ("campana", "cultivo", "producto_codigo", "sistema_explotacion",
                                                     "superficie_cultivada_ha", "cultivo_secundario")})
    out = {
        "parcel_id": p.get("id"),
        "lat": ctx.lat,
        "lon": ctx.lon,
        "area_ha": _num(p.get("ha")),
        "regadio": regadio if isinstance(regadio, bool) else None,
        "pendiente_pct": _num(p.get("pendiente_pct")),
        "suelo": {
            "textura": s.get("textura"),
            "ph": _num(s.get("ph_h2o")),
            "materia_organica_pct": _num(s.get("materia_organica_pct")),
            "salinidad_ce_dsm": None,    # SoilGrids no la da
            "profundidad_cm": None,
            "drenaje": None,
        },
        "zona_legal": ctx.zona,
        "cultivos_declarados": declarados,   # 0..N registros FEGA (campana en uso); [] = sin declaracion o sin dato
    }
    faltan = [k for k in ("parcel_id", "area_ha", "regadio", "pendiente_pct") if out[k] is None]
    faltan += [f"suelo.{k}" for k, v in out["suelo"].items() if v is None]
    if not declarados:
        faltan.append("cultivos_declarados")
    out["sin_dato"] = faltan
    return out
