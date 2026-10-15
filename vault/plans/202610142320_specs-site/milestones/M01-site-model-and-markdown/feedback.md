# Feedback — M01-site-model-and-markdown

## Attempt 1

**Blocked (1/2)**: `just lint` red, and the new package is invisible to git and ruff.

- Checked: `git status --short --ignored`, `just typecheck` (green), `just lint` (red), the worker's Verify (36 passed).
- `just lint` fails: `E501 Line too long (101 > 100)` at `booping-python/tests/specs/site_test.py:168`.
- `.gitignore` line `site/` (meant for the MkDocs build output at the repo root, `mkdocs.yml` lives there) matches `booping-python/src/booping/specs/site/`, so git does not list the package and ruff, which honours `.gitignore`, never lints it — `just lint` green would prove nothing about the package.
- Next attempt must: anchor that rule to `/site/` in `.gitignore` (runner's decision, recorded as D6 in `develop-defaults.md`; nothing else in `.gitignore` changes), fix the E501, then get `just lint` and `just typecheck` green with the package now linted, fixing whatever ruff newly reports in `booping-python/src/booping/specs/site/`, and re-run the milestone's Verify. Everything from attempt 1 is still uncommitted in the tree — keep it, fix in place.
