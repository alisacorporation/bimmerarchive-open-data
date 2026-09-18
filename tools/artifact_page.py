# -*- coding: utf-8 -*-
"""Write dist/artifact.html — the bundled site as an Artifact page.

Artifacts wrap the file in their own <!doctype>/<html>/<head>/<body>, so this
emits the page content only, with the <title> first.

Run after tools/bundle.py.
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")

src = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()

body = re.search(r"(?is)<body>(.*?)</body>", src).group(1).strip()
body = body.replace('<script src="assets/app.js"></script>',
                    '<script src="assets/bundle-shim.js"></script>\n'
                    '<script src="assets/app.js"></script>')

page = (
    "<title>BimmerArchive Open Data</title>\n"
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    'family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;600;700&display=swap">\n'
    '<link rel="stylesheet" href="assets/style.css">\n'
    + body + "\n"
)

os.makedirs(DIST, exist_ok=True)
out = os.path.join(DIST, "artifact.html")
open(out, "w", encoding="utf-8", newline="\n").write(page)
print("wrote", out, os.path.getsize(out), "bytes")
