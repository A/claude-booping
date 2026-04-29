default:
    @just --list

# Render docs and plan-template static artifacts (manual; no watcher)
build-docs:
    #!/usr/bin/env bash
    set -euo pipefail
    for tpl in src/templates/docs/*.md.j2; do
        out="docs/$(basename "${tpl%.j2}")"
        bin/booping render "$tpl" --output "$out"
    done
    for tpl in src/templates/plan_templates/*.md.j2; do
        out="docs/plan_templates/$(basename "${tpl%.j2}")"
        bin/booping render "$tpl" --output "$out"
    done

# Lint booping-python
lint:
    cd booping-python && uv run ruff check .

# Type-check booping-python
typecheck:
    cd booping-python && uv run basedpyright

# Run booping-python tests
test:
    cd booping-python && uv run pytest
