---
id: "05"
title: "Research, sync-specs and targeting work on records"
sp: 10
status: pending
plan: "plans/202610142247_docs-playbook-on-specs-records/index.md"
---

# M05: Research, sync-specs and targeting work on records

The change-set steps read the records — the feature index rendered from story records — and `sync-specs` folds the confirmed change table into the records, marking what the table does not settle, instead of rewriting `_specs/` files.

**Scope:** `vault/_playbooks/docs/research/opus-5.md` + `prompt.md`, `vault/_playbooks/docs/sync-specs/opus-5.md` + `prompt.md`, `vault/_playbooks/docs/targeting/opus-5.md` + `prompt.md`, and `_specs`/"roles file" wording in `write/fable-5.md`, `verify/opus-5.md`, `record/opus-5.md`.

**Test:** each step's fetched body at the CLI surface, integration tier — renders, names no `_specs/` path; `research` and `targeting` carry the rendered feature index (a story title such as `Playbook driver` appears).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | `research`: render the value list and the feature index (`core.docs_playbook.queries.values`, `core.docs_playbook.queries.features`) into the body; read reference/0001 and reference/0003 itself; the sub-agent brief carries the vision in a line, role names with depth (reference/0001), surface paths with audience and depth (reference/0003) and story titles; **Audience** cells come from reference/0001, **Target files** from reference/0003, the **Spec-set effect** column names the record a row moves (`story/0004`, `reference/0001`, a new story) or `none`. Prompt `summary` follows. | `vault/_playbooks/docs/research/opus-5.md`, `vault/_playbooks/docs/research/prompt.md` | 3 | pending |
| 5.2 | `sync-specs`: the landing table becomes records — vision-shift row → a `[clarify]` sentence in the affected value record's `## In practice`, the value's statement never rewritten; audience → reference/0001; surface → reference/0003; term → reference/0002; new feature → a new story record (next number in `specs/story/`, `created_by: claude`, `status: done`, the story schema's shape); refactoring → that story's criteria edited in place; feature drop → a `[clarify]` mark in the story, status untouched. Fold rules: edit only what a confirmed row says; what it does not settle → `[clarify]`; a row that itself records a disagreement between a record and the code without settling which is right → `[unknown]` on that record (rule/0002) — `sync-specs` still reads no code and detects nothing itself; every edited record bumps `updated_at`, never `reviewed`; the step ends by running `booping specs check --tier project` and reports its result line. Return lists each record as `[CREATED|UPDATED]`; prompt `summary` follows. | `vault/_playbooks/docs/sync-specs/opus-5.md`, `vault/_playbooks/docs/sync-specs/prompt.md` | 4 | pending |
| 5.3 | `targeting`: render the feature index into the body; the `booping:booping-researcher` brief covers reference/0001 and reference/0003 (not `_specs/` files) with the same per-surface / per-role return; a change is placed under the story it moves — for a new-feature row, the story `sync-specs` created for it; a change no story covers is placed by surface alone, its **Must say** cell opening `no story —`, never a home invented for it (groups are gone). Prompt `summary` follows if it names `_specs/`. | `vault/_playbooks/docs/targeting/opus-5.md`, `vault/_playbooks/docs/targeting/prompt.md` | 2 | pending |
| 5.4 | Wording: `write` and `verify` say "the audience record" / "the spec records" where they say "roles file" / "briefing, roles, surfaces or feature index"; `record` names the ledger `{vault}/docs/documented.md`. No behaviour change. | `vault/_playbooks/docs/write/fable-5.md`, `vault/_playbooks/docs/verify/opus-5.md`, `vault/_playbooks/docs/record/opus-5.md` | 1 | pending |

## Definition of Done

### Task 5.1

- [ ] `research` renders both query specs; no story or value title hand-typed.
- [ ] Audience / Target files sources are reference/0001 / reference/0003 by path.

### Task 5.2

- [ ] The landing table maps every row type (vision shift, new feature, refactoring, feature drop, chore, audience, surface, term) to one record action, as in the task description.
- [ ] Value statements are never rewritten; `reviewed` never written; `[clarify]` / `[unknown]` rules cite rule/0002.
- [ ] The step's last action is `booping specs check --tier project`, its result in the return.

### Task 5.3

- [ ] `targeting` names no `_specs/` path and no feature group; placement is by story.

### Task 5.4

- [ ] `rg -n '_specs/|roles file' vault/_playbooks/docs/{write,verify,record}` finds nothing.

## References

- `vault/_playbooks/docs/sync-specs/opus-5.md` — current landing table and fold rules; keep the table form.
- `src/specs/schemas/story.yaml`, `src/specs/README.md` (Body, Marks) — the shapes a fold must keep.
- `vault/plans/202610142247_docs-playbook-on-specs-records/clarifications.md` — C4, C5.

## Verify

```
for s in research sync-specs targeting write verify record; do bin/booping render-playbook docs --step $s > /tmp/docs-m05-$s.md || exit 1; done; ! grep -n '_specs/' /tmp/docs-m05-*.md && grep -c 'Playbook driver' /tmp/docs-m05-research.md /tmp/docs-m05-targeting.md
```

Final reply: only the list of changed files and the Verify output's last line.
