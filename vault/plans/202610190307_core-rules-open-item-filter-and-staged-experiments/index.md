---
title: "Core rules — open items only for what outlives the session, ids with titles
  in chat, staged experiments"
type: "feature"
status: done
sp: 18
related_to: null
created: 2026-10-19 03:08
planned: null
started: 2026-10-19 03:15
completed: 2026-10-19 03:27
code_reviews: []
sessions:
- 4e6bc07e-78db-5a84-9b90-8cf66430bb73
- 6b1a350c-f2b9-578a-8dd5-509a79cd2988
retro: null
summary: 'Core rules: open items only for what outlives the session, ids in chat with
  titles, experiments in staged screens'
commit: 1cc3de8662c78440c5fa7aa84852ad723f02d85a
tracker_provider: null
tracker_request: null
tracker_issue: null
return_to: null
reviewed_at: 2026-10-19 03:12
agents: '{"develop-loop-G1": "a07de547e56912a52", "develop-loop-G2": "a072e5616c347544c"}'
metrics_active_minutes: 18
metrics_models:
- claude-opus-5-5
metrics_tokens_input: 120
metrics_tokens_output: 38038
metrics_tokens_cache_creation: 189098
metrics_tokens_cache_read: 4861651
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

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [Three core rule records](milestones/M01-three-core-rule-records/M01-three-core-rule-records.md) | 5 | done |
| 02 | [Driving protocol and session start carry the untargeted rules](milestones/M02-driving-protocol-and-session-start-carry-the-untargeted-rules/M02-driving-protocol-and-session-start-carry-the-untargeted-rules.md) | 5 | done |
| 03 | [Project-manager intake files only what outlives the session](milestones/M03-project-manager-intake-files-only-what-outlives-the-session/M03-project-manager-intake-files-only-what-outlives-the-session.md) | 6 | done |
| 04 | [Docs say only what outlives the session is filed](milestones/M04-docs-say-only-what-outlives-the-session-is-filed/M04-docs-say-only-what-outlives-the-session-is-filed.md) | 2 | done |

## Groups

| group | milestones | sp |
| --- | --- | --- |
| G1 | M01, M02 | 10 |
| G2 | M03, M04 | 8 |

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
