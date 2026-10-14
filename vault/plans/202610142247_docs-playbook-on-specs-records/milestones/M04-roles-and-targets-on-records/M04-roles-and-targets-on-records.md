---
id: "04"
title: "Roles and targets refresh reference/0001 and reference/0003"
sp: 4
status: done
plan: "plans/202610142247_docs-playbook-on-specs-records/index.md"
---

# M04: Roles and targets refresh reference/0001 and reference/0003

`roles` refreshes the audience record reference/0001 and `targets` the surfaces record reference/0003, in the reference record shape, instead of writing `_specs/roles.md` and `_specs/targets.md`.

**Scope:** `vault/_playbooks/docs/roles/fable-5.md`, `vault/_playbooks/docs/roles/prompt.md`, `vault/_playbooks/docs/targets/fable-5.md`, `vault/_playbooks/docs/targets/prompt.md`.

**Test:** each step's fetched body at the CLI surface, integration tier — renders, names no `_specs/` path, names its record by path.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | `roles`: inputs are the run record's `## Briefing` and reference/0001 (`{vault}/specs/reference/0001-audience.md`); it rewrites that record's `## Facts` in place — one fact per bullet, per role who / comes for / depth / withheld / voice / reads as the record writes them today; frontmatter untouched except `updated_at` (today); never `reviewed`; a default it chose is marked `[clarify]` (rule/0002). Never reads reference/0003 (sibling in the same wave). Return names the record and per-role digest + drift lines; prompt `summary` and `review_gate` name the record and `awaiting-roles-targets-confirm`. | `vault/_playbooks/docs/roles/fable-5.md`, `vault/_playbooks/docs/roles/prompt.md` | 2 | done |
| 4.2 | `targets`: refreshes `{vault}/specs/reference/0003-documentation-surfaces.md` `## Facts` — one bullet per surface (path, audience, depth ceiling, conventions), the `CHANGELOG.md` bullet always, the spec-set bullet always (the project specs tier records the docs playbook reads — value records, reference/0001–0003, story records — audience Claude itself), and the closing "Not surfaces" bullet; frontmatter as in 4.1. Never edits reference/0001. Return and prompt `summary` follow. | `vault/_playbooks/docs/targets/fable-5.md`, `vault/_playbooks/docs/targets/prompt.md` | 2 | done |

## Definition of Done

### Task 4.1

- [x] `roles` body and prompt name no `_specs/` path; the record path is named once.
- [x] `updated_at` bump, `reviewed` never touched, `[clarify]` for defaults — each stated once.
- [x] Output shape is the reference record's `## Facts` bullets (`src/specs/schemas/reference.yaml`), not the old five-bullet sections.

### Task 4.2

- [x] `targets` body and prompt name no `_specs/` path; the spec-set bullet describes the records, not a `docs/_specs/` directory.
- [x] Frontmatter rule identical to 4.1.

## References

- `vault/specs/reference/0001-audience.md`, `vault/specs/reference/0003-documentation-surfaces.md` — the records these steps write; copy their bullet style.
- `src/specs/schemas/reference.yaml` — the record shape `booping specs check` enforces.

## Verify

```
for s in roles targets; do bin/booping render-playbook docs --step $s > /tmp/docs-m04-$s.md || exit 1; done; ! grep -n '_specs/' /tmp/docs-m04-roles.md /tmp/docs-m04-targets.md && grep -l 'reference/0001-audience.md' /tmp/docs-m04-roles.md && grep -l 'reference/0003-documentation-surfaces.md' /tmp/docs-m04-targets.md
```

Final reply: only the list of changed files and the Verify exit status.
