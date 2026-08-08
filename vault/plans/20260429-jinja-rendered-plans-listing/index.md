---
title: Render plans listing via Jinja templates
type: refactoring
status: done
sp: 12
split_from: null
created: 2026-04-29 00:00
planned: 20260429 22:33
started: 20260429 22:33
completed: null
retro: null
goal: null
summary: "Replace stubbed `booping plans` with single-purpose `render-sprints`, rendering sprints.md from context.plans via Jinja"
---

# Render plans listing via Jinja templates

## Context

`booping plans` is the only un-ported subcommand from the runtime-rendering migration (PR #6). Today its CLI stub prints "not implemented" and exits non-zero, which fails every skill that depends on it: `/chat` orient (writes `sprints.md` plus assembles two status-filtered tables), `/install` seeding step, `/develop` plan-selection prompt and post-transition verify, and the shared `_shared_instructions.j2` partial.

Naively porting the deleted `bin/booping-plans` script (TSV output, `--status` / `--columns` / `--sort` / `--format` flags) would re-introduce a parallel data flow: skills would re-shell out to a subprocess to get plan data that `Context.assemble()` already loads into `context.plans` at template-render time. The replacement should instead lean on the runtime context that's already there.

After this lands:

- A new Jinja template at `src/templates/sprints.md.j2` renders the markdown snapshot (header comment + GFM table) from `context.plans`.
- A new subcommand `booping render-sprints` is single-purpose: render that template and write the result to `<vault>/sprints.md` (override path with `--output`, `-` for stdout). No `--status`, `--columns`, `--sort`, `--format` flags. The old `booping plans` stub is removed entirely.
- Skills that needed status-filtered listings (`/chat` orient, `/develop` plan-selection) filter `context.plans` inline in their Jinja bodies. One subprocess call (`booping render-sprints` to refresh `sprints.md`) replaces N (`booping plans --status X` per status).
- Snapshot-regen call sites swap `booping plans --format=md > <vault>/sprints.md` for `booping render-sprints` — no shell pipe.

## Decisions

- **CLI surface — minimal**: `booping render-sprints` takes only `--output PATH` (default `<vault>/sprints.md`; `-` writes stdout). No `--status`, `--columns`, `--sort`, `--format`. Why: every other shape was an artefact of skills shelling out for filtering — that's now in-Jinja, so the CLI is one job.
- **Subcommand name — `render-sprints`**: replaces the never-implemented `booping plans` stub entirely; no `plans` alias kept. Why: the command renders `sprints.md`, so the verb-noun name (`render-sprints`) advertises intent more clearly than `plans` did. Clean break — easier to audit grep results.
- **Template path — `src/templates/sprints.md.j2`**: top-level, not `src/templates/snapshots/`. Why: sprints.md is the only vault snapshot today; reserving a folder for hypothetical siblings is premature.
- **Status filtering moves to skill bodies**: `/chat` orient renders the counts and active-plans tables inline by iterating `context.plans`. `/develop` renders the `ready-for-dev` / `awaiting-plan-review` candidate list inline for the AskUserQuestion call. Why: data flow is consistent — skill render time already has every plan loaded; CLI subprocess for the same data is a duplicate path.
- **No `--project` flag**: project resolution comes from `Context.assemble()` walking up from cwd for `.booping`. Why: matches every other subcommand (`render`, `debug-context`); a vault-by-name flag is YAGNI.
- **Snapshot side-effect direction**: `booping render-sprints` always writes to a file (default `<vault>/sprints.md`). No "stdout by default" mode. Why: the call sites in skills are write-side-effects (refresh the snapshot), so writing to a file by default matches intent. `--output -` is the escape hatch for piping or preview.
- **Reshape pause as final milestone**: per `skill_groom.md` extension. Why: skill / template / partial work surfaces IA issues only after rendering the touched bodies side-by-side; lesson 0004 (four-check IA pass) is easier to apply with rendered output in hand.

## Architecture

### CLI shape

```
booping render-sprints                # writes <vault>/sprints.md from src/templates/sprints.md.j2
booping render-sprints --output PATH  # writes to PATH instead
booping render-sprints --output -     # writes to stdout
```

- **stdin**: none.
- **stdout**: empty on success (file write); rendered template when `--output -`.
- **stderr**: one line summary on success (`wrote N plans to <path>`); error message on failure.
- **Exit codes**: `0` success; `2` no project resolved (no `.booping` walking up from cwd) or template render error.

### Render pipeline

1. `Context.assemble()` (already loads `project`, `plans`, `config`).
2. If `context.project is None`, error to stderr + exit 2.
3. Resolve template path: `<plugin_root>/src/templates/sprints.md.j2`. Render with the standard four-namespace globals (`context`, `config`, `tools`, `kwargs={}`).
4. Resolve output path: `args.output` if set, else `context.project.directory / "sprints.md"`. If output is `-`, write to stdout.
5. Write the rendered string. Print summary to stderr.

### Template (`src/templates/sprints.md.j2`)

Reproduces the on-disk shape `bin/booping-plans --format=md` produced before deletion:

- Header comment line: `<!-- Snapshot generated by booping render-sprints; regenerated by /chat on each orient. Do not hand-edit. -->`
- GFM table with header row, separator row, and one row per `context.plans` entry sorted by `created` descending.
- Columns: `status | sp | title | created | planned | completed | retro | path` (the deleted script's default order).
- Cells escape pipes (`|` → `\\|`) and replace newlines with spaces.

Skills that consume the file read it as plain markdown — no breaking shape change.

### Skill body changes (in-Jinja filtering)

`src/templates/skills/chat.md.j2`:

- Phase 0 Orient prose: replace the shell-pipe block with `booping render-sprints` (single line).
- "**First assistant message** must include two tables" — the **Counts** and **Active plans** tables are rendered inline via Jinja loops over `context.plans` filtered by status, instead of "Use `booping plans --status <s>` to assemble both."

`src/templates/skills/develop.md.j2`:

- Phase 1 plan-selection paragraph: replace the `booping plans --status ready-for-dev` + `--status awaiting-plan-review` shell-call instruction with an inline list rendered from `context.plans` filtered by those statuses (still surfaced via `AskUserQuestion`).
- Phase 4 verify line: replace `verify with booping plans` with `verify by re-reading the plan's frontmatter` (the post-transition status is in the file the skill just edited).

`src/templates/skills/install.md.j2`:

- Seeding step: replace `booping plans --format=md > ~/Claude/{name}/sprints.md` with `booping render-sprints` (writes the same path by default, since the freshly-created vault is the resolved project).

`src/templates/_partials/_shared_instructions.j2`:

- Replace `booping plans --format=md > ~/Claude/{project}/sprints.md` with `booping render-sprints`.

### Stale-reference cleanup

In-sprint per lesson 0005:

- All `booping plans` references (any flag form) inside `src/templates/`, `src/docs/`, `skills/`, `agents/`, `CLAUDE.md`, `README.md` are removed — the subcommand is now `render-sprints`, the bare `plans` name no longer exists.
- `CLAUDE.md` `## CLI` section gains a one-line description of the new `booping render-sprints` shape (replaces the post-M6 generic mention of the never-implemented `booping plans`).

## Milestones

### M1: New `booping render-sprints` command + Jinja template — 4 SP | done

**Goal**: `booping render-sprints` from inside a project repo writes a fresh markdown table to `<vault>/sprints.md`. `--output PATH` and `--output -` honored.

**Verify**: `cd ~/Dev/@A/claude-booping && booping render-sprints && diff -u <(head -3 ~/Claude/claude-booping/sprints.md) <(printf '<!-- Snapshot generated by booping render-sprints; regenerated by /chat on each orient. Do not hand-edit. -->\n| status | sp | title | created | planned | completed | retro | path |\n| --- | --- | --- | --- | --- | --- | --- | --- |\n')` exits 0 (header lines match). `cd booping-python && uv run pytest && uv run ruff check . && uv run basedpyright` all pass.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Author `src/templates/sprints.md.j2` — Jinja template producing the GFM table from `context.plans`. Header comment + header row + separator row + one row per plan, sorted by `created` desc. Cells escape `|` and replace newlines. Empty-plans case still emits header + separator (matches deleted script behaviour for fresh vaults). | `src/templates/sprints.md.j2` | 1 | done |
| 1.2 | Implement `booping render-sprints` command: argparse subcommand with `--output PATH` flag (default `<vault>/sprints.md`, `-` for stdout). Calls `Context.assemble()`, errors with exit 2 if `context.project is None`. Calls `render(template_path=<plugin_root>/src/templates/sprints.md.j2, ...)` (path-anchoring matches `commands/render.py`). Writes to file or stdout. Wire into `cli.py` (remove the `_not_implemented` stub for `plans`; register `render-sprints` as a real subcommand). | `booping-python/src/booping/commands/render_sprints.py`, `booping-python/src/booping/cli.py` | 2 | done |
| 1.3 | Tests: `tests/commands/render_sprints_test.py` against `tests/__fixtures__/vault-full/`. Cover (a) default writes `<vault>/sprints.md` with expected header + at least one data row, (b) `--output -` writes to stdout, (c) `--output <tmp>/x.md` writes to custom path, (d) running outside any `.booping` exits 2. Use `subprocess.run` (matches the existing `tests/commands/render_test.py` pattern). | `booping-python/tests/commands/render_sprints_test.py` | 1 | done |

#### Task 1.1 DoD

- [x] Template renders against `vault-full/` fixture and produces the expected markdown table shape (header comment, header row, separator, ≥1 data row).
- [x] Pipe characters in plan titles are escaped (`|` → `\|`).
- [x] Plans with no `created` date sort to the end (matches deleted script behaviour).
- [x] Empty `context.plans` still emits header comment + header row + separator row (no data rows).

#### Task 1.2 DoD

- [x] `booping render-sprints --help` documents `--output`.
- [x] Default invocation from inside a project repo writes `<vault>/sprints.md`.
- [x] `booping render-sprints --output -` writes the same content to stdout (no file write).
- [x] `booping render-sprints --output <path>` writes to `<path>`, creating parent dirs.
- [x] Invocation from a directory outside any `.booping` walk-up exits 2 with a clear stderr message.
- [x] `cli.py` no longer registers a `_not_implemented` stub for `plans`; the `plans` subcommand is gone entirely.

#### Task 1.3 DoD

- [x] Four tests cover default-path write, `--output -`, `--output <path>`, no-project failure.
- [x] All tests use fixture vaults under `tests/__fixtures__/`; none read from `~/Claude/`.
- [x] `uv run pytest -q` passes.

---

### M2: Migrate skill bodies to in-Jinja status filtering — 4 SP | done

**Goal**: `chat.md.j2` and `develop.md.j2` produce the status-filtered listings (chat orient counts + active-plans tables; develop plan-selection candidates) directly from `context.plans` in their Jinja bodies. No skill calls `booping plans --status X` afterward.

**Verify**: `bin/booping render src/templates/skills/chat.md.j2 | grep -A3 "Counts"` shows a populated table; `bin/booping render src/templates/skills/develop.md.j2 | grep -E 'ready-for-dev|awaiting-plan-review'` shows the candidate plans inline. `git grep -n 'booping plans --status' -- ':!plans/' ':!retrospectives/' ':!booping-python/'` returns zero hits.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | `chat.md.j2` — Phase 0 Orient: replace the "Use `booping plans --status <s>` to assemble both" instruction with the actual rendered tables. **Counts** table: one row per status in `config.plan.statuses` with `{{ context.plans \| selectattr('status', 'equalto', status_key) \| list \| length }}`. **Active plans** table: one row per plan whose status is in `['ready-for-dev', 'in-progress', 'awaiting-retro', 'awaiting-learning']`, columns `Status \| Plan`, omit table when empty. Keep the surrounding prose. | `src/templates/skills/chat.md.j2` | 2 | done |
| 2.2 | `develop.md.j2` — Phase 1 plan-selection paragraph: replace the `booping plans --status ready-for-dev` + `--status awaiting-plan-review` shell-call instruction with an inline candidate list rendered from `context.plans` filtered by those statuses (one bullet per plan, with title and status). Keep the AskUserQuestion handoff prose. Replace Phase 4 `verify with booping plans` with "re-read the plan frontmatter to confirm `status:` matches the new state". | `src/templates/skills/develop.md.j2` | 2 | done |

#### Task 2.1 DoD

- [x] No `booping plans --status` reference remains in `chat.md.j2`.
- [x] Rendered chat skill body contains a Counts table with one row per status from `config.plan.statuses` (zero counts allowed).
- [x] Rendered chat skill body contains an Active plans table when at least one plan has status in `['ready-for-dev', 'in-progress', 'awaiting-retro', 'awaiting-learning']`; the table is omitted when all four are empty.
- [x] Pipes inside plan titles are escaped.

#### Task 2.2 DoD

- [x] No `booping plans --status` reference remains in `develop.md.j2`.
- [x] Rendered develop skill body lists `ready-for-dev` and `awaiting-plan-review` candidates inline (separate sub-lists or a combined list with the status as a column).
- [x] Phase 4 verify line no longer references `booping plans`; cites frontmatter re-read instead.

#### M2 cross-cutting DoD

- [x] Four-check IA pass (lesson 0004) applied to both refactored skill bodies before saving: scoping, duplication, configurability, hierarchy.

---

### M3: Migrate snapshot-regen call sites — 2 SP | done

**Goal**: `_shared_instructions.j2`, `install.md.j2`, and `chat.md.j2`'s orient phase invoke `booping render-sprints` (no shell pipe). Surrounding prose updated where it described the old `--format=md > sprints.md` shape.

**Verify**: `git grep -nE 'booping plans --format=md|booping plans .*> .*sprints\\.md' -- ':!plans/' ':!retrospectives/' ':!booping-python/'` returns zero hits.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | `_shared_instructions.j2` and `chat.md.j2` Phase 0 Orient: replace `booping plans --format=md > ~/Claude/{project}/sprints.md` with `booping render-sprints`. Update prose around it ("Refresh the snapshot before the first assistant message" stays; the command body simplifies). | `src/templates/_partials/_shared_instructions.j2`, `src/templates/skills/chat.md.j2` | 1 | done |
| 3.2 | `install.md.j2` seeding step: replace `booping plans --format=md > ~/Claude/{name}/sprints.md` with `booping render-sprints`. Update the verification prose at line 109 ("`booping plans` on a plans-empty vault emits header + separator cleanly") to reflect the new behaviour and command name (default writes file, no shell pipe needed). | `src/templates/skills/install.md.j2` | 1 | done |

#### Task 3.1 DoD

- [x] No `booping plans --format=md` or `> sprints.md` references remain in `_shared_instructions.j2` or `chat.md.j2`.
- [x] Rendered chat skill body's orient block reads as a single CLI call (`booping render-sprints`) followed by the inline-rendered tables from M2.

#### Task 3.2 DoD

- [x] No `booping plans --format=md` or `> sprints.md` references remain in `install.md.j2`.
- [x] Rendered install skill body describes the seeding step as "run `booping render-sprints`" (the freshly-initialized vault is the resolved project).

#### M3 cross-cutting DoD

- [x] Four-check IA pass applied to each touched skill / partial before saving.

---

### M4: Stale-reference cleanup + CLAUDE.md update — 1 SP | done

**Goal**: every `booping plans` reference (any form: bare, `--format=md`, `--status`, shell-pipe `> sprints.md`) outside `plans/` and `retrospectives/` is gone. CLAUDE.md describes the new `booping render-sprints` shape.

**Verify**: `git grep -nE 'booping plans|> .*sprints\\.md' -- ':!plans/' ':!retrospectives/' ':!booping-python/'` returns zero hits. `CLAUDE.md` `## CLI` section names `booping render-sprints` with the new shape.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Audit and update prose references: `CLAUDE.md` `## CLI` section adds/refines a one-line description of `booping render-sprints` ("renders `<vault>/sprints.md` from `src/templates/sprints.md.j2`; `--output` overrides the destination"); the old generic `booping plans` line is removed. Audit `README.md`, `src/docs/*.md` for any `booping plans` / `--format=md` / `--status` / `> sprints.md` mention. Strip the stale "Plan editing" block in `groom.md.j2` body (currently shows the `--format=md > sprints.md` recipe; should now read `booping render-sprints`). | `CLAUDE.md`, `README.md`, `src/docs/*.md`, `src/templates/skills/groom.md.j2` | 1 | done |

#### Task 4.1 DoD

- [x] `CLAUDE.md` `## CLI` section names `booping render-sprints` and describes its new shape; no `booping plans` line remains.
- [x] `git grep -nE 'booping plans|> .*sprints\\.md' -- ':!plans/' ':!retrospectives/' ':!booping-python/'` returns zero hits.
- [x] `README.md` and `src/docs/*.md` contain no stale `booping plans` / `--format=md` / `--status` references.

---

### M5: Reshape pause — render-time IA review — 1 SP | pending

**Goal**: render every touched skill body and the new `sprints.md` from a populated fixture vault; hand the rendered output back to the user side-by-side with the pre-migration baseline. Apply prose-shape tweaks the user calls out before transitioning.

**Verify**: explicit user sign-off captured in this plan.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Render `chat.md.j2`, `develop.md.j2`, `install.md.j2` (and any other touched skill / partial) via `bin/booping render`. Render the new `sprints.md.j2` against the live `~/Claude/claude-booping/` vault. Walk the user through the diff vs the pre-M1 baseline. Apply requested tweaks; capture sign-off. If new follow-up plans surface, file them as `backlog` stubs. | rendered output (transient), any prose tweaks land in the original templates | 1 | pending |

#### Task 5.1 DoD

- [ ] Each rendered skill / template reviewed by user.
- [ ] Sign-off captured in the plan.
- [ ] Follow-up stubs (if any) created with `status: backlog`.

---

## Final Verification

- [ ] `bin/booping render src/templates/skills/<chat,develop,install>.md.j2` renders without errors and shows status-filtered tables / lists rendered inline (M2) and the simplified `booping render-sprints` snapshot-regen line (M3).
- [ ] `booping render-sprints` from inside the booping repo writes `~/Claude/claude-booping/sprints.md`; the file matches the deleted-script's shape (header comment + GFM table).
- [ ] `booping render-sprints --output -` prints the same content to stdout.
- [ ] `booping render-sprints` invoked from a directory with no `.booping` marker walking up exits 2.
- [ ] `git grep -nE 'booping plans|> .*sprints\\.md' -- ':!plans/' ':!retrospectives/' ':!booping-python/'` returns zero hits.
- [ ] `CLAUDE.md` `## CLI` section reflects the new `booping render-sprints` shape.
- [ ] `cd booping-python && uv run pytest && uv run ruff check . && uv run basedpyright` all green.
- [ ] No test reads from `~/Claude/` or any path outside `booping-python/tests/__fixtures__/`.
- [ ] User sign-off on rendered output (M5) captured.

## Out of scope

- `--status`, `--columns`, `--sort`, `--asc`, `--project`, `--format` flags from the deleted `bin/booping-plans` script. If a use case arises, file a follow-up.
- Per-project override of `sprints.md.j2` (e.g. `~/Claude/{project}/templates/sprints.md.j2`). Architecture leaves room (templates are paths, not names) but no second loader path lands here.
- A hook to auto-regenerate `sprints.md` on plan write — the existing follow-up note in CLAUDE.md still applies.
- Generating other vault snapshots (lessons index, retro summary). One template per vault snapshot is the design; no second snapshot lands today.
- Keeping a `booping plans` alias for the new command. Clean break — anything still referencing `booping plans` should fail loudly so it surfaces in audit.

## CLAUDE.md impact

Sections to update (covered in M4.1):

- `## CLI` — replace the post-M6 generic mention of `booping plans` with a one-line description of `booping render-sprints` (renders `<vault>/sprints.md` from `src/templates/sprints.md.j2`; `--output` overrides destination; `-` for stdout).
- `## Layout` — confirm `src/templates/sprints.md.j2` is named alongside the other template trees (skills, agents, docs, plan_templates, _partials).

No other sections need edits — the schema, plan lifecycle, and information-ownership prose are unchanged by this work.
