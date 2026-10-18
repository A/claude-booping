---
title: "Specs acceptance — ADR brief, review levels, ADR scoring, session entry to
  playbooks"
type: "feature"
status: done
sp: 34
related_to: null
created: 2026-10-19 00:29
planned: null
started: 2026-10-19 00:54
completed: 2026-10-19 01:22
code_reviews: []
sessions:
- 7dec7bb9-8bf9-4660-a129-8472076ab1bb
- 9dda877a-edbb-599f-a8d2-e9ce64a7f339
retro: null
summary: ADR accepted after a brief with an objection window, review levels with
  evidence, a cheap ADR scorer, session start points to playbooks
commit: de14fdcbee1f25f2647d64d37422b4542651b7a0
tracker_provider: null
tracker_request: null
tracker_issue: null
return_to: null
reviewed_at: 2026-10-19 00:53
metrics_active_minutes: 51
metrics_models:
- claude-opus-5-5
metrics_tokens_input: 248
metrics_tokens_output: 99617
metrics_tokens_cache_creation: 318050
metrics_tokens_cache_read: 17909422
---

# Specs acceptance — ADR brief, review levels, ADR scoring, session entry to playbooks

## Context

Four open items (OI-0029..OI-0032), one change. A session working on a booping project outside a playbook never meets the core rules or the specs guidance — they reach an agent only through `render-playbook`, agent and skill bodies. On 2026-10-18 that let a session in another booping project accept two ADRs and dispatch developers without the owner seeing the decision, its alternatives or the ADR it partly reversed; and a session here proposed a new status without checking the existing `reviewed` field.

After this sprint:

- every session in a booping project starts knowing which playbook its work belongs to and offers it (the `SessionStart` hook);
- an ADR is accepted after a brief the owner can object to, never silently;
- a record carries how far the owner engaged with it — `shown`, `discussed`, `accepted` — with the evidence, instead of a bare `reviewed` date;
- a new ADR's alternatives are scored by a context-free subagent before the brief.

Values in play: value/0009 Adjustable control and value/0008 Effective human review drive the brief and the levels; value/0016 Specs live with the work drives the session entry; value/0003 Single source keeps the playbook table rendered from the one playbook list. Departures are listed under Decisions.

Records: adr/0039 (session start points to playbooks) and adr/0040 (review levels with evidence) are drafted `proposed`; the driver accepts them through the brief this plan builds.

## Decisions

1. Accepting an ADR does not wait for a "yes": the agent shows the brief and asks for objections; none → it goes on. (user)
2. The brief is a table of the chosen and rejected options with the reason, then the chosen decision's key points so nothing important is confirmed unseen, what it touches or reverses, what the agent decided alone, and the score. Its exact content is locked below. (user + proposal)
3. The objection ask is gentle: "Если что-то не так — скажи, поправлю; если всё ок — продолжаю." (user asked for gentler wording; the line is a proposal)
4. Review levels form an axis beside `status`: no key / `shown` / `discussed` / `accepted`. They replace `reviewed`. (user; the name `shown` is a proposal — named by what the agent can prove)
5. Frontmatter: two flat keys, `review: {level}` and `review_evidence: "{evidence}"` — flat because Obsidian cannot address nested YAML as a column (precedent: migrations/003). (proposal)
6. Evidence: `accepted` needs the owner's words quoted plus date and where (`«ок, принимаем» — 2026-10-19, chat`); `discussed` the same with the discussion's gist; `shown` the date and where the brief was shown. (user for `accepted`; the rest proposal)
7. An agent may set a level, only with its evidence; never `accepted` without a quote of the owner. (proposal — today only the owner sets `reviewed`)
8. The site's "mark reviewed" becomes "accepted": the Outbox line is `{ref} — accepted {date}`, and the guide turns it into `review: accepted` with evidence `site review — {date}`. (proposal)
9. A record still carrying `reviewed:` is an error in `booping specs check`, naming the replacement; no migration ships — no known record carries the key (0 here, 0 in the other booping projects on this machine). (proposal)
10. `booping status` counts records not explicitly accepted, split by level: `records: {n} not accepted — none {a}, shown {b}, discussed {c}` plus the per-type breakdown it already prints. (proposal)
11. In an autonomous run the brief is logged as an agent decision instead of shown; the ADR is accepted with no `review` key. (proposal, follows adr/0036)
12. The ADR scorer runs inside the guide's `## Record` scenario before the brief: an agent gets the ADR text and the rubric inline in its prompt and has no tools, so it reads no file and loads no project context; it returns a 0–3 score and one line per finding; ≤ 1 sends the draft back for at most two rounds, then the brief carries the score as it stands. (user: Opus, no file reads; threshold and rounds proposal)
13. The scorer's rubric is yesterday's audit rubric (plan file `adr-audit-ground-truth.md`), with the guide's cheap options — prose, extending an existing primitive, building nothing — named in it. (user: "с учетом вчерашнего опыта")
14. The scorer runs on Opus, per rule/0031; no cheaper model is measured. (user)
15. The `SessionStart` hook is silent outside a project with a `.booping` marker and never blocks a session: any failure exits 0 with no output. (proposal)
16. The hook injects prose on when to use playbooks and a two-column table, Playbook | Trigger (~3 KB here), rendered from the same playbook list as `/playbook`; the manager is the default offer; it is never loaded at start — a project that wants it says so in its CLAUDE.md. (user; the two columns and the not-loaded default proposal)
17. A core rule record carries the brief-before-acceptance rule, targeting `specs`. (proposal from the ADR drafting pass)
18. What an ADR is and how it is checked stays core; project overrides use the tier `_schemas/` overlay and targeted rules — no new mechanism. (user)

### Locked output: the ADR brief

```
**ADR {NNNN} — {title}** · {status} · оценка альтернатив {score}/3{; findings if < 3}

| | вариант | почему |
|---|---|---|
| ✔ | {chosen option} | {its reason} |
| ✘ | {rejected option} | {why rejected} |

Ключевые моменты:
1. {each point of the chosen decision a reader must see to object to it}

Задевает: {ADR/value refs and how — "разворачивает ADR N" for a reversal} 
Решил сам: {each call the agent made alone, or "ничего"}

Если что-то не так — скажи, поправлю; если всё ок — продолжаю.
```

### Locked output: the session-start block

```
## booping

This repo is a booping project. Project work a playbook below fits — a decision or ADR, a spec record, a plan, a sprint, a review, a retro — goes through that playbook: offer it to the user by name and, once they agree, run `/booping:playbook {name}`; its render brings the project's rules. Project work nothing narrower fits → offer `project-manager`. Questions, explanations and debugging need no playbook.

| Playbook | Trigger |
| --- | --- |
| {name} | {trigger} |
```

## Architecture

- Review levels: `booping-python/src/booping/specs/records.py` owns the reading (`unreviewed()` becomes a level reader); `status.py`, the site (`specs/site/state.py`, `machine.py`, `pages.py`, `search.py`, `comments*.js`, templates) and `booping specs check` read it. The guide (`src/specs/README.md`) documents the keys; the specs playbook's guide step writes them.
- ADR flow: `playbooks/specs/guide/prompt.md` `## Record` — draft → scorer subagent → redraft if ≤ 1 → brief → accept with the level. The rubric is a lazy-loaded file beside the step. The core rule record (`specs/rule/0036-…`) targets `specs`, so `render-playbook specs` injects its brief.
- Session entry: `.claude-plugin/plugin.json` gains a `hooks.SessionStart` entry running `hooks/session-start.sh`, which walks up for `.booping` and runs `bin/booping render src/templates/hooks/session_start.md.j2`; the template iterates `context.playbooks`, the same list `src/templates/skills/playbook.md.j2` iterates.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [Review levels replace reviewed](milestones/M01-review-levels-replace-reviewed/M01-review-levels-replace-reviewed.md) | 11 | done |
| 02 | [ADR brief and the objection window](milestones/M02-adr-brief-and-the-objection-window/M02-adr-brief-and-the-objection-window.md) | 8 | done |
| 03 | [ADR scorer](milestones/M03-adr-scorer/M03-adr-scorer.md) | 7 | done |
| 04 | [Session start points to playbooks](milestones/M04-session-start-points-to-playbooks/M04-session-start-points-to-playbooks.md) | 8 | done |

## Groups

| group | milestones | sp |
| --- | --- | --- |
| G1 | M01 | 11 |
| G2 | M02, M03 | 15 |
| G3 | M04 | 8 |

## Final Verification

- [ ] `just ci` passes, except snapshot drift in `playbooks/specs/_reports/output.md` and `playbooks/learn/_reports/output.md`, which the owner accepts.
- [ ] `bin/booping render-playbook specs` shows rule/0036 under `## Rules` and the new `## Record` flow.
- [ ] A fresh `claude` session in this repo shows the session-start block.

## Out of scope

- Re-reviewing the other project's ADRs — done in that project once this ships.
- A schema rule forcing cheap-option rows in `adr.yaml` — the scorer covers it.
- Loading the manager at session start.
- A migration for `reviewed:`.
- Measuring a cheaper scorer model.

## CLAUDE.md impact

Layout gains `hooks/` (M04 task 4.4). Lifecycle and Config need no change.
