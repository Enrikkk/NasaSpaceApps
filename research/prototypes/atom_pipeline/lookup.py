#!/usr/bin/env python3
"""Consulta espacial en memoria sobre los GeoJSON gzip generados por build_recintos.py.

    from lookup import RecintoIndex
    idx = RecintoIndex.load("/ruta/a/build")           # todos los *_recintos.geojson.gz (o codigos=["30037"])
    idx.recinto_por_punto(37.7383, -0.98838)            # -> bloque `parcela` del contrato v1 (dict) o None
    idx.recintos_en_bbox((-1.0, 37.73, -0.98, 37.75))   # -> FeatureCollection (dict) con los recintos que intersecan
    idx.recintos_en_bbox_json(bbox)                     # -> mismo, como str JSON ya serializado (para FastAPI Response)

CLI:  python lookup.py --data DIR --point LAT LON   |   --bbox MINX MINY MAXX MAXY
Atribucion obligatoria al mostrar los datos: "Fuente de los datos: FONDO ESPAÑOL DE GARANTÍA AGRARIA O.A." (CC BY 4.0).
"""
import argparse
import glob
import gzip
import json
import math
import os
import time

import numpy as np
import shapely
import shapely.ops
from shapely import STRtree

ATTRIBUTION = "Fuente de los datos: FONDO ESPAÑOL DE GARANTÍA AGRARIA O.A."
# Supuesto de este prototipo (no viene en el ATOM): municipios considerados Campo de Cartagena.
COMARCA_CAMPO_CARTAGENA = {"30016", "30021", "30035", "30036", "30037", "30041", "30045"}
_M_PER_DEG_LAT = 111_320.0


class RecintoIndex:
    def __init__(self, lines, geoms, index_meta):
        self._lines = lines          # str JSON de cada Feature (para servir sin reserializar; props se parsean al pedirlas)
        self._geoms = geoms          # np.array de shapely
        self.meta = index_meta       # index.json global (nombres, tablas de codigos, atribucion)
        self._tree = STRtree(geoms)

    def _p(self, i):
        return json.loads(self._lines[i])["properties"]

    # ---- carga ---------------------------------------------------------------------------------------------
    @classmethod
    def load(cls, data_dir, codigos=None):
        files = sorted(glob.glob(os.path.join(data_dir, "*_recintos.geojson.gz")))
        if codigos:
            files = [f for f in files if os.path.basename(f)[:5] in set(codigos)]
        if not files:
            raise FileNotFoundError(f"sin *_recintos.geojson.gz en {data_dir}")
        lines = []
        for fp in files:
            with gzip.open(fp, "rt", encoding="utf-8") as fh:
                for ln in fh:
                    if ln.startswith('{"type":"Feature"'):
                        ln = ln.rstrip().rstrip(",")
                        lines.append(ln)
        geoms = shapely.from_geojson(np.array(lines, dtype=object), on_invalid="raise")
        meta = {}
        ip = os.path.join(data_dir, "index.json")
        if os.path.exists(ip):
            with open(ip, encoding="utf-8") as fh:
                meta = json.load(fh)
        return cls(lines, geoms, meta)

    def __len__(self):
        return len(self._lines)

    # ---- consultas -----------------------------------------------------------------------------------------
    def _nombre_municipio(self, cod):
        m = self.meta.get("municipios", {}).get(cod, {})
        return m.get("municipio")

    def _feature_por_punto(self, lat, lon, tol_m=0.0):
        pt = shapely.Point(lon, lat)
        cand = self._tree.query(pt, predicate="intersects")
        if len(cand) == 0 and tol_m > 0:
            dlon = tol_m / (_M_PER_DEG_LAT * math.cos(math.radians(lat)))
            dlat = tol_m / _M_PER_DEG_LAT
            near = self._tree.query(shapely.box(lon - dlon, lat - dlat, lon + dlon, lat + dlat))
            if len(near):
                # distancia en metros aproximada (equirectangular)
                best, bd = None, None
                for i in near:
                    q = shapely.ops.nearest_points(self._geoms[i], pt)[0]  # punto del recinto mas cercano
                    dm = math.hypot((q.x - lon) * _M_PER_DEG_LAT * math.cos(math.radians(lat)), (q.y - lat) * _M_PER_DEG_LAT)
                    if dm <= tol_m and (bd is None or dm < bd):
                        best, bd = int(i), dm
                cand = [] if best is None else [best]
        if len(cand) == 0:
            return None
        # un punto sobre el borde comun cae en varios recintos: determinista (menor ref lexicografica)
        return int(min(cand, key=lambda i: self._p(i)["ref"]))

    def recinto_por_punto(self, lat, lon, tol_m=0.0, detalle=False):
        """Recinto SIGPAC que contiene (lat, lon), como bloque `parcela` del contrato v1; None si no hay.

        tol_m: si el punto cae fuera de todo recinto, acepta el mas cercano a <= tol_m metros.
        detalle=True anade campos extra (uso, coef. regadio, altitud, incidencias, ref, geometria) fuera del esquema.
        `_status` = "precalculado" (dato oficial FEGA transformado offline), `zonas` = [] (no sale del ATOM).
        """
        i = self._feature_por_punto(lat, lon, tol_m)
        if i is None:
            return None
        p = self._p(i)
        prov, mun, agr, zona, pol, par, rec = (int(x) for x in p["ref"].split("/"))
        cod = f"{prov:02d}{mun:03d}"
        out = {
            "_status": "precalculado",
            "id": "-".join(str(x) for x in (prov, mun, agr, zona, pol, par, rec)),
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "ha": p["ha"],
            "regadio": bool(p.get("coef_reg", 0) and p["coef_reg"] > 0),
            "zonas": [],
            "sigpac": {"poligono": pol, "parcela": par, "recinto": rec},
            "fuente_id": "sigpac",
        }
        if "pend_pct" in p:
            out["pendiente_pct"] = p["pend_pct"]
        nombre = self._nombre_municipio(cod)
        if nombre:
            out["municipio"] = nombre
        if cod in COMARCA_CAMPO_CARTAGENA:
            out["comarca"] = "Campo de Cartagena"
        if detalle:
            cods = self.meta.get("codigos", {})
            out.update({
                "ref": p["ref"],
                "uso_sigpac": p.get("uso"),
                "uso_desc": cods.get("uso", {}).get(p.get("uso", "")),
                "coef_regadio": p.get("coef_reg"),
                "altitud_m": p.get("alt"),
                "region": p.get("region"),
                "incidencias": p.get("inc", []),
                "geometry": json.loads(shapely.to_geojson(self._geoms[i])),
                "atribucion": ATTRIBUTION,
            })
        return out

    def _indices_bbox(self, bbox):
        minx, miny, maxx, maxy = bbox
        return np.sort(self._tree.query(shapely.box(minx, miny, maxx, maxy), predicate="intersects"))

    def recintos_en_bbox_json(self, bbox, limit=None):
        """FeatureCollection como str JSON (reutiliza las lineas ya serializadas: sin reserializar)."""
        ids = self._indices_bbox(bbox)
        if limit is not None:
            ids = ids[:limit]
        return ('{"type":"FeatureCollection","attribution":"' + ATTRIBUTION + '","features":['
                + ",".join(self._lines[i] for i in ids) + "]}")

    def recintos_en_bbox(self, bbox, limit=None):
        """FeatureCollection (dict) de los recintos que intersecan bbox=(minx, miny, maxx, maxy) en lon/lat."""
        return json.loads(self.recintos_en_bbox_json(bbox, limit))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", required=True)
    ap.add_argument("--point", nargs=2, type=float, metavar=("LAT", "LON"))
    ap.add_argument("--bbox", nargs=4, type=float, metavar=("MINX", "MINY", "MAXX", "MAXY"))
    a = ap.parse_args()
    t = time.perf_counter()
    idx = RecintoIndex.load(a.data)
    print(f"cargado {len(idx)} recintos en {time.perf_counter()-t:.2f} s")
    if a.point:
        print(json.dumps(idx.recinto_por_punto(*a.point, detalle=True), ensure_ascii=False, indent=1)[:1500])
    if a.bbox:
        fc = idx.recintos_en_bbox(a.bbox)
        print(f"{len(fc['features'])} recintos en bbox")


if __name__ == "__main__":
    main()
