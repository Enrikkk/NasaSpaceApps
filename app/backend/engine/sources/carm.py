"""Monthly Region of Murcia farm-gate prices by crop VARIETY and QUALITY, from the CARM agricultural yearbooks.

Source: "Anuario de Estadística Agraria de la Región de Murcia" (CARM, esam.carm.es/anuarios-estadistica-agraria/),
tables 10.1/11.1 "Precios percibidos por los productores agrarios", campaigns 2002-03 to 2022-23. Each yearbook says
these quotes are ORIENTATIVE, not an official price: the engine labels them "orientativo CARM".
Extraction (2026-11-14): PDFs read with pdftotext -layout; every row keeps its yearbook file and PDF page; 7 values
spot-checked against the page text; 899 month values printed in two yearbooks agree exactly.

Run:  python3 -m app.backend.engine.sources.carm <extracted_csv>
Writes app/backend/engine/data/official/carm_precios_mensuales.csv
  crop_id, variety, quality, year, month, value, unit (eur_kg | eur_ud), yearbook_file, page, label
and appends source CARM-ANUARIO to sources.csv. Units are normalised only in spelling (EUR/kg, euros/kg -> eur_kg;
EUR/Ud., EUR/unidad -> eur_ud); values are never converted. Rows with no printed unit are dropped (listed in output).
"""
import csv
import datetime as dt
import pathlib
import re
import sys

OUT = pathlib.Path(__file__).resolve().parents[1] / "data" / "official"
MONTHS = {"ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6, "jul": 7, "ago": 8, "sep": 9, "oct": 10,
          "nov": 11, "dic": 12}


def unit(u):
    u = (u or "").lower().replace(" ", "")
    if "kg" in u:
        return "eur_kg"
    if "ud" in u or "unidad" in u:
        return "eur_ud"
    return None


def main(src):
    rows, dropped = [], []
    for r in csv.DictReader(open(src, encoding="utf-8")):
        if r["measure"] != "price_monthly" or r["value"] in ("", None):
            continue
        m = re.search(r"month=([A-Za-zé]+)", r["note"])
        month = MONTHS.get(m.group(1)[:3].lower()) if m else None
        u = unit(r["unit"])
        if month is None or u is None:
            dropped.append((r["crop_id"], r["variety"], r["year"], r["unit"]))
            continue
        rows.append([r["crop_id"], r["variety"], r["quality"], int(r["year"]), month, float(r["value"]), u,
                     r["yearbook_file"], r["page"], r["product_label_as_printed"]])
    rows.sort()
    with open(OUT / "carm_precios_mensuales.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["crop_id", "variety", "quality", "year", "month", "value", "unit", "yearbook_file", "page", "label"])
        w.writerows(rows)
    src_csv = OUT / "sources.csv"
    keep = [x for x in csv.reader(open(src_csv)) if x and x[0] != "CARM-ANUARIO"]
    keep.append(["CARM-ANUARIO", "Anuario de Estadística Agraria de la Región de Murcia 2002-03..2022-23, tablas "
                 "'Precios percibidos por los productores agrarios' (mensual, por variedad y calidad)",
                 "https://esam.carm.es/anuarios-estadistica-agraria/", dt.date.today().isoformat(),
                 "CARM, cite source (no explicit open licence found)",
                 f"{len(rows)} monthly quotes; ORIENTATIVE per the yearbooks, not official prices; nominal EUR"])
    csv.writer(open(src_csv, "w", newline="")).writerows(keep)
    print(f"{len(rows)} monthly quotes -> {OUT / 'carm_precios_mensuales.csv'}; dropped {len(dropped)}: "
          f"{sorted(set(dropped))[:12]}")


if __name__ == "__main__":
    main(sys.argv[1])
