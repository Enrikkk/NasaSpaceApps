#!/usr/bin/env python3
"""Prototipo T-011 (clima, ET0 y suelo con cache a disco). NO es codigo de app/.

Solo libreria estandar. Produce los bloques `clima` y `suelo` del contrato v1 (borrador).
Red: un unico punto de entrada (`http_get_json`) que cuenta las llamadas, para poder demostrar que
la segunda ejecucion no toca la red. `AGROCKHAM_OFFLINE=1` prohibe la red (lo usan los tests).

Celdas de cache (clave = celda, no coordenada):
  POWER MERRA-2 (T2M_MAX, T2M_MIN, PRECTOTCORR): nodo de la rejilla nativa 0,5 grados lat x 0,625 grados lon.
  POWER IMERG (IMERG_PRECTOT): pixel de 0,1 grados (IMERG es 0,1 grados; con celda de 0,5 se mezclarian ~25 pixeles).
  Open-Meteo (ERA5 lluvia + ET0 FAO): celda de 0,1 grados (se consulta en el centro de la celda).
  SoilGrids: celda de 0,0025 grados (~220 x 280 m, la resolucion nativa es 250 m).
Se consulta SIEMPRE en el centro de la celda, asi el valor cacheado no depende de quien llegue primero.
"""
import datetime as dt
import json
import math
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE_DIR = Path(os.environ.get("AGROCKHAM_CACHE_DIR", HERE / "cache"))
UA = {"User-Agent": "agrockham-prototype/0.1 (NASA Space Apps 2026 Murcia; research prototype)"}
ANIOS = list(range(2005, 2025))  # 2005-2024
INICIO, FIN = dt.date(2005, 1, 1), dt.date(2024, 12, 31)
N_DIAS = (FIN - INICIO).days + 1  # 7305

# ---------------------------------------------------------------------------------------------- red
NET = {"llamadas": 0, "por_host": {}, "segundos": 0.0, "esperas_s": 0.0}
SOILGRIDS_MIN_INTERVALO_S = 12.5  # 5 llamadas/min -> 12 s; 12,5 de margen


class RedBloqueada(RuntimeError):
    pass


def net_reset():
    NET.update({"llamadas": 0, "por_host": {}, "segundos": 0.0, "esperas_s": 0.0})


def http_get_json(url, timeout=120, retries=4, backoff=(10, 20, 40, 60), host_key=None):
    """GET JSON con reintentos (429/5xx/timeouts). Cuenta cada intento en NET."""
    host = host_key or urllib.parse.urlparse(url).netloc
    if os.environ.get("AGROCKHAM_OFFLINE") == "1":
        raise RedBloqueada(f"AGROCKHAM_OFFLINE=1: se intento llamar a {host}")
    ultimo = None
    for intento in range(retries + 1):
        NET["llamadas"] += 1
        NET["por_host"][host] = NET["por_host"].get(host, 0) + 1
        t0 = time.time()
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read()
            NET["segundos"] += time.time() - t0
            return json.loads(raw)
        except urllib.error.HTTPError as e:
            NET["segundos"] += time.time() - t0
            ultimo = e
            if e.code not in (429, 500, 502, 503, 504):
                raise
        except (urllib.error.URLError, TimeoutError, ConnectionError, json.JSONDecodeError) as e:
            NET["segundos"] += time.time() - t0
            ultimo = e
        if intento < retries:
            espera = backoff[min(intento, len(backoff) - 1)]
            NET["esperas_s"] += espera
            print(f"  [red] {host}: {ultimo!r}; reintento {intento + 1}/{retries} en {espera}s")
            time.sleep(espera)
    raise RuntimeError(f"{host}: agotados los reintentos: {ultimo!r}")


def _soilgrids_espera():
    """Respeta 5 llamadas/min entre procesos: guarda la hora de la ultima llamada en cache/.state/."""
    f = CACHE_DIR / ".state" / "soilgrids_last_call"
    try:
        ultimo = float(f.read_text())
    except (OSError, ValueError):
        ultimo = 0.0
    falta = SOILGRIDS_MIN_INTERVALO_S - (time.time() - ultimo)
    if falta > 0:
        NET["esperas_s"] += falta
        print(f"  [red] SoilGrids limita a 5 llamadas/min: espero {falta:.1f}s")
        time.sleep(falta)


def _soilgrids_marca():
    f = CACHE_DIR / ".state" / "soilgrids_last_call"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(str(time.time()))


# -------------------------------------------------------------------------------------------- cache
def _cache_read(name):
    p = CACHE_DIR / name
    if p.exists():
        return json.loads(p.read_text())
    return None


def _cache_write(name, obj):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (CACHE_DIR / name).write_text(json.dumps(obj, separators=(",", ":"), ensure_ascii=False))


def _hoy():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


# ---------------------------------------------------------------------------------------- celdas
def _redondea(x):
    return math.floor(x + 0.5)


def celda_power(lat, lon):
    """Nodo MERRA-2 (0,5 lat x 0,625 lon): (clave, lat_centro, lon_centro)."""
    i, j = _redondea(lat / 0.5), _redondea(lon / 0.625)
    return f"{i}_{j}", i * 0.5, j * 0.625


def celda_01(lat, lon):
    """Celda de 0,1 grados: (clave, lat_centro, lon_centro). Indices enteros para evitar errores de coma flotante."""
    i, j = math.floor(lat * 10 + 1e-9), math.floor(lon * 10 + 1e-9)
    return f"{i}_{j}", round((i + 0.5) / 10, 3), round((j + 0.5) / 10, 3)


def celda_suelo(lat, lon, paso=0.0025):
    i, j = math.floor(lat / paso + 1e-9), math.floor(lon / paso + 1e-9)
    return f"{i}_{j}", round((i + 0.5) * paso, 5), round((j + 0.5) * paso, 5)


# -------------------------------------------------------------------------------------------- POWER
def _serie_diaria(dic):
    """{'20050101': v, ...} -> lista de N_DIAS valores alineados desde INICIO; -999 y huecos -> None."""
    out = []
    n_relleno = 0
    for k in range(N_DIAS):
        d = INICIO + dt.timedelta(days=k)
        v = dic.get(d.strftime("%Y%m%d"))
        if v is None or v <= -990:  # -999 es el valor de relleno de POWER
            if v is not None:
                n_relleno += 1
            out.append(None)
        else:
            out.append(v)
    return out, n_relleno


def _power_url(params, lat, lon):
    return ("https://power.larc.nasa.gov/api/temporal/daily/point?community=AG&format=JSON"
            f"&parameters={','.join(params)}&latitude={lat}&longitude={lon}"
            f"&start={INICIO:%Y%m%d}&end={FIN:%Y%m%d}&time-standard=UTC")


def _power_fetch(nombre, params, clave, lat_c, lon_c, resolucion, fuente_id, extra):
    cache = _cache_read(f"{nombre}_{clave}.json")
    if cache:
        return cache, True
    url = _power_url(params, lat_c, lon_c)
    d = http_get_json(url, timeout=120)
    par = d["properties"]["parameter"]
    cache = {
        "fuente_id": fuente_id, "url": url, "descargado": _hoy(), "celda_clave": clave,
        "consulta": {"lat": lat_c, "lon": lon_c, "elevacion_m": d["geometry"]["coordinates"][2]},
        "resolucion": resolucion, "time_standard": d["header"].get("time_standard"),
        "api_version": d["header"].get("api", {}).get("version"), "relleno_descartado": {},
        "inicio": INICIO.isoformat(), "dias": N_DIAS,
        "unidades": {p: d["parameters"][p]["units"] for p in params},
        "nombres": {p: d["parameters"][p]["longname"] for p in params}, **extra, "series": {},
    }
    for p in params:
        serie, n = _serie_diaria(par[p])
        cache["series"][p] = serie
        cache["relleno_descartado"][p] = n
    _cache_write(f"{nombre}_{clave}.json", cache)
    return cache, False


def get_power_merra2(lat, lon):
    clave, la, lo = celda_power(lat, lon)
    return _power_fetch("power-merra2", ["T2M_MAX", "T2M_MIN", "PRECTOTCORR"], clave, la, lo,
                        "MERRA-2 0,5 x 0,625 grados (nodo mas cercano), diario", "power",
                        {"comunidad": "AG", "nota": "T2M es del nodo de rejilla (elevacion de la celda), no del campo"})


def get_power_imerg(lat, lon):
    clave, la, lo = celda_01(lat, lon)
    return _power_fetch("power-imerg", ["IMERG_PRECTOT"], clave, la, lo,
                        "GPM IMERG 0,1 grados, diario (sin la correccion de pluviometros: IMERG Final/Late segun fecha)",
                        "imerg", {"comunidad": "AG"})


# ----------------------------------------------------------------------------------------- Open-Meteo
def get_openmeteo(lat, lon):
    clave, la, lo = celda_01(lat, lon)
    nombre = f"openmeteo-era5_{clave}.json"
    cache = _cache_read(nombre)
    if cache:
        return cache, True
    url = ("https://archive-api.open-meteo.com/v1/archive?"
           f"latitude={la}&longitude={lo}&start_date={INICIO}&end_date={FIN}"
           "&daily=precipitation_sum,et0_fao_evapotranspiration&models=era5&timezone=Europe%2FMadrid")
    d = http_get_json(url, timeout=120)
    dd = d["daily"]
    assert dd["time"][0] == INICIO.isoformat() and len(dd["time"]) == N_DIAS, "Open-Meteo: rango inesperado"
    cache = {
        "fuente_id": "open-meteo", "url": url, "descargado": _hoy(), "celda_clave": clave,
        "consulta": {"lat": la, "lon": lo},
        "rejilla_devuelta": {"lat": d.get("latitude"), "lon": d.get("longitude"), "elevacion_m": d.get("elevation")},
        "resolucion": "ERA5 (reanalisis ECMWF/Copernicus, ~0,25 grados) servido por Open-Meteo, diario",
        "modelo": "era5", "zona_horaria": d.get("timezone"),
        "unidades": d["daily_units"], "inicio": INICIO.isoformat(), "dias": N_DIAS,
        "series": {"precipitation_sum": dd["precipitation_sum"],
                   "et0_fao_evapotranspiration": dd["et0_fao_evapotranspiration"]},
        "licencia": "Datos CC BY 4.0 (Open-Meteo.com); la API gratuita es solo para uso NO comercial. "
                    "Origen ERA5: Copernicus Climate Change Service (licencia C3S).",
    }
    _cache_write(nombre, cache)
    return cache, False


# ------------------------------------------------------------------------------------------ SoilGrids
SG_PROPS = ["clay", "sand", "silt", "soc", "phh2o", "nitrogen"]
SG_DEPTHS = ["0-5cm", "5-15cm", "15-30cm"]
# Factor de conversion SoilGrids -> unidad convencional (d_factor de la API; se comprueba contra la respuesta).
SG_CONV = {
    "clay": ("g/kg", 10, "%"),          # g/kg / 10 = %
    "sand": ("g/kg", 10, "%"),
    "silt": ("g/kg", 10, "%"),
    "soc": ("dg/kg", 10, "g/kg"),       # dg/kg / 10 = g/kg (carbono organico del suelo, no materia organica)
    "phh2o": ("pH*10", 10, "pH"),       # pH en agua x 10
    "nitrogen": ("cg/kg", 100, "g/kg"),  # cg/kg / 100 = g/kg
}


def get_soilgrids(lat, lon):
    clave, la, lo = celda_suelo(lat, lon)
    nombre = f"soilgrids_{clave}.json"
    cache = _cache_read(nombre)
    if cache:
        return cache, True
    q = [("lon", lo), ("lat", la)] + [("property", p) for p in SG_PROPS] + [("depth", d) for d in SG_DEPTHS] + [("value", "mean")]
    url = "https://rest.isric.org/soilgrids/v2.0/properties/query?" + urllib.parse.urlencode(q)
    _soilgrids_espera()
    _soilgrids_marca()
    d = http_get_json(url, timeout=180, retries=4, backoff=(15, 30, 60, 60), host_key="rest.isric.org")
    _soilgrids_marca()
    capas = {}
    for layer in d["properties"]["layers"]:
        p = layer["name"]
        factor = layer["unit_measure"]["d_factor"]
        if p in SG_CONV and factor != SG_CONV[p][1]:
            raise ValueError(f"SoilGrids {p}: d_factor {factor} != esperado {SG_CONV[p][1]}")
        capas[p] = {dd["label"]: dd["values"].get("mean") for dd in layer["depths"]}
        capas[p]["_unidad_cruda"] = layer["unit_measure"].get("mapped_units")
        capas[p]["_d_factor"] = factor
    cache = {
        "fuente_id": "soilgrids", "url": url, "descargado": _hoy(), "celda_clave": clave,
        "consulta": {"lat": la, "lon": lo},
        "resolucion": "SoilGrids v2.0, 250 m, MODELADO (aprendizaje automatico sobre perfiles + covariables), no medido en la parcela",
        "estadistico": "mean", "valores_crudos": capas,
        "licencia": "CC BY 4.0 (Poggio et al. 2021, SOIL 7, 217-240, doi:10.5194/soil-7-217-2021)",
    }
    _cache_write(nombre, cache)
    return cache, False


# ------------------------------------------------------------------------------ derivados de clima
def _por_anio(serie, f_agrega, min_validos=360):
    """Agrega una serie diaria alineada desde INICIO por anio natural. None si hay menos de `min_validos` dias validos."""
    out = {}
    for a in ANIOS:
        i0 = (dt.date(a, 1, 1) - INICIO).days
        i1 = (dt.date(a, 12, 31) - INICIO).days + 1
        tramo = serie[i0:i1]
        validos = [v for v in tramo if v is not None]
        out[a] = f_agrega(validos) if len(validos) >= min_validos else None
    return out


def _ols_pendiente(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx


def _media(vals):
    v = [x for x in vals if x is not None]
    return sum(v) / len(v) if v else None


def fuentes_nuevas():
    """Entradas de `fuentes[]` que el contrato borrador aun no tiene."""
    return [{
        "id": "open-meteo",
        "nombre": "Open-Meteo Historical Weather API (ERA5; ET0 FAO-56 Penman-Monteith)",
        "url": "https://open-meteo.com/en/docs/historical-weather-api",
        "licencia": "Datos CC BY 4.0 (citar Open-Meteo.com); API gratuita solo para uso no comercial; origen ERA5: licencia Copernicus C3S",
        "licencia_estado": "verify",
    }]


def build_clima(lat, lon):
    m, hit_m = get_power_merra2(lat, lon)
    im, hit_i = get_power_imerg(lat, lon)
    om, hit_o = get_openmeteo(lat, lon)
    S = m["series"]

    suma = lambda v: sum(v)
    r_power = _por_anio(S["PRECTOTCORR"], suma)
    r_imerg = _por_anio(im["series"]["IMERG_PRECTOT"], suma)
    r_era5 = _por_anio(om["series"]["precipitation_sum"], suma)
    calor = _por_anio(S["T2M_MAX"], lambda v: sum(1 for x in v if x > 38))
    tmin_min = _por_anio(S["T2M_MIN"], min)
    tmax_max = _por_anio(S["T2M_MAX"], max)
    calor35 = _por_anio(S["T2M_MAX"], lambda v: sum(1 for x in v if x > 35))
    # Heladas provisionales: dias con T2M_MIN < 0 en la celda MERRA-2 (NO FROST_DAYS). Pendiente SIAM.
    helada_prov = _por_anio(S["T2M_MIN"], lambda v: sum(1 for x in v if x < 0))

    serie = []
    for a in ANIOS:
        por_fuente = {k: round(v[a], 1) for k, v in (("power", r_power), ("imerg", r_imerg), ("era5", r_era5)) if v[a] is not None}
        fila = {"anio": a}
        if por_fuente:
            fila["lluvia_mm"] = round(sum(por_fuente.values()) / len(por_fuente), 1)
            fila["lluvia_por_fuente_mm"] = por_fuente
        else:
            fila["lluvia_mm"] = 0.0
        for k, v in (("tmin_min_c", tmin_min), ("tmax_max_c", tmax_max)):
            if v[a] is not None:
                fila[k] = round(v[a], 1)
        if calor[a] is not None:
            fila["dias_calor_gt_38"] = int(calor[a])
        serie.append(fila)

    medias = {k: _media(list(v.values())) for k, v in (("power", r_power), ("imerg", r_imerg), ("era5", r_era5))}
    medias = {k: v for k, v in medias.items() if v is not None}
    valor = sum(medias.values()) / len(medias)
    calor_vals = [calor[a] for a in ANIOS if calor[a] is not None]
    pend = _ols_pendiente([a for a in ANIOS if calor[a] is not None], calor_vals) * 10
    calor35_vals = [calor35[a] for a in ANIOS if calor35[a] is not None]
    tmax_20 = max(v for v in tmax_max.values() if v is not None)
    tmin_20 = min(v for v in tmin_min.values() if v is not None)
    hel = [helada_prov[a] for a in ANIOS if helada_prov[a] is not None]

    # ET0 mensual climatologico (media 2005-2024 de la suma mensual), mm/mes
    et0 = om["series"]["et0_fao_evapotranspiration"]
    mensual = {m_: [] for m_ in range(1, 13)}
    for a in ANIOS:
        for m_ in range(1, 13):
            i0 = (dt.date(a, m_, 1) - INICIO).days
            i1 = ((dt.date(a + (m_ == 12), m_ % 12 + 1, 1)) - INICIO).days
            v = [x for x in et0[i0:i1] if x is not None]
            if len(v) >= (i1 - i0) - 2:
                mensual[m_].append(sum(v))
    et0_mes = [round(_media(mensual[m_]), 1) for m_ in range(1, 13)]

    return {
        "_status": "real",
        "lluvia_anual_mm": {
            "valor": round(valor), "horquilla": [round(min(medias.values())), round(max(medias.values()))],
            "fuentes": ["power", "imerg", "open-meteo"],
            "por_fuente_mm": {k: round(v, 1) for k, v in medias.items()},
            "metodo": "media 2005-2024 de la lluvia anual de cada fuente; valor = media de las fuentes; horquilla = [min, max] entre fuentes (no es un intervalo de confianza)",
        },
        "dias_calor_gt_38": {
            "valor": round(sum(calor_vals) / len(calor_vals), 1),
            "tendencia": (f"{pend:+.1f} por decada (OLS 2005-2024, n=20; orientativa, sin prueba de significacion)"
                          if any(calor_vals) else "sin dias > 38 C en 20 anios en la celda MERRA-2"),
            "metodo": "dias/anio con T2M_MAX > 38 C en la celda MERRA-2 de 0,5 x 0,625 grados (no es el campo exacto)",
            "dias_calor_gt_35": round(sum(calor35_vals) / len(calor35_vals), 1),
            "tmax_max_20_anios_c": round(tmax_20, 1),
            "aviso": "MERRA-2 promedia ~50 km (incluye mar) y suaviza los extremos: aqui da 0 dias > 38 C aunque la parcela los tiene. "
                     "Tratar como cota inferior; los extremos reales vendran de SIAM (T-014).",
        },
        "dias_helada": {
            "valor": round(sum(hel) / len(hel), 1),
            "fuente": "pendiente SIAM",
            "provisional": True,
            "estacion": "pendiente SIAM (T-014): el valor real saldra de las series de la estacion IMIDA, no de POWER",
            "tmin_min_20_anios_c_power": round(tmin_20, 1),
            "valor_provisional_power": "dias/anio con T2M_MIN < 0 C (MERRA-2, celda de ~50 km, sesgo calido). NO es FROST_DAYS de POWER (no equivale a Tmin<0). No usar como cifra final.",
        },
        "serie_anual": serie,
        "et0_mm_mes": {
            "valores": et0_mes, "unidad": "mm/mes", "meses": "ene..dic", "periodo": "2005-2024 (media de cada mes)",
            "anual_mm": round(sum(et0_mes), 1), "metodo": "ET0 FAO-56 Penman-Monteith de Open-Meteo sobre ERA5",
            "fuente_id": "open-meteo",
        },
        "metadatos": {
            "periodo": "2005-2024, diario, agregado por anio natural",
            "descarga": {"power_merra2": m["descargado"], "power_imerg": im["descargado"], "open_meteo": om["descargado"]},
            "fuentes": {
                "power_merra2": {"fuente_id": "power", "parametros": ["T2M_MAX", "T2M_MIN", "PRECTOTCORR"], "unidades": m["unidades"],
                                 "resolucion": m["resolucion"], "url": m["url"], "time_standard": m["time_standard"],
                                 "celda": {"clave": m["celda_clave"], **m["consulta"]}, "relleno_descartado": m["relleno_descartado"]},
                "power_imerg": {"fuente_id": "imerg", "parametros": ["IMERG_PRECTOT"], "unidades": im["unidades"],
                                "resolucion": im["resolucion"], "url": im["url"], "time_standard": im["time_standard"],
                                "celda": {"clave": im["celda_clave"], **im["consulta"]}, "relleno_descartado": im["relleno_descartado"]},
                "open_meteo": {"fuente_id": "open-meteo", "parametros": ["precipitation_sum", "et0_fao_evapotranspiration"],
                               "unidades": om["unidades"], "resolucion": om["resolucion"], "url": om["url"],
                               "celda": {"clave": om["celda_clave"], **om["consulta"]}, "rejilla_devuelta": om["rejilla_devuelta"],
                               "licencia": om["licencia"]},
            },
            "aviso_lluvia": "Las tres fuentes difieren mucho (reanalisis y satelite no son pluviometros); por eso se da horquilla y lluvia por fuente.",
            "trampas": [
                "POWER FROST_DAYS no es Tmin<0; las heladas reales vendran de SIAM (dias_helada pendiente).",
                "POWER EVLAND (evapotranspiracion del modelo de superficie) no ve el riego: no sirve para una parcela de regadio; ET0 viene de Open-Meteo.",
                "IMERG via POWER exige time-standard=UTC; -999 es relleno y se descarta.",
                "T2M de POWER es de un nodo de ~50 km: subestima extremos locales (heladas y calor).",
            ],
            "cache": {"power_merra2": hit_m, "power_imerg": hit_i, "open_meteo": hit_o},
        },
    }


# ----------------------------------------------------------------------------- derivados de suelo
def usda_textura(arena, limo, arcilla):
    """Clase textural USDA (porcentajes) en espanol. Clasificacion del triangulo USDA."""
    s, si, c = arena, limo, arcilla
    if si + 1.5 * c < 15:
        return "arenoso"
    if si + 1.5 * c >= 15 and si + 2 * c < 30:
        return "arenoso-franco"
    if (7 <= c < 20 and s > 52 and si + 2 * c >= 30) or (c < 7 and si < 50 and si + 2 * c >= 30):
        return "franco-arenoso"
    if 7 <= c < 27 and 28 <= si < 50 and s <= 52:
        return "franco"
    if (si >= 50 and 12 <= c < 27) or (50 <= si < 80 and c < 12):
        return "franco-limoso"
    if si >= 80 and c < 12:
        return "limoso"
    if 20 <= c < 35 and si < 28 and s > 45:
        return "franco-arcillo-arenoso"
    if 27 <= c < 40 and 20 < s <= 45:
        return "franco-arcilloso"
    if 27 <= c < 40 and s <= 20:
        return "franco-arcillo-limoso"
    if c >= 35 and s > 45:
        return "arcillo-arenoso"
    if c >= 40 and si >= 40:
        return "arcillo-limoso"
    if c >= 40 and s <= 45 and si < 40:
        return "arcilloso"
    return "franco"  # limites numericos no cubiertos


FACTOR_MO = 1.724  # materia organica = carbono organico x 1,724 (van Bemmelen)


def saxton_rawls_awc(arena_pct, arcilla_pct, mo_pct):
    """Agua disponible (fraccion volumetrica) = CC (33 kPa) - PMP (1500 kPa). Saxton y Rawls 2006 (SSSAJ 70:1569)."""
    S, C, OM = arena_pct / 100, arcilla_pct / 100, mo_pct
    t1500 = -0.024 * S + 0.487 * C + 0.006 * OM + 0.005 * S * OM - 0.013 * C * OM + 0.068 * S * C + 0.031
    th1500 = t1500 + (0.14 * t1500 - 0.02)
    t33 = -0.251 * S + 0.195 * C + 0.011 * OM + 0.006 * S * OM - 0.027 * C * OM + 0.452 * S * C + 0.299
    th33 = t33 + (1.283 * t33 ** 2 - 0.374 * t33 - 0.015)
    return th33 - th1500, th33, th1500


def _capa_convertida(crudos, d):
    """Convierte los valores crudos de una profundidad a unidades convencionales."""
    out = {}
    for p, (u_cruda, f, u) in SG_CONV.items():
        v = crudos[p].get(d)
        if v is None:
            return None
        out[p] = v / f
    s = out["sand"] + out["silt"] + out["clay"]
    out["_suma_textura_pct"] = s
    return out


def build_suelo(lat, lon):
    sg, hit = get_soilgrids(lat, lon)
    crudos = sg["valores_crudos"]
    espesores = {"0-5cm": 5, "5-15cm": 10, "15-30cm": 15}
    capas, awc_mm, w_tot = [], 0.0, 0
    acum = {k: 0.0 for k in ("clay", "sand", "silt", "soc", "phh2o", "nitrogen")}
    for d, esp in espesores.items():
        c = _capa_convertida(crudos, d)
        if c is None:
            continue
        k = 100 / c["_suma_textura_pct"]  # normaliza arena+limo+arcilla a 100
        arena, limo, arcilla = c["sand"] * k, c["silt"] * k, c["clay"] * k
        mo = c["soc"] / 10 * FACTOR_MO
        awc, cc, pmp = saxton_rawls_awc(arena, arcilla, mo)
        awc_mm += awc * esp * 10
        w_tot += esp
        for p in acum:
            acum[p] += c[p] * esp
        capas.append({"profundidad_cm": d.replace("cm", ""), "arcilla_pct": round(arcilla, 1), "arena_pct": round(arena, 1),
                      "limo_pct": round(limo, 1), "soc_g_kg": round(c["soc"], 1), "materia_organica_pct": round(mo, 2),
                      "ph_h2o": round(c["phh2o"], 2), "nitrogeno_g_kg": round(c["nitrogen"], 2),
                      "agua_disponible_mm": round(awc * esp * 10, 1)})
    if w_tot == 0:
        raise ValueError("SoilGrids sin datos en el punto (celda sin suelo, p. ej. agua o urbano)")
    m = {p: acum[p] / w_tot for p in acum}  # media ponderada por espesor
    k = 100 / (m["sand"] + m["silt"] + m["clay"])
    arena, limo, arcilla = m["sand"] * k, m["silt"] * k, m["clay"] * k
    mo = m["soc"] / 10 * FACTOR_MO
    return {
        "_status": "real",
        "textura": usda_textura(arena, limo, arcilla),
        "materia_organica_pct": round(mo, 2),
        "agua_disponible_mm": round(awc_mm, 1),
        "fuente": "ISRIC SoilGrids 2.0 (modelado, 250 m)",
        "fuente_id": "soilgrids",
        "arena_pct": round(arena, 1), "limo_pct": round(limo, 1), "arcilla_pct": round(arcilla, 1),
        "soc_g_kg": round(m["soc"], 1), "ph_h2o": round(m["phh2o"], 2), "nitrogeno_g_kg": round(m["nitrogen"], 2),
        "capas": capas,
        "metadatos": {
            "profundidad": "0-30 cm, media ponderada por espesor de las capas 0-5, 5-15 y 15-30 cm",
            "agua_disponible": "Saxton y Rawls 2006 (CC 33 kPa - PMP 1500 kPa) por capa x espesor, sumado en 0-30 cm. "
                               f"Equivale a {round(awc_mm / 30 * 100)} mm por metro; NO es la reserva de toda la zona radicular (los cultivos de la rotacion enraizan 0,3-1 m+). Sin correccion por gravas.",
            "conversiones": {
                "textura": "SoilGrids clay/sand/silt en g/kg; /10 = %; se normaliza a suma 100 y se clasifica con el triangulo USDA",
                "materia_organica_pct": f"soc en dg/kg; /10 = g/kg de carbono organico; /10 = % C; x {FACTOR_MO} (van Bemmelen) = % materia organica",
                "ph_h2o": "phh2o = pH x 10; /10",
                "nitrogeno_g_kg": "nitrogen en cg/kg; /100 = g/kg",
            },
            "descarga": sg["descargado"], "resolucion": sg["resolucion"], "url": sg["url"],
            "celda": {"clave": sg["celda_clave"], **sg["consulta"]}, "licencia": sg["licencia"],
            "unidades_crudas": {p: crudos[p]["_unidad_cruda"] for p in crudos},
            "aviso": "SoilGrids es un modelo global a 250 m, no una medicion en la parcela: las incertidumbres (sobre todo SOC en suelos agricolas mediterraneos y regadios) pueden ser grandes. "
                     "En el mock el SOC parecia alto; comparar con los suelos IMIDA/analisis local antes de fiarse de la cifra de materia organica.",
            "cache": hit,
        },
    }
