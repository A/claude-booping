---
id: "01"
title: "Three core rule records"
sp: 5
status: done
plan: "plans/202610190307_core-rules-open-item-filter-and-staged-experiments/index.md"
---

# M01: Three core rule records

## Tasks

**Goal:** three accepted core rules exist in `specs/rule/` and pass `just specs-check`.
**Scope:** `specs/rule/` only; read by `render-playbook` rule injection (targeted one) and by the driving protocol / session start prose (M02).
**Tests:** surface `bin/booping specs check` over the core tier; cases — each record's frontmatter and H2 order valid, the targeted rule's `targets`/`brief` present; tier — the existing `just specs-check` integration check.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Rule "Open items hold only what outlives the session": `## Rule` states decisions 1–2 (what is an item, what is not and where it goes instead); `targets: [project-manager, specs]`; one-line `brief`; `## Follows from` links value/0002 and value/0003 plus the evidence as "an audit of another booping project: 11 of 34 open items were never work (private note, not published)", no link. | `specs/rule/{id}-open-items-outlive-the-session.md` | 2 | done |
| 1.2 | Rule "Ids in chat carry their title": every id said in chat (OI, ADR, rule, plan, …) is followed by its short title; newly filed items are listed one per line, `Создан {id}: {title}` / `Created {id}: {title}` in the user's language; untargeted, body states the driving protocol carries it (wording shape of rule/0032's last paragraph); `## Follows from` value/0008, value/0013. | `specs/rule/{id}-ids-carry-their-title.md` | 1 | done |
| 1.3 | Rule "Experiments run in stages": decision 7 in `## Rule`; untargeted, body states the driving protocol and the session-start block carry it; `brief` one line; `## Follows from` value/0012, value/0010, and the origin incident (2026-10-19, a 280-call matrix stopped after 104 calls showed the arms to drop) in aggregate words, no private data. | `specs/rule/{id}-experiments-run-in-stages.md` | 2 | done |

## Definition of Done

Task 1.1
- [x] Id taken with `bin/booping specs next rule --tier core`; `status: accepted`, `created_by: claude`, dates 2026-10-19.
- [x] `## Rule` lists both what is filed and the four non-item kinds with their destinations (session, rule via `specs`, ADR).
- [x] `targets: [project-manager, specs]` and a one-line `brief`.
- [x] No other project's name, no absolute path, no `/tmp/` in the file.

Task 1.2
- [x] Untargeted (no `targets`, no `brief`); body names `src/templates/_partials/_playbook_driving.j2` as the carrier.
- [x] Both language forms of the filed-items line given literally.

Task 1.3
- [x] Untargeted; body names the driving protocol and `src/templates/hooks/session_start.md.j2` as carriers.
- [x] The three stages and the before-each-stage sizing (calls, rough cost, what it decides) are each stated.

## References

- `specs/rule/0035-same-class-items-groomed-together.md` — targeted rule shape.
- `specs/rule/0032-approval-asked-in-prose.md` — untargeted, protocol-carried shape.
- `src/specs/schemas/rule.yaml` — the contract.

## Verify

`just specs-check`
