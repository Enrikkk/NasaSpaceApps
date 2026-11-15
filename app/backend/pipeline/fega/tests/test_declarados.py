import json
import tempfile
import unittest
from pathlib import Path

from app.backend.pipeline.fega import declarados as D

FIX = json.loads((Path(__file__).parent / "fixtures" / "cultivo_declarado_18_426.json").read_text(encoding="utf-8"))
DEMO = (30, 37, 0, 0, 18, 426, 1)


class Declarados(unittest.TestCase):
    def test_tabla_de_productos(self):
        self.assertEqual(D.nombre_producto(20), "BARBECHO TRADICIONAL")
        self.assertEqual(D.nombre_producto(155), "LECHUGA")
        self.assertTrue(D.nombre_producto(99999).startswith("PRODUCTO"))

    def test_recinto_demo_tiene_dos_registros_y_se_conservan(self):
        r = D.normalizar(FIX["features"], DEMO)
        self.assertEqual(len(r), 2, "0..N: no se asume un unico registro")
        self.assertIn("BARBECHO TRADICIONAL", [x["producto"] for x in r])
        self.assertEqual(D.cultivo_principal(r), "BARBECHO TRADICIONAL")
        barb = [x for x in r if x["producto_codigo"] == 20][0]
        self.assertEqual(barb["sistema_explotacion"], "R")
        self.assertAlmostEqual(barb["superficie_cultivada_ha"], 4.09, places=2)

    def test_no_se_copian_identificadores_de_explotacion(self):
        for x in D.normalizar(FIX["features"], DEMO):
            self.assertFalse({"exp_num", "exp_ca", "exp_provincia"} & set(x))

    def test_filtra_por_clave_completa_de_recinto(self):
        self.assertEqual(len(D.normalizar(FIX["features"], (30, 37, 0, 0, 18, 450, 1))), 1)
        self.assertEqual(D.normalizar(FIX["features"], (30, 37, 0, 0, 18, 999, 1)), [])

    def test_buscar_con_cache_y_sin_red(self):
        class Resp:
            def __init__(s, b): s.b = b
            def read(s): return s.b
            def __enter__(s): return s
            def __exit__(s, *a): return False
        llamadas = []
        def abrir(req, timeout=0):
            llamadas.append(req.full_url)
            return Resp(json.dumps(FIX).encode())
        with tempfile.TemporaryDirectory() as td:
            a = D.buscar(37.7383, -0.98838, DEMO, td, abrir=abrir, offline=False)
            self.assertEqual(len(a["registros"]), 2)
            self.assertFalse(a["de_cache"])
            b = D.buscar(37.7383, -0.98838, DEMO, td, abrir=abrir, offline=False)
            self.assertTrue(b["de_cache"])
            self.assertEqual(len(llamadas), 1, "la segunda llamada sale de cache")
            self.assertIsNone(D.buscar(37.0, -1.0, (30, 1, 0, 0, 1, 1, 1), td, offline=True))

    def test_error_de_red_degrada_a_none(self):
        def abrir(req, timeout=0): raise OSError("sin red")
        with tempfile.TemporaryDirectory() as td:
            self.assertIsNone(D.buscar(37.7, -1.0, DEMO, td, abrir=abrir, offline=False))


if __name__ == "__main__":
    unittest.main()
