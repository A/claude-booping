---
status: done
reviewed_at: 20260805 09:05
fixtures_reviewed_at: 20260805 09:05
suite_reviewed_at: 20260805 09:11
---

# summarize

[← index](../../index.md)

## Contract

- **Needs** —
  - each migration this run applied: its id, its title, and its outcome
  - the recorded migration id the run ended on — the repo `.booping` marker's `latest_migration`
    key, whose sentinel value (`-1`) means nothing has ever been applied
  - the commits the run made — one per applied migration
  - whether the vault is now current: `latest_migration` against the highest id the plugin ships
- **Value** — one run-level closing report, exactly one however many migrations ran, so the
  user leaves with a single statement of what changed, which commits carry it, and whether
  normal booping work resumes — instead of reconstructing it from a trail of per-migration
  chatter.
- **Output files** —
  - none — the step writes no file; the report is presented in chat
- **Harness return** — none in the sub-agent sense: the step is inline, so the runner presents
  the report itself. Nothing is written, so `## Changed:` stays empty.
- **Review gate** —
  - none — the run's single gate was taken up front, before anything was applied; this report
    closes the run rather than asking for anything
- **Delegation** — inline

The report is scoped to **the run just completed**. It never reconstructs the vault's whole
migration history: a re-entry after an earlier halted run is an ordinary run and reports only
the migrations *it* applied, saying in one line that earlier ids landed previously. A failed run
never reaches this step — `apply-migration` halts the sequence itself — so the report never
describes a failure. "Vault is now current" is stated as a **checked** fact, `latest_migration`
read against the highest shipped id; if that check does not hold, the mismatch is the headline
and the report names the id the vault stopped at instead of claiming success.

There is **no nothing-applied shape**. An empty pending set is `survey`'s case: it reports
"already current" and ends the run there, so this step is never reached with nothing to report.
Nor is there a path in between — a non-empty pending set yields one instance per migration, and
an instance that finds its work already done still applied, still advanced `latest_migration`
and still committed, so it appears in the table as an ordinary row. Every run that reaches this
step applied at least one migration.

## Example artifact

```markdown
Vault migrated — 2 migrations applied, vault is now current.

| id  | migration       | outcome | commit    |
| --- | --------------- | ------- | --------- |
| 003 | plans_to_dirs   | applied | `a1b2c3d` |
| 004 | lessons_targets | applied | `e4f5a6b` |

`latest_migration`: `002` → `004` — the highest migration the plugin ships, so render surfaces
stop reporting the vault as behind and normal work resumes.

Migrations `001`–`002` landed in an earlier run; this report covers only what this run applied.
```

## Return Format

The step is inline; this block exists only for the runner's own bookkeeping, while the report
above is what the user sees.

```markdown
## Changed:

## Notes:
- 2 migration(s) applied; latest_migration 002 → 004; vault current
```
