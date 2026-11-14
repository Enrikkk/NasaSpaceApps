#!/usr/bin/env python3
"""Genera los bloques `clima` y `suelo` del contrato v1.1 para una coordenada.

    python3 -m app.backend.pipeline.clima_suelo.build_blocks 37.7383 -0.98838         # resumen + app/data/cache/pipeline/blocks/<lat>_<lon>.blocks.json
    python3 -m app.backend.pipeline.clima_suelo.build_blocks 37.7383 -0.98838 --json  # solo el JSON de los bloques
    AGROCKHAM_CACHE_DIR=/ruta python3 -m app.backend.pipeline.clima_suelo.build_blocks ...   # otra carpeta de cache

(desde la raiz del repo)

Solo libreria estandar. Imprime el contador de llamadas de red (segunda ejecucion: 0).
"""
import argparse
import json
import sys
import time
from pathlib import Path

from . import pipeline as P

OUT = P.REPO_ROOT / "app" / "data" / "cache" / "pipeline" / "blocks"


def construir(lat, lon):
    return {"clima": P.build_clima(lat, lon), "suelo": P.build_suelo(lat, lon), "fuentes_nuevas": P.fuentes_nuevas()}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("lat", type=float)
    ap.add_argument("lon", type=float)
    ap.add_argument("--json", action="store_true", help="imprime solo el JSON")
    ap.add_argument("--out", help="fichero de salida (por defecto app/data/cache/pipeline/blocks/<lat>_<lon>.blocks.json)")
    a = ap.parse_args(argv)
    P.net_reset()
    t0 = time.time()
    bloques = construir(a.lat, a.lon)
    dt = time.time() - t0
    destino = Path(a.out) if a.out else OUT / f"{a.lat}_{a.lon}.blocks.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(bloques, ensure_ascii=False, indent=1))
    if a.json:
        print(json.dumps(bloques, ensure_ascii=False, indent=1))
        return 0
    c, s = bloques["clima"], bloques["suelo"]
    print(f"Punto {a.lat}, {a.lon}")
    print(f"clima: lluvia anual {c['lluvia_anual_mm']['valor']} mm, horquilla {c['lluvia_anual_mm']['horquilla']}, por fuente {c['lluvia_anual_mm']['por_fuente_mm']}")
    print(f"       dias > 38 C: {c['dias_calor_gt_38']['valor']}/anio ({c['dias_calor_gt_38']['tendencia']})")
    print(f"       dias_helada: {c['dias_helada']['valor']} PROVISIONAL (fuente: {c['dias_helada']['fuente']})")
    print(f"       ET0 anual {c['et0_mm_mes']['anual_mm']} mm; mensual {c['et0_mm_mes']['valores']}")
    print(f"suelo: {s['textura']} (arena {s['arena_pct']} / limo {s['limo_pct']} / arcilla {s['arcilla_pct']} %), "
          f"MO {s['materia_organica_pct']} % (SOC {s['soc_g_kg']} g/kg), pH {s['ph_h2o']}, agua disponible 0-30 cm {s['agua_disponible_mm']} mm")
    print(f"escrito: {destino}")
    print(f"TIEMPO {dt:.1f}s | RED: {P.NET['llamadas']} llamadas {dict(P.NET['por_host'])}, "
          f"{P.NET['segundos']:.1f}s en red, {P.NET['esperas_s']:.1f}s de esperas (limite SoilGrids / reintentos)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
