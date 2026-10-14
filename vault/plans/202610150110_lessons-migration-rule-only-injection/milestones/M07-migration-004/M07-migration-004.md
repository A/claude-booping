---
id: "07"
title: "Migration 004 converts lessons into rules; booping\u0027s vault migrated"
sp: 9
status: pending
plan: "vault/plans/202610150110_lessons-migration-rule-only-injection/index.md"
---

# M07: Migration 004 converts lessons into rules; booping's vault migrated

`/playbook migrate` applies migration 004, which turns every lesson in `{home_dir}/_lessons/` and `{vault}/_lessons/` into a rule record or drops it as a duplicate, rewrites references to the removed files, and removes the directories; booping's own vault is migrated and its marker reads 4.

**Scope**: new `migrations/004_lessons_to_rules/migration.md` — frontmatter `id: 4`, `title`, `summary`; a prompt for the context-fresh sub-agent `apply-migration` spawns (it gets the vault path only — `home_dir` comes from `booping config-get home_dir`, tier roots from the last stdout line of `booping specs init --tier global|project`). Behaviour is locked in `clarifications.md`: order and idempotence C6, duplicate judgement and the never-edited tiers C4, rule shape C4 (plan 202610142150 C5), reference rewriting C5, report lines C7 — copy them, do not paraphrase. Judged parts (duplicate verdict, writing a converted rule's `brief`, `summary` and body) are prose; the reference rewrite and the deletion are one embedded `uv run --quiet python - <<'PY'` script, as `migrations/003_session_metrics/migration.md` embeds its rewrite, fed the removed lessons and their `retro:` values. The migration ends with `booping specs check --tier project` (and `--tier global` when the global pass wrote) reporting no error. Only `{home_dir}/_lessons/` and `{vault}/_lessons/` are read — the legacy `{vault}/lessons/` is untouched (parked, C3).

Fixture (C8): `migrations/004_lessons_to_rules/_fixtures/` — `home/` (global config with `home_dir`, `_specs/rule/` with one rule, `_lessons/` with a duplicate of it and a new lesson) and `repo/` (`.booping` at `latest_migration: 3`, in-repo vault, `vault/specs/rule/` with an accepted rule lacking one target a lesson names, a retired rule, a project rule whose `sources` and body link name a lesson, `vault/retrospectives/` with one retro, `vault/_lessons/` with: a duplicate of a core `booping:` rule, a duplicate of the retired rule, a duplicate of the project rule lacking a target, a new lesson with `retro:`, a new untargeted lesson without one). `check.sh {migrated copy}` asserts the C4–C6 end state with plain `test`/`grep`/`booping specs check` calls and exits non-zero naming the first failed assertion.

Booping's own vault (C9): apply `migration.md` to `vault/` exactly as the sub-agent would — expected: all eleven lessons dropped as duplicates (0004, 0005, 0006, 0007, 0010 → `booping:rule/0006`, `0007`, `0008`, `0009`, `0010`; 0013, 0015 → `booping:rule/0013`, `0015`; 0011, 0014, 0016 → `anton:rule/0001`–`0003`; 0012 → retired `booping:rule/0012`), none converted, rule/0013 and rule/0015 untouched in targets; `sources` / links rewritten in rule/0006–0010, 0012, 0013, 0015 and runbook/0003; `vault/_lessons/` removed; `bin/booping marker-set latest_migration=4`; `playbooks/_fixtures/vault/.booping` to 4. `{home_dir}` (`~/Dev/@A/notes/projects`) is never written — C2.

Tests: the fixture run is the migration's test (agent-applied, not in `just ci`, C8); booping's vault is checked by `just specs-check`.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | Author `migration.md`: prompt, the two passes, judged steps, embedded rewrite-and-delete script, closing check, report (C7). | `migrations/004_lessons_to_rules/migration.md` | 4 | pending |
| 7.2 | Build the fixture and `check.sh`; copy the fixture to `/tmp/m004`, apply `migration.md` to the copy with `XDG_CONFIG_HOME` pointing at the copy's `home/` config, run `check.sh`; fix `migration.md` until it passes. | `migrations/004_lessons_to_rules/_fixtures/**`, `migrations/004_lessons_to_rules/_fixtures/check.sh` | 3 | pending |
| 7.3 | Apply `migration.md` to `vault/`; set the marker; bump the hermetic fixture marker. | `vault/_lessons/*`, `vault/specs/rule/*.md`, `vault/specs/runbook/0003-accept-new-baselines.md`, `.booping`, `playbooks/_fixtures/vault/.booping` | 2 | pending |

## Definition of Done

### Task 7.1

- [ ] The `migrate` survey's pending query (`core.migrate_playbook.queries.pending`, ids greater than 3) lists migration 4 and nothing under `_fixtures/`.
- [ ] Every C7 report line form appears in `migration.md` verbatim; no other line form is introduced.
- [ ] The script never edits a record outside the tier root its pass writes, and never edits a core-tier record's `targets`.

### Task 7.2

- [ ] The fixture covers every lesson case in Scope, each named in a comment in `check.sh`.
- [ ] `bash migrations/004_lessons_to_rules/_fixtures/check.sh /tmp/m004` exits 0 after applying; a second application to the same copy changes nothing (checked with `diff -r` against a copy taken before it).

### Task 7.3

- [ ] `vault/_lessons/` no longer exists; `git status --short vault/specs` lists only `sources` / link rewrites (no `targets:` line changed).
- [ ] `bin/booping specs check --tier project` reports no error; `.booping` reads `latest_migration: 4`.
- [ ] `bin/booping render-playbook develop` renders without a migration STOP.
- [ ] Nothing under `~/Dev/@A/notes/projects` changed (`git -C ~/Dev/@A/notes status --short` identical before and after).

Return: the list of changed files, nothing else.

## References

- `migrations/003_session_metrics/migration.md` — shape: prose, a look-first command block, an embedded `uv run` script.
- `migrations/002_tracks_and_lessons/migration.md` `## Part 2` — precedent for a judged, per-file conversion.
- `src/specs/README.md` — the rule record format the converted rules follow.

## Verify

`bash migrations/004_lessons_to_rules/_fixtures/check.sh /tmp/m004`
