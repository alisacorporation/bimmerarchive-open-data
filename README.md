# BimmerArchive Open Data

A rescue mirror of **bimmerarchive.org** (also published as bmwarchive.org / bimmerarchiv.de) —
BMW, MINI and Rolls-Royce chassis codes, factory production type keys and engine codes —
turned into **structured JSON** and served as a **free static API** plus a browsable website.

The original site is gone. Its contents survive only as Internet Archive snapshots, which are
themselves slow and periodically unreachable. This repository exists so the data no longer
depends on either.

## Why this matters

The valuable part of the site was never the news articles. It was the **production code tables**
on each chassis page — BMW's internal 4-character *Typschlüssel*, the key encoded in the VIN
that resolves a car to an exact market, body, engine, output and steering side:

| Production dates | Code | Model | Body | Engine | Power | Drivetrain | Steering | Region |
|---|---|---|---|---|---|---|---|---|
| 1998-06 – 2001-08 | AL11 | 316i | Sedan | M43/TU | 77 kW | Rear-Wheel Drive | left | Europe |

That mapping is what VIN decoders are built from, and it is not published in usable form
anywhere else.

## Layout

```
index.html, assets/          the website — reads api/v1 directly
api/v1/                      static JSON API (the deliverable), 4,833 files
data/*.csv                   the same data as flat CSV
dist/                        bundled single-page build (10 files, 3.1 MB)
tools/fetch.sh               harvester (archive or live origin)
tools/ingest.py              HTML -> JSON + CSV build step
tools/bundle.py              api/v1 -> dist/ bundles
tools/artifact_page.py       dist/artifact.html for Artifact hosting
cache/                       raw harvested HTML (gitignored, regenerate with fetch.sh)
```

## What's in it

| | |
|---|---|
| chassis codes | 285 (241 BMW, 35 MINI, 9 Rolls-Royce) |
| production codes | 4,339, all globally unique |
| engine variants | 202 in 54 families |
| plants | 11 |
| market regions | 14 |
| harvest | 485/485 pages, zero failures |

## API

Static files only. No server, no key, no rate limit. Host anywhere that serves JSON over HTTPS
(GitHub Pages, Cloudflare Pages, Netlify, S3).

| Endpoint | Returns |
|---|---|
| `GET /api/v1/meta.json` | dataset metadata, counts, endpoint list |
| `GET /api/v1/models.json` | every chassis code |
| `GET /api/v1/models/{slug}.json` | one chassis code and all its production codes |
| `GET /api/v1/engines.json` | every engine variant |
| `GET /api/v1/engines/{slug}.json` | one engine with full specs |
| `GET /api/v1/production-codes.json` | every type key, flat |
| `GET /api/v1/production-codes/{CODE}.json` | look up a single type key |
| `GET /api/v1/plants.json` | production plants |
| `GET /api/v1/regions.json` | market regions |
| `GET /api/v1/brands.json` | brands |
| `GET /api/v1/search.json` | compact index for client-side search |

### Example

```bash
curl https://<your-host>/api/v1/production-codes/AL11.json
```

```json
{
  "code": "AL11",
  "count": 1,
  "results": [
    {
      "code": "AL11",
      "model": "316i",
      "body": "Sedan",
      "engine": "M43/TU",
      "power_kw": 77,
      "drivetrain": "Rear-Wheel Drive",
      "steering": "left",
      "region": "Europe",
      "from": "1998-06",
      "to": "2001-08",
      "chassis": "E46 (4)",
      "chassis_slug": "e46-4",
      "brand": "BMW"
    }
  ]
}
```

Production codes are **globally unique** in this dataset — 4,339 codes, zero collisions — so a
lookup resolves to exactly one factory configuration. The endpoint still returns a list, so the
response shape stays stable if a collision ever turns up.

## Rebuilding

```bash
sh tools/fetch.sh            # harvest HTML into cache/ (resumable, skips what it has)
python tools/ingest.py       # parse cache/ into api/v1/ and data/*.csv
python tools/bundle.py       # optional: collapse api/v1 into dist/ bundles
python tools/artifact_page.py
```

## Serving it

Any static host works. The site reads `api/v1/` with relative paths, so publishing the repo
root is enough:

```bash
python -m http.server 8765
```

For hosts that cap the number of files, `dist/` carries the same site against seven bundled
JSON files instead of 4,833 individual ones.

`tools/fetch.sh` reads `BASE` from the environment, so it can be pointed at a live origin
instead of the archive if one ever returns:

```bash
BASE=https://www.bimmerarchive.org sh tools/fetch.sh
```

The harvester is deliberately sequential with retries — the archive throttles hard on
concurrent connections and starts returning truncated bodies.

## License

Code is MIT (`LICENSE`). The dataset is a set of facts extracted from a site that no longer
exists — see `DATA.md` for provenance, attribution and the jurisdiction note.

## Provenance and caveats

- Source: public Wayback Machine snapshots of bimmerarchive.org (June 2026 index captures,
  nearest-2026 captures for detail pages). Snapshot timestamps are recorded in `meta.json`.
- This is a **research mirror**, not an official BMW source. Figures are the site's own and
  carry its errors.
- `power_kw` is `null` where the source table was blank or `0` — common on pre-1990 entries.
- **97 of 285 chassis pages carry no production code table at all** in the source, mostly
  pre-war models, recent arrivals and MINI/Rolls-Royce entries. Their `production_code_count`
  is 0. The 4,339 codes come from the remaining 188 chassis; E30 alone accounts for 274.
- The site's deepest layer, `/code/{CODE}.html`, is largely unarchived. Everything those pages
  displayed is already present in the chassis-level tables captured here.
