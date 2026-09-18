# -*- coding: utf-8 -*-
"""Parse harvested bimmerarchive.org HTML into the static JSON API under api/v1.

Usage:  python tools/ingest.py [--cache DIR] [--out DIR]

Reads   <cache>/index/e-code.html, <cache>/index/m-code.html
        <cache>/e/<slug>.html, <cache>/m/<slug>.html
Writes  <out>/*.json
"""
import re, os, json, html, datetime, collections, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ap = argparse.ArgumentParser()
ap.add_argument("--cache", default=os.path.join(ROOT, "cache"))
ap.add_argument("--out", default=os.path.join(ROOT, "api", "v1"))
args = ap.parse_args()

CACHE = args.cache
API = args.out
SRC = "https://www.bimmerarchive.org"
IDX_E = os.path.join(CACHE, "index", "e-code.html")
IDX_M = os.path.join(CACHE, "index", "m-code.html")


def W(path, obj):
    p = os.path.join(API, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))


def clean(x):
    x = re.sub(r"(?is)<[^>]+>", " ", x)
    return re.sub(r"\s+", " ", html.unescape(x).replace("\xa0", " ")).strip()


def cells(tr, tag="td"):
    return re.findall(r"(?is)<%s[^>]*>(.*?)</%s>" % (tag, tag), tr)


def rows(htm):
    return re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", htm)


def nostrip(s):
    return re.sub(r"(?is)<script.*?</script>|<style.*?</style>", " ", s)


def years(raw):
    ys = re.findall(r"(\d{4})", raw or "")
    a = int(ys[0]) if ys else None
    b = int(ys[1]) if len(ys) > 1 else None
    return a, b


def brand_of(desc, code):
    d = (desc or "").lower()
    if d.startswith("mini"):
        return "MINI"
    if "rolls-royce" in d or code.upper().startswith("RR"):
        return "Rolls-Royce"
    return "BMW"


# ---------------------------------------------------------------- models index
idx = nostrip(open(IDX_E, encoding="utf-8", errors="replace").read())
models = []
for tr in rows(idx):
    td = cells(tr)
    if len(td) != 4:
        continue
    m = re.search(r'href="[^"]*?/e-code/([a-z0-9._-]+)\.html"', tr, re.I)
    if not m:
        continue
    yrs, code, desc, mtype = [clean(t) for t in td]
    y0, y1 = years(yrs)
    models.append({
        "code": code,
        "slug": m.group(1),
        "brand": brand_of(desc, code),
        "description": desc,
        "years": yrs,
        "year_from": y0,
        "year_to": y1,
        "type": mtype,
    })

# ---------------------------------------------------------- model detail pages
all_codes = []
plants = collections.OrderedDict()
model_out = {}
for mo in models:
    f = os.path.join(CACHE, "e", mo["slug"] + ".html")
    detail = {"production_codes": [], "plants": [], "photos": [], "articles": []}
    if os.path.exists(f):
        s = nostrip(open(f, encoding="utf-8", errors="replace").read())
        for tr in rows(s):
            th = cells(tr, "th")
            td = cells(tr)
            if len(th) == 1 and len(td) == 1 and clean(th[0]).lower() == "plant":
                pat = r'href="[^"]*?/production/([a-z0-9-]+)\.html"[^>]*>(.*?)</a>'
                for ph, pn in re.findall(pat, tr, re.I | re.S):
                    name = clean(pn) or ph.replace("-", " ").title()
                    plants.setdefault(ph, name)
                    if ph not in [p["slug"] for p in detail["plants"]]:
                        detail["plants"].append({"slug": ph, "name": name})
        for tr in rows(s):
            td = cells(tr)
            if len(td) != 9:
                continue
            v = [clean(t) for t in td]
            cm = re.search(r"/code/([a-z0-9-]+)\.html", tr, re.I)
            dm = re.findall(r"(\d{4}-\d{2})", v[0])
            kw = re.search(r"(\d+)\s*kW", v[5], re.I)
            kwv = int(kw.group(1)) if kw else None
            rec = {
                "code": v[1].upper(),
                "model": v[2],
                "body": v[3],
                "engine": v[4],
                "power_kw": kwv or None,
                "drivetrain": v[6],
                "steering": v[7],
                "region": v[8],
                "from": dm[0] if dm else None,
                "to": dm[1] if len(dm) > 1 else None,
            }
            if cm:
                rec["source"] = SRC + "/code/" + cm.group(1) + ".html"
            detail["production_codes"].append(rec)
            flat = dict(rec)
            flat["chassis"] = mo["code"]
            flat["chassis_slug"] = mo["slug"]
            flat["brand"] = mo["brand"]
            flat["chassis_description"] = mo["description"]
            all_codes.append(flat)
        pat = r'href="[^"]*?/photo/([a-z0-9-]+)\.html"[^>]*class="thumbnail".*?<div class="caption">(.*?)</div>'
        for pslug, cap in re.findall(pat, s, re.I | re.S):
            detail["photos"].append({"slug": pslug, "title": clean(cap)})
        pat = r'href="[^"]*?/article/([a-z0-9-]+)\.html"[^>]*>(.*?)</a>'
        for aslug, title in re.findall(pat, s, re.I | re.S):
            t = clean(title)
            if t and not any(a["slug"] == aslug for a in detail["articles"]):
                detail["articles"].append({"slug": aslug, "title": t})
    mo["production_code_count"] = len(detail["production_codes"])
    mo["has_detail"] = os.path.exists(f)
    out = dict(mo)
    out.update(detail)
    out["source"] = SRC + "/e-code/" + mo["slug"] + ".html"
    model_out[mo["slug"]] = out

# --------------------------------------------------------------- engines index
midx = nostrip(open(IDX_M, encoding="utf-8", errors="replace").read())
engines = []
parts = re.split(r"(?is)(<h[1-6][^>]*>.*?</h[1-6]>)", midx)
fam = None
for chunk in parts:
    hm = re.match(r"(?is)<h[1-6][^>]*>(.*?)</h[1-6]>", chunk or "")
    if hm:
        fam = clean(hm.group(1))
        continue
    if not fam:
        continue
    for tr in rows(chunk):
        td = cells(tr)
        if len(td) != 4:
            continue
        m = re.search(r'href="[^"]*?/m-code/([a-z0-9._-]+)\.html"', tr, re.I)
        if not m:
            continue
        dates, code, disp, _ = [clean(t) for t in td]
        pw = clean(re.sub(r"(?is)<br\s*/?>", " || ", td[3]))
        bits = [b.strip() for b in pw.split("||")]
        power = bits[0] if bits else ""
        torque = bits[1] if len(bits) > 1 else ""
        y0, y1 = years(dates)
        cc = re.search(r"(\d+)\s*cm", disp)
        kw = re.search(r"([\d.]+)\s*kW", power)
        ps = re.search(r"\((\d+)\s*PS\)", power)
        prpm = re.search(r"at\s*([\d\-]+)\s*U", power)
        nm = re.search(r"(\d+)\s*Nm", torque)
        trpm = re.search(r"at\s*([\d\-]+)\s*U", torque)
        engines.append({
            "code": code,
            "slug": m.group(1),
            "family": fam,
            "years": dates,
            "year_from": y0,
            "year_to": y1,
            "displacement_cc": int(cc.group(1)) if cc else None,
            "power_kw": int(float(kw.group(1))) if kw else None,
            "power_ps": int(ps.group(1)) if ps else None,
            "power_rpm": prpm.group(1) if prpm else None,
            "torque_nm": int(nm.group(1)) if nm else None,
            "torque_rpm": trpm.group(1) if trpm else None,
        })

engine_out = {}
for en in engines:
    f = os.path.join(CACHE, "m", en["slug"] + ".html")
    extra = {}
    if os.path.exists(f):
        s = nostrip(open(f, encoding="utf-8", errors="replace").read())
        facts = {}
        for tr in rows(s):
            th = cells(tr, "th")
            td = cells(tr)
            if len(th) == 1 and len(td) == 1:
                facts[clean(th[0]).lower()] = clean(td[0])
        con = re.sub(r"[\s,]+$", "", facts.get("type of construction", ""))
        cyl = re.search(r"(\d+)\s*Cylinder", con, re.I)
        val = re.search(r"(\d+)\s*Valve", con, re.I)
        bs = re.search(r"([\d,.]+)\s*mm\s*x\s*([\d,.]+)\s*mm", facts.get("bore x stroke", ""), re.I)
        extra = {
            "construction": con or None,
            "cylinders": int(cyl.group(1)) if cyl else None,
            "valves": int(val.group(1)) if val else None,
            "compression_ratio": facts.get("compression ratio") or None,
            "bore_mm": float(bs.group(1).replace(",", ".")) if bs else None,
            "stroke_mm": float(bs.group(2).replace(",", ".")) if bs else None,
            "fuel": facts.get("fuel") or None,
        }
    en["has_detail"] = os.path.exists(f)
    out = dict(en)
    out.update(extra)
    out["source"] = SRC + "/m-code/" + en["slug"] + ".html"
    engine_out[en["slug"]] = out

# ------------------------------------------------------------------ emit files
today = datetime.date.today().isoformat()
os.makedirs(API, exist_ok=True)

for slug, obj in model_out.items():
    W("models/%s.json" % slug, obj)
for slug, obj in engine_out.items():
    W("engines/%s.json" % slug, obj)

W("models.json", {"count": len(models), "results": models})
W("engines.json", {"count": len(engines), "results": engines})

by_code = collections.defaultdict(list)
for c in all_codes:
    by_code[c["code"]].append(c)
for code, lst in by_code.items():
    safe = re.sub(r"[^A-Z0-9_-]", "_", code)
    W("production-codes/%s.json" % safe, {"code": code, "count": len(lst), "results": lst})

W("production-codes.json", {"count": len(all_codes), "unique_codes": len(by_code), "results": all_codes})
W("plants.json", {"count": len(plants), "results": [{"slug": k, "name": v} for k, v in plants.items()]})

brands = collections.Counter(m["brand"] for m in models)
W("brands.json", {"results": [{"name": b, "model_count": n} for b, n in brands.most_common()]})

regions = collections.Counter(c["region"] for c in all_codes if c["region"])
W("regions.json", {"count": len(regions), "results": [{"name": r, "production_code_count": n} for r, n in regions.most_common()]})

search = []
for m in models:
    search.append({"t": "model", "c": m["code"], "s": m["slug"], "d": m["description"],
                   "y": m["years"], "b": m["brand"], "n": m["production_code_count"]})
for e in engines:
    d = "%s · %s cm³ · %s PS" % (e["family"], e["displacement_cc"] or "?", e["power_ps"] or "?")
    search.append({"t": "engine", "c": e["code"], "s": e["slug"], "d": d,
                   "y": e["years"], "b": "BMW", "n": 0})
W("search.json", {"count": len(search), "results": search})

meta = {
    "name": "BimmerArchive Open Data",
    "description": "BMW / MINI / Rolls-Royce chassis codes, factory production type keys and engine codes as static JSON.",
    "version": "v1",
    "generated": today,
    "source": {
        "site": SRC,
        "retrieved_via": "Internet Archive Wayback Machine",
        "snapshots": {
            "home": "20260611203026",
            "e-code": "20260608081203",
            "m-code": "20260419191424",
            "detail_pages": "2026 (nearest capture)",
        },
    },
    "counts": {
        "models": len(models),
        "models_with_detail": sum(1 for m in models if m["has_detail"]),
        "engines": len(engines),
        "engines_with_detail": sum(1 for e in engines if e["has_detail"]),
        "production_codes": len(all_codes),
        "unique_production_codes": len(by_code),
        "models_without_production_codes": sum(1 for m in models if m["production_code_count"] == 0),
        "plants": len(plants),
        "regions": len(regions),
    },
    "endpoints": {
        "GET /api/v1/models.json": "all chassis codes",
        "GET /api/v1/models/{slug}.json": "one chassis code plus its production codes",
        "GET /api/v1/engines.json": "all engine variants",
        "GET /api/v1/engines/{slug}.json": "one engine plus full specs",
        "GET /api/v1/production-codes.json": "every factory type key, flat",
        "GET /api/v1/production-codes/{CODE}.json": "look up one type key",
        "GET /api/v1/plants.json": "production plants",
        "GET /api/v1/regions.json": "market regions",
        "GET /api/v1/brands.json": "brands",
        "GET /api/v1/search.json": "compact client-side search index",
    },
    "notes": [
        "Static JSON only - no server, no rate limit, no key.",
        "Derived from public Wayback Machine snapshots of bimmerarchive.org; a research mirror, not an official BMW source.",
        "power_kw is null where the source table was blank or 0.",
        "Production codes are globally unique in this dataset - 4339 codes, zero collisions - but production-codes/{CODE}.json still returns a list so the shape stays stable if a collision ever appears.",
        "97 of 285 chassis pages carry no production code table in the source; their production_code_count is 0.",
    ],
}
W("meta.json", meta)
W("index.json", meta)

# ------------------------------------------------- CSV exports (data/*.csv)
import csv

DATA = os.path.join(ROOT, "data")
os.makedirs(DATA, exist_ok=True)


def csv_out(name, header, keys, rowsrc):
    with open(os.path.join(DATA, name), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        for r in rowsrc:
            w.writerow([r.get(k) for k in keys])


csv_out("models.csv",
        ["code", "brand", "description", "years", "production_codes", "source"],
        ["code", "brand", "description", "years", "production_code_count", "source"],
        [dict(m, source=SRC + "/e-code/" + m["slug"] + ".html") for m in models])

csv_out("engines.csv",
        ["code", "family", "years", "displacement_cc", "power_kw", "power_ps",
         "torque_nm", "cylinders", "valves", "compression_ratio", "bore_mm", "stroke_mm", "fuel"],
        ["code", "family", "years", "displacement_cc", "power_kw", "power_ps",
         "torque_nm", "cylinders", "valves", "compression_ratio", "bore_mm", "stroke_mm", "fuel"],
        [engine_out[e["slug"]] for e in engines])

csv_out("production-codes.csv",
        ["code", "chassis", "brand", "model", "body", "engine", "power_kw",
         "drivetrain", "steering", "region", "from", "to"],
        ["code", "chassis", "brand", "model", "body", "engine", "power_kw",
         "drivetrain", "steering", "region", "from", "to"],
        all_codes)

print(json.dumps(meta["counts"], indent=2))
