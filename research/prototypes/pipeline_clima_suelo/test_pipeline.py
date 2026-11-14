"""Tests unitarios (sin red): usan la cache de la parcela demo de cache/. Ejecutar:  python3 -m unittest -v
(los tests de esquema se saltan si jsonschema no esta instalado)."""
import json
import os
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

os.environ["AGROCKHAM_OFFLINE"] = "1"  # cualquier intento de red falla
HERE = Path(__file__).resolve().parent
os.environ["AGROCKHAM_CACHE_DIR"] = str(HERE / "cache")

import pipeline as P  # noqa: E402

LAT, LON = 37.7383, -0.98838
try:
    import jsonschema  # noqa: F401
    TIENE_JSONSCHEMA = True
except ImportError:
    TIENE_JSONSCHEMA = False


class TestCeldas(unittest.TestCase):
    def test_celda_power_demo(self):
        self.assertEqual(P.celda_power(LAT, LON), ("75_-2", 37.5, -1.25))

    def test_celda_01_demo_es_centro_de_pixel(self):
        self.assertEqual(P.celda_01(LAT, LON), ("377_-10", 37.75, -0.95))

    def test_misma_celda_para_puntos_cercanos_y_distinta_para_lejanos(self):
        self.assertEqual(P.celda_01(37.7383, -0.9884)[0], P.celda_01(37.7101, -0.9501)[0])
        self.assertNotEqual(P.celda_01(37.7383, -0.9884)[0], P.celda_01(37.8101, -0.9884)[0])
        self.assertEqual(P.celda_suelo(LAT, LON)[0], P.celda_suelo(LAT + 0.0003, LON + 0.0003)[0])
        self.assertNotEqual(P.celda_suelo(LAT, LON)[0], P.celda_suelo(LAT + 0.01, LON)[0])

    def test_centro_de_celda_de_suelo_dentro_de_la_celda(self):
        _, la, lo = P.celda_suelo(LAT, LON)
        self.assertLess(abs(la - LAT), 0.0013)
        self.assertLess(abs(lo - LON), 0.0013)


class TestDerivados(unittest.TestCase):
    def test_serie_diaria_descarta_relleno(self):
        dic = {"20050101": 1.5, "20050102": -999.0, "20050104": 2.0}
        s, n = P._serie_diaria(dic)
        self.assertEqual(len(s), P.N_DIAS)
        self.assertEqual(s[:4], [1.5, None, None, 2.0])  # relleno y hueco -> None
        self.assertEqual(n, 1)

    def test_por_anio_exige_dias_validos(self):
        s = [1.0] * P.N_DIAS
        self.assertEqual(P._por_anio(s, sum)[2005], 365.0)
        for i in range(10):  # 10 dias sin dato en 2005 -> anio descartado
            s[i] = None
        self.assertIsNone(P._por_anio(s, sum)[2005])
        self.assertEqual(P._por_anio(s, sum)[2006], 365.0)

    def test_textura_usda(self):
        casos = {(90, 5, 5): "arenoso", (33, 34, 33): "franco-arcilloso", (20, 60, 20): "franco-limoso",
                 (20, 20, 60): "arcilloso", (40, 40, 20): "franco", (18.7, 43.8, 37.4): "franco-arcillo-limoso",
                 (10, 85, 5): "limoso", (60, 15, 25): "franco-arcillo-arenoso"}
        for (s, si, c), esperado in casos.items():
            self.assertEqual(P.usda_textura(s, si, c), esperado, (s, si, c))

    def test_saxton_rawls_franco(self):
        awc, cc, pmp = P.saxton_rawls_awc(40, 20, 2.5)  # franco tipico
        self.assertAlmostEqual(cc, 0.28, delta=0.02)
        self.assertAlmostEqual(pmp, 0.137, delta=0.01)
        self.assertTrue(0.12 < awc < 0.17, awc)

    def test_conversion_materia_organica(self):
        # soc 124 dg/kg -> 12,4 g/kg -> 1,24 % C -> x1,724 = 2,14 % MO
        c = P._capa_convertida({"clay": {"d": 370}, "sand": {"d": 190}, "silt": {"d": 440}, "soc": {"d": 124},
                                "phh2o": {"d": 80}, "nitrogen": {"d": 110}}, "d")
        self.assertAlmostEqual(c["soc"], 12.4)
        self.assertAlmostEqual(c["soc"] / 10 * P.FACTOR_MO, 2.138, places=2)
        self.assertAlmostEqual(c["clay"], 37.0)
        self.assertAlmostEqual(c["phh2o"], 8.0)
        self.assertAlmostEqual(c["nitrogen"], 1.1)

    def test_pendiente_ols(self):
        self.assertAlmostEqual(P._ols_pendiente([0, 1, 2, 3], [1, 3, 5, 7]), 2.0)


class TestBloquesDesdeCache(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        P.net_reset()
        cls.clima = P.build_clima(LAT, LON)
        cls.suelo = P.build_suelo(LAT, LON)
        cls.llamadas = P.NET["llamadas"]

    def test_cero_llamadas_de_red(self):
        self.assertEqual(self.llamadas, 0)

    def test_clima_estructura(self):
        c = self.clima
        self.assertEqual(c["_status"], "real")
        self.assertEqual([f["anio"] for f in c["serie_anual"]], list(range(2005, 2025)))
        self.assertEqual(set(c["lluvia_anual_mm"]["fuentes"]), {"power", "imerg", "open-meteo"})
        self.assertEqual(len(c["et0_mm_mes"]["valores"]), 12)
        lo, hi = c["lluvia_anual_mm"]["horquilla"]
        self.assertLessEqual(lo, c["lluvia_anual_mm"]["valor"])
        self.assertLessEqual(c["lluvia_anual_mm"]["valor"], hi)

    def test_lluvia_en_rango_y_fuentes_distintas(self):
        ll = self.clima["lluvia_anual_mm"]
        self.assertTrue(250 <= ll["valor"] <= 350, ll)
        self.assertGreater(ll["horquilla"][1] - ll["horquilla"][0], 50)

    def test_2024_coincide_con_la_investigacion(self):
        f24 = next(f for f in self.clima["serie_anual"] if f["anio"] == 2024)["lluvia_por_fuente_mm"]
        self.assertAlmostEqual(f24["era5"], 185, delta=2)
        self.assertAlmostEqual(f24["power"], 211, delta=2)
        self.assertAlmostEqual(f24["imerg"], 263, delta=2)

    def test_sin_valores_de_relleno(self):
        def numeros(o):
            if isinstance(o, dict):
                for v in o.values():
                    yield from numeros(v)
            elif isinstance(o, list):
                for v in o:
                    yield from numeros(v)
            elif isinstance(o, (int, float)) and not isinstance(o, bool):
                yield o
        self.assertTrue(all(x > -990 for x in numeros(self.clima)))  # ningun -999 de relleno colado
        for f in self.clima["serie_anual"]:
            self.assertGreaterEqual(f["lluvia_mm"], 0)
            self.assertGreater(f["tmin_min_c"], -90)

    def test_helada_pendiente_siam(self):
        h = self.clima["dias_helada"]
        self.assertEqual(h["fuente"], "pendiente SIAM")
        self.assertTrue(h["provisional"])
        self.assertNotIn("FROST_DAYS", json.dumps(self.clima["serie_anual"]))

    def test_metadatos_de_trazabilidad(self):
        m = self.clima["metadatos"]["fuentes"]
        self.assertIn("time-standard=UTC", m["power_imerg"]["url"])
        self.assertEqual(m["power_imerg"]["time_standard"], "UTC")
        self.assertTrue(all(v for v in self.clima["metadatos"]["descarga"].values()))
        self.assertIn("NO comercial", m["open_meteo"]["licencia"])
        self.assertIn("mm/day", m["power_merra2"]["unidades"].values())

    def test_suelo(self):
        s = self.suelo
        self.assertEqual(s["_status"], "real")
        self.assertEqual(s["fuente_id"], "soilgrids")
        self.assertAlmostEqual(s["arena_pct"] + s["limo_pct"] + s["arcilla_pct"], 100, delta=0.3)
        self.assertEqual(s["textura"], P.usda_textura(s["arena_pct"], s["limo_pct"], s["arcilla_pct"]))
        self.assertAlmostEqual(s["materia_organica_pct"], round(s["soc_g_kg"] / 10 * P.FACTOR_MO, 2), delta=0.02)
        self.assertEqual(len(s["capas"]), 3)
        self.assertIn("modelo", s["metadatos"]["aviso"].lower())
        self.assertIn("CC BY 4.0", s["metadatos"]["licencia"])

    @unittest.skipUnless(TIENE_JSONSCHEMA, "jsonschema no instalado")
    def test_bloques_validan_contra_el_esquema(self):
        import validate_blocks as V
        schema = json.loads((HERE.parent.parent / "contract-v1-draft" / "contract.schema.json").read_text())
        self.assertEqual(V.validar_bloque("clima", self.clima, schema), [])
        self.assertEqual(V.validar_bloque("suelo", self.suelo, schema), [])
        import copy
        malo = copy.deepcopy(self.clima)
        del malo["serie_anual"][0]["lluvia_mm"]
        self.assertTrue(V.validar_bloque("clima", malo, schema))  # el validador detecta una mutacion


class TestRedYCache(unittest.TestCase):
    def test_sin_cache_y_offline_falla_y_cuenta(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(P, "CACHE_DIR", Path(d)):
            P.net_reset()
            with self.assertRaises(P.RedBloqueada):
                P.get_power_merra2(LAT, LON)
            self.assertEqual(P.NET["llamadas"], 0)  # bloqueada antes de salir

    def test_cache_en_hit_no_llama(self):
        P.net_reset()
        _, hit = P.get_openmeteo(LAT, LON)
        self.assertTrue(hit)
        self.assertEqual(P.NET["llamadas"], 0)

    def test_reintento_en_429_y_conteo(self):
        class R:
            def __enter__(s): return s
            def __exit__(s, *a): return False
            def read(s): return b'{"ok": 1}'
        llamadas = []

        def fake(req, timeout=None):
            llamadas.append(1)
            if len(llamadas) == 1:
                raise urllib.error.HTTPError(req.full_url, 429, "Too Many", {}, None)
            return R()
        with mock.patch.dict(os.environ, {"AGROCKHAM_OFFLINE": "0"}), mock.patch.object(P.urllib.request, "urlopen", fake), \
                mock.patch.object(P.time, "sleep") as sl:
            P.net_reset()
            self.assertEqual(P.http_get_json("https://x.example/a", backoff=(7,)), {"ok": 1})
            self.assertEqual(P.NET["llamadas"], 2)
            sl.assert_called_once_with(7)

    def test_404_no_se_reintenta(self):
        def fake(req, timeout=None):
            raise urllib.error.HTTPError(req.full_url, 404, "nf", {}, None)
        with mock.patch.dict(os.environ, {"AGROCKHAM_OFFLINE": "0"}), mock.patch.object(P.urllib.request, "urlopen", fake):
            P.net_reset()
            with self.assertRaises(urllib.error.HTTPError):
                P.http_get_json("https://x.example/a")
            self.assertEqual(P.NET["llamadas"], 1)

    def test_limite_soilgrids_5_por_minuto(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(P, "CACHE_DIR", Path(d)):
            with mock.patch.object(P.time, "sleep") as sl:
                P._soilgrids_espera()  # primera llamada: sin espera
                sl.assert_not_called()
                P._soilgrids_marca()
                P._soilgrids_espera()  # inmediatamente despues: debe esperar casi 12,5 s
                self.assertTrue(sl.called)
                self.assertGreater(sl.call_args[0][0], 12.0)
        self.assertGreaterEqual(60 / P.SOILGRIDS_MIN_INTERVALO_S, 4.7)
        self.assertLessEqual(60 / P.SOILGRIDS_MIN_INTERVALO_S, 5)


if __name__ == "__main__":
    unittest.main()
