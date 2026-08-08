#!/usr/bin/env bash
# `just eval` / `just smoke` / `just regress` — run promptfoo over one suite, or every suite.
#
#   eval-run.sh <tier|-> [<playbook>/<step>|all|-c <path>] [promptfoo args...]
#
# A leading `-` in the first user argument means the caller passed promptfoo flags
# themselves; everything is forwarded untouched. With no arguments at all, promptfoo
# would search the repo root, find no config and fail — so name the suites instead.
set -uo pipefail
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)

tier=${1:?eval-run.sh: tier (or -) is required}
shift

filter=()
[ "$tier" != "-" ] && filter=(--filter-metadata "tier=$tier")

recipe=${JUST_RECIPE:-eval}

if [ "$#" -eq 0 ]; then
    {
        echo "no suite named — promptfoo has no config at the repo root."
        echo
        echo "Usage: just $recipe <playbook>/<step> [promptfoo args...]"
        echo "       just $recipe all          # every suite, in sequence"
        echo "       just $recipe -c <path>    # explicit config, forwarded as-is"
        echo
    } >&2
    "$here/eval-target.sh" --list
    exit 1
fi

case $1 in
    -*) exec npx promptfoo@latest eval "${filter[@]}" "$@" ;;
esac

target=$1
shift

mapfile -t configs < <("$here/eval-target.sh" "$target") || exit 1
[ "${#configs[@]}" -gt 0 ] || exit 1

# Results are captured per suite so the run can be posted to the PR as one sticky comment.
# EVAL_PR=0 opts out; no `gh` or no PR for the branch degrades to printing the report.
results=$(mktemp -d -t booping-eval-XXXXXX)
trap 'rm -rf "$results"' EXIT

rc=0
failed=()
for config in "${configs[@]}"; do
    [ "${#configs[@]}" -gt 1 ] && echo "==> $config"
    suite=$(echo "$config" | sed 's#^playbooks/##; s#/promptfooconfig\.yaml$##; s#/#__#g')
    npx promptfoo@latest eval "${filter[@]}" -c "$config" \
        --output "$results/$suite.json" "$@" || { rc=$?; failed+=("$config"); }
done

if [ "${EVAL_PR:-1}" != "0" ] && command -v gh >/dev/null; then
    "$here/eval-pr-comment.sh" "$tier" "$results" || true
fi

if [ "${#failed[@]}" -gt 0 ]; then
    echo >&2
    echo "failed suites:" >&2
    printf '  %s\n' "${failed[@]}" >&2
fi
exit $rc
