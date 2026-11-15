"""Daily weather from a SIAM-IMIDA ground station (Region of Murcia agro network), via its public report form.

Why: gridded products (NASA POWER, ERA5-Land, ERA5) show 0-1 frost years in 2005-2024 at the demo parcel, but the
SIAM station TP91 (Torre Pacheco) records sub-zero nights (e.g. 4 Dec 2010: Tmin -0.45 degC). Frost risk must come
from a station. This is the engine's offline copy; T-014 (arturo) owns the team's SIAM collector.

Run:  python3 -m app.backend.engine.sources.siam [STATION] [FROM_YEAR] [TO_YEAR]     (default TP91 2005 2024)
Writes app/backend/engine/data/official/siam_<station>_daily.csv and appends to sources.csv.
One request per year (falls back to per month if a year comes back short), 2 s apart, to be gentle with the server.
"""
import calendar
import csv
import datetime as dt
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar

BASE = "http://siam.imida.es/apex/"
FORM = BASE + "f?p=101:46"  # "Informe Agrometeorologico Personalizado"
OUT = pathlib.Path(__file__).resolve().parents[1] / "data" / "official"
VARS = ["TMIN", "TMINABS", "HORAS0", "TMAX", "TMAXABS", "TMED", "PREC", "ETO_PM_FAO", "HRMED", "VVMED", "RADMED"]


def _num(s):
    s = s.replace(".", "").replace(",", ".").strip() if re.search(r"\d,\d", s) else s.strip()
    try:
        return float(s)
    except ValueError:
        return ""


def query(station, d0, d1):
    """Rows [date, var...] for station between two dates (inclusive), from one form submission."""
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
    page = op.open(FORM, timeout=60).read().decode("utf-8", "ignore")
    form = page[page.find('id="wwvFlowForm"'):]
    fields = []
    for m in re.finditer(r"<(input|select)([^>]*)>", form):
        attrs = m.group(2)
        name = re.search(r'name="([^"]+)"', attrs)
        if not name or name.group(1) == "p_v100" or 'type="button"' in attrs:
            continue
        n = name.group(1)
        idm = re.search(r'id="([^"]+)"', attrs)
        i = idm.group(1) if idm else ""
        val = re.search(r'value="([^"]*)"', attrs)
        v = val.group(1) if val else ""
        if i == "P46_FECHADESDE":
            v = d0.strftime("%d/%m/%Y")
        elif i == "P46_FECHAHASTA":
            v = d1.strftime("%d/%m/%Y")
        elif i == "P46_TIPOLOGIA":
            v = "DIA"
        elif i == "P46_ESTACIONES_RIGHT":
            fields.append((n, station))
            continue
        elif i == "P46_DISPOSITIVOS_RIGHT":
            fields += [(n, x) for x in VARS]
            continue
        elif n == "p_request":
            v = "GENERARINFORME"
        fields.append((n, v))
    html = op.open(BASE + "wwv_flow.accept", data=urllib.parse.urlencode(fields).encode(), timeout=120)
    html = html.read().decode("utf-8", "ignore")
    ths = [" ".join(re.sub(r"<[^>]+>", " ", t).split()) for t in re.findall(r"<th[^>]*>(.*?)</th>", html, re.S)]
    cols = [m.group(1) for t in ths for m in [re.match(r"([A-Z0-9_]+) \(", t)] if m]
    if not cols:  # no results table: period without data (e.g. before the station started)
        return [], []
    rows = []
    for r in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S):
        c = [" ".join(re.sub(r"<[^>]+>", " ", x).split()) for x in re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)]
        if len(c) >= 5 and c[0] == station:
            day = dt.datetime.strptime(c[4], "%d/%m/%y").date()
            rows.append([day.isoformat()] + [_num(x) for x in c[5:5 + len(cols)]])
    return cols, rows


def main(station="TP91", y0=2005, y1=2024):
    OUT.mkdir(parents=True, exist_ok=True)
    allrows, cols, notes = {}, None, []
    for y in range(y0, y1 + 1):
        c, rows = query(station, dt.date(y, 1, 1), dt.date(y, 12, 31))
        expected = 366 if calendar.isleap(y) else 365
        if len(rows) < expected - 5:  # short year: retry month by month
            rows = []
            for m in range(1, 13):
                time.sleep(2)
                c2, r2 = query(station, dt.date(y, m, 1), dt.date(y, m, calendar.monthrange(y, m)[1]))
                c = c2 or c
                rows += r2
        cols = cols or c
        for r in rows:
            allrows[r[0]] = r
        notes.append(f"{y}:{len(rows)}/{expected}")
        print(f"{station} {y}: {len(rows)}/{expected} days", flush=True)
        time.sleep(2)
    name = OUT / f"siam_{station}_daily.csv"
    with open(name, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date"] + (cols or VARS))
        w.writerows(allrows[k] for k in sorted(allrows))
    with open(OUT / "sources.csv", "a", newline="") as f:
        csv.writer(f).writerow([f"SIAM-{station}", "SIAM-IMIDA Informe Agrometeorologico Personalizado (diario)", FORM,
                                dt.date.today().isoformat(), "SIAM-IMIDA, CARM: cite source (no explicit open licence found)",
                                f"station {station}; days per year " + " ".join(notes)])
    print(f"{len(allrows)} days -> {name}")


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0], int(a[1]), int(a[2])) if len(a) == 3 else main()
