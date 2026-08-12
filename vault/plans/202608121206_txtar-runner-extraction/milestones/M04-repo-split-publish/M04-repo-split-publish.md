---
id: "04"
title: "Repo split and PyPI publish"
sp: 7
status: done
plan: "vault/plans/202608121206_txtar-runner-extraction/index.md"
---

# M04: Repo split and PyPI publish

Goal: `pytest-txtar` lives in its own GitHub repository with CI and PyPI trusted publishing, v0.1.0 is on PyPI, and booping depends on the published release instead of the in-repo copy.

Scope: new external repo `pytest-txtar` (bootstrap + CI), then `booping-python/pyproject.toml` and deletion of the in-repo `pytest-txtar/` directory. Requires M03 complete. One manual user step: creating the PyPI project/trusted-publisher binding.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Bootstrap the external repo: `gh repo create pytest-txtar --public`, copy the package tree in as the initial commit (fresh history), add GitHub Actions CI — one workflow with a test job (`uv sync`, ruff, basedpyright, pytest) on push/PR and a publish job on `v*` tags using PyPI trusted publishing (`permissions: id-token: write`, `uv build` + `uv publish`, no stored secret) | external repo: full package tree, `.github/workflows/ci.yml` | 3 | done |
| 4.2 | Release v0.1.0: **user step** — create the pending trusted publisher on pypi.org for the new repo/workflow; then set version 0.1.0, tag `v0.1.0`, push, confirm the publish job uploads and `https://pypi.org/project/pytest-txtar/` serves 0.1.0 | external repo: `pyproject.toml`, tag | 2 | done |
| 4.3 | Flip booping to the release: replace the path source with `pytest-txtar>=0.1.0` from PyPI (drop the `[tool.uv.sources]` entry), delete the in-repo `pytest-txtar/` directory, relock | `booping-python/pyproject.toml`, `booping-python/uv.lock`, `pytest-txtar/` (deleted) | 2 | done |

## Definition of Done

### Task 4.1

- [x] External repo exists with the package tree, LICENSE (MIT + BSD-3 block), spec-bearing README from M03.
- [x] CI test job green on the initial push.
- [x] Publish workflow present, gated on `v*` tags, authenticates with the `PYPI_TOKEN` repo secret (user decision 2026-08-12 superseding the OIDC/trusted-publishing plan line).

### Task 4.2

- [x] Hard gate before any tag is pushed: satisfied — the user configured publish auth (`PYPI_TOKEN` secret) and confirmed in chat before the tag was pushed.
- [x] Tag `v0.1.0` pushed; publish job green; `pip index versions pytest-txtar` (or the PyPI JSON API) shows 0.1.0.

### Task 4.3

- [x] `booping-python/pyproject.toml` has no `[tool.uv.sources]` entry for pytest-txtar; dependency reads `pytest-txtar>=0.1.0`; `uv sync` resolves it from PyPI.
- [x] In-repo `pytest-txtar/` directory removed; `git status` clean of it.
- [x] `just e2e` green against the published package.

## Verify

```
gh run list --repo "$(gh repo view pytest-txtar --json nameWithOwner -q .nameWithOwner)" --limit 3
curl -s https://pypi.org/pypi/pytest-txtar/json | jq -r .info.version
cd booping-python && uv sync && cd .. && just e2e
```

