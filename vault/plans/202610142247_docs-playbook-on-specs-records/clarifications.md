# Clarifications

Autonomous run: the owner was unavailable, so every point below was settled by a default chosen by the agent ([rule/0002](../../specs/rule/0002-unknown-is-marked.md)). Each answer is a default to revisit, not an owner decision.

## C1 — ledger location — answered

**Asked:** 2026-10-14 — intake

**Question:** Where does the `documented.md` ledger live once `vault/docs/_specs/` is deleted?

**Options:**

- `vault/docs/documented.md` — the workdir root, beside `_runs/`
- `vault/docs/_runs/documented.md` — beside the run records
- derive it from the run records' `documented:` lists — no file

**Answer:**

`vault/docs/documented.md`, moved with `git mv` so its history follows. The request keeps it a file ("stays a run artefact"), which rules out deriving it; `_runs/` holds one file per run, and a cross-run ledger there would sit among the records `survey` and `briefing` glob. `close-documented` writes the new path and `survey` subtracts it.

## C2 — where the briefing lands — answered

**Asked:** 2026-10-14 — intake

**Question:** `briefing` stops writing `_specs/index.md`; where does its output go, and what is the vision shift measured against?

**Answer:**

`briefing` reads the value records (rendered into its body by a `core.docs_playbook.queries.values` query spec), the audience record reference/0001 and the repo's own account of itself, and writes a `## Briefing` section (`What it is` / `Who it serves` / `Where it is heading`) into the run record. The vision shift is measured against the `## Briefing` section of the newest earlier run record under `vault/docs/_runs/` that carries one — `none` when there is none. The run record is the run's artefact, so the briefing is reviewable and kept (value/0004) without a second stored copy of what the value records say.

## C3 — reviewed_at stamps — answered

**Asked:** 2026-10-14 — intake

**Question:** The gate hooks stamping `reviewed_at` on `_specs/index.md`, `roles.md`, `targets.md` and `features.md` lose their targets; drop them or move them?

**Answer:**

Move them onto the run record: the briefing gate stamps `briefing_reviewed_at`, the roles-and-surfaces gate stamps `specs_reviewed_at`. They are never stamped on a spec record: `reviewed` on a record is set only by the owner, never by an agent (`src/specs/README.md`, Frontmatter), and a hook a run executes is the agent's write. A record a step edits bumps `updated_at` and leaves `reviewed` untouched, so what the agent changed alone stays visible (value/0009).

## C4 — feature index — answered

**Asked:** 2026-10-14 — intake

**Question:** "`feature-index` → generated from story records, not stored" — does the step stay, and what replaces the groups?

**Answer:**

The `feature-index` step, its directory and its `awaiting-features-confirm` gate are removed. The index is a query spec `core.docs_playbook.queries.features` in `vault/config.yaml` over `specs/story/*.md` (columns title, summary, status), rendered with the `| query` filter into the bodies that read it (`research`, `targeting`). A step that only runs a query spends a sub-agent on mechanics (rule/0025, value/0012). The feature groups are dropped: story records carry none, and the format is not extended for one playbook; `targeting` places a change under the story it moves, and the documentation structure comes from reference/0003. The `commit-docs` hook the removed gate carried moves to the roles-and-surfaces confirming edge.

## C5 — how sync-specs folds into records — answered

**Asked:** 2026-10-14 — intake

**Question:** Which record does each change-table row land in, and when does `sync-specs` edit versus mark?

**Answer:**

- vision-shift row → a `[clarify]` sentence in the affected value record's `## In practice`, naming the shift; a value's statement is never rewritten (values are the owner's, `created_by: owner`; value/0001)
- audience row → reference/0001; surface row → reference/0003; term row → reference/0002 — fact bullets edited in place
- new-feature row → a new story record (next number, `created_by: claude`, `status: done`); refactoring row → the story's criteria edited in place; feature-drop row → a `[clarify]` mark in the story, status untouched
- what the confirmed row does not settle → `[clarify]`; a record that disagrees with the code where the row does not say which is right → `[unknown]` (rule/0002)
- every edited record bumps `updated_at`; `booping specs check --tier project` passes after the fold.

## C6 — sources pointing at the deleted set — answered

**Asked:** 2026-10-14 — intake

**Question:** 32 records list `vault/docs/_specs/*.md` in `sources:`; deleting the set fails the `sources` check. Drop the entries or repoint them?

**Answer:**

Repoint each to a GitHub permalink pinned at `gh/master` commit `c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e` — `https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/{file}.md`. The `sources` check skips an entry containing `://`, the provenance survives (value/0004), and `gh/master..HEAD` has not touched `vault/docs/_specs/`, so the pinned content equals the deleted one.

## C7 — survey's spec-set sweep — answered

**Asked:** 2026-10-14 — intake

**Question:** Sweep 1 judged four `_specs/` files by shape; what does it judge now?

**Answer:**

The docs-relevant records — the value records, reference/0001, reference/0002, reference/0003 and the story records — judged by `booping specs check --tier project` (errors naming that record → `incomplete`; file absent → `missing`; else `present`) plus a count of open `[clarify]` / `[unknown]` marks per record. The three state words stay. The spec waves are needed when reference/0001 or reference/0003 is not `present`, or the user picks them for refresh at the scope gate.

## C8 — vault commits reach the records — answered

**Asked:** 2026-10-14 — intake

**Question:** `commit-docs` commits only the `{vault}/docs` subtree; `roles`, `targets` and `sync-specs` now write `{vault}/specs/`. Who commits those?

**Answer:**

`commit-docs` commits both `{vault}/docs` and `{vault}/specs` with an explicit pathspec, never anything else.

## C9 — committed report and evals — answered

**Asked:** 2026-10-14 — intake

**Question:** How do "its committed report and evals beside the steps" follow the change?

**Answer:**

`vault/_playbooks/docs/_reports/output.md` is not covered by `just snapshots` (it renders `playbooks/*` only) and is already stale against the current sources. It is regenerated once at the end with `bin/booping render-playbook docs --stub-macro core.macros.date=2026-10-14 --output vault/_playbooks/docs/_reports/output.md` and committed with the sources. The docs steps carry no eval suites (no `tests.yaml` / `promptfooconfig.yaml` beside any step), so no eval changes. The plan touches no core playbook source, so `just snapshots` is expected clean and the snapshot policy is not exercised. Regenerating the report inside the run departs from rule/0013 (a run never writes a committed report); the departure rests on the request itself ("its committed report … follow[s] the change") and the owner's standing snapshot permission for this feature dated 2026-10-14, and develop lists it in its defaults file.

## C10 — what stays untouched — answered

**Asked:** 2026-10-14 — intake

**Question:** Which `_specs` mentions are out of scope?

**Answer:**

- `vault/_playbooks/docs/_specs/` and `playbooks/*/_specs/` — playbook-authoring design history, intentionally stale (CLAUDE.md, Layout)
- `vault/docs/_runs/*.md`, plans, retrospectives, researches — history (value/0004)
- the `vault/_lessons/` half of the deprecation notes in `vault/specs/README.md` and adr/0001 — lesson injection still reads `_lessons/`; only the `vault/docs/_specs/` half is removed.

## C11 — roles and targets write shape — answered

**Asked:** 2026-10-14 — intake

**Question:** The old roles/targets files had their own shapes (five-bullet sections, a four-column table); the records have `## Facts` bullets only.

**Answer:**

`roles` and `targets` refresh reference/0001 and reference/0003 in the reference record shape — one fact per bullet, as the records are written today, frontmatter preserved apart from `updated_at`. reference/0003's spec-set fact names the project specs tier records the docs playbook reads (values, reference/0001–0003, stories) as the surface for Claude itself. `glossary` (reference/0002) is edited only by `sync-specs` from term rows, as the old `feature-index` co-write goes away with that step.
