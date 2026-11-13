#!/usr/bin/env python3
"""Smoke test: do the open data APIs for Field Shift answer for a real Murcia parcel?

Not product code. It only checks that each source answers (status, time, one useful number),
so the team knows on Saturday morning what works without keys.

Usage:
    python3 research/api_smoke_test.py            # default demo parcel (Torre-Pacheco)
    python3 research/api_smoke_test.py --slow     # also SoilGrids (5 calls/min, can take 30-60 s)
    python3 research/api_smoke_test.py --lat 37.7383 --lon -0.9883

Standard library only. No keys, no accounts.
"""
import argparse
import gzip
import json
import math
import time
import urllib.parse
import urllib.request

# Demo parcel: Torre-Pacheco (30037), SIGPAC 18/426/1, ~4.1 ha irrigated arable land.
# 2025 declared crop: MELON; current campaign: BARBECHO TRADICIONAL (fallow, bare soil).
DEFAULT_LAT, DEFAULT_LON = 37.73830, -0.98838

UA = {"User-Agent": "field-shift-smoke-test/0.1", "Accept-Encoding": "gzip"}


def fetch(url, timeout=60, data=None, headers=None):
    h = dict(UA)
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, data=data, headers=h)
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        status = r.status
        hdrs = dict(r.headers)
    dt = time.time() - t0
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return status, dt, raw, hdrs


def fetch_json(url, **kw):
    status, dt, raw, hdrs = fetch(url, **kw)
    return status, dt, json.loads(raw), hdrs


def haversine_km(lat1, lon1, lat2, lon2):
    p = math.pi / 180
    a = (math.sin((lat2 - lat1) * p / 2) ** 2
         + math.cos(lat1 * p) * math.cos(lat2 * p) * math.sin((lon2 - lon1) * p / 2) ** 2)
    return 12742 * math.asin(math.sqrt(a))


def t_power(lat, lon):
    params = "T2M_MAX,T2M_MIN,PRECTOTCORR,IMERG_PRECTOT"
    url = ("https://power.larc.nasa.gov/api/temporal/daily/point?community=AG&format=JSON"
           f"&parameters={params}&latitude={lat}&longitude={lon}"
           "&start=20050101&end=20241231&time-standard=UTC")
    s, dt, d, _ = fetch_json(url, timeout=90)
    p = d["properties"]["parameter"]
    years = 20
    rain = sum(v for v in p["PRECTOTCORR"].values() if v >= 0) / years
    imerg = sum(v for v in p["IMERG_PRECTOT"].values() if v >= 0) / years
    frost = sum(1 for v in p["T2M_MIN"].values() if -90 < v < 0) / years
    hot = sum(1 for v in p["T2M_MAX"].values() if v > 35) / years
    return s, dt, (f"2005-2024: lluvia {rain:.0f} mm/año (PRECTOTCORR) vs {imerg:.0f} (IMERG); "
                   f"heladas {frost:.1f} d/año; Tmax>35 °C {hot:.1f} d/año")


def t_sigpac_point(lat, lon):
    url = f"https://sigpac-hubcloud.es/servicioconsultassigpac/query/recinfobypoint/4258/{lon}/{lat}.json"
    s, dt, d, _ = fetch_json(url)
    r = d[0] if isinstance(d, list) else d
    return s, dt, (f"recinto {r['municipio']}/{r['poligono']}/{r['parcela']}/{r['recinto']}, "
                   f"uso {r['uso_sigpac']}, {r['superficie']} ha, pendiente {r['pendiente_media']} %, "
                   f"regadío {r['coef_regadio']} %, altitud {r['altitud']} m")


def t_sigpac_crop(lat, lon):
    e = 0.0002
    url = ("https://sigpac-hubcloud.es/ogcapi/collections/cultivo_declarado/items?f=json&limit=10"
           f"&bbox={lon - e},{lat - e},{lon + e},{lat + e}")
    s, dt, d, _ = fetch_json(url)
    prods = sorted({f["properties"].get("parc_producto") for f in d.get("features", [])} - {None})
    return s, dt, f"códigos de producto declarados (campaña en curso): {prods or 'ninguno'} (ver cod_producto.csv del FEGA)"


def t_siam(lat, lon):
    url = ("https://geoportal.imida.es/gis/rest/services/3_14_ASPECTOS_GEOGRAFICOS_DE_CARACTER_METEOROLOGICO/"
           "SIAM_DATOS/MapServer/0/query?where=1%3D1&outFields=*&returnGeometry=true&outSR=4326&f=json")
    s, dt, d, _ = fetch_json(url)
    feats = d.get("features", [])
    best = min(feats, key=lambda f: haversine_km(lat, lon, f["geometry"]["y"], f["geometry"]["x"]))
    a = best["attributes"]
    km = haversine_km(lat, lon, best["geometry"]["y"], best["geometry"]["x"])
    keys = [k for k in a if any(t in k.upper() for t in ("ESTACION", "NOMBRE", "FECHA", "ETO", "ET0", "TMED", "PREC"))]
    sample = {k: a[k] for k in keys[:6]}
    if isinstance(sample.get("FECHA"), (int, float)):  # ArcGIS dates are epoch milliseconds
        sample["FECHA"] = time.strftime("%Y-%m-%d", time.gmtime(sample["FECHA"] / 1000))
    return s, dt, f"{len(feats)} estaciones; más cercana a {km:.1f} km: {sample}"


def t_nitrates(lat, lon):
    url = ("https://geoportal.imida.es/gis/rest/services/PROYECTOS/ZONAS_VULNERABLES_NITRATOS/MapServer/0/query?"
           f"geometry={lon},{lat}&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects"
           "&outFields=*&returnGeometry=false&f=json")
    s, dt, d, _ = fetch_json(url)
    feats = d.get("features", [])
    attrs = feats[0]["attributes"] if feats else {}
    short = {k: v for k, v in list(attrs.items())[:4]}
    return s, dt, f"zona vulnerable a nitratos: {'sí ' + str(short) if feats else 'no'}"


def t_corine(lat, lon):
    url = ("https://image.discomap.eea.europa.eu/arcgis/rest/services/Corine/CLC2018_WM/MapServer/identify?"
           f"geometry={lon},{lat}&geometryType=esriGeometryPoint&sr=4326&layers=all&tolerance=1"
           f"&mapExtent={lon - 0.1},{lat - 0.1},{lon + 0.1},{lat + 0.1}&imageDisplay=400,400,96"
           "&returnGeometry=false&f=json")
    s, dt, d, _ = fetch_json(url)
    res = d.get("results", [])
    a = res[0]["attributes"] if res else {}
    code = next((v for k, v in a.items() if "CODE" in k.upper()), None)
    return s, dt, f"CORINE 2018 clase {code}"


def t_openmeteo(lat, lon):
    url = ("https://archive-api.open-meteo.com/v1/archive?"
           f"latitude={lat}&longitude={lon}&start_date=2024-01-01&end_date=2024-12-31"
           "&daily=precipitation_sum,et0_fao_evapotranspiration&models=era5&timezone=Europe%2FMadrid")
    s, dt, d, _ = fetch_json(url)
    dd = d["daily"]
    rain = sum(v for v in dd["precipitation_sum"] if v is not None)
    et0 = sum(v for v in dd["et0_fao_evapotranspiration"] if v is not None)
    return s, dt, f"ERA5 2024: lluvia {rain:.0f} mm, ET0 {et0:.0f} mm → déficit {et0 - rain:.0f} mm"


def t_cdse_stac(lat, lon):
    e = 0.001
    q = urllib.parse.urlencode({
        "collections": "sentinel-2-l2a",
        "bbox": f"{lon - e},{lat - e},{lon + e},{lat + e}",
        "datetime": "2025-01-01T00:00:00Z/2025-12-31T23:59:59Z",
        "limit": 200,
    })
    s, dt, d, _ = fetch_json(f"https://stac.dataspace.copernicus.eu/v1/search?{q}")
    feats = d.get("features", [])
    clear = [f for f in feats if (f["properties"].get("eo:cloud_cover") or 100) < 20]
    return s, dt, f"Sentinel-2 L2A 2025: {len(feats)} escenas, {len(clear)} con nubes < 20 % (página de 200)"


def t_cmr_hls(lat, lon):
    out = []
    total_dt = 0
    status = None
    for sn in ("HLSS30", "HLSL30"):
        q = urllib.parse.urlencode({
            "short_name": sn, "point": f"{lon},{lat}",
            "temporal": "2025-01-01T00:00:00Z,2025-12-31T23:59:59Z", "page_size": 1,
        })
        status, dt, _, hdrs = fetch(f"https://cmr.earthdata.nasa.gov/search/granules.json?{q}")
        total_dt += dt
        hits = {k.lower(): v for k, v in hdrs.items()}.get("cmr-hits")
        out.append(f"{sn} {hits}")
    return status, total_dt, "gránulos HLS 2025 en el punto: " + ", ".join(out) + " (descargar requiere Earthdata Login)"


def t_ign_mdt(lat, lon):
    e = 0.001
    url = ("https://servicios.idee.es/wcs-inspire/mdt?SERVICE=WCS&VERSION=2.0.1&REQUEST=GetCoverage"
           f"&COVERAGEID=Elevacion4258_5&SUBSET=Lat({lat - e},{lat + e})&SUBSET=Long({lon - e},{lon + e})"
           "&FORMAT=image/tiff")
    s, dt, raw, _ = fetch(url)
    return s, dt, f"GeoTIFF MDT 5 m recortado: {len(raw) / 1024:.0f} KB"


def t_soilgrids(lat, lon):
    url = ("https://rest.isric.org/soilgrids/v2.0/properties/query?"
           f"lon={lon}&lat={lat}&property=clay&property=sand&property=soc&property=phh2o"
           "&depth=0-5cm&value=mean")
    s, dt, d, _ = fetch_json(url, timeout=120)
    vals = {}
    for layer in d["properties"]["layers"]:
        v = layer["depths"][0]["values"]["mean"]
        f = layer["unit_measure"]["d_factor"]
        vals[layer["name"]] = None if v is None else round(v / f, 1)
    return s, dt, f"0-5 cm: {vals} (arcilla/arena %, soc g/kg, pH)"


TESTS = [
    ("NASA POWER (clima + IMERG)", t_power),
    ("SIGPAC recinto por punto", t_sigpac_point),
    ("SIGPAC cultivo declarado", t_sigpac_crop),
    ("SIAM-IMIDA estaciones", t_siam),
    ("IMIDA zonas nitratos", t_nitrates),
    ("CORINE Land Cover", t_corine),
    ("Open-Meteo ERA5", t_openmeteo),
    ("Copernicus STAC Sentinel-2", t_cdse_stac),
    ("NASA CMR HLS", t_cmr_hls),
    ("IGN MDT 5 m", t_ign_mdt),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lat", type=float, default=DEFAULT_LAT)
    ap.add_argument("--lon", type=float, default=DEFAULT_LON)
    ap.add_argument("--slow", action="store_true", help="include SoilGrids")
    a = ap.parse_args()
    tests = TESTS + ([("SoilGrids (lento)", t_soilgrids)] if a.slow else [])
    print(f"Punto: lat {a.lat}, lon {a.lon}\n")
    ok = 0
    for name, fn in tests:
        try:
            s, dt, msg = fn(a.lat, a.lon)
            ok += 1
            print(f"OK   {name:28s} HTTP {s}  {dt:5.1f}s  {msg}")
        except Exception as ex:  # report and keep going
            print(f"FAIL {name:28s} {type(ex).__name__}: {str(ex)[:160]}")
    print(f"\n{ok}/{len(tests)} fuentes responden sin clave.")


if __name__ == "__main__":
    main()
