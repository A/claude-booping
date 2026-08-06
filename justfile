default:
    @just --list

# Render src/files/**/*.j2 to plugin-root destinations (skills/, agents/)
build:
    bin/booping build

# Watch src/files/ and src/config_files.yaml; rebuild on change (requires watchexec)
dev:
    watchexec -w src/files -w src/config_files.yaml -- bin/booping build

# Lint booping-python
lint:
    cd booping-python && uv run ruff check .

# Type-check booping-python
typecheck:
    cd booping-python && uv run basedpyright

# Run booping-python tests
pytest:
    cd booping-python && uv run pytest

# Every check CI runs, in order, stopping at the first failure.
ci: lint typecheck pytest snapshots mdcheck

# Structural checks over the rendered reports. Rules land in M4.
mdcheck:
    @echo "mdcheck: no rules yet"

# Writes nothing under playbooks/: renders into a temp dir, then diffs against the baselines.
[doc("Check the committed reports against a fresh hermetic render")]
snapshots:
    #!/usr/bin/env bash
    set -euo pipefail
    tmp=$(mktemp -d)
    trap 'rm -rf "$tmp"' EXIT
    {{ just_executable() }} snapshots-render --fixture --dest "$tmp" >/dev/null
    drifted=()
    for rendered in "$tmp"/*/_reports/output.md; do
        name=$(basename "$(dirname "$(dirname "$rendered")")")
        committed="playbooks/$name/_reports/output.md"
        if [[ ! -f "$committed" ]]; then
            echo "missing snapshot: $committed" >&2
            drifted+=("$name")
            continue
        fi
        if ! diff -u --label "$committed" --label "$committed (rendered)" \
            "$committed" "$rendered"; then
            drifted+=("$name")
        fi
    done
    if (( ${#drifted[@]} )); then
        printf 'snapshot drift: %s\n' "${drifted[*]}" >&2
        echo "run 'just snapshots-accept' to take the rendered output as the baseline" >&2
        exit 1
    fi

# Take the fresh render as the new baseline: rewrite the committed reports.
snapshots-accept target="":
    @{{ just_executable() }} snapshots-render --fixture {{ target }}

# Render worker. --fixture renders against playbooks/_fixtures/vault (hermetic, the vault's
# own config declares `macro_stubs:`) into <dest>/<name>/_reports/output.md and fails on a
# STOP notice; without it, the attached project's own vault with macros executed for real
# into <dest>/<name>/_reports/local.md (gitignored), where STOP notices print rather than
# fail. A trailing argument narrows to one playbook; --dest <dir> moves the destination root
# (default `playbooks`).
[doc("Render worker: snapshots-render [--fixture] [--dest <dir>] [playbook]")]
snapshots-render *args:
    #!/usr/bin/env bash
    set -euo pipefail
    set -- {{ args }}
    fixture=0
    dest=playbooks
    target='*'
    while (( $# )); do
        case "$1" in
            --fixture) fixture=1 ;;
            --dest) dest="$2"; shift ;;
            --dest=*) dest="${1#--dest=}" ;;
            *) target="$1" ;;
        esac
        shift
    done
    failed=()
    for manifest in playbooks/$target/playbook.md; do
        name=$(basename "$(dirname "$manifest")")
        if (( fixture )); then
            out="$dest/$name/_reports/output.md"
        else
            out="$dest/$name/_reports/local.md"
        fi
        mkdir -p "$(dirname "$out")"
        echo "$out"
        if (( fixture )); then
            bin/booping render-playbook "$name" \
                --project playbooks/_fixtures/vault \
                --output "$out"
            if grep -q '^\*\*STOP' "$out"; then
                failed+=("$name")
            fi
        else
            bin/booping render-playbook "$name" --output "$out"
            grep -h '^\*\*STOP' "$out" || true
        fi
    done
    if (( ${#failed[@]} )); then
        printf 'STOP notice in report: %s\n' "${failed[@]}" >&2
        exit 1
    fi

# Playbook evals — promptfoo over `claude -p` on subscription auth. Suites live at
# playbooks/<name>/<step>/promptfooconfig.yaml; pass one with -c, e.g.
#   just smoke -c playbooks/groom/intake/promptfooconfig.yaml

# run promptfoo eval — args pass straight through
[no-exit-message]
eval *args:
    npx promptfoo@latest eval {{ args }}

# run promptfoo eval, then render a markdown report (status, per-check reasons) in glow
[no-exit-message]
eval-md *args:
    @bin/eval-md.sh {{ args }}

# run only the deterministic tier — cheap, no judge calls
[no-exit-message]
smoke *args:
    npx promptfoo@latest eval --filter-metadata tier=smoke {{ args }}

# run only the judged tier — the real signal, costs judge calls
[no-exit-message]
regress *args:
    npx promptfoo@latest eval --filter-metadata tier=regress {{ args }}

# Build the documentation site (strict)
docs:
    uv run --group docs --project booping-python mkdocs build --strict

# Serve the documentation site locally with live reload
docs-serve:
    uv run --group docs --project booping-python mkdocs serve
