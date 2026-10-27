#!/usr/bin/env python3
"""Henter alle kamper for barne- og ungdomslagene i Gjerpen IF håndball
(handball.no klubbid 60697) og lager kampoversikt.html og kamper.json.

Kjør:  python3 build.py [utmappe]
Kjøres f.eks. hver time fra GitHub Actions, og resultatet publiseres på GitHub Pages.
"""
import html, json, re, sys, time, urllib.request, datetime, pathlib

KLUBBID = 60697
UTELAT = {205939}  # Kvinner sr (damelaget) er ikke barne/ungdom
BASE = "https://www.handball.no"
HDR = {"User-Agent": "Mozilla/5.0 (kampoversikt Gjerpen IF)", "X-Requested-With": "XMLHttpRequest"}

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=30) as r:
        return r.read().decode("utf-8")

def lag_i_klubben():
    s = get(f"{BASE}/system/kamper/klubb/?klubbid={KLUBBID}")
    m = re.search(r"teams='(\[\{.*?\}\])'", s, re.S)
    return [t for t in json.loads(html.unescape(m.group(1))) if t["orgId"] not in UTELAT]

def sesong(lagid):
    s = get(f"{BASE}/system/kamper/lag/?lagid={lagid}")
    return int(re.search(r"TerminListeForTeam\?id=\d+\\u0026seasonId=(\d+)", s).group(1))

def kort(navn):  # "Gjerpen 2 - J16 2" -> "J16 2"
    return navn.split(" - ", 1)[1] if navn and " - " in navn else navn

def main(ut):
    lag = lag_i_klubben()
    sid = sesong(lag[0]["orgId"])
    ids = {t["orgId"] for t in lag}
    kamper = {}
    for t in lag:
        d = json.loads(get(f"{BASE}/api/AjaxData/TerminListeForTeam?id={t['orgId']}&seasonId={sid}"))
        for m in d.get("matches") or []:
            kamper[m["matchId"]] = m
        time.sleep(0.3)
    rader = []
    for m in kamper.values():
        hjemme, borte = m["homeTeamId"] in ids, m["awayTeamId"] in ids
        vårt = kort(m["homeTeamDescribingName"]) if hjemme else kort(m["awayTeamDescribingName"])
        res = None
        if m["publicResult"] and m["goalsHome"] is not None and m["isPast"]:
            res = [m["goalsHome"], m["goalsAway"]]
        rader.append({
            "id": m["matchId"], "dato": m["matchDate"][:10],
            "tid": f"{m['matchStartTime']:04d}" if m["matchStartTime"] else None,
            "lag": vårt, "lag2": kort(m["awayTeamDescribingName"]) if hjemme and borte else None, "hjemme": m["homeTeamDisplayName"], "borte": m["awayTeamDisplayName"],
            "gjerpenHjemme": hjemme, "internt": hjemme and borte,
            "res": res, "spilt": m["isPast"], "utsatt": m["postponed"], "avlyst": m["cancelled"],
            "hall": m["venueUnitName"], "bane": m["activityAreaName"],
            "turnering": m["tournamentName"], "turnid": m["tournamentId"],
        })
    rader.sort(key=lambda r: (r["dato"], r["tid"] or ""))
    data = {"oppdatert": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="minutes"),
            "sesong": sid, "kamper": rader}
    ut = pathlib.Path(ut); ut.mkdir(parents=True, exist_ok=True)
    (ut / "kamper.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), "utf-8")
    mal = (pathlib.Path(__file__).parent / "mal.html").read_text("utf-8")
    side = mal.replace("/*DATA*/null", json.dumps(data, ensure_ascii=False))
    (ut / "index.html").write_text('<!doctype html>\n<html lang="no"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1"></head><body>\n'
        + side + "\n</body></html>\n", "utf-8")
    (ut / "fragment.html").write_text(side, "utf-8")
    print(f"{len(rader)} kamper, {len(lag)} lag, sesong {sid}")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "ut")
