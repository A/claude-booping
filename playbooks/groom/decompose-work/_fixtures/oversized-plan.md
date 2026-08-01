# Input — local vault directories

The plan below was written by `draft-plan` against the `backend` template and cross-reviewed in
place; the user has not read it yet. Refine it against the sizing thresholds and write the
decomposition artifact into the run workdir.

## Run-time context

- project: `claude-booping` — the booping plugin repository; the vault it grooms into is the
  default `~/Claude/claude-booping/`
- run slug: `20260801-14-30_local-vault-directories`
- run workdir: `_runs/groom/20260801-14-30_local-vault-directories/`, relative to the current
  working directory — it already holds the confirmed framing, the blast-radius map and the
  confirmed design
- plan file: `plans/20260801-14-30_local-vault-directories.md`, on disk, written and complete

## Inputs

- the written plan — `plans/20260801-14-30_local-vault-directories.md`, on disk: 5 milestones,
  per-task and per-milestone story points, the sprint total mirrored in its `sp:` frontmatter
- the re-decompose threshold — **5 SP**: a task at or over it needs another pass before a single
  agent briefing can carry it
- the split threshold — **35 SP**: a sprint total past it should be proposed as two siblings
- the SP scale:
  - 1 — simple text/config change, no risk
  - 2 — simple task, predictable, no risk
  - 3 — medium task, minor risks but predictable overall
  - 4 — complex task, medium risk, may need small research but clear enough
  - 5 — research task: the developer would have to clarify and decompose it further before
    proceeding
- rework from the user: none — this is the run's first pass through decomposition

## Context files

<file path="plans/20260801-14-30_local-vault-directories.md">
---
title: Local vault directories
type: feature
status: in-spec
sp: 38
split_from: null
created: 2026-08-01
planned: null
started: null
completed: null
retro: null
goal: null
summary: "A repo can keep its booping vault inside its own working tree instead of under ~/Claude"
commit: null
---

# Local vault directories

## Context

**Current state** — a project's vault always lands at `~/Claude/{project}/`. The `.booping` marker
in the repo root is checked for existence only; nothing inside it is read. Every vault path in the
codebase is derived from the home base plus the project name.

**Motivation** — plans, retros and lessons are project artefacts, and for repos that want them
reviewed in pull requests and versioned with the code, a vault outside the working tree is the
wrong home. Two teams already keep a hand-maintained copy of their plans in-repo and sync it by
hand.

**Scope** — reading a vault location out of the `.booping` marker, honouring it everywhere the
vault is resolved, and scaffolding one. Not: moving an existing vault, syncing between the two
layouts, or any change to what a vault contains.

## Decisions

- **Marker carries the path**: the location lives in the repo's own `.booping` marker rather than
  in config — the marker is already the per-repo attachment point, and a vault path is a property
  of the repo, not of the user's machine.
- **Relative to the repo root**: a relative `vault_path:` resolves against the repo root, never
  against the process cwd — skills and hooks run from wherever the user invoked them.
- **No migration path**: an existing `~/Claude/{project}/` vault stays where it is; adopting a
  local vault is a manual move plus a marker edit, documented rather than automated.

## Architecture

`Context.assemble()` resolves the vault once, through a new `resolve_vault(repo_root, config)` in
`booping-python/src/booping/context/vault.py`. It reads the parsed `.booping` marker, takes
`vault_path:` when present and resolves it, and otherwise falls back to `<home_dir>/{project}` as
today. Every caller that builds a vault path — plan loading, `render-sprints`, `vault-commit`,
`transition` — takes the resolved value off the context instead of re-deriving it. The resolver
also reports whether the result sits inside the repo working tree, which the project-context
partial exposes to skill templates as `is_local_vault`.

## Milestones

### M1: Marker parsing — 6 SP | pending

**Goal**: the `.booping` marker is parsed as YAML and its keys reach the assembled context.

**Verify**: `just test booping-python/tests/test_project.py && just typecheck`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Parse `.booping` as YAML, tolerating the empty legacy marker | `booping-python/src/booping/context/project.py` | 3 | pending |
| 1.2 | Expose the parsed marker keys on the assembled context | `booping-python/src/booping/context/__init__.py` | 3 | pending |

#### Task 1.1 DoD

- [ ] An empty or whitespace-only `.booping` parses to an empty mapping rather than raising.
- [ ] A marker that is not a YAML mapping fails with a message naming the marker path.
- [ ] Unknown keys are preserved, not dropped.
- [ ] `just test booping-python/tests/test_project.py` passes.

**Verify**: `just test booping-python/tests/test_project.py`

#### Task 1.2 DoD

- [ ] `context.marker` carries the parsed mapping, empty when the marker is empty.
- [ ] `booping debug-context` prints it.
- [ ] No caller reads the marker file directly any more.

**Verify**: `bin/booping debug-context | grep -A3 '^marker:'`

---

### M2: Path resolution — 8 SP | pending

**Goal**: the vault path comes from the marker when it names one, and from the home base otherwise.

**Verify**: `just test booping-python/tests/test_vault.py && just typecheck`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Resolve the vault path from the marker | `booping-python/src/booping/context/vault.py` | 5 | pending |
| 2.2 | Fall back to `<home_dir>/{project}` when the marker names no path | `booping-python/src/booping/context/vault.py`, `booping-python/src/booping/config.py` | 3 | pending |

#### Task 2.1 DoD

- [ ] `resolve_vault()` reads `vault_path:` off the parsed marker; a marker without the key leaves
      the resolution to the fallback.
- [ ] A non-string `vault_path:` fails with a message naming the marker path and the offending
      value.
- [ ] A relative value resolves against the repo root, not the process cwd — asserted by a test
      that runs the resolver from a subdirectory.
- [ ] An absolute value is honoured as given, and a leading `~` expands to the user's home.
- [ ] A resolved path outside the repo working tree still resolves, and is not reported as local.
- [ ] `just test booping-python/tests/test_vault.py` passes.

**Verify**: `just test booping-python/tests/test_vault.py`

#### Task 2.2 DoD

- [ ] With no `vault_path:` the resolver returns `<home_dir>/{project}`, `home_dir` coming from the
      core + global config merge.
- [ ] The project config tier cannot influence `home_dir` — asserted by a test.
- [ ] Existing vaults resolve to exactly the path they resolve to today.

**Verify**: `just test booping-python/tests/test_vault.py::test_default_home_fallback`

---

### M3: Callers honour the override — 8 SP | pending

**Goal**: no command re-derives a vault path; every one of them reads the resolved value.

**Verify**: `just test && rg -n 'home_dir' booping-python/src/booping/commands/`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Route sprint rendering and vault commits through the resolved vault | `booping-python/src/booping/commands/render_sprints.py`, `booping-python/src/booping/commands/vault_commit.py` | 4 | pending |
| 3.2 | Route plan loading and `transition` through the resolved vault | `booping-python/src/booping/context/plan.py`, `booping-python/src/booping/commands/transition.py` | 4 | pending |

#### Task 3.1 DoD

- [ ] `render-sprints` writes `sprints.md` into the resolved vault, local or default.
- [ ] `vault-commit` stages against the git repo owning the resolved vault — the repo itself when
      the vault is local.
- [ ] Neither command builds a path from `home_dir` any more.

**Verify**: `just test booping-python/tests/test_render_sprints.py booping-python/tests/test_vault_commit.py`

#### Task 3.2 DoD

- [ ] `context.plans` loads from the resolved vault's `plans/`.
- [ ] `booping transition` finds a plan by path relative to the resolved vault.
- [ ] A local vault's plans appear in `sprints.md` in the same order as a default vault's.

**Verify**: `just test booping-python/tests/test_transition.py`

---

### M4: Scaffolding — 8 SP | pending

**Goal**: `booping-create-project` can scaffold a repo-local vault, and skills know they are on one.

**Verify**: `bin/booping-create-project demo --local` in a scratch repo, then `bin/booping debug-context`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Scaffold a repo-local vault | `bin/booping-create-project` | 5 | pending |
| 4.2 | Expose `is_local_vault` to skill templates | `src/templates/_partials/_project_context.j2`, `booping-python/src/booping/context/__init__.py` | 3 | pending |

#### Task 4.1 DoD

- [ ] `--local [dir]` takes an optional directory and defaults to `./booping`.
- [ ] The scaffolded vault carries the same directory set as the default mode — `plans/`,
      `lessons/`, `notes/`, `_booping/`.
- [ ] The repo's `.booping` marker gains a `vault_path:` key pointing at the scaffolded directory,
      relative to the repo root, without clobbering keys already in the marker.
- [ ] The scaffolded vault carries a `.gitignore` ignoring `_runs/` and `_booping/.booping.log`.
- [ ] Running it twice is refused rather than overwriting an existing vault.

**Verify**: `bin/booping-create-project demo --local` in a scratch repo, then `bin/booping debug-context | grep vault`

#### Task 4.2 DoD

- [ ] `context.is_local_vault` is true exactly when the resolved vault sits inside the repo working
      tree.
- [ ] `_project_context.j2` renders it, and every skill rendering that partial sees it.
- [ ] `bin/booping render src/templates/skills/groom.md.j2` shows the local-vault branch offer only
      when it is true.

**Verify**: `just test booping-python/tests/test_context.py && bin/booping render src/templates/skills/groom.md.j2`

---

### M5: Docs and migration notes — 8 SP | pending

**Goal**: the marker key, the flag and the manual move are documented where users look for them.

**Verify**: `just docs` builds clean; the new sections are reachable from the vault page

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Document the marker key and `--local` across the project guide and the docs site | `CLAUDE.md`, `documentation/vault.md`, `documentation/cli.md` | 4 | pending |
| 5.2 | Migration note for existing `~/Claude/{project}` vaults | `documentation/vault.md`, `README.md` | 4 | pending |

#### Task 5.1 DoD

- [ ] `CLAUDE.md`'s vault-layout section names `vault_path:` and its resolution rules.
- [ ] `documentation/vault.md` documents both layouts side by side, with the trade-off stated.
- [ ] `documentation/cli.md` documents `--local [dir]` and its default.
- [ ] `just docs` builds without warnings.

**Verify**: `just docs`

#### Task 5.2 DoD

- [ ] A step-by-step manual move is documented: move the directory, add the marker key, re-run
      `debug-context` to confirm.
- [ ] The note states what is *not* automated and why.
- [ ] `README.md`'s vault paragraph links to it.

**Verify**: `just docs`

## Key Files Reference

| File | Role |
|------|------|
| `booping-python/src/booping/context/vault.py` | the single resolver every caller reads from |
| `booping-python/src/booping/context/project.py` | marker discovery and parsing |
| `bin/booping-create-project` | the only writer of a marker key |
| `src/templates/_partials/_project_context.j2` | how skills learn which layout they are on |

## Final Verification

- [ ] A repo with `vault_path: ./booping` resolves every command against that directory.
- [ ] A repo without the key behaves exactly as before.
- [ ] `just test` — all tests pass.
- [ ] `just lint && just typecheck` — clean.

## Out of scope

- Moving or copying an existing vault, in either direction.
- Any change to what a vault contains or how plans are named.
- Per-user overrides of a repo's vault location.

## CLAUDE.md impact

| Section | Change | Owning task |
|---------|--------|-------------|
| `## Project vault layout` | document `vault_path:` and its resolution rules | M5.1 |
| `## CLI` | document `--local [dir]` on `booping-create-project` | M5.1 |
</file>
