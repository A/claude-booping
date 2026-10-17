---
id: "02"
title: "Manifest and guidance on records — feature-index step and its gate removed"
sp: 5
status: done
plan: "plans/202610142247_docs-playbook-on-specs-records/index.md"
---

# M02: Manifest and guidance on records — feature-index step and its gate removed

The docs playbook's graph, state machine and preamble describe a spec set made of specs records: no `feature-index` step, no `awaiting-features-confirm` gate, and every review stamp on the run record.

**Scope:** `vault/_playbooks/docs/playbook.yaml`, `vault/_playbooks/docs/playbook.md`, `vault/_playbooks/docs/feature-index/` (deleted). Step bodies are M03–M05.

**Test:** the composed render (`bin/booping render-playbook docs`) at the CLI surface, integration tier — it renders with no STOP notice, its step table has no `feature-index` row, and its State table has no `awaiting-features-confirm` status and no hook naming a `_specs/` file.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | `playbook.yaml`: drop the `feature-index` node (`research` depends on `[roles, targets]`) and delete `vault/_playbooks/docs/feature-index/`; drop `awaiting-features-confirm` (and from the `spec-set` superstate); `spec-building` → `awaiting-roles-targets-confirm` when roles and targets each refreshed their record; the roles-and-targets confirm edge goes to `researching` with hooks `frontmatter-update specs_reviewed_at=…` and `script commit-docs`; the briefing confirm edge stamps `briefing_reviewed_at=…` on the run record (bare `frontmatter-update`, no file argument); the `briefing` exit `when:` names the run record's `## Briefing` section and the vision shift against the previous run's; the scope edges speak of spec records, not spec files. No hook names a `_specs/` path. | `vault/_playbooks/docs/playbook.yaml`, `vault/_playbooks/docs/feature-index/` | 3 | done |
| 2.2 | `playbook.md` Guidance: the spec set is the project specs tier records — the value records (`core.docs_playbook.queries.values`), reference/0001 audience, reference/0002 glossary, reference/0003 surfaces, the story records (the feature index, `core.docs_playbook.queries.features`, rendered and never stored); the ledger is `{vault}/docs/documented.md`; a step that edits a record bumps `updated_at`, never sets `reviewed` (the owner's, `src/specs/README.md`), and marks what its source does not settle `[clarify]` / `[unknown]` per rule/0002. Keep the "both context and target" point in one sentence, naming reference/0003's spec-set fact instead of a `_specs/` row. Pass the four-check information-architecture pass (rule/0006) over every changed block; refer to the query keys, never restate a glob. | `vault/_playbooks/docs/playbook.md` | 2 | done |

## Definition of Done

### Task 2.1

- [x] `vault/_playbooks/docs/feature-index/` no longer exists.
- [x] `playbook.yaml` contains no `feature-index`, no `awaiting-features-confirm`, no `_specs/`.
- [x] Briefing confirm edge stamps `briefing_reviewed_at`; roles-and-targets confirm edge stamps `specs_reviewed_at` and runs `script commit-docs`.
- [x] The composed render has no STOP notice.

### Task 2.2

- [x] `playbook.md` contains no `_specs/` path and names the ledger at `{vault}/docs/documented.md`.
- [x] The two query keys are named by dotted path; no glob literal restated in prose.
- [x] `reviewed` is stated as never written by a step; `updated_at` bump and rule/0002 marks stated once.

## References

- `vault/_playbooks/docs/playbook.yaml` — the current manifest; keep its hook and gate wording style.
- `src/specs/README.md` — Frontmatter (`reviewed`, `updated_at`) and Marks.
- `vault/plans/202610142247_docs-playbook-on-specs-records/clarifications.md` — C2, C3, C4, C7 settle the shapes named here.

## Verify

```
bin/booping render-playbook docs > /tmp/docs-m02.md && ! grep -nE 'STOP — tell the user|feature-index|awaiting-features-confirm|frontmatter-update _specs/' /tmp/docs-m02.md
```

Final reply: only the list of changed files and the Verify exit status.
