---
title: "Core rules — open items only for what outlives the session, ids with titles in chat, staged experiments"
type: feature
---

# Core rules — open items only for what outlives the session, ids with titles in chat, staged experiments

## Context

Request: [request.md](request.md); items [OI-0033](../../open-items/OI-0033.md) — "Open items: only what outlives the session; ids in chat carry a short summary", [OI-0034](../../open-items/OI-0034.md) — "Experiments run in stages: a cheap screen first, then a shortlist, then significance".

The project-manager `intake` step files "each distinct ask, asides included" (`playbooks/project-manager/intake/prompt.md`), so in-session instructions ("ping me at the release"), gate answers, policies and decisions become open items and bury real work; ids said in chat come bare. Separately, agents launch experiment and eval matrices whole (a 280-call run, stopped by the owner after 104 calls already showed which arms to drop).

After this sprint: an open item is filed only for what must outlive the session; every id said in chat carries its short title and newly filed items are listed as `Создан OI-NNNN: {title}`; an experiment runs cheap screen → shortlist → significance, each stage sized before launch. All three ship as core rules (`specs/rule/`), so every user's runs get them.

Values in play: value/0002 Minimal effective context (open items stay a short index of real work; rule briefs one line), value/0008 Effective human review (an id with its title is readable at a glance), value/0012 Quality at a rational cost (staged experiments spend budget only on arms that survive a screen), value/0003 Single source (a policy goes to a rule, a decision to an ADR — not duplicated into an item).

## Decisions

1. An open item is filed only for what must outlive the session: work for later (a feature, a bug, a fix, a scope question) or a question for the owner that waits for an answer. (user, OI-0033 d1)
2. Not an item: an instruction for this session ("ping me", "wait", "do it now"), an answer to a gate or a UAT confirmation, a standing policy (→ a rule through `specs`), a decision (→ an ADR); the agent does it or keeps it in the session. (user, OI-0033 d2)
3. The intake step's "each distinct ask, asides included" is replaced by the filter of 1–2. (user, OI-0033 d3)
4. Core rule "Open items hold only what outlives the session", `targets: [project-manager, specs]`. (user, OI-0033 d4)
5. Every id said in chat (OI, ADR, rule, …) carries its short title; newly filed items are listed as `Создан OI-NNNN: {title}`. Its own core rule record, untargeted, carried by the driving protocol like rule/0032 and rule/0033. (user, OI-0033 d5–d6)
6. An eval fixture for `intake`: "пингани, как будет релиз" and "пауза pi на 2 часа" file no item. (user, OI-0033 d7)
7. Experiments run in stages: a cheap screen on a small sample, a shortlist on more cases, significance only for finalists when needed; before each stage the agent names its size (calls, rough cost) and what it decides; a stage past a small screen without a reason is not launched. Core rule, untargeted, one-line brief. (user, OI-0034 d1–d3)
8. The experiments rule reaches runs through the driving protocol and non-playbook sessions through the session-start block — the only surface such a session loads. (proposal)
9. The filed-items line follows the user's language: `Создан {id}: {title}` in Russian (the owner's locked wording), `Created {id}: {title}` in English. [clarify] — departs from the literal Russian-only wording of OI-0033 d5, since core prompts serve every user. (proposal)
10. A smalltalk aside that is real later work (the README version fix in the existing `two-requests-and-an-aside` fixture) still files an item — it passes filter 1; that case keeps its three items. (proposal)
11. Rule ids: the next three free core ids, taken with `bin/booping specs next rule --tier core` at write time (0037–0039 today). (proposal)
12. The open-items audit OI-0033 asked for is not in this sprint: the decisions above already turned it into rules; closing stale items is specs / project-manager work. (proposal)
13. Snapshot reports that drift (`playbooks/project-manager/_reports/output.md`, `playbooks/specs/_reports/output.md`) are left for the owner to accept with `just snapshots-accept`; no worker writes `_reports/`. (proposal)

## Architecture

- Rule records live in the core tier `specs/rule/`; `targets:` + `brief:` inject a rule into the targeted playbooks' renders (`render-playbook`), an untargeted rule injects nowhere and is carried by prose — here the driving protocol `src/templates/_partials/_playbook_driving.j2` (included by `src/templates/skills/playbook.md.j2`, so every `/playbook` run) and the session-start block `src/templates/hooks/session_start.md.j2` (every session in a booping project).
- The intake filter is prose in `playbooks/project-manager/intake/prompt.md`, read by the model only (rule/0025) — no CLI.
- Contract pins: e2e `booping-python/e2e/cases/render/driving-protocol-carries-both-modes.txtar` (grep-filtered, untouched by new lines outside its filter) and `booping-python/e2e/cases/render/session-start-block-lists-project-and-global-playbooks.txtar` (full block, rebaselined).

## Milestones

### M01 — Three core rule records

sp: 5
depends_on: []

#### Tasks

**Goal:** three accepted core rules exist in `specs/rule/` and pass `just specs-check`.
**Scope:** `specs/rule/` only; read by `render-playbook` rule injection (targeted one) and by the driving protocol / session start prose (M02).
**Tests:** surface `bin/booping specs check` over the core tier; cases — each record's frontmatter and H2 order valid, the targeted rule's `targets`/`brief` present; tier — the existing `just specs-check` integration check.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Rule "Open items hold only what outlives the session": `## Rule` states decisions 1–2 (what is an item, what is not and where it goes instead); `targets: [project-manager, specs]`; one-line `brief`; `## Follows from` links value/0002 and value/0003 plus the evidence as "an audit of another booping project: 11 of 34 open items were never work (private note, not published)", no link. | `specs/rule/{id}-open-items-outlive-the-session.md` | 2 | pending |
| 1.2 | Rule "Ids in chat carry their title": every id said in chat (OI, ADR, rule, plan, …) is followed by its short title; newly filed items are listed one per line, `Создан {id}: {title}` / `Created {id}: {title}` in the user's language; untargeted, body states the driving protocol carries it (wording shape of rule/0032's last paragraph); `## Follows from` value/0008, value/0013. | `specs/rule/{id}-ids-carry-their-title.md` | 1 | pending |
| 1.3 | Rule "Experiments run in stages": decision 7 in `## Rule`; untargeted, body states the driving protocol and the session-start block carry it; `brief` one line; `## Follows from` value/0012, value/0010, and the origin incident (2026-10-19, a 280-call matrix stopped after 104 calls showed the arms to drop) in aggregate words, no private data. | `specs/rule/{id}-experiments-run-in-stages.md` | 2 | pending |

#### Definition of Done

Task 1.1
- [ ] Id taken with `bin/booping specs next rule --tier core`; `status: accepted`, `created_by: claude`, dates 2026-10-19.
- [ ] `## Rule` lists both what is filed and the four non-item kinds with their destinations (session, rule via `specs`, ADR).
- [ ] `targets: [project-manager, specs]` and a one-line `brief`.
- [ ] No other project's name, no absolute path, no `/tmp/` in the file.

Task 1.2
- [ ] Untargeted (no `targets`, no `brief`); body names `src/templates/_partials/_playbook_driving.j2` as the carrier.
- [ ] Both language forms of the filed-items line given literally.

Task 1.3
- [ ] Untargeted; body names the driving protocol and `src/templates/hooks/session_start.md.j2` as carriers.
- [ ] The three stages and the before-each-stage sizing (calls, rough cost, what it decides) are each stated.

#### References

- `specs/rule/0035-same-class-items-groomed-together.md` — targeted rule shape.
- `specs/rule/0032-approval-asked-in-prose.md` — untargeted, protocol-carried shape.
- `src/specs/schemas/rule.yaml` — the contract.

#### Verify

`just specs-check`

### M02 — Driving protocol and session start carry the untargeted rules

sp: 5
depends_on: [M01]

#### Tasks

**Goal:** every `/playbook` render carries the ids-with-titles and staged-experiments lines; every booping session's start block carries the staged-experiments line.
**Scope:** `src/templates/_partials/_playbook_driving.j2`, `src/templates/hooks/session_start.md.j2`, the two e2e render cases; no config keys.
**Tests:** surface `booping render` of the skill and the session-start template; cases — the skill render carries both new lines, the session-start block carries the experiments line; tier — e2e txtar contract.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Add to the driving protocol one line: every id said in chat carries its short title, filed items listed `Создан {id}: {title}` / `Created {id}: {title}` in the user's language, linking M01's rule; and one line: an experiment, eval or benchmark matrix runs cheap screen → shortlist → significance, each stage's size (calls, rough cost) and what it decides named before launch, linking M01's rule. Place them where the protocol speaks of chat output (near the completion report / questions paragraph), one paragraph each, no restated rule body. | `src/templates/_partials/_playbook_driving.j2` | 2 | pending |
| 2.2 | Add one line to the session-start block: experiments run in stages, size named before each stage, linking the rule record by `${CLAUDE_PLUGIN_ROOT}` path. | `src/templates/hooks/session_start.md.j2` | 1 | pending |
| 2.3 | Rebaseline the session-start e2e case; add an e2e render case pinning the two new driving-protocol lines (grep-filtered like `driving-protocol-carries-both-modes.txtar`). | `booping-python/e2e/cases/render/session-start-block-lists-project-and-global-playbooks.txtar`, `booping-python/e2e/cases/render/driving-protocol-carries-ids-and-experiments.txtar` | 2 | pending |

#### Definition of Done

Task 2.1
- [ ] `bin/booping render src/templates/skills/playbook.md.j2` shows both lines once each, links resolving to the M01 records.
- [ ] No other line of the partial changed; `driving-protocol-carries-both-modes.txtar` passes unchanged.

Task 2.2
- [ ] The block grows by one line; nothing else in it changes; silent-outside-a-project behaviour of `hooks/session-start.sh` untouched.

Task 2.3
- [ ] The rebaselined case differs from its old baseline only by the new line.
- [ ] The new case fails if either driving-protocol line is removed.

#### References

- `booping-python/e2e/cases/render/driving-protocol-carries-both-modes.txtar` — grep-filtered render case shape.
- `specs/rule/0032-approval-asked-in-prose.md` — how a protocol-carried rule names its carrier.

#### Verify

`just e2e -k "driving-protocol or session-start"`

### M03 — Project-manager intake files only what outlives the session

sp: 6
depends_on: [M01]

#### Tasks

**Goal:** intake files an item only for later work or a waiting owner question, keeps session instructions, gate answers, policies and decisions out, and lists filed items as `Создан {id}: {title}` / `Created {id}: {title}`.
**Scope:** `playbooks/project-manager/intake/` (prompt, tests, fixtures); the targeted rule from M01 reaches this step through `render-playbook`.
**Tests:** surface the intake step under the promptfoo smoke harness; cases — "пингани, как будет релиз" files nothing, "пауза pi на 2 часа" files nothing, two requests + a real-work aside still file three, the filed-ids reply uses the new line; tier — smoke (deterministic asserts on written files and the return).

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Replace "each distinct ask, asides included" with the filter: a request is filed only when it must outlive the session — work for later or a question waiting on the owner; an instruction for this session, a gate answer or UAT confirmation, a standing policy (→ `specs` rule) or a decision (→ ADR) files nothing and is done or kept in the session. Change the final posting line to `Создан {id}: {title}` / `Created {id}: {title}`, one line each, in the user's language. Keep the verbatim-heredoc and answer paragraphs as they are. | `playbooks/project-manager/intake/prompt.md` | 2 | pending |
| 3.2 | Two new smoke fixtures + cases, Russian dialogues: "пингани, как будет релиз" and "пауза pi на 2 часа" — each asserts no file written (`allow_no_files` already on). | `playbooks/project-manager/intake/_fixtures/session-instruction-ping.md`, `playbooks/project-manager/intake/_fixtures/session-instruction-pause.md`, `playbooks/project-manager/intake/tests.yaml` | 3 | pending |
| 3.3 | Update the `filed-ids-posted` case's ONE-LINE-PER-ITEM asserts to the new line — an entry regex for `Created OI-000N: {title}` (or `Создан`, matching the fixture's language) at line start. | `playbooks/project-manager/intake/tests.yaml` | 1 | pending |

#### Definition of Done

Task 3.1
- [ ] The phrase "asides included" is gone from the prompt; the filter names both item kinds and the four non-item kinds with their destinations.
- [ ] `bin/booping render-playbook project-manager --step intake` shows the new filter and the M01 rule under `## Rules`.

Task 3.2
- [ ] Both new cases pass under `just smoke project-manager/intake`; the fixtures follow `two-requests-and-an-aside.md`'s shape (no shell, stated outputs).

Task 3.3
- [ ] `two-requests-and-an-aside`, `answer-only` and `filed-ids-posted` still pass.

#### References

- `playbooks/project-manager/intake/_fixtures/answer-only.md` — a no-new-item fixture.
- `playbooks/project-manager/intake/tests.yaml` — case and assert shapes.

#### Verify

`just smoke project-manager/intake`

### M04 — Docs say only what outlives the session is filed

sp: 2
depends_on: [M03]

#### Tasks

**Goal:** the public docs and the playbook summary describe the new intake filter, not "every request, asides included".
**Scope:** `documentation/project_manager.md`, `README.md`, `playbooks/project-manager/playbook.md` (summary frontmatter only).
**Tests:** none beyond the grep in Verify — prose only.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Rewrite the "Every message" paragraph: only what outlives the session becomes an item; session instructions, gate answers, policies and decisions do not; filed ids listed with their titles. Align README's project-manager sentence and the playbook `summary:`. | `documentation/project_manager.md`, `README.md`, `playbooks/project-manager/playbook.md` | 2 | pending |

#### Definition of Done

Task 4.1
- [ ] Audience filter: only what a user of the manager sees — which messages become items, how ids appear; no rule ids, no internal step names beyond `project-manager`.
- [ ] "asides included" and "every request" appear in none of the three files.

#### References

- `documentation/project_manager.md` — the paragraph at "**Every message.**".

#### Verify

`! grep -rn -i "asides included\|every request" documentation/project_manager.md README.md playbooks/project-manager/playbook.md`

## Final Verification

- [ ] `bin/booping render src/templates/skills/playbook.md.j2` produces clean output carrying both new driving-protocol lines.
- [ ] `bin/booping render-playbook project-manager` and `bin/booping render-playbook specs` list the open-items rule under `## Rules`.
- [ ] `just ci` green except `just snapshots`, whose diff touches only `playbooks/project-manager/_reports/output.md` and `playbooks/specs/_reports/output.md` and is left for the owner to accept.
- [ ] Worker return per milestone: the changed file paths, one per line, and the Verify command's exit code — nothing else.

## Out of scope

- Auditing and closing this project's existing open items (decision 12).
- `vault/story/0023-project-manager.md` line 16 ("asides included") is made untrue by M03; it is vault, the driver's, and goes to a `specs` run after the sprint — recorded as a departure, story/0023, [clarify].
- No config keys, no CLI change, no new playbook step.
- `just snapshots-accept` — the owner's.

## CLAUDE.md impact

No CLAUDE.md changes required — no config key, partial API or rendered-artifact path changes; CLAUDE.md describes neither the intake filter nor individual core rules.
