#!/usr/bin/env bash
# Resolve one eval-suite token into promptfoo config paths, one per line.
#
#   eval-target.sh groom/intake           -> playbooks/groom/intake/promptfooconfig.yaml
#   eval-target.sh playbooks/groom/intake -> same
#   eval-target.sh path/to/config.yaml    -> path/to/config.yaml
#   eval-target.sh all                    -> every suite in the repo
#
# Exit 1 with a suite listing on stderr when the token names nothing.
# Callers own the no-token and leading-dash (passthrough) cases.
set -uo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)

suites() { (cd "$root" && ls playbooks/*/*/promptfooconfig.yaml 2>/dev/null); }

list_suites() {
    echo "Suites:" >&2
    suites | sed 's#playbooks/##; s#/promptfooconfig.yaml##; s#^#  #' >&2
}

if [ "${1:-}" = "--list" ]; then list_suites; exit 0; fi

token=${1:?eval-target.sh: a suite token is required}

if [ "$token" = "all" ]; then
    found=$(suites)
    [ -n "$found" ] || { echo "no suites under playbooks/*/*/promptfooconfig.yaml" >&2; exit 1; }
    printf '%s\n' "$found"
    exit 0
fi

for candidate in "$token" "playbooks/$token"; do
    for path in "$candidate" "$candidate/promptfooconfig.yaml"; do
        if [ -f "$root/$path" ] || [ -f "$path" ]; then
            printf '%s\n' "$path"
            exit 0
        fi
    done
done

echo "no suite matches '$token'." >&2
echo >&2
list_suites
exit 1
