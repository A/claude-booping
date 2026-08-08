---
title: Playbook Lessons — scoped learning artifacts wired into playbook 
  rendering
type: feature
status: done
sp: 18
split_from: null
created: 2026-07-31 18:13
planned: 20260731 10:28
started: 20260731 10:51
completed: 2026-07-31 11:13
retro: null
goal: null
summary: Lessons for playbooks at global/project/playbook/step scope, injected 
  into render-playbook; name clash becomes STOP
commit: e5fb99ad4f5c016fb7ece9d188034385ce30b8d0
sessions:
- 1e890c40-45b3-4bd2-b527-222d87f843b3
- 9aa7ff0b-088b-469a-b098-3fe317343aa3
metrics_active_minutes: 37
metrics_models:
- claude-fable-5
metrics_tokens_input: 385
metrics_tokens_output: 206773
metrics_tokens_cache_creation: 781200
metrics_tokens_cache_read: 18833297
---

# Playbook Lessons — scoped learning artifacts wired into playbook rendering

## Context

`booping render-playbook` composes a playbook's procedure (preamble + graph + step sections) and serves step bodies via `--step`. Vault-level lessons exist for skills (`{vault}/lessons/`, rendered by `_lessons.j2`) but playbooks have no learning channel: nothing persists run-to-run guidance at the playbook or step level, and lessons about core/global playbooks have nowhere to live that the user can write.

After this plan: lesson files are discovered at four scopes — global root (all playbooks), project root (all playbooks, this vault), playbook (one playbook, merged across discovery roots), step (targeted via frontmatter) — and injected unconditionally by `render-playbook`: playbook-scoped lessons as a `## Lessons` section in the composed render (driver/harness level), step-scoped lessons appended to `--step` stdout (agent level). Same-named playbooks across roots become a blocking STOP (shadowing is no longer a supported pattern) because lesson merge keys on playbook name.

Authorship of playbook lessons (retro/learn integration) is **out of scope** — this plan delivers storage, discovery, and wiring only.

## Decisions

- **Storage — flat `_lessons/` dirs + frontmatter targeting**: `<root>/_lessons/*.md` = root scope (all playbooks under that root); `<root>/<name>/_lessons/*.md` = playbook scope; optional frontmatter `step: <step-name>` retargets a playbook-dir lesson to one step. No nested per-step dirs — flat, greppable, overlay dirs need no `prompt.md` mirroring. (User-confirmed.)
- **Merge across roots**: playbook-level lessons union across core/global/local roots even where `playbook.md` is absent in the overlay root — so users add lessons to core playbooks vault-side without touching the plugin repo. Filename collision: most specific root wins (local > global > core). (User-confirmed.)
- **Name clash = blocking STOP**: `playbook.md` for the same name in 2+ roots emits a STOP notice; render is blocked (notices + preamble only, existing blocking behavior). Replaces silent replace-on-collision shadowing. `/playbook` listing marks the clash. (User-confirmed.)
- **Python-side unconditional injection**: `compose()` / `compose_step()` inject lessons for plain and `jinja: true` playbooks alike — no authoring opt-in, no `{% include %}` burden. (User-confirmed.)
- **Step lessons are fetch-only**: they ride `--step` stdout; the composed step section and the driver bootstrap prompt are unchanged. Driver context stays lean. (User-confirmed.)
- **File format = existing lesson format**: `NNNN_title.md`, frontmatter `id/title/created` (+ optional `retro`, new optional `step`), body verbatim. Reuse the `Lesson` model; loader generalized to `load_dir`.
- **Scope labels**: `core` (core root `_lessons/`), `global` (global root), `project` (vault root), `playbook` (playbook dir, any root). Core root supported for symmetry even though the plugin ships no lessons today.

## Architecture

- `booping-python/src/booping/context/lesson.py` — `Lesson` gains `step: str | None` and `scope: str | None`; `load_all` refactors onto a new `Lesson.load_dir(path, scope=...)` primitive. Existing consumers (`Context.assemble`, `_lessons.j2`) unchanged.
- `booping-python/src/booping/context/playbook.py` — `load_all` scans root-level `_lessons/` per root and per-playbook `_lessons/` across all roots; `Playbook` gains `lessons: list[Lesson]` (ordered core → global → project → playbook, filename-sorted within scope) and `clash_scopes: list[str]` (empty = no clash). Name clash appends a `GraphProblem(kind="name_clash")`.
- `booping-python/src/booping/commands/render_playbook.py` — new notice text for `name_clash` (STOP); `compose()` renders `## Lessons` between preamble and `## Execution graph` via a new partial `src/templates/_partials/_playbook_lessons.j2`; `compose_step()` appends step-scoped lessons to stdout for plain and jinja playbooks.
- Consumers: `/playbook` listing (`src/templates/skills/playbook.md.j2`) shows the clash marker; `_playbook_driving.j2` tells the driver the composed `## Lessons` binds the whole run. `playbook-state` / `playbook-transition` untouched.

## Milestones

### M1: Lesson discovery for playbooks — 7 SP | done

**Goal**: `Playbook.load_all` returns playbooks carrying scoped lessons merged across roots, and records name clashes as STOP-level problems.

**Verify**: `cd booping-python && uv run pytest tests/context/lesson_test.py tests/context/playbook_test.py -q` — all pass, including new cases below.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Generalize lesson loader: extract `Lesson.load_dir(path, scope=None) -> list[Lesson]` from `load_all` (filename-sorted, missing dir → `[]`); add `step: str | None` (from frontmatter `step:`) and `scope: str | None` fields | `booping-python/src/booping/context/lesson.py`, `booping-python/tests/context/lesson_test.py` | 2 | done |
| 1.2 | Playbook lesson scan in `load_all` (roots already in hand via the existing `(vault, home_dir, plugin_root)` signature; step names known from the dir scan that precedes graph parse): root-level `<root>/_lessons/` per root (scopes `core`/`global`/`project`) + per-playbook `<root>/<name>/_lessons/` across all roots (scope `playbook`); filename collision resolved most-specific-wins **at both levels** (root-level and playbook-level); attach ordered union to `Playbook.lessons`; lesson `step:` naming an unknown step → non-blocking `GraphProblem(kind="orphan_lesson")`, lesson excluded from both render surfaces | `booping-python/src/booping/context/playbook.py`, `booping-python/tests/context/playbook_test.py` | 3 | done |
| 1.3 | Name-clash detection: same playbook name with `playbook.md` in 2+ roots → `GraphProblem(kind="name_clash", detail=<scopes>)` on the surviving (most specific) playbook + `Playbook.clash_scopes` populated; loading otherwise proceeds local-wins so the listing can still show the winner | `booping-python/src/booping/context/playbook.py`, `booping-python/tests/context/playbook_test.py` | 2 | done |

#### Task 1.1 DoD

- [x] `Lesson.load_dir(tmp_path)` loads `NNNN_title.md` files filename-sorted; missing dir → `[]`.
- [x] `Lesson.load_all(vault)` behavior unchanged (delegates to `load_dir(vault/"lessons")`; existing tests still pass).
- [x] Frontmatter `step: research-web` populates `lesson.step`; absent → `None`.
- [x] `scope` passed to `load_dir` lands on every returned lesson.

#### Task 1.2 DoD

- [x] A lesson in `{vault}/_playbooks/_lessons/` appears on **every** loaded playbook with `scope == "project"`.
- [x] A lesson in `{vault}/_playbooks/groom/_lessons/` (no `playbook.md` in that dir) appears on the core `groom` playbook with `scope == "playbook"` — overlay works without a manifest.
- [x] Same filename in core and local playbook `_lessons/` → only the local copy loads.
- [x] Same filename in `<global-root>/_lessons/` and `{vault}/_playbooks/_lessons/` → only the project copy loads (root-level collision, most-specific-wins).
- [x] `Playbook.lessons` order: core-root → global-root → project-root → playbook-level, filename-sorted within each.
- [x] `step:` naming an unknown step → `orphan_lesson` problem recorded, lesson absent from `Playbook.lessons`.
- [x] Playbook with no lesson dirs anywhere → `lessons == []`, no problems.

#### Task 1.3 DoD

- [x] `playbook.md` for name `x` in global + local roots → surviving playbook has `clash_scopes == ["global", "local"]` and a `name_clash` problem.
- [x] No clash → `clash_scopes == []`, no `name_clash` problem.
- [x] Lesson merge for a clashing name still unions `_lessons/` across roots (STOP blocks render, not loading).

---

### M2: Render injection — 6 SP | done

**Goal**: composed render carries the `## Lessons` section; `--step` stdout carries step-scoped lessons; name clash blocks the render with a STOP notice.

**Verify**: `cd booping-python && uv run pytest tests/test_render_playbook.py -q` — all pass; then against a fixture playbook: `bin/booping render-playbook <fixture>` shows the `## Lessons` section after the preamble and `bin/booping render-playbook <fixture> --step <s>` ends with the step's lessons.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | New partial `_playbook_lessons.j2` — the **single** formatter for both surfaces (parameterized `step_mode` flag; lesson bodies inserted as template *variables*, never parsed as Jinja — same mechanism as `_lessons.j2`). `compose()` wiring: render playbook-scoped lessons (`step is None`) between preamble and `## Execution graph` via the same plain-env template loading `compose()` already uses for `_playbook_graph.j2`/`_playbook_step.j2`; exact locked format below; no lessons → no section | `src/templates/_partials/_playbook_lessons.j2`, `booping-python/src/booping/commands/render_playbook.py`, `booping-python/tests/test_render_playbook.py` | 2 | done |
| 2.2 | `compose_step()` append: lessons with `step == <step>` appended after the body (blank line + locked step format, rendered through the **same** `_playbook_lessons.j2` with `step_mode`) for plain **and** jinja playbooks; no lessons → body unchanged; exit codes unchanged | `booping-python/src/booping/commands/render_playbook.py`, `booping-python/tests/test_render_playbook.py` | 2 | done |
| 2.3 | `name_clash` STOP notice text + blocking behavior (notices + preamble only, matching existing blocking kinds) | `booping-python/src/booping/commands/render_playbook.py`, `booping-python/tests/test_render_playbook.py` | 1 | done |
| 2.4 | `--no-lessons` flag on `render-playbook`: suppresses lesson injection on both surfaces (composed `## Lessons` section and `--step` append); everything else identical. Needed by the vault eval harness (`verify-wrapper.sh` diffs `--step` output against the raw body file) | `booping-python/src/booping/commands/render_playbook.py`, `booping-python/tests/test_render_playbook.py` | 1 | done |

**Locked output formats** (user-confirmed; do not restyle):

Composed render, between preamble and `## Execution graph`:

```markdown
## Lessons

The following {n} lesson(s) apply to this playbook. Never silently violate one; conflict → stop and flag.

### {stem} — {title}
*(scope: {core|global|project|playbook})*

{body verbatim, rstripped}
```

`--step` stdout, appended after the body:

```markdown
## Lessons

The following {n} lesson(s) apply to this step. Never silently violate one.

### {stem} — {title}

{body verbatim, rstripped}
```

STOP notice:

```markdown
**STOP — tell the user:** playbook '{name}' is defined in more than one root ({scopes}) — playbook names must be unique; rename one.
```

Orphan-lesson Note:

```markdown
**Note — tell the user:** lesson '{file}' targets unknown step '{step}' in playbook '{name}'; it is ignored.
```

#### Task 2.1 DoD

- [x] Section renders byte-for-byte per the locked format (heading, count line, per-lesson `### {stem} — {title}` + scope tag + body).
- [x] Step-targeted lessons never appear in the composed section.
- [x] No applicable lessons → no `## Lessons` heading anywhere in the composed output.
- [x] Section order: notices → preamble → `## Lessons` → `## Execution graph`.
- [x] Both surfaces render through the one partial — no duplicated format string in Python.
- [x] Four-check IA pass (scoping / duplication / configurability / hierarchy, lesson 0004) run on the new partial.

#### Task 2.2 DoD

- [x] Plain-markdown playbook `--step` output = body + appended lessons (no Jinja pass introduced).
- [x] `jinja: true` playbook `--step` output = rendered body + appended lessons; lessons bodies are **not** Jinja-rendered.
- [x] Step with no targeted lessons → stdout identical to today.
- [x] Unknown step still exits 1 with stderr message.

#### Task 2.3 DoD

- [x] Clash → output is notices + preamble only; `## Lessons`, graph, and step sections absent.
- [x] Notice text matches the locked string exactly.
- [x] Exit code stays 0 (in-band notice, matching existing STOP kinds).

#### Task 2.4 DoD

- [x] `render-playbook <name> --no-lessons` output has no `## Lessons` section even when playbook-scoped lessons exist.
- [x] `render-playbook <name> --step <s> --no-lessons` output byte-identical to the pre-plan body output even when step-scoped lessons exist.
- [x] Without the flag, behavior per tasks 2.1/2.2 unchanged.
- [x] `--help` shows the flag.

---

### M3: Skill surfaces — 2 SP | done

**Goal**: `/playbook` listing flags name clashes; the driving protocol binds the driver to the composed `## Lessons`.

**Verify**: `bin/booping render src/templates/skills/playbook.md.j2` renders cleanly; with a clashing fixture pair in the vault, the listing row shows the clash marker.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Listing clash marker: Scope column renders `{scope} ⚠ clash ({scopes})` when `clash_scopes` is non-empty, plus one line under the table telling the user clashing playbooks are blocked until renamed | `src/templates/skills/playbook.md.j2` | 1 | done |
| 3.2 | Driving partial: add that the composed render's `## Lessons` section binds the driver for the whole run, and that step-scoped lessons arrive via the step fetch — the driver must not duplicate them into bootstrap prompts | `src/templates/_partials/_playbook_driving.j2` | 1 | done |

#### Task 3.1 DoD

- [x] Clash-free playbooks render Scope exactly as today.
- [x] Clashing playbook renders `⚠ clash` marker with the scope list.
- [x] Rendered skill output valid markdown (table intact).

#### Task 3.2 DoD

- [x] One short addition; no restatement of lesson bodies or formats in the partial.
- [x] Four-check IA pass (lesson 0004) run on the modified partial.
- [x] `/groom-playbook` (shares the partial) renders cleanly: `bin/booping render src/templates/skills/groom-playbook.md.j2`.

---

### M4: Docs + stale-reference cleanup — 3 SP | done

**Goal**: docs describe unique-name playbooks + lessons; no reference to replace-on-collision shadowing survives.

**Verify**: `grep -rn "shadow" documentation/ CLAUDE.md` returns no hit describing playbook name shadowing as supported; `just docs` builds clean.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | `documentation/playbook.md`: rewrite "Scopes and shadowing" (lines 6, 13–21, 64, 325) → unique names + clash STOP; add a user-facing "Lessons" section: the four scopes, file layout, `step:` targeting, where each scope surfaces. Audience-scoped — no Python internals (lesson 0006) | `documentation/playbook.md` | 2 | done |
| 4.2 | `CLAUDE.md`: playbooks bullet — replace precedence/replace-on-collision claims with unique-name STOP; add lessons discovery + injection summary; update `render-playbook` CLI entry for the two new output surfaces | `CLAUDE.md` | 1 | done |

#### Task 4.1 DoD

- [x] All four enumerated shadowing references rewritten.
- [x] New Lessons section covers: layout (`_lessons/` at root and playbook level), `step:` frontmatter, overlay-without-manifest for core playbooks, where lessons appear at run time.
- [x] No internal implementation detail (class names, function names) in the page.

#### Task 4.2 DoD

- [x] Playbooks bullet no longer claims core < global < local shadowing; states unique-name STOP + lesson scopes.
- [x] CLI section's `render-playbook` entry mentions `## Lessons` in composed output, step-lesson append on `--step`, and the `--no-lessons` flag.

---

## I/O contract

- **`booping render-playbook <name>`** stdout gains one optional section: `## Lessons` between preamble and `## Execution graph` (locked format above). Absent when no playbook-scoped lessons apply. New STOP notice kind `name_clash`; new Note kind `orphan_lesson`. Exit codes unchanged (0 incl. in-band notices; 1 unknown playbook).
- **`booping render-playbook <name> --step <step>`** stdout gains an optional appended `## Lessons` block (locked format above). Exit codes unchanged (1 on unknown step).
- **`booping render-playbook <name> [--step <step>] --no-lessons`** — suppresses lesson injection on both surfaces; output then matches pre-plan shape exactly. For eval harnesses diffing rendered bodies. No other new flags, no new subcommands. `playbook-state`, `playbook-transition` untouched.
- **stderr**: existing loader warnings unchanged; lesson parsing stays lenient (unparseable frontmatter → title falls back to stem, as today).

## Out of scope

- Retro/learn authorship of playbook lessons (writing, numbering, dedup) — separate plan.
- Per-instance (subgraph) lesson scoping.
- Lesson tagging/filtering beyond the single `step:` key.
- Migrating existing vault `lessons/` (skill-level pipeline untouched).
- Eval-suite updates under `~/Claude/_playbooks/` (vault-side, user-owned).

## Risk register

- Blocking STOP on clash breaks any vault that intentionally shadows a core/global playbook today. Accepted by user (2026-07-31): shadowing is no longer a supported pattern; the STOP text tells the user to rename.
- Cross-validation flagged eager lesson/step parsing at `load_all` as a boot-time concern. Deferred: `load_all` is already fully eager (dir scans + graph parse per playbook); a few extra small-file reads per root are negligible. Revisit only if vault boot time regresses.

## CLAUDE.md impact

Covered as task 4.2 — playbooks bullet (discovery semantics + lessons) and CLI `render-playbook` entry.
