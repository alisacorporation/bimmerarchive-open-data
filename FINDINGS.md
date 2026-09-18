# bimmerarchive.org — source structure notes

*Reconnaissance notes from the first pass. The finished dataset is described in `README.md`.*

Source: Wayback Machine snapshots
- Home: `/web/20260611203026/https://www.bimmerarchive.org/`
- E-Code index: `/web/20260608081203/.../e-code` (captured 2026-06-08)
- M-Code index: `/web/20260419191424/.../m-code/` (captured 2026-04-19)

## What the site is
German-run reference archive ("Model Archive for BMW models", sister site bmwarchive.org /
bimmerarchiv.de) covering BMW, MINI and Rolls-Royce. Bilingual (EN/DE). Not a blog — the
articles are just BMW press releases; the value is in the code databases.

## Live navigation (depth 0)
| Nav label | Path | Status |
|---|---|---|
| Vehicles | `/e-code/` | live — model/chassis code database |
| Drivetrain | `/m-code/` | live — engine code database |
| Photo | `/photo/` | live — 670+ galleries |
| Video | `/video/` | live |
| Motorcycles | — | **commented out in HTML** (dead section) |
| VIN | — | **commented out in HTML** (dead section) |
| Production | `/production/` | commented out of nav, but pages exist (e.g. `/production/bmw-plant-steyr.html`) |
| (footer) | `/document/`, `/rss/`, `/article/page-1..6.html` | brochures & pricelists, RSS, news archive |

## Depth 1 — the two index pages
### `/e-code/` — 285 chassis codes
Columns: Years · Code · Model example and description · Model type (all "Serie").
Span: 1955 Isetta 100 → 2026 NA0 (new electric i3) / NA5 (iX3 Neue Klasse).
Includes variant suffixes that are the real value: `(MUE)` = LCI/facelift, `(FL)` = Facelift,
`(2)` = LWB, `(C)` = Convertible, `(Z)`, `(JCW)`, `(BEV)`, `(M5)`, `(PL)` = Protection Line.
Covers MINI (R50…U25, J01, J05) and Rolls-Royce (RR1…RR25).
→ `api/v1/models.json`, `data/models.csv`

### `/m-code/` — 202 engine variants in 54 families
Grouped by family heading: B37 B38 B47 B48 B57 B58 · DA · HA0 (+XE electric) ·
M2 M21 M40 M41 M42 M43 M44 M47 M50 M51 M57 M62 M67 M70 M72 M73 ·
N13 N16 N18 N20 N26 N40 N42 N43 N45 N46 N47 N51 N52 N53 N54 N55 N57 N62 N63 N73 N74 ·
S14 S50 S52 S54 S55 S58 S63 S65 S85.
Columns: Production Dates · Engine Code · Displacement · Power / Torque.
Largest families: N52 (16), M57 (15), N47 (15), N57 (9), B47 (9), N62 (8).
Note: same code string appears multiple times at different outputs (e.g. B38A12U0 at 75 PS
and 102 PS) — the engine code alone is **not** a unique key; code + power is.
→ `api/v1/engines.json`, `data/engines.csv`

## Depth 2 — where the actual value is
### `/e-code/<code>.html` — **Production Codes table**  ← MOST IMPORTANT
Example `/e-code/e30.html` carries **274 rows**, one per factory type key:

`Production dates | Production Code | Model | Chassis | Engine | Power | Drivetrain | Steering | Region`

e.g. `1983-03 – 1988-07 | 1351 | 316 | Sedan | M10 | 0 kW | Rear-Wheel Drive | left | Europe`

This is BMW's internal **Typschlüssel** — the code embedded in the VIN that pins down exact
market + body + engine + LHD/RHD. That mapping is what VIN decoders are built from and it is
*not* published in a usable form almost anywhere else.

**Harvested in full: 4,339 production codes across 188 chassis** (97 of the 285 chassis pages
carry no code table at all). E30 alone accounts for 274. Every code is globally unique — zero
collisions — so a code resolves to exactly one factory configuration.
→ `api/v1/production-codes/` and `data/production-codes.csv`

### `/m-code/<code>.html` — engine spec sheet
Adds beyond the index: construction (e.g. "6 Cylinder, 24 Valves, Reihe"), compression ratio,
bore × stroke, fuel grade. Example B58B30M0: 2998 cm³, 240 kW/326 PS, 450 Nm, 11:1,
82 × 94,6 mm, Normal–Super Plus bleifrei.

## Depth 3
Each production code links to `/code/<4-digit>.html` (274 distinct links from the E30 page
alone). These are the leaf records. Wayback has a large number of them archived, but coverage
is spotty — `/code/1351.html` returned "not archived". Depth-2 E-code pages are the reliable
layer.

## Ranking — which info matters most
1. **`/e-code/<code>.html` production-code tables** — unique, structured, VIN-relevant. The prize.
2. **`/m-code/` + `/m-code/<code>.html`** — full engine spec set; harder to find collected elsewhere.
3. **`/e-code/` index** — useful as a spine/join key, but this list is widely mirrored.
4. Photo / Video / article pages — BMW press material, reproducible from BMW PressClub.

## Caveats
- Everything is a Wayback snapshot; the live site may differ.
- Power reads `0kW` for many older E30 entries — gaps in the source data, not a parse error.
- Internet Archive CDX API was intermittently returning "Temporarily Offline" during this run,
  so full per-section archived-URL counts were not obtained.
