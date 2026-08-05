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

# Render every playbook against the fixture vault into playbooks/<name>/_reports/output.md
playbook-reports:
    #!/usr/bin/env bash
    set -euo pipefail
    for manifest in playbooks/*/playbook.md; do
        name=$(basename "$(dirname "$manifest")")
        bin/booping render-playbook "$name" \
            --project playbooks/_fixtures/vault \
            --stub-macro macros.now=19700101-00-00 \
            --output "playbooks/$name/_reports/output.md"
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
