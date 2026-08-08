---
title: Local Vault Directories
type: feature
status: done
sp: 17
split_from: null
created: 2026-06-28 00:00
planned: null
started: 20260628 15:17
completed: 2026-06-28 15:33
retro: retrospectives/20260722-seven-plan-retro.md
goal: success|partial|fail
summary: Optional local in-repo vault via .booping vault_path key, prompted at 
  install, resolved everywhere, with groom branch-offer
commit: 2b7bef215f068d9ec996eadb8d87a1ff9254110f
---

# Local Vault Directories

# Plan Body

## Context

Today the booping vault is always `~/Claude/{project}/` — hardcoded at
`booping-python/src/booping/context/project.py:28` in `Project.load_cwd`. The
`.booping` marker carries one key, `project_name:`. Every CLI consumer
(`render`, `render-sprints`, `transition`, `frontmatter-update`, `vault-commit`,
`debug-context`) obtains the vault root through `project.directory`, so the
single resolution point governs all of them.

**Gap**: a user cannot keep plans/lessons/retros *inside the code repo*. The
global `~/Claude` location is invisible in the repo, not shared via the code
remote, and not version-controlled alongside the code it plans.

**Change after**: the `.booping` marker gains an optional `vault_path:` key. When
present, the vault resolves relative to the repo root (absolute paths allowed);
when absent, behavior is unchanged (`~/Claude/{name}`). `/install` prompts for
the location and writes the key. With the chosen **track-in-code-repo** strategy,
`vault-commit` commits plan files into the code repo working tree — which forces a
correctness fix: scope its `git commit` to the plan pathspec so it never sweeps
pre-staged code into a plan commit.

## Decisions

- **Marker shape**: stay YAML, add optional `vault_path:` — back-compat (absent =
  `~/Claude/{name}`); existing markers load unchanged. Locked content:
  ```yaml
  project_name: <name>
  vault_path: ./booping   # optional. relative → resolved against repo root;
                          # absolute allowed; absent → ~/Claude/{name}
  ```
- **Resolution**: `vault_path` resolved against `repo_directory` (the dir holding
  `.booping`), with `~` expansion. Relative is the headline case; absolute is
  permitted but the user owns its git context. — keeps one resolution point.
- **Git strategy = track in code repo**: plans live inside the code repo and are
  committed by `vault-commit` into that repo. No nested repo, no separate vault
  git. — plans shipped with code, shared via the code remote.
- **vault-commit scoping**: scope both the `git status` precheck and the
  `git commit` to the staged plan pathspec (`-- <paths>`). — in the shared repo a
  bare `git commit -m` would commit any unrelated pre-staged code; scoping makes
  the *same* code path correct for both the legacy separate-vault repo and the new
  shared repo. — single code path, no `vault_path`-conditional branching in
  vault-commit.
- **Default location prompt**: `/install` offers `~/Claude/{name}` (default) vs a
  local dir; local default name is `./booping/`, user may rename. — matches the
  requested UX.
- **No migration**: moving an existing `~/Claude` vault to local is manual (move
  files + add `vault_path:`). — out of scope; keeps the sprint bounded.
- **Branch-offer on local vault**: with track-in-repo, groom's first plan-committing
  transition lands the plan on the current branch — on `main` that pollutes the
  default branch. Groom **always offers** (local vault only) to create/switch to a
  branch before that first commit. Default name derived from `git.branches` by plan
  type (e.g. `feat/<plan-slug>`), so `/develop` reuses the same branch — no second
  branch. User may keep the current branch. — fixes the cleanup-on-master problem.

## Architecture

`Project.load_cwd` is the sole resolution point; once it returns the right
`directory`, all consumers follow (`render`, `render-sprints`, `transition`,
`frontmatter-update`, `debug-context`, `Context.assemble` config/lessons/templates
loading, and `logger.log`'s `vault/_booping` log dir — researcher-confirmed they
all read `project.directory`). `vault_commit.resolve_vault` independently calls
`Project.load_cwd` first, so it inherits the new resolution automatically; its only
change is pathspec scoping.

`@head` interpolation reads HEAD from `repo_directory` (code repo) — unaffected.
The per-project config override `vault/config.yaml` follows `vault` automatically —
unaffected.

**Local-vault signal**: a `Project.is_local_vault` property (vault `directory` is
under `repo_directory`) is the gate for the groom branch-offer and any future
local-vault-only behavior. Exposed through `_project_context.j2` so skill templates
can branch on it. The branch name reuses the `git.branches` config already consumed
by `/develop`'s branch selection — so a groom-created `feat/<slug>` is exactly what
`/develop` would have picked, and `/develop` lands on it without creating a second
branch.

Callers of the marker writer: `bin/booping-create-project` (new mode) and the
`/install` skill (writes marker directly in attach mode, delegates to
create-project in new mode) — both must learn to write `vault_path:`.

## Milestones

### M1: Vault resolution + marker `vault_path` — 3 SP | pending

**Goal**: `Project.load_cwd` resolves a local vault when the marker carries
`vault_path:`, and is unchanged when it doesn't.

**Verify**:
```bash
cd booping-python && uv run pytest tests/context/project_test.py -q
```
plus a manual smoke:
```bash
# in a tmp repo with `.booping` containing `vault_path: ./booping`
booping debug-context | grep -A2 'project:' | grep directory
# -> directory: <repo>/booping
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Read `vault_path` from marker in `load_cwd`; resolve against `repo_directory` (`candidate`) with `~` expansion; absolute kept as-is; absent → `~/Claude/{name}`. | `booping-python/src/booping/context/project.py` | 2 | pending |
| 1.2 | Tests: local relative `vault_path` → `<repo>/booping`; absolute `vault_path` → as-is; absent → `~/Claude/{name}` (existing assertion preserved); `~`-prefixed path expands. | `booping-python/tests/context/project_test.py` | 1 | pending |

#### Task 1.1 DoD

- [ ] `data.get("vault_path")` truthy → `directory` resolves relative to
      `candidate` (repo root) when relative, used as-is when absolute, `~` expanded.
- [ ] Falsy / missing `vault_path` → `Path.home() / "Claude" / project_name`
      (byte-for-byte current behavior).
- [ ] Returned `directory` is normalized (`.resolve()` on the relative branch).
- [ ] No other field of `Project` changes.

#### Task 1.2 DoD

- [ ] Fixture/marker with `vault_path: ./booping` asserts `directory ==
      repo_dir / "booping"`.
- [ ] Absolute `vault_path` asserts `directory` equals that absolute path.
- [ ] Existing `directory == ~/Claude/<name>` assertion (`project_test.py:16`)
      still passes for markers without `vault_path`.
- [ ] `~`-prefixed `vault_path` expands to home-rooted path.

---

### M2: Scope `vault-commit` to its pathspec — 3 SP | pending

**Goal**: `vault-commit` commits only the plan + sprints.md (+ `--also`) paths,
never unrelated pre-staged code in the shared repo, while staying correct for a
separate vault repo.

**Verify**:
```bash
cd booping-python && uv run pytest tests/commands/vault_commit_test.py -q
```
plus a manual shared-repo smoke: in a repo with a local vault, `git add` an
unrelated code file, run a transition, confirm `git log -1 --name-only` shows only
the plan/sprints paths and the code file is still staged (`git status`).

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Reuse the EXISTING `rel_paths` list (`_rel(vault, path)`, vault-relative; already built and `git add`-staged at `vault_commit.py:93-102` — keep that `git add` unchanged). Pass `rel_paths` as a pathspec to the precheck and commit: `_git(vault, ["status", "--porcelain", "--", *rel_paths])` and `_git(vault, ["commit", "-m", msg, "--", *rel_paths])`. cwd stays `vault`, so vault-relative paths resolve correctly. | `booping-python/src/booping/commands/vault_commit.py` | 2 | pending |
| 2.2 | Tests: shared repo with an unrelated pre-staged file → commit contains only plan/sprints paths, unrelated file remains staged; existing separate-vault tests still green; local-subdir vault resolves + commits via `resolve_vault`. | `booping-python/tests/commands/vault_commit_test.py` | 1 | pending |

#### Task 2.1 DoD

- [ ] `git status --porcelain` precheck is pathspec-scoped to `rel_paths`; the
      "nothing to commit" guard fires correctly when only the plan paths are clean
      even if unrelated changes are staged.
- [ ] `git commit` is pathspec-scoped (`-- <rel_paths>`); a pre-staged unrelated
      file is NOT included in the commit and remains in the index afterward.
- [ ] A brand-new (previously untracked) plan/`--also` file commits cleanly under
      the scoped pathspec — the retained `git add -- <rel_paths>` stages it first, so
      `git commit -- <rel_paths>` includes it without error.
- [ ] Behavior in a dedicated separate-vault repo is unchanged (all current
      `vault_commit_test.py` assertions pass).

#### Task 2.2 DoD

- [ ] New test: shared repo, unrelated file `git add`ed → after `do_vault_commit`,
      `git log -1 --name-only` lists only plan + sprints paths; `git diff --cached
      --name-only` still lists the unrelated file.
- [ ] New test: vault is a `plans/`-bearing subdir of the repo → `resolve_vault`
      (via `Project.load_cwd`) returns the subdir and commit succeeds.
- [ ] All pre-existing tests in the file pass.

---

### M3: `booping-create-project` local scaffolding — 2 SP | pending

**Goal**: `booping-create-project` can scaffold the vault inside the repo and
write `vault_path:` into the marker.

**Verify**:
```bash
# in a tmp repo
booping-create-project demo --local ./booping
test -d ./booping/plans && grep -q 'vault_path: ./booping' .booping && echo OK
```
(exact flag/arg shape per I/O contract below)

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | `booping-create-project` is a **Bash script** (`set -euo pipefail`, positional `<name> [cwd]`, no argparse) — add the flag with bash arg handling, not Python. Add a local-vault mode: scaffold `{plans,retrospectives,lessons,_booping,notes}` under a repo-relative dir, append `vault_path: <dir>` to the written marker, and write a `.gitignore` inside the vault dir ignoring `_booping/*.log`. Default local dir `./booping`. Preserve current `~/Claude/$PROJECT` default path when local mode is not requested. | `bin/booping-create-project` | 2 | pending |

#### Task 3.1 DoD

- [ ] Flag parsing added with bash idioms; existing positional `<name> [cwd]` and
      the absolute-path smoketest form still parse correctly.
- [ ] Local mode scaffolds the five subdirs under the repo-relative dir.
- [ ] Marker written with both `project_name:` and `vault_path:` lines in local
      mode; `vault_path:` omitted in the default (`~/Claude`) mode.
- [ ] Local mode writes `<vault>/.gitignore` ignoring `_booping/*.log` so the
      append-only log never pollutes `git status` in track-in-repo mode.
- [ ] Default `~/Claude/$PROJECT` path + existing absolute-path smoketest form
      unchanged.
- [ ] `--help`/usage text documents the local-vault flag.
- [ ] Refuses (exit ≠ 0, stderr message) when the target local dir already exists,
      matching the existing `~/Claude` already-exists guard.

---

### M4: `/install` prompts for vault location — 3 SP | pending

**Goal**: `/install` asks where to keep the vault and wires the choice through both
new and attach modes.

**Verify**:
```bash
bin/booping render src/templates/skills/install.md.j2   # renders cleanly
just build && git diff --quiet -- skills/install/SKILL.md || echo "rebuilt"
```
then a manual `/install` dry read confirming the new prompt + both write paths.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Add a vault-location `AskUserQuestion` step (default `~/Claude/{name}`; local default `./booping`, user-renamable). Wire: new mode → pass local dir to `booping-create-project`; attach mode → write `vault_path:` into the marker the skill authors. | `src/templates/skills/install.md.j2` | 2 | pending |
| 4.2 | `just build` to materialize `skills/install/SKILL.md`; confirm the only diff is the intended one. | `skills/install/SKILL.md` (artefact) | 1 | pending |

#### Task 4.1 DoD

- [ ] Install offers location choice; default keeps current `~/Claude/{name}`
      behavior with no extra marker key.
- [ ] Local choice: new mode delegates the local dir to `booping-create-project`
      (M3 flag); attach mode writes `project_name:` + `vault_path:` to `.booping`.
- [ ] Phase 5 verification (`booping render-sprints`) resolves the chosen vault.
- [ ] `bin/booping render src/templates/skills/install.md.j2` renders without error.
- [ ] New prompt block passes the four-check IA pass (lesson 0004): the location
      prompt sits at the right phase (Scoping), is not duplicated across new/attach
      branches beyond the path value (Duplication), and the local-default name is the
      single tunable knob (Configurability/Hierarchy).

#### Task 4.2 DoD

- [ ] `just build` run; `git diff -- skills/install/SKILL.md` shows only the
      intended change; no other artefact drifts.

---

### M5: Reference + docs cleanup — 2 SP | pending

**Goal**: every doc/reference that implies the vault is *always* `~/Claude/{project}`
acknowledges the configurable local option. (Lesson 0005 — in-sprint, not a sweep.)

**Verify**:
```bash
grep -rn 'vault_path' CLAUDE.md documentation/ && echo "documented"
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Update `CLAUDE.md`: vault layout intro + `.booping` marker description + create-project CLI entry note the optional `vault_path:` and local-vault resolution; Skill-design/groom note records the branch-offer step + groom's new `Bash(git:*)` allowance + `_project_context.j2` exposing `is_local_vault`. | `CLAUDE.md` | 1 | pending |
| 5.2 | Update user-facing docs that describe install / vault location to mention the local option. | `documentation/*.md` (install/getting-started pages that name `~/Claude`) | 1 | pending |

#### Task 5.1 DoD

- [ ] `## Project vault layout` intro states the vault path is `~/Claude/{project}`
      by default OR a repo-local dir via `.booping` `vault_path:`.
- [ ] `.booping` marker + `booping-create-project` descriptions mention `vault_path:`.
- [ ] No remaining CLAUDE.md prose asserts the vault is *only* `~/Claude/{project}`.

#### Task 5.2 DoD

- [ ] The doc page(s) describing install / where plans live mention the local-vault
      choice and the `vault_path:` marker key.
- [ ] No broken internal links introduced.

---

### M6: Groom branch-offer on local vault — 4 SP | pending

**Goal**: with a local vault, groom offers to create/switch to a branch (default
derived from `git.branches` by plan type) before the first plan-committing
transition, so the plan never lands on the default branch unintentionally.

**Verify**:
```bash
cd booping-python && uv run pytest tests/context/project_test.py -k local_vault -q
bin/booping render src/templates/skills/groom.md.j2 | grep -i branch   # branch-offer step present
just build && git diff --stat -- skills/groom/SKILL.md
```
plus a manual dry read of the rendered groom skill confirming the conditional step
and that `git.branches` drives the default name.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Add `Project.is_local_vault` (true when `directory` resolves under `repo_directory`); expose it through `_project_context.j2` so skill templates can gate on it. Test both branches. | `booping-python/src/booping/context/project.py`, `src/templates/_partials/_project_context.j2`, `booping-python/tests/context/project_test.py` | 2 | pending |
| 6.2 | Groom runtime template: add a conditional branch-offer step (gated on `is_local_vault`) that runs **before** the first plan-committing transition — derive the default branch name from `git.branches` matched to the plan's `type` + plan slug, offer it (user may keep the current branch), and `git switch -c <name>` / `git switch <name>` on accept. Add `Bash(git:*)` to groom's `allowed-tools` in the build shell; `just build`. | `src/templates/skills/groom.md.j2`, `src/files/skills/groom/SKILL.md.j2`, `skills/groom/SKILL.md` (artefact) | 2 | pending |

#### Task 6.1 DoD

- [ ] `is_local_vault` returns `True` when the vault is under the repo, `False` for
      a `~/Claude` vault — covered by tests for both.
- [ ] `_project_context.j2` exposes the flag (rendered into skill bodies that gate
      on it); default-vault renders unchanged.
- [ ] No change to `Project`'s existing fields or their serialization.

#### Task 6.2 DoD

- [ ] Branch-offer step renders only when `is_local_vault` is true; remote-vault
      groom body is unchanged.
- [ ] Default branch name = `git.branches` prefix matched to the plan `type` +
      kebab plan slug (e.g. `feat/local-vault-directories`); user can decline and
      keep the current branch.
- [ ] Step sits before the first `booping transition` that commits the plan.
- [ ] `git switch -c <name>` (new) / `git switch <name>` (existing) executed on
      accept; groom `allowed-tools` includes `Bash(git:*)`.
- [ ] `just build` run; `git diff -- skills/groom/SKILL.md` shows only the intended
      change.

---

## I/O contract

**`.booping` marker (read by `Project.load_cwd`)**
- `project_name: <str>` — unchanged.
- `vault_path: <path>` — optional. Relative → resolved against repo root; absolute
  → used as-is; `~` expanded. Absent → `~/Claude/{project_name}`.

**`booping-create-project <name> [--local <dir>]`** (exact flag name finalized in M3)
- stdout: progress lines (`Initialized: <root>`, `Wrote marker: ...`).
- stderr + exit ≠ 0: target dir already exists; missing args.
- Exit `0` success.

**`vault-commit`** — I/O unchanged; only the internal git pathspec scoping changes.
stdout = commit message; stderr + exit `2` on git failure; exit `0` / nothing-to-commit
message on a clean pathspec.

## Final Verification

- [ ] `just lint && just typecheck && just test` green.
- [ ] `project_test.py` + `vault_commit_test.py` cover local + back-compat paths.
- [ ] `/install` renders and offers the location prompt; both modes write the
      correct marker.
- [ ] Manual: a repo with `vault_path: ./booping` runs a full transition
      (`booping transition` from a real status edge) and the plan + sprints.md land
      as a scoped commit in the code repo, leaving any unrelated staged file alone.
- [ ] Manual: groom on a local-vault repo offers a `feat/<slug>` branch and the
      plan's first commit lands there, not on the default branch.
- [ ] `just build` leaves no unintended drift under `skills/`.

## Out of scope

- Migrating an existing `~/Claude` vault to local (manual move + add `vault_path:`).
- Nested/separate git repo for a local vault (strategy is track-in-code-repo).
- Auto-managing the *host repo's* root `.gitignore` (M3 writes a vault-local
  `.gitignore` for `_booping/*.log`; touching the repo-root file is out of scope).
- Branch-offer in `/chat` or `/develop`. `/develop` already selects/creates its
  branch from `git.branches`; since groom's default name matches, `/develop` reuses
  it. `/chat` plan-committing chores keep the current branch — not addressed here.
- A global base-path config tier (`~/Claude/config.yaml`) — separate future work.

## CLAUDE.md impact

- `## Project vault layout (~/Claude/{project}/)` — note the configurable local path.
- `.booping` marker + `bin/booping-create-project` descriptions — add `vault_path:`.
- `## Skill design` / groom notes — record the local-vault branch-offer step and
  groom's new `Bash(git:*)` allowance; `_project_context.j2` now exposes
  `is_local_vault`.
- No status/transition changes → README Statuses section untouched.

---

# Quality Checklist

## Frontmatter

- [x] Frontmatter matches plan frontmatter shape.
- [x] `sp` (17) equals the sum of per-task SP (2+1 + 2+1 + 2 + 2+1 + 1+1 + 2+2).

## Content

- [x] Context names the user-visible behavior change (local vault via `vault_path:`).
- [x] DoD bullets verifiable by invocation + output/test.
- [x] Every task lists exact files.
- [x] Every task DoD uses checkboxes.
- [x] Every milestone has a `Verify` invocation.
- [x] Each milestone executable from a fresh session with only the plan as context.

## I/O contract

- [x] Marker key + create-project flag shapes enumerated.
- [x] stdout/stderr/exit codes specified for the changed CLI surfaces.

## Anti-patterns (must be absent)

- [x] No "TBD"/"TODO"/"later".
- [x] No task spanning unrelated concerns.
- [x] No "add a command for X" without argument shape.
- [x] No silent failures — error paths carry exit code + stderr.

## External references validated

- [x] No new package dependencies introduced.
- [x] Shell-out commands (`git`) already in use on supported platforms.

## CLAUDE.md impact

- [x] M5 enumerates the CLAUDE.md + docs updates as in-sprint tasks.
