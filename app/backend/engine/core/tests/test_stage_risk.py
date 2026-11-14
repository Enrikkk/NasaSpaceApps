"""Stage-risk indicator: alerts counted per stage over historical cycles, 'sin evidencia' where nothing is documented."""
import datetime as dt

from app.backend.engine.core import stage_risk as sr
from app.backend.engine.core.data import Day


def climate(years, hot_run=None, cold_day=None):
    """Mild constant climate 2001-2001+years; optional: a run of hot days (start date, n) and one cold night date."""
    out, d = {}, dt.date(2001, 1, 1)
    while d < dt.date(2001 + years, 1, 1):
        out[d] = Day(5.0, 20.0, 0.0, 3.0)
        d += dt.timedelta(days=1)
    if hot_run:
        for i in range(hot_run[1]):
            out[hot_run[0] + dt.timedelta(days=i)] = Day(15.0, 38.0, 0.0, 3.0)
    if cold_day:
        out[cold_day] = Day(-4.0, 12.0, 0.0, 3.0)
    return out


def test_run_of_days_needed_not_isolated_days():
    # broccoli sown 1 Sep, stages 35/45/40/15: floral window = first 20 days of 'mid' = 24 Nov .. 13 Dec 2001
    four = climate(2, hot_run=(dt.date(2001, 11, 25), 4))
    five = climate(2, hot_run=(dt.date(2001, 11, 25), 5))
    a4 = {e["id"]: e for e in sr.assess("brocoli", (35, 45, 40, 15), 9, 1, four)["etapas"]}["brocoli_calor_iniciacion"]
    a5 = {e["id"]: e for e in sr.assess("brocoli", (35, 45, 40, 15), 9, 1, five)["etapas"]}["brocoli_calor_iniciacion"]
    assert a4["anios_con_episodio"] == 0 and a5["anios_con_episodio"] == 1
    assert a5["n"] == 1 and a5["nivel"] == "alto"       # 1 of 1 cycle: frequency 100 %


def test_calendar_window_with_wrap_and_levels():
    # lemon ripe fruit window 15 Oct .. 15 Feb wraps the year; a -4 night on 10 Jan 2002 is inside it
    c = climate(3, cold_day=dt.date(2002, 1, 10))
    ev = {e["id"]: e for e in sr.assess("limon", (60, 90, 120, 95), 1, 1, c)["etapas"]}
    assert ev["limon_maduro_dano"]["anios_con_episodio"] == 1 and ev["limon_maduro_dano"]["n"] == 3
    assert ev["limon_maduro_dano"]["gravedad"] == "daño" and ev["limon_maduro_aviso"]["gravedad"] == "aviso"
    assert ev["limon_flor_helada"]["anios_con_episodio"] == 0     # flowering window is Feb 15 - Apr 15
    assert sr.level(0.05) == "bajo" and sr.level(0.2) == "medio" and sr.level(0.5) == "alto"


def test_stages_without_documented_alert_say_no_evidence_not_low_risk():
    r = sr.assess("brocoli", (35, 45, 40, 15), 9, 1, climate(2))
    sin = [e for e in r["etapas"] if e["nivel"] == "sin evidencia"]
    assert {e["etapas_fao"][0] for e in sin} == {"ini", "dev", "late"} and all(e["frecuencia"] is None for e in sin)
    assert all(e["nivel"] != "bajo" for e in sin)


def test_every_alert_has_source_confidence_and_transfer_note():
    assert all(a["fuente"] and a["conf"] and a["transfer"] and a["ventana_nota"] for a in sr.ALERTS)
