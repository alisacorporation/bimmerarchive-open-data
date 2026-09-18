#!/bin/sh
# Harvest bimmerarchive.org HTML into cache/.
#
#   sh tools/fetch.sh
#   BASE=https://www.bimmerarchive.org sh tools/fetch.sh      # live origin, if one returns
#
# Resumable: anything already in cache/ larger than 2 KB is skipped, so re-running
# after an interruption only fetches what is missing.
#
# Deliberately sequential. The Wayback Machine throttles concurrent connections hard
# and starts returning truncated bodies; parallel harvesting corrupts the cache.

set -e
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"

BASE=${BASE:-https://web.archive.org/web/2026id_/https://www.bimmerarchive.org}
UA="Mozilla/5.0 (bimmerarchive open data harvester)"
MINSIZE=2000

mkdir -p cache/index cache/e cache/m

fetch() {
  url="$1"
  out="$2"
  if [ -s "$out" ]; then
    if [ "$(wc -c < "$out")" -gt "$MINSIZE" ]; then
      return 0
    fi
  fi
  sleep 1
  curl -sL --compressed --max-time 90 --retry 3 --retry-delay 4 --retry-all-errors \
       -A "$UA" -o "$out.tmp" "$url" || true
  if [ -s "$out.tmp" ] && [ "$(wc -c < "$out.tmp")" -gt "$MINSIZE" ] \
     && ! grep -q "Temporarily Offline" "$out.tmp"; then
    mv "$out.tmp" "$out"
    echo "  ok   $out"
  else
    rm -f "$out.tmp"
    echo "  FAIL $out"
  fi
}

echo "== index pages"
fetch "$BASE/e-code" cache/index/e-code.html
fetch "$BASE/m-code/" cache/index/m-code.html

echo "== building target lists"
grep -o '/e-code/[a-z0-9._-]*\.html' cache/index/e-code.html | sort -u | tr -d '\r' > cache/targets-e.txt
grep -o '/m-code/[a-z0-9._-]*\.html' cache/index/m-code.html | sort -u | tr -d '\r' > cache/targets-m.txt
echo "   $(wc -l < cache/targets-e.txt) chassis pages, $(wc -l < cache/targets-m.txt) engine pages"

# Several passes: a page that failed once usually succeeds on a later, quieter pass.
pass=1
while [ "$pass" -le 4 ]; do
  echo "== pass $pass  $(date)"
  while IFS= read -r p; do
    [ -n "$p" ] && fetch "$BASE$p" "cache/e/$(basename "$p")"
  done < cache/targets-e.txt
  while IFS= read -r p; do
    [ -n "$p" ] && fetch "$BASE$p" "cache/m/$(basename "$p")"
  done < cache/targets-m.txt

  ne=$(ls cache/e | wc -l)
  nm=$(ls cache/m | wc -l)
  te=$(wc -l < cache/targets-e.txt)
  tm=$(wc -l < cache/targets-m.txt)
  echo "== after pass $pass: chassis $ne/$te, engines $nm/$tm"
  if [ "$ne" -ge "$te" ] && [ "$nm" -ge "$tm" ]; then
    break
  fi
  pass=$((pass + 1))
done

echo "== done $(date).  Now run: python tools/ingest.py"
