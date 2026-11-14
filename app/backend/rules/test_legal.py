"""Tests del semáforo legal (unittest). Desde la raíz del repo:

    python -m unittest discover -s app/backend/rules      # o: python -m unittest app.backend.rules.test_legal

La validación contra el esquema del contrato necesita jsonschema (usa un venv, nunca el sistema); sin él esos tests se omiten.
Esquema: app/data/contract.schema.json si existe; si no, research/contract-v1-draft/v1.1/contract.schema.v1.1.json.
"""
import copy
import json
import unittest
from pathlib import Path

try:
    from . import legal
except ImportError:  # `unittest discover -s app/backend/rules` importa este fichero como módulo suelto
    import legal

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover
    Draft202012Validator = None

HERE = Path(__file__).resolve().parent
RAIZ = HERE.parents[2]  # app/backend/rules -> raíz del repo
RUTAS_ESQUEMA = (RAIZ / "app/data/contract.schema.json",
                 RAIZ / "research/contract-v1-draft/v1.1/contract.schema.v1.1.json")
RUTA_BORRADOR = RAIZ / "research/contract-v1-draft/torre-pacheco.contract-v1.draft.json"

# Copia de la parcela y las 3 rotaciones demo del borrador de contrato (torre-pacheco.contract-v1.draft.json). Los tests de
# colores usan ESTA copia para no romperse si el borrador cambia; `BorradorVivo` comprueba además el fichero real si existe.
DRAFT = {
    "parcela": {"regadio": True, "ha": 4.1, "municipio": "Torre-Pacheco"},
    "ndvi": {"meses_desnudo": ["2025-10", "2025-11", "2025-12", "2026-01", "2026-02"]},
    "rotaciones": [
        {"id": "actual", "es_actual": True, "ciclos": ["melon", "barbecho", "lechuga"], "suelo_desnudo_meses": 5},
        {"id": "alt-a", "es_actual": False, "ciclos": ["brocoli", "haba", "alcachofa"], "suelo_desnudo_meses": 1},
        {"id": "alt-b", "es_actual": False, "ciclos": ["cebada", "veza", "cebada"], "suelo_desnudo_meses": 1},
    ],
}


def _cargar_esquema():
    for ruta in RUTAS_ESQUEMA:
        if ruta.exists():
            return json.loads(ruta.read_text(encoding="utf-8"))
    return None


SCHEMA = _cargar_esquema()
PARCELA = dict(DRAFT["parcela"], ndvi=DRAFT["ndvi"])


def rot(rid, **extra):
    """Rotación del borrador de contrato + ciclos_por_anio=1 (supuesto: cada elemento de `ciclos` es una campaña anual)."""
    r = next(x for x in DRAFT["rotaciones"] if x["id"] == rid)
    base = {"id": r["id"], "es_actual": r["es_actual"], "ciclos": r["ciclos"],
            "suelo_desnudo_meses": r["suelo_desnudo_meses"], "ciclos_por_anio": 1}
    base.update(extra)
    return base


def colores(zona, **extra):
    return {rid: legal.check(rot(rid, **extra), PARCELA, zona) for rid in ("actual", "alt-a", "alt-b")}


class TablaDatos(unittest.TestCase):
    def test_estado_de_reglas_valido(self):
        self.assertTrue(legal.REGLAS)
        for r in legal.REGLAS.values():
            self.assertIn(r["estado"], ("por_verificar", "verificado"), r["id"])
            if r["estado"] == "verificado":
                self.assertIn("Contrastado con el texto consolidado", r["notas"], r["id"])
            self.assertIn(r["tipo"], ("dura", "aviso", "informativo"))
            self.assertIn(r["ambito"], ("zona_1", "ambas", "PAC"))

    def test_reglas_implementadas_existen(self):
        for rid in legal.ORDEN:
            self.assertIn(rid, legal.REGLAS)
            self.assertIn(legal.REGLAS[rid]["implementada"], ("si", "parcial"))

    def test_grupos(self):
        g = lambda c: legal.info_cultivo(c)["grupo"]
        self.assertEqual([g("melon"), g("alcachofa"), g("haba"), g("Brócoli"), g("lechuga")], [2, 2, 2, 1, 1])
        self.assertEqual(legal.info_cultivo("lechuga")["confianza"], "inferido")
        for c in ("cebada", "veza", "vezas", "limon", "limón", "alcaparra", "planta-inventada"):
            self.assertIsNone(g(c), c)
        self.assertEqual(legal.info_cultivo("barbecho")["tipo"], "sin_cultivo")


class Zona2(unittest.TestCase):
    def test_colores_y_articulo(self):
        for rid, s in colores("zona_2").items():
            self.assertEqual(s["color"], "verde", rid)
            self.assertIn("art. 39.2", s["articulo"], rid)

    def test_reglas_de_zona_1_no_aplican(self):
        s = colores("zona_2")["actual"]
        res = {c["id"]: c["resultado"] for c in s["comprobaciones"]}
        for rid in ("L-14", "L-15", "L-16", "L-17"):
            self.assertEqual(res[rid], "no_aplica", rid)
        self.assertEqual(res["L-07"], "ok")
        self.assertNotIn("51.6", s["articulo"])
        self.assertIn("no es obligación legal", s["motivo"])

    def test_nota_fija(self):
        for s in colores("zona_2").values():
            self.assertEqual(s["nota"], "Herramienta de apoyo, no es asesoría legal. Consulta a tu técnico.")

    def test_sin_ciclos_por_anio_es_ambar(self):
        r = rot("actual")
        del r["ciclos_por_anio"]
        s = legal.check(r, PARCELA, "zona_2")
        self.assertEqual(s["color"], "amarillo")
        self.assertIn("39.2", s["articulo"])
        self.assertEqual(next(c for c in s["comprobaciones"] if c["id"] == "L-07")["resultado"], "no_evaluable")

    def test_tres_ciclos_al_anio(self):
        r = rot("alt-a", ciclos_por_anio=3)
        s = legal.check(r, PARCELA, "zona_2")
        self.assertEqual(s["color"], "rojo")
        self.assertIn("art. 39.2", s["articulo"])
        # 3 ciclos de hoja < 45 días sí se permiten (art. 39.2)
        r = {"ciclos": ["lechuga", "lechuga", "lechuga"], "ciclos_por_anio": 3, "ciclo_dias": {"lechuga": 40}}
        self.assertEqual(legal.check(r, PARCELA, "zona_2")["comprobaciones"][0]["resultado"], "ok")
        r["ciclo_dias"] = {"lechuga": 50}
        self.assertEqual(legal.check(r, PARCELA, "zona_2")["color"], "rojo")
        r["ciclo_dias"] = {}
        self.assertEqual(legal.check(r, PARCELA, "zona_2")["color"], "amarillo")

    def test_fertilizacion(self):
        r = rot("alt-a", abonado=[{"forma_n": "urea"}])
        s = legal.check(r, PARCELA, "zona_2")
        self.assertEqual((s["color"], s["articulo"]), ("rojo", "Ley 3/2020 art. 40.2"))
        r = rot("alt-a", abonado=[{"forma_n": "nitrato_amonico", "fondo": True}])
        self.assertEqual(legal.check(r, PARCELA, "zona_2")["color"], "rojo")  # L-10
        r = rot("alt-a", abonado=[{"forma_n": "nitrato_amonico", "ultimo_tercio": True}])
        self.assertEqual(legal.check(r, PARCELA, "zona_2")["articulo"], "Ley 3/2020 art. 40.3")
        r = rot("alt-a", abonado=[{"forma_n": "otro"}])
        self.assertEqual(legal.check(r, PARCELA, "zona_2")["color"], "verde")

    def test_franja(self):
        p = dict(PARCELA, distancia_orilla_m=800)
        r = rot("alt-a", n_kg_ha_anio=200)
        s = legal.check(r, p, "zona_2")
        self.assertEqual((s["color"], s["articulo"]), ("rojo", "Ley 3/2020 art. 29.4.b"))
        s = legal.check(rot("alt-a", n_kg_ha_anio=150), p, "zona_2")
        self.assertEqual(s["color"], "amarillo")  # en franja: art. 29.4.a no se cierra
        s = legal.check(rot("alt-a"), dict(PARCELA, distancia_orilla_m=9000), "zona_2")
        self.assertEqual(s["color"], "verde")

    def test_bcam7(self):
        r = {"ciclos": ["melon", "melon", "melon"], "ciclos_por_anio": 1}
        s = legal.check(r, PARCELA, "zona_2")
        self.assertEqual((s["color"], "BCAM 7" in s["articulo"]), ("amarillo", True))
        s = legal.check(r, dict(PARCELA, explotacion_ha=25), "zona_2")
        self.assertEqual(s["color"], "rojo")


class PorVerificar(unittest.TestCase):
    def test_todas_ambar(self):
        for rid, s in colores("por_verificar").items():
            self.assertEqual(s["color"], "amarillo", rid)
            self.assertIn("por verificar", s["motivo"].lower(), rid)

    def test_articulos(self):
        c = colores("por_verificar")
        self.assertIn("art. 51.6", c["actual"]["articulo"])   # sería falla en Zona 1
        self.assertIn("art. 51.2", c["alt-a"]["articulo"])
        self.assertIn("art. 51.4", c["alt-b"]["articulo"])    # grupo NO CONFIRMADO

    def test_z1_no_se_afirma(self):
        for s in colores("por_verificar").values():
            for c in s["comprobaciones"]:
                if c["id"] in ("L-14", "L-15", "L-16", "L-17"):
                    self.assertEqual(c["resultado"], "no_evaluable", c["id"])
        self.assertIn("«falla»", colores("por_verificar")["actual"]["motivo"])

    def test_regla_de_ambas_zonas_si_se_afirma(self):
        r = rot("alt-a", abonado=[{"forma_n": "urea"}])
        self.assertEqual(legal.check(r, PARCELA, "por_verificar")["color"], "rojo")


class Zona1(unittest.TestCase):
    def test_colores_y_articulo(self):
        c = colores("zona_1")
        self.assertEqual(c["actual"]["color"], "rojo")
        self.assertEqual(c["actual"]["articulo"], "Ley 3/2020 art. 51.6")
        self.assertEqual(c["alt-a"]["color"], "verde")
        for a in ("art. 51.2", "art. 51.3"):
            self.assertIn(a, c["alt-a"]["articulo"])
        self.assertEqual(c["alt-b"]["color"], "amarillo")
        self.assertEqual(c["alt-b"]["articulo"], "Ley 3/2020 art. 51.4")

    def test_ndvi_en_vez_de_numero(self):
        r = rot("actual")
        del r["suelo_desnudo_meses"]
        self.assertEqual(legal.check(r, PARCELA, "zona_1")["color"], "rojo")       # 5 meses seguidos oct-feb
        r["cobertera_invierno"] = True
        self.assertEqual(legal.check(r, PARCELA, "zona_1")["color"], "verde")
        r2 = rot("alt-a")
        del r2["suelo_desnudo_meses"]                                               # no es la rotación actual: sin dato
        self.assertEqual(next(c for c in legal.check(r2, PARCELA, "zona_1")["comprobaciones"] if c["id"] == "L-17")["resultado"], "no_evaluable")

    def test_invernadero_y_secano(self):
        for p in (dict(PARCELA, invernadero=True), dict(PARCELA, regadio=False)):
            s = legal.check(rot("actual"), p, "zona_1")
            self.assertEqual(next(c for c in s["comprobaciones"] if c["id"] == "L-17")["resultado"], "no_aplica")
            self.assertEqual(s["color"], "verde")

    def test_grupo1_consecutivo(self):
        r = {"ciclos": ["brocoli", "brocoli", "haba"], "ciclos_por_anio": 1, "suelo_desnudo_meses": 0}
        s = legal.check(r, PARCELA, "zona_1")          # sin ciclo_dias no se puede aplicar la excepción de 45 días
        self.assertEqual((s["color"], s["articulo"]), ("amarillo", "Ley 3/2020 art. 51.3"))
        r["ciclo_dias"] = {"brocoli": 80}
        s = legal.check(r, PARCELA, "zona_1")
        self.assertEqual((s["color"], s["articulo"]), ("rojo", "Ley 3/2020 art. 51.3"))
        r["ciclo_dias"] = {"brocoli": 40}              # excepción de ciclo < 45 días
        self.assertFalse(any(c["resultado"] == "falla" for c in legal.check(r, PARCELA, "zona_1")["comprobaciones"]))

    def test_lechuga_inferida_no_da_rojo(self):
        r = {"ciclos": ["brocoli", "lechuga", "haba"], "ciclos_por_anio": 1, "ciclo_dias": {"brocoli": 80, "lechuga": 60}}
        s = legal.check(r, PARCELA, "zona_1")
        self.assertEqual((s["color"], s["articulo"]), ("amarillo", "Ley 3/2020 art. 51.3"))  # falla pero con grupo INFERIDO

    def test_dos_grupo1_en_un_anio(self):
        # dos años de 2 ciclos: [brócoli, haba], [melón, alcachofa] -> 1 Grupo 1 por año
        r = {"ciclos": ["brocoli", "haba", "melon", "alcachofa"], "ciclos_por_anio": 2, "suelo_desnudo_meses": 0}
        self.assertEqual(legal.check(r, PARCELA, "zona_1")["color"], "verde")
        # [brócoli, brócoli] en un año: 2 Grupo 1 (y 2 consecutivos); con ciclo 80 días no hay excepción
        r = {"ciclos": ["brocoli", "brocoli", "melon", "alcachofa"], "ciclos_por_anio": 2, "suelo_desnudo_meses": 0, "ciclo_dias": {"brocoli": 80}}
        s = legal.check(r, PARCELA, "zona_1")
        self.assertEqual(s["color"], "rojo")
        self.assertIn(s["articulo"], ("Ley 3/2020 art. 51.2", "Ley 3/2020 art. 51.3"))
        self.assertEqual(next(c for c in s["comprobaciones"] if c["id"] == "L-14")["resultado"], "falla")
        # sin ciclo_dias: la excepción podría aplicar -> no se afirma
        r = {"ciclos": ["brocoli", "brocoli", "melon", "alcachofa"], "ciclos_por_anio": 2, "suelo_desnudo_meses": 0}
        self.assertEqual(legal.check(r, PARCELA, "zona_1")["color"], "amarillo")
        # con lechuga (grupo INFERIDO) el fallo del art. 51.2 no se afirma en rojo
        r = {"ciclos": ["brocoli", "lechuga", "melon", "alcachofa"], "ciclos_por_anio": 2, "suelo_desnudo_meses": 0, "ciclo_dias": {"brocoli": 80, "lechuga": 60}}
        s = legal.check(r, PARCELA, "zona_1")
        self.assertEqual(s["color"], "amarillo")


class Gris(unittest.TestCase):
    def test_gris(self):
        self.assertEqual(legal.check(rot("actual"), PARCELA, "fuera_mar_menor")["color"], "gris")
        self.assertEqual(legal.check(rot("actual"), dict(PARCELA, cobertura="basico"), "zona_2")["color"], "gris")
        self.assertEqual(legal.check({"ciclos": []}, PARCELA, "zona_2")["color"], "gris")


class Allowed(unittest.TestCase):
    def test_zona_1(self):
        ok, motivo, art = legal.allowed("brocoli", "lechuga", "zona_1")
        self.assertFalse(ok)
        self.assertIn("art. 51.3", art)
        self.assertTrue(legal.allowed("brocoli", "lechuga", "zona_1", ciclo_dias={"brocoli": 40, "lechuga": 40})[0])  # excepción < 45 días
        self.assertTrue(legal.allowed("brocoli", "haba", "zona_1")[0])
        self.assertTrue(legal.allowed("melon", "alcachofa", "zona_1")[0])  # G2-G2 permitido
        self.assertTrue(legal.allowed("brocoli", "barbecho", "zona_1")[0])

    def test_zona_2(self):
        ok, motivo, art = legal.allowed("brocoli", "lechuga", "zona_2")
        self.assertTrue(ok)
        self.assertIn("Zona 2", motivo)

    def test_por_verificar(self):
        self.assertTrue(legal.allowed("brocoli", "lechuga", "por_verificar")[0])
        ok, motivo, _ = legal.allowed("brocoli", "lechuga", "por_verificar", conservador=True)
        self.assertFalse(ok)
        self.assertIn("por verificar", motivo)

    def test_desconocido(self):
        ok, motivo, art = legal.allowed("cebada", "brocoli", "zona_1")
        self.assertTrue(ok)
        self.assertIn("NO CONFIRMADO", motivo)
        self.assertIn("51.4", art)
        self.assertFalse(legal.allowed("cebada", "brocoli", "zona_1", conservador=True)[0])
        self.assertTrue(legal.allowed("cebada", "haba", "zona_1")[0])  # G2 conocido: no puede ser G1-G1

    def test_coherente_con_check(self):
        # lo que allowed prohíbe en Zona 1 lo marca check() en rojo
        for a in ("brocoli", "lechuga", "haba", "melon"):
            for b in ("brocoli", "lechuga", "haba", "melon"):
                ok = legal.allowed(a, b, "zona_1")[0]
                dias = {"brocoli": 80, "lechuga": 80}
                ok = legal.allowed(a, b, "zona_1", ciclo_dias=dias)[0]
                s = legal.check({"ciclos": [a, b, "haba"], "ciclos_por_anio": 1, "ciclo_dias": dias}, PARCELA, "zona_1")
                l15 = next(c for c in s["comprobaciones"] if c["id"] == "L-15")
                if not ok:
                    self.assertEqual(l15["resultado"], "falla", (a, b))


@unittest.skipIf(Draft202012Validator is None or SCHEMA is None, "falta jsonschema (usa el venv) o el esquema del contrato")
class Esquema(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sch = Draft202012Validator(SCHEMA)
        defs = {"$schema": SCHEMA["$schema"], "$defs": SCHEMA["$defs"], "$ref": "#/$defs/semaforo_legal"}
        cls.sub = Draft202012Validator(defs)

    def test_vocabulario_v1_1(self):
        for zona in legal.ZONAS_OK:
            for rid, s in colores(zona).items():
                for c in s["comprobaciones"]:
                    self.assertIn(c["resultado"], ("ok", "falla", "no_aplica", "no_evaluable"), (zona, rid, c["id"]))

    def test_semaforo_valido(self):
        for zona in legal.ZONAS_OK:
            for rid, s in colores(zona).items():
                for c in (s, legal.to_contract(s)):
                    errs = list(self.sub.iter_errors(c))
                    self.assertEqual(errs, [], (zona, rid, [e.message for e in errs]))
                self.assertEqual(legal.check(rot(rid), PARCELA, zona, contrato=True), legal.to_contract(s))
                self.assertTrue(legal.to_contract(s)["provisional"])

    def test_gris_valido(self):
        self.assertEqual(list(self.sub.iter_errors(legal.to_contract(legal.check(rot("actual"), PARCELA, "fuera")))), [])

    def test_documento_completo_del_borrador(self):
        """Inserta el semáforo en cada rotación de un documento mínimo y valida los bloques que cambian."""
        for zona in legal.ZONAS_OK:
            for r in DRAFT["rotaciones"]:
                sem = legal.check(rot(r["id"]), PARCELA, zona, contrato=True)
                sem["_status"] = "simulado"
                self.assertEqual(list(self.sub.iter_errors(sem)), [], (zona, r["id"]))

    def test_el_esquema_rechaza_el_vocabulario_antiguo(self):
        s = legal.to_contract(legal.check(rot("actual"), PARCELA, "zona_2"))
        s["comprobaciones"][0]["resultado"] = "cumple"
        self.assertTrue(list(self.sub.iter_errors(s)))

    def test_to_contract_rechaza_resultado_fuera_de_vocabulario(self):
        s = legal.check(rot("actual"), PARCELA, "zona_2")
        s["comprobaciones"][0]["resultado"] = "aviso"
        with self.assertRaises(ValueError):
            legal.to_contract(s)


@unittest.skipUnless(RUTA_BORRADOR.exists(), "no existe el borrador de contrato")
class BorradorVivo(unittest.TestCase):
    """Con el borrador real: no debe romperse aunque cambie (solo se comprueba forma, no colores)."""

    def test_no_se_rompe(self):
        try:
            doc = json.loads(RUTA_BORRADOR.read_text(encoding="utf-8"))
            parcela = dict(doc["parcela"], ndvi=doc.get("ndvi"))
            rotaciones = doc["rotaciones"]
        except (ValueError, KeyError, TypeError):
            self.skipTest("el borrador cambió de forma")
        for zona in legal.ZONAS_OK:
            for r in rotaciones:
                s = legal.check(dict(r, ciclos_por_anio=1), parcela, zona, contrato=True)
                self.assertIn(s["color"], ("verde", "amarillo", "rojo", "gris"))
                self.assertEqual(s["nota"], "Herramienta de apoyo, no es asesoría legal. Consulta a tu técnico.")
                for c in s["comprobaciones"]:
                    self.assertIn(c["resultado"], legal.RESULTADOS)


if __name__ == "__main__":
    unittest.main()
