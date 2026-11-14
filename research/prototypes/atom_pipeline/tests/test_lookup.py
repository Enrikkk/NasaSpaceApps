"""Tests de lookup.py. Datos: ATOM_BUILD_DIR (salida de build_recintos.py) o, si no, ATOM_SRC_DIR (ZIPs del ATOM;
se construye 30037+30045 en un directorio temporal). Sin ninguno de los dos, se omiten.

    ATOM_SRC_DIR=/ruta/zips /ruta/venv/bin/python -m unittest discover -s tests -v
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import build_recintos  # noqa: E402
from lookup import RecintoIndex  # noqa: E402

SCHEMA = HERE.parents[2] / "contract-v1-draft" / "contract.schema.json"
LAT, LON = 37.7383, -0.98838  # parcela demo: SIGPAC 30/37/0/0/18/426/1
_TMP = None


def _data_dir():
    global _TMP
    d = os.environ.get("ATOM_BUILD_DIR")
    if d:
        return d
    src = os.environ.get("ATOM_SRC_DIR")
    if src:
        _TMP = tempfile.TemporaryDirectory()
        build_recintos.main(["--src", src, "--out", _TMP.name, "--municipios", "30037,30045"])
        return _TMP.name
    return None


class TestLookup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        d = _data_dir()
        if not d:
            raise unittest.SkipTest("define ATOM_BUILD_DIR o ATOM_SRC_DIR")
        cls.idx = RecintoIndex.load(d, codigos=["30037", "30045"])
        cls.rest = json.loads((HERE / "fixtures" / "sigpac_recinfobypoint_30-37-18-426-1.json").read_text())[0]

    def test_punto_demo_es_recinto_18_426_1(self):
        r = self.idx.recinto_por_punto(LAT, LON)
        self.assertEqual(r["sigpac"], {"poligono": 18, "parcela": 426, "recinto": 1})
        self.assertEqual(r["municipio"], "Torre-Pacheco")
        self.assertEqual(r["comarca"], "Campo de Cartagena")
        self.assertAlmostEqual(r["ha"], 4.09, delta=0.005)
        self.assertTrue(r["regadio"])
        self.assertEqual(r["id"], "30-37-0-0-18-426-1")

    def test_coincide_con_respuesta_rest_de_sigpac(self):
        """Contraste con recinfobypoint (respuesta guardada en fixtures/, 1 peticion hecha a mano)."""
        r = self.idx.recinto_por_punto(LAT, LON, detalle=True)
        rest = self.rest
        self.assertEqual((rest["poligono"], rest["parcela"], rest["recinto"]), (18, 426, 1))
        self.assertAlmostEqual(r["ha"], rest["superficie"], delta=0.0002)
        self.assertAlmostEqual(r["pendiente_pct"], rest["pendiente_media"], places=1)
        self.assertEqual(r["coef_regadio"], rest["coef_regadio"])
        self.assertEqual(r["uso_sigpac"], rest["uso_sigpac"])
        self.assertEqual(r["altitud_m"], rest["altitud"])
        self.assertEqual(r["region"], rest["region"])
        self.assertEqual(",".join(map(str, r["incidencias"])), rest["incidencias"])
        import shapely
        a = shapely.from_wkt(rest["wkt"])
        b = shapely.geometry.shape(r["geometry"])
        iou = a.intersection(b).area / a.union(b).area
        self.assertGreater(iou, 0.999)

    def test_bloque_valido_contra_esquema_contrato(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("jsonschema no instalado")
        s = json.loads(SCHEMA.read_text())
        v = Draft202012Validator({"$ref": "#/$defs/bloque_parcela", "$defs": s["$defs"]})
        errs = list(v.iter_errors(self.idx.recinto_por_punto(LAT, LON)))
        self.assertEqual(errs, [], errs)

    def test_otro_municipio(self):
        r = self.idx.recinto_por_punto(37.7617, -0.8715)  # Los Alcazares (fichero 30045)
        self.assertEqual(r["id"].split("-")[:2], ["30", "45"])
        self.assertEqual(r["municipio"], "Los Alcázares")

    def test_punto_en_el_mar_es_none_y_tolerancia(self):
        self.assertIsNone(self.idx.recinto_por_punto(37.80, -0.70))
        self.assertIsNone(self.idx.recinto_por_punto(37.80, -0.70, tol_m=5))

    def test_tolerancia_recoge_el_borde(self):
        # 3 m al oeste de la esquina ya fuera del recinto: sin tolerancia puede no devolver el mismo recinto
        r0 = self.idx.recinto_por_punto(LAT, LON, detalle=True)
        from shapely.geometry import shape
        minx = shape(r0["geometry"]).bounds[0]
        lon_out = minx - 3e-5  # ~2,6 m
        self.assertIsNotNone(self.idx.recinto_por_punto(LAT, lon_out, tol_m=50))

    def test_bbox(self):
        bbox = (-0.992, 37.736, -0.985, 37.741)
        fc = self.idx.recintos_en_bbox(bbox)
        refs = {f["properties"]["ref"] for f in fc["features"]}
        self.assertIn("30/37/0/0/18/426/1", refs)
        self.assertTrue(10 < len(refs) < 500)
        self.assertEqual(self.idx.recintos_en_bbox(bbox, limit=3)["features"].__len__(), 3)
        self.assertIn("FONDO ESPAÑOL", fc["attribution"])
        # todo recinto devuelto interseca de verdad el bbox
        import shapely
        box = shapely.box(*bbox)
        for f in fc["features"]:
            self.assertTrue(box.intersects(shapely.geometry.shape(f["geometry"])))


if __name__ == "__main__":
    unittest.main()
