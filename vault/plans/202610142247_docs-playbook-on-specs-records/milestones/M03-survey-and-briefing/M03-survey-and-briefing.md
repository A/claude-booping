---
id: "03"
title: "Survey judges records, briefing reads values into the run record"
sp: 6
status: done
plan: "plans/202610142247_docs-playbook-on-specs-records/index.md"
---

# M03: Survey judges records, briefing reads values into the run record

`survey` judges the spec records with `booping specs check` and subtracts the moved ledger; `briefing` reads the value records and writes its briefing into the run record instead of `_specs/index.md`.

**Scope:** `vault/_playbooks/docs/survey/opus-5.md`, `vault/_playbooks/docs/survey/prompt.md` (summary, gate text), `vault/_playbooks/docs/briefing/fable-5.md`, `vault/_playbooks/docs/briefing/prompt.md` (summary).

**Test:** each step's fetched body (`bin/booping render-playbook docs --step {step}`) at the CLI surface, integration tier — renders, names no `_specs/` path, and for `briefing` carries the rendered value list (a value title such as `Single source` appears in it).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | `survey`: Sweep 1 judges the docs-relevant records — the value records, reference/0001, reference/0002, reference/0003, the story records — by running `booping specs check --tier project` (a record named in an error → `incomplete`, absent → `missing`, else `present`) and counting open `[clarify]` / `[unknown]` marks per record (`rg -n '\[(clarify\|unknown)\]'`); the `## Spec set` table becomes `Record \| State \| Open marks \| Gap`, value and story records each summarised as one row (`specs/value/` , `specs/story/`) with counts; the route reads "spec waves needed" when reference/0001 or reference/0003 is not `present`. Sweep 2 subtracts `{vault}/docs/documented.md`. Return format and prompt `summary` / `review_gate` follow. | `vault/_playbooks/docs/survey/opus-5.md`, `vault/_playbooks/docs/survey/prompt.md` | 3 | done |
| 3.2 | `briefing`: render the value list into the body with `{% set values = 'core.docs_playbook.queries.values' \| query %}` and read reference/0001 plus the repo's own account (README, `CLAUDE.md`); write a `## Briefing` section (`### What it is`, `### Who it serves`, `### Where it is heading`) into the run record, rewritten in place on a rework; measure the vision shift against the `## Briefing` section of the newest earlier run record under `{vault}/docs/_runs/` that has one (`none` when none); a shift that contradicts a value record is named in the return's `vision shift:` note with the value's path, never written into a value. Writes nothing under `specs/`. Return format names the run record as `[UPDATED]`; prompt `summary` follows. | `vault/_playbooks/docs/briefing/fable-5.md`, `vault/_playbooks/docs/briefing/prompt.md` | 3 | done |

## Definition of Done

### Task 3.1

- [x] `survey` body names no `_specs/` path; the ledger it subtracts is `{vault}/docs/documented.md`.
- [x] Sweep 1 runs `booping specs check --tier project` — one procedure, no "by shape" judging alternative.
- [x] The `## Spec set` table columns, the closing line and the return's `spec set:` note agree with each other.

### Task 3.2

- [x] `briefing` body renders the value list from `core.docs_playbook.queries.values`; no value title is hand-typed into the prompt.
- [x] It writes only the run record's `## Briefing` section; no file under `specs/` or `_specs/`.
- [x] Vision shift baseline is the newest earlier run record's `## Briefing`.
- [x] Both bodies pass the information-architecture pass (rule/0006): no motivation prose, no restated config.

## References

- `vault/_playbooks/docs/survey/opus-5.md`, `vault/_playbooks/docs/briefing/fable-5.md` — current bodies; keep their section and return-format shape.
- `playbooks/learn/playbook.md` — the `{% set … = '…' | query %}` render pattern.
- `src/specs/README.md` — Marks and Check.

## Verify

```
for s in survey briefing; do bin/booping render-playbook docs --step $s > /tmp/docs-m03-$s.md || exit 1; done; ! grep -n '_specs/' /tmp/docs-m03-survey.md /tmp/docs-m03-briefing.md && grep -c 'Single source' /tmp/docs-m03-briefing.md
```

Final reply: only the list of changed files and the Verify output's last line.
