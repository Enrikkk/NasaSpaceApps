#!/usr/bin/env python3
"""Genera torre-pacheco.contract-v1.draft.json (BORRADOR del contrato v1, T-009).

Solo libreria estandar. Semilla fija: la misma salida byte a byte en cada ejecucion.
TODOS los numeros son ILUSTRATIVOS (_status "simulado"): sirven para desarrollar la UI y el
validador, no son datos medidos ni salida del motor. El motor real (T-012/T-020) los sustituira.

Uso:  python3 generate_draft.py            (escribe el JSON junto a este script)
"""
import json
import math
import random
import textwrap
from pathlib import Path

SEED = 20261114
N_ESCENARIOS = 200
ANIOS = list(range(2005, 2025))  # 20 anios, como la serie POWER cacheada por enrique
HERE = Path(__file__).resolve().parent
OUT = HERE / "torre-pacheco.contract-v1.draft.json"

AVISO = ("MOCK: valores ilustrativos para desarrollar la UI y el validador. No son datos medidos ni salida del "
         "motor. Generado con semilla fija por generate_draft.py. Sustituir por la salida real de la tuberia.")


# ---------------------------------------------------------------- utilidades estadisticas
def percentile(values, q):
    """Percentil con interpolacion lineal (igual que numpy por defecto). q en [0,1]."""
    v = sorted(values)
    pos = (len(v) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    return v[lo] + (v[hi] - v[lo]) * (pos - lo)


def wilson(successes, n, z=1.959964):
    p = successes / n
    d = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / d
    mitad = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, centro - mitad), min(1.0, centro + mitad)


def slope(xs, ys):
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)


# ---------------------------------------------------------------- JSON bonito (listas de escalares compactas)
def dumps(obj, indent=0):
    pad = "  " * indent
    pad2 = "  " * (indent + 1)
    if isinstance(obj, dict):
        if not obj:
            return "{}"
        items = [f"{pad2}{json.dumps(k, ensure_ascii=False)}: {dumps(v, indent + 1)}" for k, v in obj.items()]
        return "{\n" + ",\n".join(items) + "\n" + pad + "}"
    if isinstance(obj, list):
        if not obj:
            return "[]"
        if all(not isinstance(x, (dict, list)) for x in obj):
            flat = ", ".join(json.dumps(x, ensure_ascii=False) for x in obj)
            if len(flat) + len(pad2) <= 110:
                return "[" + flat + "]"
            if all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in obj):
                lines = textwrap.wrap(flat, width=110, break_long_words=False, break_on_hyphens=False)
                return "[\n" + "\n".join(pad2 + ln for ln in lines) + "\n" + pad + "]"
            return "[\n" + ",\n".join(pad2 + json.dumps(x, ensure_ascii=False) for x in obj) + "\n" + pad + "]"
        return "[\n" + ",\n".join(pad2 + dumps(x, indent + 1) for x in obj) + "\n" + pad + "]"
    return json.dumps(obj, ensure_ascii=False)


# ---------------------------------------------------------------- fuentes
FUENTES = [
    {"id": "power", "nombre": "NASA POWER (temperatura, radiacion, lluvia)", "url": "https://power.larc.nasa.gov/",
     "licencia": "Datos abiertos NASA; citar el DOI del producto", "licencia_estado": "verify"},
    {"id": "imerg", "nombre": "GPM IMERG (lluvia)", "url": "https://gpm.nasa.gov/data",
     "licencia": "Datos abiertos NASA; citar el DOI del producto", "licencia_estado": "verify"},
    {"id": "hls", "nombre": "HLS v2.0 L30 (NDVI, Landsat/Sentinel-2 armonizado)",
     "url": "https://lpdaac.usgs.gov/products/hlsl30v002/",
     "licencia": "Datos abiertos NASA; citar el DOI del producto", "licencia_estado": "verify"},
    {"id": "soilgrids", "nombre": "ISRIC SoilGrids 2.0", "url": "https://soilgrids.org/",
     "licencia": "CC BY 4.0 (Poggio et al. 2021, SOIL 7, 217-240)", "licencia_estado": "verify"},
    {"id": "sigpac", "nombre": "SIGPAC y cultivo declarado (FEGA)", "url": "https://sigpac.mapa.es/fega/visor/",
     "licencia": "CC BY 4.0 segun INSPIRE/datos.gob.es; acceso desde codigo por confirmar con el FEGA",
     "licencia_estado": "verify"},
    {"id": "siam", "nombre": "SIAM-IMIDA, estacion TP91 (series horarias)",
     "url": "https://datosabiertos.carm.es/odata/Agricultura/IMIDA_estaciones.csv",
     "licencia": "Por verificar (no revisada)", "licencia_estado": "verify"},
    {"id": "ley-3-2020", "nombre": "Ley 3/2020 de recuperacion y proteccion del Mar Menor (BOE)",
     "url": "https://www.boe.es/buscar/act.php?id=BOE-A-2020-9793",
     "licencia": "Informacion del sector publico, reutilizacion permitida; citar BOE-A-2020-9793",
     "licencia_estado": "ok"},
    {"id": "fao-56", "nombre": "FAO Riego y Drenaje 56 (evapotranspiracion de cultivos)",
     "url": "https://www.fao.org/4/x0490e/x0490e0b.htm", "licencia": "Por verificar (no revisada)",
     "licencia_estado": "verify"},
    {"id": "fao-29", "nombre": "FAO Riego y Drenaje 29 (calidad del agua para la agricultura)",
     "url": "https://www.fao.org/4/Y4263E/y4263e0e.htm", "licencia": "Por verificar (no revisada)",
     "licencia_estado": "verify"},
    {"id": "eurostat-precios", "nombre": "Eurostat apri_ap_crpouta (precios de productos agricolas)",
     "url": "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/apri_ap_crpouta?format=JSON&geo=ES",
     "licencia": "Por verificar (no revisada)", "licencia_estado": "verify"},
    {"id": "mock", "nombre": "Valores ilustrativos de este borrador (no son un dataset)", "url": "",
     "licencia": "Propios del equipo", "licencia_estado": "ok"},
]

# ---------------------------------------------------------------- definicion de las 3 rotaciones
# k_clima: anios con perdida climatica >= 20 % (se reparten por rango); margen_obj y coste: calibran el margen medio.
ROTS = [
    dict(id="actual", nombre="Lo que haces hoy: melon, barbecho, lechuga", es_actual=True,
         ciclos=["melon", "barbecho", "lechuga"], k_clima=8, margen_obj=2900, coste=6600, vol=0.22,
         agua=5200, pef=60, sobreoferta=0.35, suelo_n=0.25, desnudo=5, caja=6000, meses_ingreso=4,
         color="amarillo",
         motivo=("Suelo de regadio desnudo mas de 2 meses en otono-invierno (5 meses segun el NDVI simulado); "
                 "reglas exclusivas de zona 1 sin evaluar hasta verificar la zona"),
         articulo="Ley 3/2020 art. 51.6 (por verificar en el BOE)",
         comprobaciones=[
             ("Suelo de regadio desnudo > 2 meses en otono-invierno exige cubierta", "no_cumple",
              "Ley 3/2020 art. 51.6", "por_verificar"),
             ("Maximo 2 ciclos por anio (3 solo hoja < 45 dias)", "cumple", "Ley 3/2020 art. 39", "por_verificar"),
             ("Un solo ciclo del grupo 1 y nunca dos seguidos (solo zona 1)", "indeterminado",
              "Ley 3/2020 art. 51", "por_verificar"),
             ("Rotacion de cultivos (BCAM 7 de la PAC)", "cumple", "BCAM 7 (FEGA)", "por_verificar"),
         ],
         por_que="Es tu rotacion actual, sirve de referencia.",
         beneficios=["Cultivos y mercados que ya conoces", "Sin inversion nueva en maquinaria ni semilla"],
         evidencia=[{"dato": "5 meses de suelo desnudo (simulado)", "dataset": "HLS-VI NDVI", "fuente_id": "hls",
                     "url": "https://lpdaac.usgs.gov/products/hlsl30v002/"}],
         huecos=["Sin rendimientos reales de tu parcela",
                 "Zona 1 o 2 del Mar Menor sin verificar en el Anexo I de la Ley 3/2020"],
         riesgos=["Arrastre de nitrato con lluvia fuerte en otono", "Precio de la lechuga por debajo del coste en varios anios"]),
    dict(id="alt-a", nombre="Brocoli, haba (leguminosa), alcachofa", es_actual=False,
         ciclos=["brocoli", "haba", "alcachofa"], k_clima=6, margen_obj=3300, coste=6500, vol=0.16,
         agua=4300, pef=70, sobreoferta=0.20, suelo_n=0.70, desnudo=1, caja=7800, meses_ingreso=5,
         color="verde",
         motivo=("Cubierta en otono-invierno y leguminosa que reduce abono N; un solo ciclo del grupo 1 "
                 "(reglas de zona 1 por verificar)"),
         articulo="Ley 3/2020 art. 51.6 y art. 40 (por verificar en el BOE)",
         comprobaciones=[
             ("Suelo de regadio desnudo > 2 meses en otono-invierno exige cubierta", "cumple",
              "Ley 3/2020 art. 51.6", "por_verificar"),
             ("Maximo 2 ciclos por anio (3 solo hoja < 45 dias)", "cumple", "Ley 3/2020 art. 39", "por_verificar"),
             ("Un solo ciclo del grupo 1 y nunca dos seguidos (solo zona 1)", "indeterminado",
              "Ley 3/2020 art. 51", "por_verificar"),
             ("Sin urea ni N mineral en fondo", "aviso", "Ley 3/2020 art. 40", "por_verificar"),
             ("Rotacion de cultivos (BCAM 7 de la PAC)", "cumple", "BCAM 7 (FEGA)", "por_verificar"),
         ],
         por_que="La haba fija nitrogeno y cubre el suelo en invierno; menos agua y menos riesgo de nitrato.",
         beneficios=["Menos abono nitrogenado gracias a la leguminosa", "Suelo cubierto en invierno",
                     "Posible ingreso del ecorregimen de rotacion (por verificar)"],
         evidencia=[{"dato": "Lluvia anual ilustrativa en la serie simulada", "dataset": "NASA POWER / IMERG",
                     "fuente_id": "power", "url": "https://power.larc.nasa.gov/"}],
         huecos=["Precio de la alcachofa y del brocoli sin serie larga de fuente oficial",
                 "Grupo legal de alcachofa y haba sin confirmar"],
         riesgos=["Mercado de la alcachofa saturado si todos la plantan"]),
    dict(id="alt-b", nombre="Cebada, veza (cubierta), cebada", es_actual=False,
         ciclos=["cebada", "veza", "cebada"], k_clima=5, margen_obj=1800, coste=2100, vol=0.12,
         agua=2100, pef=90, sobreoferta=0.10, suelo_n=0.80, desnudo=1, caja=1800, meses_ingreso=6,
         color="verde", motivo="Bajo consumo de agua y suelo cubierto con la veza",
         articulo="Ley 3/2020 art. 51.6 (por verificar en el BOE)",
         comprobaciones=[
             ("Suelo de regadio desnudo > 2 meses en otono-invierno exige cubierta", "cumple",
              "Ley 3/2020 art. 51.6", "por_verificar"),
             ("Maximo 2 ciclos por anio (3 solo hoja < 45 dias)", "cumple", "Ley 3/2020 art. 39", "por_verificar"),
             ("Rotacion de cultivos (BCAM 7 de la PAC)", "cumple", "BCAM 7 (FEGA)", "por_verificar"),
         ],
         por_que="Aguanta calor y sequia; margen menor pero muy estable bajo clima 2050.",
         beneficios=["Muy poca agua", "La veza cubre el suelo y aporta nitrogeno"],
         evidencia=[{"dato": "Dias de calor > 38 C en la serie simulada, con tendencia al alza", "dataset": "NASA POWER",
                     "fuente_id": "power", "url": "https://power.larc.nasa.gov/"}],
         huecos=["La veza se trata como cubierta de ingreso cero: sin precio, coste ni rendimiento verificados",
                 "Sin rendimientos reales de cebada de regadio"],
         riesgos=["Ingresos bajos si tu prioridad es maximizar margen"]),
]

# Umbral a y pendiente b de FAO-29 (tabla de la investigacion). Cultivos sin dato: no cuentan.
FAO29 = {"melon": (1.0, 8.4), "lechuga": (1.3, 13.0), "haba": (1.6, 9.6), "brocoli": (2.8, 9.2), "cebada": (8.0, 5.0)}
BREAKEVEN = {"melon": 0.30, "lechuga": 0.36, "brocoli": 0.52, "haba": 0.45, "alcachofa": 0.40, "cebada": 0.20}
ECW, ETA, TARIFA = 1.2, 0.90, 0.35


def build():
    rng = random.Random(SEED)

    # ---- clima: serie anual simulada
    serie = []
    for i, y in enumerate(ANIOS):
        tmin = round(rng.gauss(-0.8, 1.3), 1)
        serie.append({
            "anio": y,
            "lluvia_mm": max(120, round(rng.gauss(285, 55))),
            "tmin_min_c": tmin,
            "tmax_max_c": round(rng.gauss(40.5, 1.4), 1),
            "dias_calor_gt_38": max(0, round(rng.gauss(3 + 0.2 * i, 2))),
            "dias_helada": 0 if tmin >= 0 else 1 + int(abs(tmin)),
        })
    lluvias = [s["lluvia_mm"] for s in serie]
    calor = [s["dias_calor_gt_38"] for s in serie]
    heladas = [s["dias_helada"] for s in serie]
    clima = {
        "_status": "simulado",
        "lluvia_anual_mm": {"valor": round(sum(lluvias) / 20),
                            "horquilla": [round(percentile(lluvias, 0.10)), round(percentile(lluvias, 0.90))],
                            "fuentes": ["power", "imerg", "siam"]},
        "dias_calor_gt_38": {"valor": round(sum(calor) / 20),
                             "tendencia": f"{slope(ANIOS, calor) * 10:+.1f} por decada"},
        "dias_helada": {"valor": round(sum(heladas) / 20), "estacion": "SIAM TP91 (estacion, no tu campo exacto)"},
        "escenario_2050": {"lluvia_pct": -12, "temp_c": 1.8,
                           "metodo": "deltas aplicados a los umbrales (simulado; NEX-GDDP-CMIP6 es hoja de ruta)"},
        "serie_anual": serie,
    }

    # ---- severidad climatica y de precio comunes a todas las rotaciones (anio emparejado clima+precio)
    sev = [rng.gauss(0, 1) for _ in ANIOS]
    zprice = [0.35 * sev[i] + rng.gauss(0, 0.9) for i in range(20)]  # anios de helada tienden a subir precios

    # ---- escenarios alineados: la muestra i usa el mismo anio, beta y factor de coste en todas las rotaciones
    anio_idx = [rng.randrange(20) for _ in range(N_ESCENARIOS)]
    phi = [rng.uniform(-1.5, -0.3) for _ in range(N_ESCENARIOS)]
    cuota = [rng.uniform(0.2, 0.4) for _ in range(N_ESCENARIOS)]
    beta = [phi[i] * cuota[i] for i in range(N_ESCENARIOS)]
    fcoste = [rng.uniform(0.85, 1.15) for _ in range(N_ESCENARIOS)]
    escenarios_meta = {
        "_status": "simulado",
        "n": N_ESCENARIOS,
        "semilla": SEED,
        "unidad": "eur_ha_por_anio_medio_de_la_secuencia",
        "metodo": ("Remuestreo con reemplazo de los 20 anios historicos (clima y precio emparejados) + beta de "
                   "sobreoferta + factor de coste +-15 %. El indice i es el MISMO anio y los MISMOS parametros en "
                   "todas las rotaciones, para que 'B gana en el X %' compare muestra a muestra. 20 anios no son "
                   "200 realizaciones independientes: se propaga incertidumbre de parametros, no informacion "
                   "climatica nueva."),
        "rotaciones_orden": [r["id"] for r in ROTS],
        "anio_clima": [ANIOS[i] for i in anio_idx],
        "beta_sobreoferta": [round(b, 4) for b in beta],
        "factor_coste": [round(f, 3) for f in fcoste],
    }

    rotaciones = []
    for r in ROTS:
        # perdida climatica por anio: los k_clima anios peores (severidad + ruido propio) superan el 20 %
        score = [sev[i] + rng.gauss(0, 0.6) for i in range(20)]
        orden = sorted(range(20), key=lambda i: -score[i])
        malos = set(orden[:r["k_clima"]])
        thr_bad = score[orden[r["k_clima"] - 1]]
        good_scores = [score[i] for i in range(20) if i not in malos]
        lo, hi = min(good_scores), max(good_scores)
        perdida = []
        for i in range(20):
            if i in malos:
                perdida.append(round(min(48.0, 20 + 5.5 * (score[i] - thr_bad) + 3 * rng.random()), 1))
            else:
                perdida.append(round(19.0 * ((score[i] - lo) / (hi - lo)) ** 1.5, 1))
        factor = [(1 - 1.4 * perdida[i] / 100) * (1 + r["vol"] * zprice[i]) for i in range(20)]
        base_rev = (r["margen_obj"] + r["coste"]) / (sum(factor) / 20)
        rev = [base_rev * f for f in factor]
        marg_hist = [rev[i] - r["coste"] for i in range(20)]

        # exito conjunto (D-008): anio malo si perdida >= 20 % O margen < 0 con el precio de ese anio
        mal_clima = [perdida[i] >= 20 for i in range(20)]
        mal_eco = [marg_hist[i] < 0 for i in range(20)]
        mal_conj = [a or b for a, b in zip(mal_clima, mal_eco)]
        n, k = 20, sum(mal_conj)
        w_lo, w_hi = wilson(n - k, n)
        peores = sorted([i for i in range(20) if mal_conj[i]], key=lambda i: marg_hist[i])[:3]
        exito = {
            "_status": "simulado",
            "valor": round(100 * (n - k) / n),
            "horquilla": [round(100 * w_lo), round(100 * w_hi)],
            "k_malos": k, "n": n,
            "metodo": "conjunto_20_anios_wilson_95 (D-008: perdida clima < 20 % Y margen >= 0, mismo anio)",
            "desglose": {
                "clima": {"k_malos": sum(mal_clima), "n": n, "umbral_perdida_pct": 20},
                "economico": {"k_malos": sum(mal_eco), "n": n, "umbral": "margen_eur_ha < 0"},
                "conjunto": {"k_malos": k, "n": n},
            },
            "peores_anios": [{
                "anio": ANIOS[i], "perdida_clima_pct": perdida[i], "margen_eur_ha": round(marg_hist[i]),
                "motivo": ("clima+economico" if mal_clima[i] and mal_eco[i] else "clima" if mal_clima[i] else "economico"),
            } for i in peores],
        }

        # muestras de margen (escenarios alineados)
        muestras = [round(rev[anio_idx[j]] * math.exp(beta[j] * r["sobreoferta"]) - r["coste"] * fcoste[j])
                    for j in range(N_ESCENARIOS)]
        p10, p50, p90 = (round(percentile(muestras, q)) for q in (0.10, 0.50, 0.90))
        be = {c: BREAKEVEN[c] for c in dict.fromkeys(r["ciclos"]) if c in BREAKEVEN}
        margen = {
            "_status": "simulado",
            "valor": round(sum(muestras) / len(muestras)),
            "horquilla": [p10, p90], "p10": p10, "p50": p50, "p90": p90,
            "breakeven_precio_eur_kg": be,
            "nota": "valor = media de las muestras; la horquilla es exactamente [p10, p90]",
        }

        # agua y sal (FAO-56 / FAO-29, ilustrativo)
        bruto = r["agua"]
        ece = round(1.5 * ECW, 2)
        perdidas = [max(0.0, b * (ece - a)) for c, (a, b) in FAO29.items() if c in r["ciclos"]]
        perdida_sal = round(sum(perdidas) / len(perdidas), 1) if perdidas else None
        agua_detalle = {
            "_status": "simulado",
            "etc_mm": round(bruto * ETA / 10 + r["pef"]),
            "precipitacion_efectiva_mm": r["pef"],
            "eficiencia_riego": ETA,
            "bruto_m3_ha": bruto,
            "tarifa_eur_m3": TARIFA,
            "coste_eur_ha": round(bruto * TARIFA),
            "ecw_dSm": ECW, "ece_dSm": ece,
            "perdida_sal_pct": perdida_sal,
            "nota": "ECw ilustrativa; perdida media de los cultivos con dato FAO-29 (los demas no cuentan)",
        }

        # sobreoferta
        a = r["sobreoferta"]
        efectos = [100 * (math.exp(beta[j] * a) - 1) for j in range(N_ESCENARIOS)]
        sobre = {
            "_status": "simulado",
            "indice_SI": a,
            "beta": round(percentile(beta, 0.5), 3),
            "efecto_precio_pct": {"valor": round(percentile(efectos, 0.5), 1),
                                  "horquilla": [round(percentile(efectos, 0.10), 1), round(percentile(efectos, 0.90), 1)]},
            "semaforo": "verde" if a <= 0.2 else "amarillo" if a <= 0.4 else "rojo",
            "escala": "indice 0-1 (proxy: superficie declarada del cultivo en la comarca); efecto = exp(beta*a)-1",
        }

        criterios = {
            "margen": round(min(1, max(0, margen["valor"] / 4000)), 3),
            "agua": round(min(1, max(0, 1 - bruto / 6000)), 3),
            "suelo_n": r["suelo_n"],
            "riesgo": round(exito["valor"] / 100, 3),
        }

        rotaciones.append({
            "id": r["id"], "nombre": r["nombre"], "es_actual": r["es_actual"], "ciclos": r["ciclos"],
            "_status": "simulado",
            "exito_pct": exito,
            "margen_eur_ha": margen,
            "agua_m3_ha": bruto,
            "agua_detalle": agua_detalle,
            "sobreoferta": a,
            "sobreoferta_detalle": sobre,
            "criterios": criterios,
            "suelo_desnudo_meses": r["desnudo"],
            "inversion": {"_status": "simulado", "pico_caja_negativa_eur_ha": r["caja"],
                          "meses_hasta_primer_ingreso": r["meses_ingreso"]},
            "semaforo_legal": {
                "_status": "simulado", "color": r["color"], "motivo": r["motivo"], "articulo": r["articulo"],
                "comprobaciones": [{"regla": a_, "resultado": b_, "articulo": c_, "estado": d_}
                                   for (a_, b_, c_, d_) in r["comprobaciones"]],
            },
            "escenarios_margen_eur_ha": muestras,
            "por_que": r["por_que"], "beneficios": r["beneficios"], "evidencia": r["evidencia"],
            "huecos": r["huecos"], "riesgos": r["riesgos"],
        })

    doc = {
        "schema_version": "1.0.0-draft",
        "_meta": {
            "aviso": AVISO,
            "borrador_fecha": "2026-11-14",
            "generador": "research/contract-v1-draft/generate_draft.py",
            "semilla": SEED,
            "congelado": False,
            "bloques_pendientes": [],
            "cobertura": {"nivel": "completo", "ambito": "Campo de Cartagena (por municipio, D-009)"},
            "normalizacion_criterios": ("Todos en 0-1 con 1 = mejor para el agricultor. margen = margen_eur_ha.valor/4000; "
                                        "agua = 1 - agua_m3_ha/6000; riesgo = exito_pct.valor/100; suelo_n = supuesto "
                                        "etiquetado. Escalas de referencia fijas (no min-max entre rotaciones)."),
            "unidades": {"margen_eur_ha": "euros 2025 por ha y anio medio de la secuencia", "agua_m3_ha": "m3 brutos por ha y anio"},
        },
        "parcela": {
            "_status": "simulado",
            "id": "30-0-0-0-0-0-demo (SIGPAC 18/426/1)",
            "lat": 37.7383, "lon": -0.98838, "ha": 4.1, "pendiente_pct": 1.2, "regadio": True,
            "municipio": "Torre-Pacheco", "comarca": "Campo de Cartagena",
            "sigpac": {"poligono": 18, "parcela": 426, "recinto": 1},
            "zonas": ["zona_vulnerable_nitratos", "mar_menor_zona_por_verificar"],
            "fuente_id": "sigpac",
        },
        "historia": {
            "_status": "simulado",
            "fuente_id": "sigpac",
            "cultivos_declarados": [
                {"campana": "2023", "anio": 2023, "cultivo": "lechuga", "fuente": "FEGA"},
                {"campana": "2024", "anio": 2024, "cultivo": "brocoli", "fuente": "FEGA"},
                {"campana": "2025", "anio": 2025, "cultivo": "melon", "fuente": "FEGA"},
                {"campana": "2026", "anio": 2026, "cultivo": "barbecho", "fuente": "FEGA"},
            ],
        },
        "ndvi": {
            "_status": "simulado",
            "fuente": "HLS-VI (mock)", "fuente_id": "hls",
            "meses_desnudo": ["2025-10", "2025-11", "2025-12", "2026-01", "2026-02"],
            "meses_vulnerable": ["2025-08"],
        },
        "clima": clima,
        "suelo": {"_status": "simulado", "textura": "franco-arcilloso", "materia_organica_pct": 1.1,
                  "agua_disponible_mm": 120, "fuente": "SoilGrids", "fuente_id": "soilgrids"},
        "prioridades_defecto": {"rentabilidad": 0.4, "agua": 0.25, "suelo": 0.2, "riesgo": 0.15},
        "escenarios_meta": escenarios_meta,
        "rotaciones": rotaciones,
        "variantes": {
            "_status": "simulado",
            "definiciones": [
                {"id": "lluvia_-30", "descripcion": "Lluvia -30 %", "delta": {"lluvia_pct": -30, "temp_c": 0}},
                {"id": "lluvia_-15", "descripcion": "Lluvia -15 %", "delta": {"lluvia_pct": -15, "temp_c": 0}},
                {"id": "lluvia_+10", "descripcion": "Lluvia +10 %", "delta": {"lluvia_pct": 10, "temp_c": 0}},
                {"id": "temp_+1", "descripcion": "Temperatura +1 C", "delta": {"lluvia_pct": 0, "temp_c": 1}},
                {"id": "temp_+2", "descripcion": "Temperatura +2 C", "delta": {"lluvia_pct": 0, "temp_c": 2}},
                {"id": "2050", "descripcion": "Escenario 2050 (simulado)", "delta": {"lluvia_pct": -12, "temp_c": 1.8}},
            ],
            "resultados": {},
            "nota": "Esqueleto P2: el motor rellenara resultados[id] con los criterios, exito_pct y margen por rotacion.",
        },
        "sensores": {
            "_status": "cargando",
            "fuente_id": "siam",
            "estacion": {"id": "TP91", "red": "SIAM", "distancia_parcela_km": 1.1},
            "resolucion": "horaria",
            "variables": ["tmin_c", "tmax_c", "hr_pct", "lluvia_mm", "et0_mm"],
            "periodo": None,
            "lecturas": [],
            "nota": "Esqueleto para el export SIAM de T-014: lecturas[] con t (ISO 8601 UTC) y las variables listadas.",
        },
        "fuentes": FUENTES,
        "no_sustituye": "Herramienta de apoyo. Consulta a tu tecnico agricola antes de decidir.",
    }
    return doc


if __name__ == "__main__":
    OUT.write_text(dumps(build()) + "\n", encoding="utf-8")
    print(f"escrito {OUT}")
