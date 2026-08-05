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
test:
    cd booping-python && uv run pytest

# Committed reports: fixture vault + stubbed macros, byte-reproducible. One playbook
# with `just playbook-reports groom`. A STOP notice in the output fails the recipe.
playbook-reports which="*":
    #!/usr/bin/env bash
    set -euo pipefail
    failed=()
    for manifest in playbooks/{{ which }}/playbook.md; do
        name=$(basename "$(dirname "$manifest")")
        out="playbooks/$name/_reports/output.md"
        bin/booping render-playbook "$name" \
            --project playbooks/_fixtures/vault \
            --stub-macro "core.macros.date=19700101-00-00" \
            --stub-macro "core.macros.date +%Y%m%d%H%M=197001010000" \
            --stub-macro "core.macros.date +%Y-%m-%d %H:%M=1970-01-01 00:00" \
            --output "$out"
        grep -q '^\*\*STOP' "$out" && failed+=("$name")
    done
    if (( ${#failed[@]} )); then
        printf 'STOP notice in report: %s\n' "${failed[@]}" >&2
        exit 1
    fi

# Debug reports: the attached project's own vault, macros executed for real. Written to
# playbooks/<name>/_reports/local.md, which is gitignored. STOP notices are the point here,
# so they print rather than fail.
playbook-reports-live which="*":
    #!/usr/bin/env bash
    set -euo pipefail
    for manifest in playbooks/{{ which }}/playbook.md; do
        name=$(basename "$(dirname "$manifest")")
        out="playbooks/$name/_reports/local.md"
        bin/booping render-playbook "$name" --output "$out"
        grep -h '^\*\*STOP' "$out" || true
    done

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
