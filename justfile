default:
    @just --list

# Lint booping-python
lint:
    cd booping-python && uv run ruff check .

# Typecheck booping-python
typecheck:
    cd booping-python && uv run basedpyright

# Test booping-python
test:
    cd booping-python && uv run pytest

# Render doc and plan templates to docs/
build-docs:
    #!/usr/bin/env bash
    for f in src/templates/docs/*.md.j2; do
        name="$(basename "$f" .md.j2)"
        bin/booping render "$f" --output "docs/$name.md"
    done
    for f in src/templates/plan_templates/*.md.j2; do
        name="$(basename "$f" .md.j2)"
        bin/booping render "$f" --output "docs/plan_templates/$name.md"
    done
