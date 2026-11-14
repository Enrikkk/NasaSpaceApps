#!/usr/bin/env python3
"""Valida los bloques `clima` y `suelo` contra contract.schema.json y comprueba cifras de cordura.

Necesita jsonschema (venv, no en el sistema):
    /ruta/venv/bin/python validate_blocks.py [out/37.7383_-0.98838.blocks.json]

1. Cada bloque contra `#/$defs/bloque_clima` / `#/$defs/bloque_suelo` del esquema.
2. Mezcla los bloques en una copia del borrador (research/contract-v1-draft), anade las fuentes nuevas y pasa el
   esquema completo + los 12 invariantes de validate.py (la copia sigue llevando bloques simulados: es solo para probar).
3. Cordura: lluvia anual 250-350 mm, las tres fuentes difieren, la serie de 2024 frente a la investigacion (185/211/263).
"""
import copy
import importlib.util
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
DRAFT = HERE.parent.parent / "contract-v1-draft"


def cargar_validate_py():
    spec = importlib.util.spec_from_file_location("contract_validate", DRAFT / "validate.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def validar_bloque(nombre, bloque, schema):
    sub = {"$schema": schema["$schema"], "$ref": f"#/$defs/bloque_{nombre}", "$defs": schema["$defs"]}
    return [f"{nombre}/{'/'.join(str(p) for p in e.absolute_path)}: {e.message[:200]}"
            for e in Draft202012Validator(sub).iter_errors(bloque)]


def cordura(clima, suelo):
    """Devuelve lista de (comprobacion, ok, detalle)."""
    r = []
    ll = clima["lluvia_anual_mm"]
    r.append(("lluvia anual media 250-350 mm", 250 <= ll["valor"] <= 350, f"{ll['valor']} mm, horquilla {ll['horquilla']}"))
    pf = ll["por_fuente_mm"]
    dif = max(pf.values()) - min(pf.values())
    r.append(("las tres fuentes difieren (> 10 % del valor)", dif > 0.10 * ll["valor"], f"{pf}; diferencia {dif:.0f} mm"))
    r.append(("serie de 20 anios 2005-2024", [f["anio"] for f in clima["serie_anual"]] == list(range(2005, 2025)), ""))
    f24 = next(f for f in clima["serie_anual"] if f["anio"] == 2024)["lluvia_por_fuente_mm"]
    esperado = {"era5": 185, "power": 211, "imerg": 263}
    ok24 = all(abs(f24[k] - v) <= 2 for k, v in esperado.items())
    r.append(("2024 coincide con la investigacion (ERA5 185 / POWER 211 / IMERG 263)", ok24, f"medido {f24}"))
    et0 = clima["et0_mm_mes"]["anual_mm"]
    r.append(("ET0 anual 1100-1500 mm (semiarido mediterraneo)", 1100 <= et0 <= 1500, f"{et0} mm; deficit medio {et0 - ll['valor']:.0f} mm"))
    r.append(("ET0 maxima en jun-ago, minima en dic-ene", max(clima["et0_mm_mes"]["valores"]) in clima["et0_mm_mes"]["valores"][5:8]
              and min(clima["et0_mm_mes"]["valores"]) in (clima["et0_mm_mes"]["valores"][0], clima["et0_mm_mes"]["valores"][11]), ""))
    r.append(("dias_helada marcado pendiente SIAM", clima["dias_helada"]["fuente"] == "pendiente SIAM" and clima["dias_helada"]["provisional"], ""))
    r.append(("MO 0,5-5 % y pH 6-9", 0.5 <= suelo["materia_organica_pct"] <= 5 and 6 <= suelo["ph_h2o"] <= 9,
              f"MO {suelo['materia_organica_pct']} %, pH {suelo['ph_h2o']}"))
    s = suelo["arena_pct"] + suelo["limo_pct"] + suelo["arcilla_pct"]
    r.append(("arena + limo + arcilla = 100 %", abs(s - 100) < 0.5, f"{s:.1f}"))
    r.append(("agua disponible 0-30 cm 20-70 mm", 20 <= suelo["agua_disponible_mm"] <= 70, f"{suelo['agua_disponible_mm']} mm"))
    return r


def main(argv):
    ruta = Path(argv[1]) if len(argv) > 1 else HERE / "out" / "37.7383_-0.98838.blocks.json"
    b = json.loads(ruta.read_text())
    schema = json.loads((DRAFT / "contract.schema.json").read_text())
    fallos = 0

    print("== 1. Bloques contra el esquema ==")
    for n in ("clima", "suelo"):
        errs = validar_bloque(n, b[n], schema)
        print(f"  bloque {n}: {'OK' if not errs else 'FALLO'}")
        for e in errs:
            print("    -", e)
        fallos += len(errs)

    print("== 2. Mezcla en una copia del borrador: esquema completo + invariantes ==")
    V = cargar_validate_py()
    doc = json.loads((DRAFT / "torre-pacheco.contract-v1.draft.json").read_text())
    doc = copy.deepcopy(doc)
    doc["clima"], doc["suelo"] = b["clima"], b["suelo"]
    doc["fuentes"] += [f for f in b["fuentes_nuevas"] if f["id"] not in {x["id"] for x in doc["fuentes"]}]
    errs = V.validar(doc, schema)
    print(f"  esquema completo: {'OK' if not errs else 'FALLO'}")
    for e in errs:
        print("    -", e)
    fallos += len(errs)
    for nombre, e in V.check_invariantes(doc):
        # los invariantes que miran rotaciones usan el mock; aqui solo cuenta que no se rompan por clima/suelo
        print(f"  [{'OK' if not e else 'FALLO'}] {nombre}")
        for x in e:
            print("      -", x)
        fallos += len(e)

    print("== 3. Cordura ==")
    for nombre, ok, det in cordura(b["clima"], b["suelo"]):
        print(f"  [{'OK' if ok else 'NO'}] {nombre} {('| ' + det) if det else ''}")
        fallos += 0 if ok else 1

    print(f"\nRESULTADO: {'TODO OK' if fallos == 0 else str(fallos) + ' fallos'}")
    return 0 if fallos == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
