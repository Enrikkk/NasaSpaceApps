"""Official Spanish crop prices and areas from Eurostat (free JSON API, no key, licence CC BY 4.0).

Run:  python3 -m app.backend.engine.sources.eurostat      (from the repo root)
Writes app/backend/engine/data/official/:
  eurostat_prices_es.csv   crop_id, year, eur_100kg (nominal), eur_100kg_real (deflated to 2015 by HICP), code
  eurostat_area_es.csv     crop_id, year, area_kha, prod_kt, yield_t_ha, code
  sources.csv              one row per API call: source_id, dataset, url, retrieved, licence, note
Nothing here is invented: a crop without an official series gets no rows and a note in sources.csv.
"""
import csv
import datetime as dt
import json
import pathlib
import urllib.request

BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
OUT = pathlib.Path(__file__).resolve().parents[1] / "data" / "official"
LICENCE = "Eurostat, CC BY 4.0 (https://ec.europa.eu/eurostat/about-us/policies/copyright)"

# The 8 demo crops (coordination/PLAN.md). Codes checked against the live code lists on 2026-11-14.
PRICE_CODES = {  # apri_ap_crpouta, prod_veg: first-stage selling price, EUR per 100 kg
    "lechuga": ("04192100", "Lettuce in the open: all qualities"),
    "brocoli": ("04110000", "Cauliflowers: all qualities (PROXY: Eurostat has no broccoli price)"),
    "melon": ("04199913", "Melons"),
    "haba": ("02230000", "Dried broad beans (dry grain; no green broad bean series)"),
    "cebada": ("01300000", "Barley"),
    "limon": ("06230000", "Lemons: all varieties"),
}
NO_PRICE = {
    "alcachofa": "No Eurostat price series; needs MAPA/ESAM weekly prices (T-021)",
    "veza": "Cover crop, not sold: no price by design",
}
AREA_CODES = {  # apro_cpsh1, crops
    "lechuga": "V2300", "brocoli": "V1100", "melon": "V3510", "alcachofa": "V2800",
    "haba": "P1200", "cebada": "C1300", "veza": "P9400", "limon": "T3000",
}


def fetch(dataset, query):
    url = f"{BASE}{dataset}?format=JSON&lang=en&geo=ES&{query}"
    with urllib.request.urlopen(url, timeout=90) as r:
        return url, json.load(r)


def cells(d):
    """Decode a JSON-stat cube into {(code_dim1, code_dim2, ...): value}. `value` is keyed by row-major index."""
    ids, sizes = d["id"], d["size"]
    index = []
    for k in ids:
        pos = d["dimension"][k]["category"]["index"]
        index.append(sorted(pos, key=pos.get))
    out = {}
    for flat, v in d["value"].items():
        flat, key = int(flat), []
        for size, codes in zip(reversed(sizes), reversed(index)):
            key.append(codes[flat % size])
            flat //= size
        out[tuple(reversed(key))] = v
    return ids, out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    today = dt.date.today().isoformat()
    sources = []

    url, d = fetch("prc_hicp_aind", "coicop=CP00&unit=INX_A_AVG&sinceTimePeriod=1999")
    ids, c = cells(d)
    hicp = {k[ids.index("time")]: v for k, v in c.items()}  # 2015 = 100
    sources.append(["EUR-HICP", "prc_hicp_aind", url, today, LICENCE, "Spain HICP all items, 2015=100, deflator"])

    url, d = fetch("apri_ap_crpouta", "sinceTimePeriod=2000&currency=EUR")
    ids, c = cells(d)
    sources.append(["EUR-PRICE", "apri_ap_crpouta", url, today, LICENCE,
                    "first-stage selling price EUR/100 kg, Spain, annual; broccoli = cauliflower proxy"])
    rows = []
    for crop, (code, _label) in PRICE_CODES.items():
        for k, v in c.items():
            if k[ids.index("prod_veg")] == code and k[ids.index("currency")] == "EUR":
                y = k[ids.index("time")]
                real = round(v / hicp[y] * 100, 2) if y in hicp else ""
                rows.append([crop, int(y), v, real, code])
    rows.sort()
    with open(OUT / "eurostat_prices_es.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["crop_id", "year", "eur_100kg", "eur_100kg_real2015", "code"])
        w.writerows(rows)

    url, d = fetch("apro_cpsh1", "sinceTimePeriod=1999")
    ids, c = cells(d)
    sources.append(["EUR-AREA", "apro_cpsh1", url, today, LICENCE,
                    "area (kha), harvested production (kt), yield (t/ha), Spain, annual"])
    area = {}
    for crop, code in AREA_CODES.items():
        for k, v in c.items():
            if k[ids.index("crops")] == code:
                y = int(k[ids.index("time")])
                area.setdefault((crop, y), {"code": code})[k[ids.index("strucpro")]] = v
    with open(OUT / "eurostat_area_es.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["crop_id", "year", "area_kha", "prod_kt", "yield_t_ha", "code"])
        for (crop, y), m in sorted(area.items()):
            w.writerow([crop, y, m.get("AR_THS_HA", ""), m.get("HPRD_HUMD_EU_THS_T", ""),
                        m.get("YLD_HUMD_EU_T_HA", ""), m["code"]])

    for crop, why in NO_PRICE.items():
        sources.append([f"GAP-PRICE-{crop}", "", "", today, "", why])
    with open(OUT / "sources.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["source_id", "dataset", "url", "retrieved", "licence", "note"])
        w.writerows(sources)
    print(f"prices: {len(rows)} rows, area: {len(area)} rows -> {OUT}")


if __name__ == "__main__":
    main()
