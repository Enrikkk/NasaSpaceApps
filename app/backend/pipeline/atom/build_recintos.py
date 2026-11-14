#!/usr/bin/env python3
"""ATOM del FEGA (recintos SIGPAC, GPKG por municipio) -> GeoJSON gzip + indice ligero.

Paso de preparacion offline (T-011). No usa la API en vivo de SIGPAC.

Uso:
    python -m app.backend.pipeline.atom.build_recintos --src DIR_CON_ZIPS --out DIR_SALIDA [--municipios 30037,30045] [--bbox minx,miny,maxx,maxy]

Entrada: ficheros `{prov2}{mun3}_rec_{campana}_{fecha}_gpkg.zip` (o `.gpkg` ya extraidos) del ATOM
https://www.fega.gob.es/atom/2026/rec_2026/30%20-%20MURCIA/ . Se leen directamente del ZIP (GDAL /vsizip/), sin extraer
ni ejecutar nada de ellos.

Salida por municipio (CODIGO = provincia+municipio SIGPAC, p. ej. 30037):
    CODIGO_recintos.geojson.gz   FeatureCollection, UN feature por linea (sigue siendo GeoJSON valido),
                                 coordenadas WGS84/ETRS89 con 6 decimales, solo las propiedades necesarias.
    CODIGO.index.json            metadatos y estadisticas del municipio.
Mas un `index.json` global (todos los municipios, tablas de codigos, atribucion).

Propiedades por feature (nombres cortos, mismas unidades que la API REST de SIGPAC):
    ref        "30/37/0/0/18/426/1"  (provincia/municipio/agregado/zona/poligono/parcela/recinto)
    ha         superficie en ha (dn_surface en m2 / 10000), 4 decimales
    pend_pct   pendiente media en % (pendiente_media viene en milesimas -> / 10), 1 decimal (se omite si es nula)
    uso        codigo de uso SIGPAC (TA, CI, IV, ...)
    coef_reg   coeficiente de regadio 0-100 (se omite si es nulo en origen)
    alt        altitud en m (se omite si es nula)
    region     codigo de region de produccion (se omite si es nulo)
    inc        lista de codigos de incidencia (se omite si no hay)
"""
import argparse
import collections
import datetime as dt
import glob
import gzip
import io
import json
import os
import re
import sys
import time

import numpy as np
import shapely
from pyogrio.raw import read as ogr_read

ATTRIBUTION = "Fuente de los datos: FONDO ESPAÑOL DE GARANTÍA AGRARIA O.A."
LICENSE = "CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/deed.es)"
SOURCE_URL = "https://www.fega.gob.es/atom/es.fega.sigpac.rec.2026.xml"
TERMS_URL = "https://www.fega.gob.es/orig/pdfs/Terminos_de_uso_de_informacion_de_alto_valor_del_SIGC.pdf"

# Codigo SIGPAC (30 + municipio SIGPAC 3 cifras) -> nombre. NO son todos codigos INE (ver research/sigpac-atom-campo-cartagena.md).
# Solo los verificados en ese informe; el resto queda como None.
MUNICIPIOS = {
    "30016": "Cartagena",
    "30021": "Fuente Álamo de Murcia",
    "30030": "Murcia",
    "30035": "San Javier",
    "30036": "San Pedro del Pinatar",
    "30037": "Torre-Pacheco",
    "30041": "La Unión",
    "30045": "Los Alcázares",
}
FNAME_RE = re.compile(r"(?P<prov>\d{2})(?P<mun>\d{3})_rec_(?P<camp>\d{4})_(?P<fecha>\d{8})")
COORD_PRECISION = 1e-6  # 6 decimales (~0,1 m)


def find_sources(src):
    """Devuelve {codigo: ruta} de ZIP o GPKG en `src` (si hay ZIP y GPKG del mismo codigo, gana el ZIP)."""
    out = {}
    for pat in ("*.gpkg", "*_gpkg.zip"):
        for p in sorted(glob.glob(os.path.join(src, pat))):
            m = FNAME_RE.search(os.path.basename(p))
            if m:
                out[m["prov"] + m["mun"]] = p
    return out


def gdal_path(p):
    return "/vsizip/" + os.path.abspath(p) if p.endswith(".zip") else os.path.abspath(p)


def read_code_tables(path):
    """Tablas de codigos que vienen dentro del propio GPKG (uso, incidencia, region)."""
    tables = {}
    _, _, _, d = ogr_read(path, layer="cod_usosigpac", read_geometry=False)
    tables["uso"] = {str(a): str(b) for a, b in zip(d[0], d[1])}
    for key, layer in (("incidencia", "cod_incidencia"), ("region", "cod_region_2023")):
        _, fids, _, d = ogr_read(path, layer=layer, read_geometry=False, return_fids=True)
        tables[key] = {str(int(f)): str(v) for f, v in zip(fids, d[0])}  # el codigo es el fid de la tabla
    return tables


def build_municipio(path, outdir, bbox=None):
    m = FNAME_RE.search(os.path.basename(path))
    code = m["prov"] + m["mun"]
    t0 = time.perf_counter()
    gp = gdal_path(path)
    meta, _, wkb, data = ogr_read(gp, layer="recinto")
    f = dict(zip(meta["fields"], data))
    t_read = time.perf_counter()
    tables = read_code_tables(gp)
    geom = shapely.from_wkb(wkb)  # EPSG:4258 (ETRS89 geografico); lon/lat, equivalente a WGS84 a nivel de metros
    n_src = len(geom)

    keep = np.ones(n_src, bool)
    if bbox:
        b = shapely.bounds(geom)
        keep = (b[:, 0] <= bbox[2]) & (b[:, 2] >= bbox[0]) & (b[:, 1] <= bbox[3]) & (b[:, 3] >= bbox[1])
    idx = np.flatnonzero(keep)
    # set_precision: redondea a 6 decimales y devuelve geometrias VALIDAS (round simple dejaba ~0,3 % invalidas;
    # unos pocos recintos se parten en MultiPolygon).
    geom = shapely.set_precision(geom[idx], COORD_PRECISION)
    # astillas < 1 m2 pueden colapsar a geometria vacia al redondear: se descartan (y se cuentan en el indice)
    nonempty = ~shapely.is_empty(geom)
    n_vacios = int((~nonempty).sum())
    idx, geom = idx[nonempty], geom[nonempty]
    gj = shapely.to_geojson(geom)

    ha = np.round(f["dn_surface"][idx] / 10000.0, 4)
    pend = np.round(f["pendiente_media"][idx].astype(float) / 10.0, 1)  # NaN si nulo
    coef = f["coef_regadio"][idx].astype(float)  # NaN si nulo
    reg = f["region"][idx].astype(float)
    alt = f["altitud"][idx].astype(float)
    uso = f["uso_sigpac"][idx]
    inc = f["incidencias"][idx]
    ref_cols = [f[k][idx] for k in ("provincia", "municipio", "agregado", "zona", "poligono", "parcela", "recinto")]

    raw_path = os.path.join(outdir, f"{code}_recintos.geojson.gz")
    nbytes = 0
    ha_uso = collections.defaultdict(float)
    n_uso = collections.Counter()
    ha_reg = 0.0
    n_reg = 0
    n_multi = 0
    refs = []
    buf = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buf, compresslevel=9, mtime=0) as gz:
        def w(s):
            nonlocal nbytes
            b = s.encode("utf-8")
            nbytes += len(b)
            gz.write(b)

        w('{"type":"FeatureCollection","features":[\n')
        n = len(idx)
        for i in range(n):
            ref = "/".join(str(int(c[i])) for c in ref_cols)
            props = {"ref": ref, "ha": float(ha[i])}
            if not np.isnan(pend[i]):
                props["pend_pct"] = float(pend[i])
            u = uso[i] if uso[i] is not None else ""
            props["uso"] = u
            if not np.isnan(coef[i]):
                props["coef_reg"] = int(coef[i])
            if not np.isnan(alt[i]):
                props["alt"] = int(alt[i])
            if not np.isnan(reg[i]):
                props["region"] = int(reg[i])
            if inc[i]:
                props["inc"] = [int(x) for x in str(inc[i]).split(",") if x.strip()]
            ha_uso[u] += float(ha[i])
            n_uso[u] += 1
            if not np.isnan(coef[i]) and coef[i] > 0:
                ha_reg += float(ha[i])
                n_reg += 1
            if gj[i].startswith('{"type":"MultiPolygon"'):
                n_multi += 1
            refs.append(ref)
            w('{"type":"Feature","properties":' + json.dumps(props, separators=(",", ":"), ensure_ascii=False)
              + ',"geometry":' + gj[i] + "}" + ("," if i < n - 1 else "") + "\n")
        w("]}\n")
    gzb = buf.getvalue()
    with open(raw_path, "wb") as fh:
        fh.write(gzb)
    t_end = time.perf_counter()

    b = shapely.bounds(geom)
    m_val = re.search(r"(\d{4})(\d{2})(\d{2})", m["fecha"])
    info = {
        "codigo": code,
        "municipio": MUNICIPIOS.get(code),
        "fichero_origen": os.path.basename(path),
        "campana": int(m["camp"]),
        "fecha_validez": f"{m_val[1]}-{m_val[2]}-{m_val[3]}",
        "crs": "EPSG:4258 en origen; salida lon/lat con 6 decimales (ETRS89, equivalente a WGS84 a escala de metros)",
        "n_recintos_origen": int(n_src),
        "n_recintos": int(n),
        "n_descartados_vacios_tras_redondeo": n_vacios,
        "n_multipolygon_tras_redondeo": int(n_multi),
        "bbox": [float(b[:, 0].min()), float(b[:, 1].min()), float(b[:, 2].max()), float(b[:, 3].max())],
        "ha_total": round(float(ha.sum()), 2),
        "ha_regadio_coef_gt0": round(ha_reg, 2),
        "n_regadio_coef_gt0": n_reg,
        "ha_por_uso": {k: round(v, 2) for k, v in sorted(ha_uso.items(), key=lambda kv: -kv[1])},
        "n_por_uso": dict(n_uso.most_common()),
        "fichero_salida": os.path.basename(raw_path),
        "bytes_geojson": nbytes,
        "bytes_gzip": len(gzb),
        "segundos_lectura_gpkg": round(t_read - t0, 3),
        "segundos_total": round(t_end - t0, 3),
        "extraido_el": dt.date.today().isoformat(),
    }
    with open(os.path.join(outdir, f"{code}.index.json"), "w", encoding="utf-8") as fh:
        json.dump(info, fh, ensure_ascii=False, indent=1)
    return info, tables


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True, help="directorio con los *_gpkg.zip (o .gpkg) del ATOM")
    ap.add_argument("--out", required=True, help="directorio de salida (NO dentro del repo)")
    ap.add_argument("--municipios", help="lista de codigos SIGPAC separados por comas (por defecto, todos los encontrados)")
    ap.add_argument("--bbox", help="minx,miny,maxx,maxy: conserva solo recintos que intersecan (p. ej. recortar Murcia)")
    a = ap.parse_args(argv)

    srcs = find_sources(a.src)
    if a.municipios:
        want = [c.strip() for c in a.municipios.split(",") if c.strip()]
        missing = [c for c in want if c not in srcs]
        if missing:
            sys.exit(f"Faltan ficheros para: {missing}. Encontrados: {sorted(srcs)}")
        srcs = {c: srcs[c] for c in want}
    if not srcs:
        sys.exit("No se encontro ningun *_gpkg.zip / .gpkg en --src")
    bbox = tuple(float(x) for x in a.bbox.split(",")) if a.bbox else None
    os.makedirs(a.out, exist_ok=True)

    infos, tables = {}, {}
    t0 = time.perf_counter()
    for code, p in sorted(srcs.items()):
        info, tables = build_municipio(p, a.out, bbox)
        infos[code] = info
        print(f"{code} {str(info['municipio']):<24} {info['n_recintos']:>6} recintos  geojson {info['bytes_geojson']/1e6:6.2f} MB  "
              f"gzip {info['bytes_gzip']/1e6:5.2f} MB  {info['segundos_total']:5.2f} s")
    total = round(time.perf_counter() - t0, 3)
    index = {
        "atribucion": ATTRIBUTION,
        "licencia": LICENSE,
        "fuente": SOURCE_URL,
        "terminos_de_uso": TERMS_URL,
        "aviso": "Datos transformados por Agrockham: unidades (m2->ha, milesimas->%), redondeo a 6 decimales, "
                 "recorte opcional. Sin respaldo ni patrocinio del FEGA.",
        "generado": dt.datetime.now().isoformat(timespec="seconds"),
        "segundos_total": total,
        "municipios": infos,
        "codigos": tables,
    }
    with open(os.path.join(a.out, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=1)
    n = sum(i["n_recintos"] for i in infos.values())
    print(f"TOTAL {n} recintos en {total:.2f} s -> {a.out}")


if __name__ == "__main__":
    main()
