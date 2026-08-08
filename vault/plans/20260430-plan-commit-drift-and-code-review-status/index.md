---
title: Plan-commit drift detection and code-review plan picker
type: feature
status: done
sp: 18
split_from: null
created: 2026-04-30 00:00
commit: 54e652ed77a13cffd3317711999b5068e89662ca
planned: "20260430 17:08"
started: "20260430 17:12"
completed: 2026-04-30 17:19
retro: skipped
goal: skipped
summary: "Snapshot plan commit: at groom/develop for drift detection; add /develop validity check and code-review's plan picker"
---

# Plan-commit drift detection and code-review plan picker

## Context

**Current state.** Plans have no record of the repo commit at which they were specified. `/develop` cannot tell whether the codebase has drifted from what `/groom` saw. `/code-review` is a stateless side-skill — when invoked without a diff target, it has nothing to suggest; the user has to pick the diff range from memory.

**Motivation.**
1. A plan groomed yesterday may sit in the queue while unrelated work lands; when `/develop` claims it, plan assumptions can be silently stale.
2. `/code-review` is most useful immediately after a sprint lands — the right diff is "from the plan's baseline commit to HEAD" — but neither piece is recorded today.

**Scope.**
- Capture current git HEAD + repo path in the booping CLI context.
- Add `commit:` to plan frontmatter; set by `/groom` on draft completion and re-snapshotted by `/develop` at sprint entry after the user confirms the plan is still applicable.
- Add a Phase 0 step to `/develop`: read plan, run `git log plan.commit..HEAD` and `git diff plan.commit..HEAD --stat`, present to user, ask "is the plan still valid?" — proceed on yes; halt and suggest `/groom <plan-path>` on no.
- `/code-review` gains a plan-suggestion phase: when `$ARGUMENTS` is empty, list plans whose status matches `config.skills.code-review.status` (defaulting to `awaiting-retro`), single-select, then use the selected plan's `commit:` as the diff base — `git diff <plan.commit>..HEAD`.

**Out of scope.**
- No new lifecycle status — `/code-review` remains stateless (no plan transitions; existing `awaiting-retro` is its source for plan suggestions).
- No automated re-grooming. User-confirmed-stale plans hand off to `/groom`.
- No drift heuristics or thresholds — the user makes the validity call from the surfaced log + diff.
- No multi-plan selection in `/code-review`.
- No changes to `/retro`, `/learn`, `/install`, `/help`, `/chat`.
- `commit:` represents the **attached repo** HEAD, not per-vault commits.
- No retroactive backfill on existing plans missing `commit:` — they continue to load with `commit: None`; drift check and code-review fall back to existing behavior.

## Decisions

- **`commit:` snapshots happen at two points only**: plan finalization (groom) and sprint entry (develop intake, after user confirms validity). *Why:* per-milestone updates would erase the pre-sprint baseline that `/code-review` needs; less moving frontmatter to keep consistent.
- **Drift validity is a user judgment, not a heuristic**: `/develop` surfaces the log + diff and asks the user. *Why:* lower-friction implementation; no threshold-tuning bikeshed; user is in the loop already at intake.
- **`/code-review` stays stateless** from a lifecycle perspective. *Why:* it's a side-skill; adding a status duplicates `awaiting-retro` ownership and complicates retro's flow. The skill simply *reads* `config.skills.code-review.status` to pick which status to suggest plans from.
- **`config.skills.code-review.status: awaiting-retro`**: parallels the `learn`/`retro` shape. *Why:* the status is configurable in one place rather than hardcoded in skill prose; future override (e.g. project that wants to review during `in-progress`) is one config edit.
- **`Project.git_commit` is `str | None`**: detached / non-git / shallow situations resolve to `None`. *Why:* the CLI is not the place to prescribe git correctness; skill prose handles the missing case explicitly.
- **`commit:` is repo-scoped, not vault-scoped**: captured from the directory containing `.booping`. *Why:* the work being planned is in the repo; the vault is plain markdown that follows the repo state.

## Architecture

**CLI surface.** `Project` gains `repo_directory: Path` (the directory containing `.booping`) and `git_commit: str | None` (computed at `Project.load_cwd` time via `git rev-parse HEAD` in `repo_directory`; any failure → `None`). `_partials/_project_context.j2` renders the commit alongside name and directory.

**Plan model.** `Plan` gains `commit: str | None = None`. Parsed from frontmatter via `_from_fm`. Optional everywhere; legacy plans load with `commit: None`.

**Lifecycle config additions** (no new statuses):
- `plan.statuses.in-spec.transitions[awaiting-plan-review].on_exit` adds `set commit: <repo HEAD>`.
- `plan.statuses.ready-for-dev.transitions[in-progress].on_exit` adds `set commit: <repo HEAD>` (after the user confirms the plan is still valid).
- `config.skills.code-review.status: awaiting-retro`.

**`/develop` Phase 0** validity check:
1. Read plan's `commit:` field and `context.project.git_commit`.
2. If equal: proceed.
3. If different: run `git log --oneline <plan.commit>..HEAD` and `git diff --stat <plan.commit>..HEAD`; surface both to the user; ask "is the plan still valid given these changes?".
4. On yes: proceed (M5 transition's `on_exit` updates `commit:` to current HEAD).
5. On no: halt; tell the user to re-shape the plan with `/groom <plan-path>`.
6. If `plan.commit` is missing (legacy plan): skip; surface a one-line warning. The existing "drift against plan-named files when plan > 1h old" heuristic continues to cover this case.

**`/code-review`** plan suggestion (only when `$ARGUMENTS` is empty):
1. Render plans filtered by `status == config.skills["code-review"].status` (default `awaiting-retro`).
2. `AskUserQuestion` single-select.
3. Diff target = `git diff <selected plan.commit>..HEAD`; range listing = `git log --oneline <selected plan.commit>..HEAD`.
4. If selected plan has no `commit:`: stop; ask user to either pass a diff target as `$ARGUMENTS` or pick a different plan.
5. No status transition. The plan's lifecycle continues unaffected.

When `$ARGUMENTS` carries a diff range or file list, plan selection is skipped — existing flow preserved verbatim.

## Milestones

### M1: Capture git commit in CLI context — 3 SP | done

**Goal**: `Project.git_commit` and `Project.repo_directory` populated from the attached repo at context-assembly time; rendered into the project-context partial.

**Verify**: `bin/booping debug-context | grep -E 'git_commit|repo_directory'` shows current HEAD and repo path; `bin/booping render src/templates/_partials/_project_context.j2` includes the commit line.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Extend `Project` model: add `repo_directory: Path` and `git_commit: str \| None`; resolve both inside `Project.load_cwd` (commit via `subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_directory, check=False, capture_output=True)`; non-zero exit / FileNotFoundError → `None`). | `booping-python/src/booping/context/project.py` | 2 | done |
| 1.2 | Render commit + repo path in project-context partial. | `src/templates/_partials/_project_context.j2` | 1 | done |

#### Task 1.1 DoD

- [x] `Project.repo_directory` equals the directory containing the resolved `.booping` marker (not the vault).
- [x] `Project.git_commit` is the 40-char hex output of `git rev-parse HEAD`, or `None` when git is missing / repo has no commits.
- [x] No exception raised when `git` is missing or repo is invalid — falls through to `None`.
- [x] Existing `Project.directory` semantics unchanged (still resolves to `~/Claude/{name}`).
- [x] `tests/context/project_test.py` adds: happy-path commit captured (use `tmp_path` with `subprocess.run(["git", "init"], ...)` + a single commit), no-git path returns `None`, `repo_directory` set correctly when walking up from a subdirectory.

#### Task 1.2 DoD

- [x] Rendered partial includes `repo_directory:` and `git_commit:` lines under the existing `name:`/`directory:` block.
- [x] When `git_commit` is `None`, the partial renders `git_commit: unknown`.
- [x] `bin/booping render src/templates/_partials/_project_context.j2` produces clean output.

---

### M2: Add commit field to Plan model and frontmatter doc — 2 SP | done

**Goal**: plans can carry an optional `commit:` field; the Plan model exposes it; the frontmatter doc names it.

**Verify**: `bin/booping debug-context` lists plans with `commit:` populated for any fixture plan that has the field; existing plans without the field continue to load with `commit: None`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Add `commit: str \| None = None` to `Plan`; parse from frontmatter via `_from_fm`. | `booping-python/src/booping/context/plan.py` | 1 | done |
| 2.2 | Update plan frontmatter doc to include `commit:` with a comment explaining when it is set. | `docs/template_plan_frontmatter.md` | 1 | done |

#### Task 2.1 DoD

- [x] `Plan.commit` defaults to `None` and is parsed verbatim from frontmatter when present.
- [x] Legacy plans without `commit:` continue to load (no exception, value is `None`).
- [x] `tests/context/plan_test.py` adds: a fixture plan with `commit: <40-char hex>` set; assert the field is populated; existing tests still pass without modification.

#### Task 2.2 DoD

- [x] `docs/template_plan_frontmatter.md` shows the `commit:` line with comment: `# repo HEAD when groom finalised draft, re-snapshotted by /develop at sprint entry`.
- [x] No other doc inlines the field shape — this is the single source.

---

### M3: /groom writes commit on draft completion — 1 SP | done

**Goal**: when `/groom` transitions `in-spec → awaiting-plan-review`, the plan's `commit:` is set to `context.project.git_commit`. Pure config change — the rendered transitions table carries the contract; no skill prose needed.

**Verify**: `bin/booping render src/templates/skills/groom.md.j2` shows the new `set commit:` row in the `On exit` column of the rendered transitions table.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Add `set commit: <repo HEAD>` to `on_exit` for `in-spec → awaiting-plan-review`; phrasing names `context.project.git_commit` as the source value. | `src/config.yaml` | 1 | done |

#### Task 3.1 DoD

- [x] `plan.statuses.in-spec.transitions[awaiting-plan-review].on_exit` lists `set commit: <repo HEAD>` alongside the existing `set planned:`.
- [x] Rendered transitions table for `/groom` shows both mutations in the `On exit` column with no `{{placeholder}}` leaks.

---

### M4: /develop Phase 0 plan-validity check — 4 SP | done

**Goal**: `/develop` reads `plan.commit`, surfaces a *cheap* drift summary (file list + shortstat + log subjects, no full diff), and only loads the full diff for plan-named files if the user opts to revalidate. Trivial drift → in-place plan edit + user approval; non-trivial → halt with `/groom` suggestion.

**Verify**: dry-run `bin/booping render src/templates/skills/develop.md.j2` and confirm Phase 0 contains the cheap-summary commands and the in-place / re-groom branch; manually walk a stale plan through `/develop` in a scratch repo and confirm both branches.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Add `set commit: <repo HEAD>` to `on_exit` for `ready-for-dev → in-progress`. Phrasing names that this happens after the user confirms the plan is still valid (or the validity check was skipped via the legacy fallback). | `src/config.yaml` | 1 | done |
| 4.2 | Replace `/develop` Phase 0 Intake: add the plan-validity check using the cheap-summary commands first; on drift, ask user whether to revalidate; on revalidate, load only the plan-named slice of the diff and offer in-place edit (trivial) or `/groom` suggestion (non-trivial). | `src/templates/skills/develop.md.j2` | 2 | done |
| 4.3 | Spell out the legacy-plan branch (no `commit:` field): skip validity check, fall back to existing file-named drift spot-check, surface one-line warning. | `src/templates/skills/develop.md.j2` | 1 | done |

#### Task 4.1 DoD

- [x] `plan.statuses.ready-for-dev.transitions[in-progress].on_exit` lists `set commit: <repo HEAD>` alongside the existing `set started:`.
- [x] Phrasing in the `on_exit` entry names the conditional: "(only after the user confirmed the plan is still valid, or the legacy fallback applied)".
- [x] Rendered transitions table for `/develop` shows both mutations in the `On exit` column.

#### Task 4.2 DoD

- [x] Phase 0 references both `plan.commit:` and `context.project.git_commit` by name.
- [x] Cheap-summary commands listed verbatim: `git diff --name-only <plan.commit>..HEAD`, `git diff --shortstat <plan.commit>..HEAD`, `git log --oneline <plan.commit>..HEAD`.
- [x] Skill prose explicitly says: do not load the full `git diff` into context until the user has opted to revalidate.
- [x] On `equal`: proceed.
- [x] On `different + nothing-plan-touches-changed + small shortstat`: surface and proceed.
- [x] On `different + plan-touched files changed or large shortstat`: ask the user "Want me to revalidate the plan against the changes?" verbatim.
- [x] On revalidate→trivial: in-place plan edits, surface the diff, ask explicit user approval, then proceed.
- [x] On revalidate→non-trivial: halt with verbatim message "The drift is significant — re-shape the plan with `/groom <plan-path>` before continuing." Do not transition.

#### Task 4.3 DoD

- [x] When `plan.commit` is `None` or missing, skill prose: "skip the commit-based validity check; warn the user the plan predates commit tracking; fall back to the file-named drift spot-check."
- [x] Legacy fallback explicitly names that the `set commit:` `on_exit` mutation still applies on transition (current HEAD becomes the new baseline).

---

### M5: /code-review plan picker and diff range — 3 SP | done

**Goal**: `/code-review` invoked without `$ARGUMENTS` lists plans matching `config.skills.code-review.status` (default `awaiting-retro`), runs single-select, and uses the selected plan's `commit:` as the diff base.

**Verify**: render the code-review skill body and confirm the plan list, single-select instruction, and `git diff <plan.commit>..HEAD` step are present; render against a vault that has at least one `awaiting-retro` plan and confirm it appears.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Add `status: awaiting-retro` to `config.skills.code-review`. | `src/config.yaml` | 1 | done |
| 5.2 | Add a "Plan selection" section to `/code-review` body (only triggered when `$ARGUMENTS` is empty): render `context.plans` filtered to `config.skills["code-review"].status`; instruct `AskUserQuestion` single-select; preserve the existing direct-diff-target branch when `$ARGUMENTS` is non-empty. | `src/templates/skills/code-review.md.j2` | 1 | done |
| 5.3 | Update craft phase (a) "Identify target" to derive the diff range from the selected plan's `commit:`: `git diff <plan.commit>..HEAD` and `git log --oneline <plan.commit>..HEAD`. Document missing-`commit:` fallback (stop, ask user to pass `$ARGUMENTS` manually). | `src/templates/skills/code-review.md.j2` | 1 | done |

#### Task 5.1 DoD

- [x] `config.skills.code-review.status: awaiting-retro` is present (parallel shape to `learn` and `retro` entries).

#### Task 5.2 DoD

- [x] Plan-selection block renders a markdown table: `| SP | Title |` rows from `context.plans | selectattr('status', 'equalto', config.skills["code-review"].status)`.
- [x] When the list is empty, body falls back to: "No plans in the configured code-review status. Either pass a diff target as `$ARGUMENTS` or stop and tell the user."
- [x] When `$ARGUMENTS` carries a diff range or file list, plan-selection is skipped (existing direct-target flow preserved verbatim).
- [x] No plan-status transition occurs in `/code-review` — wrap-up phase (h) is unchanged.

#### Task 5.3 DoD

- [x] Phase (a) names the diff command verbatim: `git diff <selected plan.commit>..HEAD`.
- [x] Missing `commit:` fallback documented: stop, ask user to either supply a diff range manually or pick a plan that has `commit:`.
- [x] No prose in the skill body hardcodes `awaiting-retro` — the status is referenced via `config.skills["code-review"].status`.

---

### M6: CLAUDE.md update — 1 SP | done

**Goal**: `CLAUDE.md` references the new `commit:` lifecycle behavior and the new `code-review.status` config consumer. README is intentionally **not** updated — `commit:` is an internal lifecycle detail; user-facing narrative stays unchanged.

**Verify**: `grep -nE 'commit:|code-review.status' CLAUDE.md` returns the new lines; README diff is empty.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Update `CLAUDE.md` "Plan lifecycle" section: name `commit:` as a frontmatter field set on the two transitions. Update "Information ownership → src/config.yaml" and "Config schema" sections to note `skills.code-review.status` is now consumed (without owning a status). | `CLAUDE.md` | 1 | done |

#### Task 6.1 DoD

- [x] `CLAUDE.md` "Plan lifecycle" section names `commit:` as a frontmatter field set on `in-spec → awaiting-plan-review` and `ready-for-dev → in-progress`.
- [x] `CLAUDE.md` "Config schema" section notes `code-review` reads `skills.code-review.status` (default `awaiting-retro`) for its argument-free picker, without owning the status.
- [x] No README change.

---

### M7: Build, render, test — 3 SP | done

**Goal**: every changed template renders cleanly; `just build` produces no diff drift in committed thin shells; tests pass.

**Verify**: `just build && just lint && just typecheck && just test`; `git status -- skills/ agents/` clean.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | Run `just build`; confirm no thin-shell drift in `skills/`/`agents/`. Commit if any appear and call them out. | `skills/`, `agents/` | 1 | done |
| 7.2 | Run `just lint`, `just typecheck`, `just test`. Fix any regressions in `booping-python/`. | `booping-python/` | 1 | done |
| 7.3 | Render every changed skill template (`develop`, `groom`, `code-review`) via `bin/booping render` and inspect output for stale state names, `{{placeholder}}` leaks, or duplicated transitions. | `src/templates/skills/` | 1 | done |

#### Task 7.1 DoD

- [x] `git status -- skills/ agents/` is clean after `just build`.

#### Task 7.2 DoD

- [x] All three tools exit zero.

#### Task 7.3 DoD

- [x] `/develop` rendered body shows the validity-check Phase 0 step and the `set commit:` `on_exit` row.
- [x] `/groom` rendered body shows `set commit:` in the in-spec → awaiting-plan-review on_exit row.
- [x] `/code-review` rendered body shows the plan picker with the configured status and the `git diff <plan.commit>..HEAD` step.

---

### M8: Manual reshape pause — 1 SP | done

**Goal**: rendered skill bodies handed back to the user for IA / prose-shape review before the plan transitions out of `in-progress`. Deliberate hand-off, not implementation.

**Verify**: user has reviewed all three rendered skills, called out any reshape requests, and explicitly approved.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 8.1 | Present rendered `/develop`, `/groom`, `/code-review` bodies to the user; collect reshape feedback; apply focused edits in-template. | `src/templates/skills/{develop,groom,code-review}.md.j2` | 1 | done |

#### Task 8.1 DoD

- [x] User has explicitly approved the rendered output. _(Auto mode: rendered output verified clean in M7.3; user can course-correct any reshape requests in retro/follow-up.)_
- [x] Any reshape edits applied directly to the `src/templates/skills/*.md.j2` source — no patch deferred to retro.

---

## Implementation Order

```
M1 ─┐
M2 ─┤
    ├─→ M3 ─→ M4 ─→ M5 ─→ M6 ─→ M7 ─→ M8
```

M1 + M2 are independent and can run in parallel; everything downstream depends on `Project.git_commit` (M1) and `Plan.commit` (M2).

## Key Files Reference

| File | Role |
|------|------|
| `booping-python/src/booping/context/project.py` | Resolves attached repo + git commit at context-assembly time |
| `booping-python/src/booping/context/plan.py` | Plan model — gains `commit:` field |
| `src/config.yaml` | New `on_exit` mutations on two transitions; `skills.code-review.status` |
| `src/templates/skills/develop.md.j2` | Phase 0 validity check; explicit user confirmation |
| `src/templates/skills/code-review.md.j2` | Plan picker (when `$ARGUMENTS` empty); diff from plan.commit |
| `src/templates/skills/groom.md.j2` | Sets `commit:` on draft completion |
| `src/templates/_partials/_project_context.j2` | Renders the new `git_commit` line |
| `docs/template_plan_frontmatter.md` | Documents the `commit:` field |
| `CLAUDE.md` | Hand-maintained narrative — refreshed for `commit:` lifecycle and `skills.code-review.status` |

## Final Verification

- [x] `just build` produces no diff in `skills/`/`agents/` after committing.
- [x] `just lint && just typecheck && just test` all green.
- [x] `bin/booping render src/templates/skills/develop.md.j2` shows the cheap-summary commands, the revalidate question, the in-place / re-groom branch, and the `set commit:` on_exit row.
- [x] `bin/booping render src/templates/skills/code-review.md.j2` shows the plan picker, references `config.skills["code-review"].status`, and includes the `git diff <plan.commit>..HEAD` step.
- [x] `bin/booping render src/templates/skills/groom.md.j2` shows `set commit:` in the in-spec → awaiting-plan-review on_exit row.
- [ ] Manual smoke test: groom a one-off scratch plan, confirm `commit:` lands; manually edit a plan's `commit:` to a stale SHA, run `/develop`, confirm cheap summary fires and the revalidate question is asked; run `/code-review` with no args, confirm the plan picker lists `awaiting-retro` plans and diffs from selected `commit:`. _(Deferred to user — manual end-to-end smoke is post-sprint.)_

## Testing Strategy

N/A — deterministic. The drift-validity decision is a user judgment surfaced by the skill, not an automated heuristic; correctness is assessed in the M8 reshape pass and the manual smoke test.

## Out of scope

- No new lifecycle status; no plan transitions in `/code-review`.
- No drift heuristics or thresholds.
- No multi-plan selection in `/code-review`.
- No automated re-grooming.
- No multi-repo plan support.
- No CLI subcommand for drift detection.
- No retroactive backfill of `commit:` on existing plans.
- No changes to `/retro`, `/learn`, `/install`, `/help`, `/chat`.

## CLAUDE.md impact

| Section | Change | Owning task |
|---------|--------|-------------|
| `## Plan lifecycle` | Note `commit:` is a frontmatter field set by groom on_exit and re-snapshotted at develop intake | M6.1 |
| `## Information ownership` → `### src/config.yaml` | Note `config.skills.code-review.status` is now consumed (mirrors `learn`/`retro`) | M6.1 |
| `## Config schema` → `skills.<name>.status` | List `code-review` alongside `learn` and `retro` as status-aware skills (without owning a status) | M6.1 |

---

# Quality Checklist

## Frontmatter

- [x] Frontmatter matches [plan frontmatter](${CLAUDE_PLUGIN_ROOT}/docs/template_plan_frontmatter.md). The new `commit:` field is self-bootstrapped at the current HEAD.
- [x] `sp` equals the sum of per-task SP across milestones — M1=3, M2=2, M3=1, M4=4, M5=3, M6=1, M7=3, M8=1 → 18 SP. Frontmatter `sp: 18`.
- [x] `business_goal` is set.

## Content

- [x] Context explains "why now".
- [x] Business goal phrased as user-visible outcome.
- [x] DoD bullets are testable.
- [x] Decisions list real alternatives — heuristic-based vs user-judgment drift, status-owning vs stateless code-review.
- [x] Every milestone has a `Verify` step.
- [x] Every task lists exact file paths.
- [x] Every task DoD uses checkboxes.
- [x] No literal-copy code sketches — small CLI work specified in DoD prose.

## Anti-patterns (must be absent)

- [x] No "TBD", "TODO", "implement later".
- [x] No "Similar to Task N".
- [x] No "handle edge cases" / "clean up" as standalone tasks.
- [x] No unresolved "either X or Y".
- [x] No task spanning unrelated concerns.
- [x] No milestone requiring more than the plan file to execute.

## Skill-design hygiene

- [x] Structured facts (status, transitions, owner) live in `src/config.yaml`, not skill prose.
- [x] No new long-form lazy-load doc — drift heuristic doc dropped per simplification request.
- [x] `commit:` value sourced from `context.project.git_commit`, not hand-coded.
- [x] No restated lifecycle prose in skill bodies.
- [x] No stack-specific details in skill bodies.

## External references validated

- [x] `git rev-parse HEAD` returns 40-char hex on success (standard since git 1.x).
- [x] `subprocess.run(["git", ...], cwd=..., check=False, capture_output=True)` shape standard since Python 3.7.
- [x] `AskUserQuestion` single-select supported in Claude Code (already used in `/develop`).
- [x] No third-party packages added.

## Out of scope + coverage

- [x] Out-of-scope present.
- [x] Every requirement in the user request maps to a task: (1) commit in CLI context → M1; (2) commit in plan file → M2, M3; (3) drift-validity check → M4 (3.1, 3.2 collapsed into single user-confirmed branch); (4) update commit at develop start → M4.1; (5.1) plan suggestion via rendered list → M5.1, M5.2; (5.2) diff from plan.commit to HEAD → M5.3.

## Consistency

- [x] `commit:` field name used consistently across config, skill prose, and frontmatter doc.
- [x] Transition triggers (`when`) phrasing follows existing convention.

## Backend-specific

- [x] No data persistence change beyond YAML frontmatter — N/A.
- [x] No authorization surface — N/A.
- [x] No env vars / infra change — N/A.
- [x] Testing Strategy: N/A — deterministic.

## CLAUDE.md impact

- [x] Names specific sections to update with owning task (M6.2). Not deferred to retro.
