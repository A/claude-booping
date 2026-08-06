#!/usr/bin/env bash
# Assemble the eval report and post it as the PR's single sticky comment.
#
#   eval-pr-comment.sh <tier> <results-dir>
#
# <results-dir> holds one promptfoo JSON per suite, named after the suite with `/` -> `__`.
# The marker line is what makes the comment sticky (re-runs PATCH it) and what the
# `evals` CI gate greps for; the `sha:` it carries is the head commit the run covered, so
# a later push makes the recorded attestation stale rather than silently authoritative.
#
# No PR for the current branch, or no `gh`, is not an error: the report goes to stdout and
# the run's own exit status stands.
set -uo pipefail
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)

MARKER='<!-- booping-eval -->'

tier=${1:?eval-pr-comment.sh: tier is required}
dir=${2:?eval-pr-comment.sh: results dir is required}

# `-` is eval-run.sh's "no --filter-metadata" sentinel: both tiers ran.
[ "$tier" = "-" ] && tier="smoke+regress"

shopt -s nullglob
results=("$dir"/*.json)
[ "${#results[@]}" -gt 0 ] || { echo "eval-pr-comment.sh: no results in $dir" >&2; exit 1; }

sha=$(git rev-parse HEAD 2>/dev/null || echo unknown)
branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)

total_pass=0 total_fail=0 total_err=0
failing=() passing=()

for json in "${results[@]}"; do
    suite=$(basename "$json" .json | sed 's#__#/#g')

    read -r p f e < <(jq -r '.results.stats
        | "\(.successes) \(.failures) \(.errors // 0)"' "$json" 2>/dev/null) \
        || { p=0; f=0; e=1; }
    : "${p:=0}" "${f:=0}" "${e:=0}"

    total_pass=$((total_pass + p))
    total_fail=$((total_fail + f))
    total_err=$((total_err + e))

    section=$(jq -r --arg suite "$suite" -f "$here/report-pr.jq" "$json" 2>/dev/null) \
        || section=$(printf '# %s\nERROR: unreadable results JSON' "$suite")
    # Failing suites first: the reader wants them without scrolling.
    if (( f + e == 0 )); then passing+=("$section"); else failing+=("$section"); fi
done

summary="PASSED: $total_pass, FAILED: $total_fail"
(( total_err )) && summary="$summary, ERRORED: $total_err"

md=$(mktemp -t booping-eval-XXXXXX.md)
{
    echo "$MARKER"
    echo "<!-- sha: $sha -->"
    echo '```text'
    echo "booping evals — ${tier} tier — ${branch} @ ${sha:0:7} — just ${JUST_RECIPE:-eval}"
    echo "$summary over ${#results[@]} suite(s)"
    # Command substitution ate each section's trailing newline; separate them by hand
    # rather than trailing every one, so the fence closes without a blank line.
    for section in "${failing[@]}" "${passing[@]}"; do
        echo
        printf '%s\n' "$section"
    done
    echo '```'
} > "$md"

pr=$(gh pr view --json number -q .number 2>/dev/null)
if [ -z "$pr" ]; then
    echo "no PR for the current branch — report not posted:" >&2
    cat "$md"
    echo "report md: $md" >&2
    exit 0
fi

id=$(gh api "repos/{owner}/{repo}/issues/$pr/comments" --paginate \
    -q ".[] | select(.body | startswith(\"$MARKER\")) | .id" 2>/dev/null | head -1)

if [ -n "$id" ]; then
    url=$(gh api -X PATCH "repos/{owner}/{repo}/issues/comments/$id" \
        -F body=@"$md" -q .html_url) || exit 1
    echo "eval comment updated: $url"
else
    url=$(gh api -X POST "repos/{owner}/{repo}/issues/$pr/comments" \
        -F body=@"$md" -q .html_url) || exit 1
    echo "eval comment posted: $url"
fi

# The merge gate. A commit status is per-sha, so a later push leaves the new head without
# one and a branch rule requiring `evals` blocks until the suites are re-run — which is why
# this is a status rather than a workflow (an issue_comment-triggered job attaches its check
# to the default branch, never to the PR head).
if (( total_fail + total_err == 0 )); then
    state=success
    desc="$summary"
else
    state=failure
    desc="$summary"
fi

if err=$(gh api -X POST "repos/{owner}/{repo}/statuses/$sha" \
    -f state="$state" \
    -f context="evals" \
    -f description="${desc:0:139}" \
    -f target_url="$url" 2>&1 >/dev/null); then
    echo "commit status: evals=$state on ${sha:0:7}"
else
    # The common case is an unpushed HEAD: GitHub refuses a status for a sha it has
    # never seen. Report what it actually said rather than guessing at scopes.
    echo "commit status not set for ${sha:0:7} — ${err%%$'\n'*}" >&2
    case "$err" in
        *"No commit found"*) echo "  push the branch first, then re-run the evals." >&2 ;;
    esac
fi
