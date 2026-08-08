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

[doc("Structural checks over the rendered reports")]
mdcheck:
    @uv run scripts/mdcheck.py

[doc("Check the committed reports against a fresh hermetic render")]
snapshots:
    @uv run scripts/snapshots.py check

# Take the fresh render as the new baseline: rewrite the committed reports.
snapshots-accept target="":
    @uv run scripts/snapshots.py accept {{ target }}

[doc("Render worker: snapshots-render [--fixture] [--dest <dir>] [playbook]")]
snapshots-render *args:
    @uv run scripts/snapshots.py render {{ args }}

# Playbook evals — promptfoo over `claude -p` on subscription auth. Suites live at
# playbooks/<name>/<step>/promptfooconfig.yaml and are named <playbook>/<step>:
#   just smoke groom/intake      one suite
#   just smoke all               every suite, in sequence
#   just smoke -c <path>         explicit config, forwarded to promptfoo untouched
# Naming no suite lists them — promptfoo has no config at the repo root.
#
# Every run posts its results to the PR for the current branch: one sticky comment
# (updated in place) plus an `evals` commit status on HEAD, which is the merge gate —
# a new commit has no status, so a branch rule requiring `evals` blocks until the suites
# are re-run. `EVAL_PR=0 just smoke …` opts out; no gh or no PR degrades to printing.

# run promptfoo eval over a suite — see `just suites`
[no-exit-message]
eval *args:
    @JUST_RECIPE=eval bin/eval-run.sh - {{ args }}

# run promptfoo eval, then render a markdown report (status, per-check reasons) in glow
[no-exit-message]
eval-md *args:
    @JUST_RECIPE=eval-md bin/eval-md.sh {{ args }}

# run only the deterministic tier — cheap, no judge calls
[no-exit-message]
smoke *args:
    @JUST_RECIPE=smoke bin/eval-run.sh smoke {{ args }}

# run only the judged tier — the real signal, costs judge calls
[no-exit-message]
regress *args:
    @JUST_RECIPE=regress bin/eval-run.sh regress {{ args }}

# list the eval suites by name
suites:
    @bin/eval-target.sh --list

# Build the documentation site (strict)
docs:
    uv run --group docs --project booping-python mkdocs build --strict

# Serve the documentation site locally with live reload
docs-serve:
    uv run --group docs --project booping-python mkdocs serve
