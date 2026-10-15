#!/usr/bin/env bash
# Render every scene, join them into out/binomial_full.mp4, write out/beats.csv.
#
#   ./render.sh          final quality: 1080p60 (-qh)
#   ./render.sh l        quick drafts:  480p15  (-ql)
#   ./render.sh h S08    re-render one scene, then re-assemble
#
# Manim caches every animation it has rendered before, so re-running after
# changing one scene only re-renders the animations that changed.
set -euo pipefail
cd "$(dirname "$0")"

mkdir -p out/logs
Q="${1:-h}"
ONLY="${2:-}"

SCENES=(
  "S01 s01_lookup S01Lookup"
  "S02 s02_choosing S02Choosing"
  "S03 s03_theorem S03Theorem"
  "S04 s04_question S04Question"
  "S05 s05_multiply S05Multiply"
  "S06 s06_counts S06Counts"
  "S07 s07_tree S07Tree"
  "S08 s08_fold S08Fold"
  "S09 s09_last_step S09LastStep"
  "S10 s10_two_ways S10TwoWays"
  "S11 s11_builds S11Builds"
  "S12 s12_galton S12Galton"
)

for entry in "${SCENES[@]}"; do
  read -r id module cls <<< "$entry"
  if [[ -n "$ONLY" && "$ONLY" != "$id" ]]; then continue; fi
  echo "== $id $cls (-q$Q)"
  .venv/bin/manim -q"$Q" --progress_bar none "$module.py" "$cls" > "out/logs/$id.log" 2>&1 \
    || { echo "   failed, see out/logs/$id.log"; exit 1; }
done

.venv/bin/python tools/assemble.py "$Q"
