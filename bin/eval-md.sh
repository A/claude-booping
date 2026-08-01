#!/usr/bin/env bash
# `just eval-md` — run promptfoo, render a markdown report, show it in glow.
set -uo pipefail
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)

out=$(mktemp -t promptfoo-eval-XXXXXX.json)
md="${out%.json}.md"
rc=0
npx promptfoo@latest eval "$@" --output "$out" || rc=$?
jq -r -f "$here/report-md.jq" "$out" > "$md"
glow -w "$(tput cols)" "$md"
echo "report md:    $md"
echo "results json: $out"
exit $rc
