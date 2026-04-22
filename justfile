test:
    uv run --with pytest --with pytest-cov --with "ruamel.yaml>=0.18" pytest bin/tests/ -v --cov=bin --cov-report=term-missing

lint-backlog:
    ! grep -rniE 'backlog/' agents/ skills/ docs/

check: lint-backlog test
