# -*- coding: utf-8 -*-
"""Bundle api/v1 into a handful of files for single-page hosting (Artifacts etc).

The full API is ~4,800 files, one per record. Some hosts cap the number of
supporting files, so this collapses the per-record endpoints into three bundles
and writes a build of the site that reads them instead.

Usage: python tools/bundle.py   ->   dist/
"""
import os, json, shutil, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = os.path.join(ROOT, "api", "v1")
DIST = os.path.join(ROOT, "dist")


def rd(p):
    with open(os.path.join(API, p), encoding="utf-8") as f:
        return json.load(f)


def wr(p, obj):
    full = os.path.join(DIST, p)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
    return os.path.getsize(full)


if os.path.isdir(DIST):
    shutil.rmtree(DIST)
os.makedirs(DIST)

meta = rd("meta.json")
sizes = {}

sizes["meta.json"] = wr("bundle/meta.json", meta)
sizes["models.json"] = wr("bundle/models.json", rd("models.json"))
sizes["engines.json"] = wr("bundle/engines.json", rd("engines.json"))
sizes["search.json"] = wr("bundle/search.json", rd("search.json"))

models = {}
for fn in os.listdir(os.path.join(API, "models")):
    models[fn[:-5]] = rd(os.path.join("models", fn))
sizes["models-detail.json"] = wr("bundle/models-detail.json", models)

engines = {}
for fn in os.listdir(os.path.join(API, "engines")):
    engines[fn[:-5]] = rd(os.path.join("engines", fn))
sizes["engines-detail.json"] = wr("bundle/engines-detail.json", engines)

codes = {}
for fn in os.listdir(os.path.join(API, "production-codes")):
    codes[fn[:-5]] = rd(os.path.join("production-codes", fn))
sizes["codes.json"] = wr("bundle/codes.json", codes)

# site build: same markup, but app.js reads the bundles through a tiny shim
shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(DIST, "assets"))
html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
html = html.replace('<script src="assets/app.js"></script>',
                    '<script src="assets/bundle-shim.js"></script>\n'
                    '<script src="assets/app.js"></script>')
open(os.path.join(DIST, "index.html"), "w", encoding="utf-8", newline="\n").write(html)

shim = """/* Serves the per-record API endpoints out of three bundle files, so the page
   works on hosts that cap the number of supporting files. Installed before
   app.js; app.js is unchanged. */
(function () {
  const B = {};
  const load = p => fetch('bundle/' + p).then(r => r.json());
  const ready = Promise.all([
    load('meta.json').then(d => B['meta.json'] = B['index.json'] = d),
    load('models.json').then(d => B['models.json'] = d),
    load('engines.json').then(d => B['engines.json'] = d),
    load('search.json').then(d => B['search.json'] = d),
    load('models-detail.json').then(d => B.models = d),
    load('engines-detail.json').then(d => B.engines = d),
    load('codes.json').then(d => B.codes = d),
  ]);
  const real = window.fetch.bind(window);
  window.fetch = async function (url, opts) {
    const u = String(url);
    const m = u.match(/^api\\/v1\\/(.+)\\.json$/);
    if (!m) return real(url, opts);
    await ready;
    const key = m[1];
    let hit = B[key + '.json'];
    if (!hit) {
      const parts = key.split('/');
      if (parts.length === 2) {
        const group = parts[0] === 'production-codes' ? 'codes' : parts[0];
        hit = B[group] && B[group][parts[1]];
      }
    }
    if (hit) return new Response(JSON.stringify(hit), { status: 200 });
    return new Response('not found', { status: 404 });
  };
})();
"""
open(os.path.join(DIST, "assets", "bundle-shim.js"), "w", encoding="utf-8", newline="\n").write(shim)

total = sum(sizes.values())
for k, v in sorted(sizes.items(), key=lambda x: -x[1]):
    print("%-22s %8.1f KB" % (k, v / 1024))
print("%-22s %8.1f KB total in %d bundle files" % ("", total / 1024, len(sizes)))
print("dist/ ready")
