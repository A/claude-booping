#!/usr/bin/env bash
# `just eval-md` — run promptfoo over one suite, render a markdown report, show it in glow.
set -uo pipefail
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)

if [ "$#" -eq 0 ]; then
    {
        echo "no suite named — promptfoo has no config at the repo root."
        echo
        echo "Usage: just eval-md <playbook>/<step> [promptfoo args...]"
        echo "       just eval-md -c <path>    # explicit config, forwarded as-is"
        echo
    } >&2
    "$here/eval-target.sh" --list
    exit 1
fi

args=("$@")
case $1 in
    -*) ;;                                  # explicit promptfoo flags — forward untouched
    *)
        mapfile -t configs < <("$here/eval-target.sh" "$1") || exit 1
        if [ "${#configs[@]}" -ne 1 ]; then
            echo "eval-md renders one report — name a single suite, not 'all'." >&2
            exit 1
        fi
        shift
        args=(-c "${configs[0]}" "$@")
        ;;
esac

out=$(mktemp -t promptfoo-eval-XXXXXX.json)
md="${out%.json}.md"
rc=0
npx promptfoo@latest eval "${args[@]}" --output "$out" || rc=$?
jq -r -f "$here/report-md.jq" "$out" > "$md"
glow -w "$(tput cols)" "$md"
echo "report md:    $md"
echo "results json: $out"
exit $rc
