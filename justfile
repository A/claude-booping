default:
    @just --list

# Render src/templates + src/config.yaml into skills/ and docs/
build:
    bin/booping-build

# Watch src/ and re-render on change
watch:
    bin/booping-build --watch

# Lint booping-python
lint:
    cd booping-python && uv run ruff check .

# Typecheck booping-python
typecheck:
    cd booping-python && uv run basedpyright

# Test booping-python
test:
    cd booping-python && uv run pytest
