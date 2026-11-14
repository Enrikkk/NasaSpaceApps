"""20 years of daily NASA POWER climate for a parcel (free API, no key; NASA data, no copyright restrictions).

Engine-side cache so the engine can be built now. The team's official climate block comes from T-011 (gonzalo,
app/data/cache/pipeline/); switch to it when it lands and keep this file only as the engine's offline fixture.

Run:  python3 -m app.backend.engine.sources.power [lat lon]      (default: demo parcel Torre-Pacheco 18/426/1)
Writes app/backend/engine/data/official/power_daily_<lat>_<lon>.csv and appends its row to sources.csv.
Traps (research notes): POWER is a ~0.5 deg cell (~50 km), so every parcel of the Campo de Cartagena shares it;
its Tmin under-sees local frost (frost comes from SIAM TP91, T-014); EVLAND/EVPTRNS ignore irrigation.
"""
import csv
import datetime as dt
import json
import pathlib
import sys
import urllib.request

OUT = pathlib.Path(__file__).resolve().parents[1] / "data" / "official"
LAT, LON = 37.73830, -0.98838  # Torre-Pacheco SIGPAC 18/426/1 (coordination/PLAN.md)
START, END = 2005, 2024        # 20 full calendar years, paired by year with Eurostat prices
# Everything FAO-56 Penman-Monteith needs, plus rain and soil moisture.
PARAMS = ["T2M", "T2M_MAX", "T2M_MIN", "T2MDEW", "RH2M", "WS2M", "ALLSKY_SFC_SW_DWN", "CLRSKY_SFC_SW_DWN",
          "PRECTOTCORR", "PS", "GWETROOT"]


def main(lat=LAT, lon=LON):
    url = ("https://power.larc.nasa.gov/api/temporal/daily/point?"
           f"parameters={','.join(PARAMS)}&community=AG&latitude={lat}&longitude={lon}"
           f"&start={START}0101&end={END}1231&format=JSON&time-standard=UTC")
    with urllib.request.urlopen(url, timeout=180) as r:
        d = json.load(r)
    p = d["properties"]["parameter"]
    fill = d.get("header", {}).get("fill_value", -999)
    days = sorted(p[PARAMS[0]])
    OUT.mkdir(parents=True, exist_ok=True)
    name = OUT / f"power_daily_{lat:.4f}_{lon:.4f}.csv"
    missing = 0
    with open(name, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date"] + PARAMS)
        for day in days:
            vals = [p[k].get(day) for k in PARAMS]
            missing += sum(v in (None, fill) for v in vals)
            w.writerow([f"{day[:4]}-{day[4:6]}-{day[6:]}"] + ["" if v in (None, fill) else v for v in vals])
    src = OUT / "sources.csv"
    new = not src.exists()
    with open(src, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["source_id", "dataset", "url", "retrieved", "licence", "note"])
        w.writerow(["NASA-POWER-DAILY", "POWER daily point AG", url, dt.date.today().isoformat(),
                    "NASA POWER, public domain (https://power.larc.nasa.gov/docs/referencing/)",
                    f"~0.5 deg cell; {len(days)} days {START}-{END}; {missing} missing values"])
    print(f"{len(days)} days, {missing} missing values -> {name}")


if __name__ == "__main__":
    a = sys.argv[1:]
    main(float(a[0]), float(a[1])) if len(a) == 2 else main()
