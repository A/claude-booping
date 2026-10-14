---
id: "06"
title: "Retire vault/docs/_specs — sources, deprecation notes, report"
sp: 6
status: pending
plan: "plans/202610142247_docs-playbook-on-specs-records/index.md"
---

# M06: Retire vault/docs/_specs — sources, deprecation notes, report

`vault/docs/_specs/` is deleted, no live surface points at it, and the docs playbook's committed report matches its sources.

**Scope:** `vault/docs/_specs/` (deleted), the 32 records whose `sources:` name it, `vault/specs/README.md`, `vault/specs/adr/0001-specs-tiers.md`, `vault/specs/reference/0002-glossary.md`, `vault/specs/reference/0003-documentation-surfaces.md`, `CLAUDE.md`, `vault/_playbooks/docs/_reports/output.md`.

**Test:** `booping specs check --tier project` at its CLI surface, integration tier — zero errors after the delete (the `sources` and `link` checks are the ones the delete would break); a repo grep for `docs/_specs` over live surfaces finds nothing.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | In every `vault/specs/**` record, replace each `sources:` entry `vault/docs/_specs/{file}.md` with `https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/{file}.md` (one `sed` over the files `git grep -l 'vault/docs/_specs' vault/specs` lists); other entries untouched; `updated_at` untouched (provenance fix, not a content change). Then `git rm -r vault/docs/_specs`. | `vault/specs/**`, `vault/docs/_specs/` | 2 | pending |
| 6.2 | Remove the deprecation notes on `vault/docs/_specs/`: `vault/specs/README.md` (the paragraph keeps only the `vault/_lessons/` sentence), adr/0001 Consequences (the bullet keeps only `vault/_lessons/`), `CLAUDE.md` Vault section (replace the `docs/_specs/` sentences with one: the `docs` playbook reads and keeps current the value records, reference/0001–0003 and the story records, its feature index rendered from the stories), reference/0002 **Spec set** entry (the project specs tier records the docs playbook reads), reference/0003 spec-set bullet (if M04 left a deprecation clause). Bump `updated_at` on the edited records. | `vault/specs/README.md`, `vault/specs/adr/0001-specs-tiers.md`, `vault/specs/reference/0002-glossary.md`, `vault/specs/reference/0003-documentation-surfaces.md`, `CLAUDE.md` | 2 | pending |
| 6.3 | Regenerate the committed report: `bin/booping render-playbook docs --stub-macro core.macros.date=2026-10-14 --output vault/_playbooks/docs/_reports/output.md`. | `vault/_playbooks/docs/_reports/output.md` | 1 | pending |
| 6.4 | Stale-reference sweep (rule/0007): `git grep -n 'docs/_specs'` excluding history (`vault/plans`, `vault/retrospectives`, `vault/codereviews`, `vault/researches`, `vault/docs/_runs`, `vault/_playbooks/docs/_specs`, `playbooks/*/_specs`) and the permalinks from 6.1 finds nothing; fix any hit. | any hit | 1 | pending |

## Definition of Done

### Task 6.1

- [ ] `vault/docs/_specs/` does not exist; `vault/docs/` holds `_runs/` and `documented.md`.
- [ ] Every former `vault/docs/_specs/…` source is the pinned permalink; `just specs-check` reports 0 errors.

### Task 6.2

- [ ] None of the five files mentions `docs/_specs` as a live or deprecated location; the `vault/_lessons/` deprecation survives in README and adr/0001.
- [ ] `CLAUDE.md` change is one or two sentences — the map, not the data.

### Task 6.3

- [ ] The report has no `_specs/` path, no `feature-index` row, and no STOP notice.

### Task 6.4

- [ ] The sweep command prints nothing.

## References

- `vault/plans/202610142247_docs-playbook-on-specs-records/clarifications.md` — C6 (permalink), C9 (report), C10 (what stays).
- `src/specs/README.md` — Check (`sources` skips entries containing `://`).

## Verify

```
just specs-check && ! git grep -n 'docs/_specs' -- . ':!vault/plans' ':!vault/retrospectives' ':!vault/codereviews' ':!vault/researches' ':!vault/docs/_runs' ':!vault/_playbooks/docs/_specs' ':!playbooks/*/_specs' | grep -v 'blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e'
```

Final reply: only the list of changed files and the Verify exit status.
