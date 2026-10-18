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

### M01 — Review levels replace `reviewed`

sp: 11
depends_on: []

#### Tasks

**Goal:** a record carries `review` and `review_evidence`; every reader of `reviewed` reads the level; the site marks a record `accepted`.
**Scope:** `src/specs/README.md`, `booping-python/src/booping/specs/records.py`, `status.py`, `specs/site/**`, `booping specs check`, unit tests and e2e cases touching `reviewed`; `documentation/specs.md`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Guide: replace the `reviewed` entry with `review` (no key / `shown` / `discussed` / `accepted`) and `review_evidence` (Decisions 5–7), keep both in the list of keys a tier schema may not rename | `src/specs/README.md` | 2 | pending |
| 1.2 | Records and status: a level reader replacing `unreviewed()`; `booping status` prints the not-accepted line of Decision 10; `booping specs check` errors on a `reviewed:` key naming the replacement, and on a level outside the enum or a level without evidence | `booping-python/src/booping/specs/records.py`, `booping-python/src/booping/status.py`, the specs check module | 3 | pending |
| 1.3 | Site: state, machine layer, facts, filters, search facets and icons read the level (accepted vs not accepted, the level shown as a fact); the "mark reviewed" control becomes "accepted" and its Outbox line `{ref} — accepted {date}` | `booping-python/src/booping/specs/site/*.py`, `comments.js`, `comments-format.js`, `templates/*.j2` | 4 | pending |
| 1.4 | Tests and e2e: rewrite every case seeding `reviewed:`; add check cases for `reviewed:` present, level without evidence, bad level; status case for the not-accepted line; site case for the accepted icon and Outbox line; docs page `documentation/specs.md` Outbox section | `booping-python/tests/specs/*`, `booping-python/e2e/cases/specs/*`, `booping-python/e2e/cases/status/*`, `documentation/specs.md` | 2 | pending |

Test surface: `booping specs check`, `booping status` and the site render, integration tier through e2e txtar cases — record with each level, legacy `reviewed:`, missing evidence.

#### Definition of Done

Task 1.1
- [ ] The guide lists `review` and `review_evidence` with the four levels and the evidence each needs; `reviewed` appears nowhere in it.

Task 1.2
- [ ] `booping status` prints `records: {n} not accepted — none {a}, shown {b}, discussed {c}` on a fixture with one record per level.
- [ ] `booping specs check` reports an error for `reviewed:`, for an unknown level, and for a level without `review_evidence`.

Task 1.3
- [ ] A rendered record page shows its level; the unreviewed filter is renamed to "not accepted" and selects every record below `accepted`.
- [ ] The Outbox emits `{ref} — accepted {date}`.

Task 1.4
- [ ] `grep -rn "reviewed" booping-python/src documentation/specs.md src/specs` returns only the word inside prose that means "read", never the key.
- [ ] `just pytest` and `just e2e -k "specs or status"` pass.

Return: the files changed and the Verify verdict, nothing else.

#### References

- `migrations/003_session_metrics/migration.md` — why flat keys.
- `booping-python/e2e/cases/specs/site-writes-search-index-and-body.txtar` — the case seeding `reviewed:` to rewrite.

#### Verify

`just pytest && just e2e -k "specs or status"`

### M02 — ADR brief and the objection window

sp: 8
depends_on: [M01]

#### Tasks

**Goal:** recording an ADR in the specs playbook ends with the locked brief and a gentle objection ask; the answer sets the level with evidence.
**Scope:** `playbooks/specs/guide/prompt.md` (`## Record`, `## Site review`), a new core rule record, the lines elsewhere that say `reviewed` is the owner's alone.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | `## Record`: an ADR is drafted `proposed`, then the brief (locked output above) is shown; no objection → `status: accepted`, `review: shown` with evidence; an explicit yes → `review: accepted` with the quote; a discussion → `discussed`; an objection → back to the draft. Autonomous: the brief is logged as an agent decision, no `review` key (Decision 11) | `playbooks/specs/guide/prompt.md` | 3 | pending |
| 2.2 | `## Site review`: the `{ref} — accepted {date}` line sets `review: accepted`, `review_evidence: "site review — {date}"` | `playbooks/specs/guide/prompt.md` | 1 | pending |
| 2.3 | Core rule record `specs/rule/0036-adr-accepted-after-a-brief.md`: the brief before acceptance and the objection window, `targets: [specs]`, a `brief:` line, `## Follows from` value/0008 and value/0009 | `specs/rule/0036-adr-accepted-after-a-brief.md` | 1 | pending |
| 2.4 | Stale lines: every "never set `reviewed`" / "reviewed stays yours" becomes the level rule of Decision 7 | `playbooks/specs/playbook.md`, `documentation/specs_playbook.md`, `documentation/learn.md`, `playbooks/learn/**` where it says so, `migrations/004_lessons_to_rules/migration.md` left as history | 1 | pending |
| 2.5 | Eval fixture for the guide: recording an ADR from a dialogue ends with the brief in the locked shape and the objection ask; smoke tier asserts the table, `Ключевые моменты:`, `Задевает:`, `Решил сам:` and the ask line | `playbooks/specs/guide/tests.yaml`, `playbooks/specs/guide/_fixtures/` | 2 | pending |

Test surface: the specs guide step, eval smoke tier (deterministic asserts on the brief's shape); `just specs-check` for the rule record.

#### Definition of Done

Task 2.1
- [ ] `## Record` names the brief's parts in the locked order and the three answers with the level each sets.

Task 2.2
- [ ] `## Site review` has no `reviewed` key left.

Task 2.3
- [ ] `just specs-check` passes with the new rule; `bin/booping render-playbook specs` shows its brief under `## Rules`.

Task 2.4
- [ ] `grep -rn "never set \`reviewed\`\|reviewed\` stays" playbooks documentation src` returns nothing.

Task 2.5
- [ ] `just smoke specs/guide` passes on the new fixture.

Return: the files changed and the Verify verdict, nothing else.

#### References

- `playbooks/specs/guide/_fixtures/what-is-open.md` — fixture shape.
- `specs/rule/0033-decisions-listed-for-acceptance.md` — rule record shape.

#### Verify

`bin/booping render-playbook specs | grep -n "rule/0036" && just specs-check`

### M03 — ADR scorer

sp: 7
depends_on: [M02]

#### Tasks

**Goal:** a new ADR is scored 0–3 before the brief by an Opus agent that gets the ADR text and the rubric inline and has no tool to read anything else.
**Scope:** a rubric file beside the guide step, a new internal agent, the `## Record` scenario, an eval suite for the agent.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Rubric: the audit rubric verbatim from `adr-audit-ground-truth.md`, plus the three cheap options by name and the output contract — first line `score: {0-3}`, then one line per finding | `playbooks/specs/guide/adr-rubric.md` | 1 | pending |
| 3.2 | Agent `adr-scorer`: model opus, no tools at all — check the Claude Code agent frontmatter for how a definition grants zero tools and use that; a static body (no render step, it could not run one) saying it scores only the text in its prompt against the rubric there and returns the output contract | `agents/adr-scorer.md` | 2 | pending |
| 3.3 | `## Record`: before the brief, spawn `booping:adr-scorer` with the ADR file's text and the rubric's text pasted into the prompt — no paths; ≤ 1 → redraft, at most two rounds; the brief's header carries the score | `playbooks/specs/guide/prompt.md` | 2 | pending |
| 3.4 | Eval suite for the agent: three ground-truth ADRs scored 1, 2 and 3; smoke asserts the output contract and that the agent made no tool call, regress asserts each score within ±1 of the ground truth | `agents/_evals/adr-scorer/` or the repo's existing place for agent evals | 2 | pending |

Test surface: the scorer agent, eval smoke (contract, zero tool calls) and regress (score against the hand-derived ground truth).

#### Definition of Done

Task 3.1
- [ ] The rubric file holds the four score lines, the three cheap options and the output contract.

Task 3.2
- [ ] The agent definition grants no tool and names `model: opus`; its body names no file to read.

Task 3.3
- [ ] `## Record` passes the ADR and the rubric as text, names the threshold and the round limit, and never passes a path.

Task 3.4
- [ ] The smoke tier passes; the regress tier result is reported.

Return: the files changed, the regress scores and the Verify verdict, nothing else.

#### References

- `vault/plans/202610190033_specs-acceptance-and-session-entry/adr-audit-ground-truth.md` — rubric and scores.
- `agents/booping-researcher.md` — agent frontmatter shape.

#### Verify

`just smoke adr-scorer || just suites | grep -i scorer`

### M04 — Session start points to playbooks

sp: 8
depends_on: []

#### Tasks

**Goal:** a Claude Code session started anywhere inside a booping project gets the locked session-start block; elsewhere it gets nothing.
**Scope:** `.claude-plugin/plugin.json`, a new `hooks/` directory, a new template, e2e cases, docs, CLAUDE.md layout.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | `hooks/session-start.sh`: walk up from the cwd for `.booping`; none → exit 0 silent; found → `"$CLAUDE_PLUGIN_ROOT/bin/booping" render src/templates/hooks/session_start.md.j2`; any failure → exit 0, no output. `plugin.json` gains `hooks.SessionStart` with a 10 s timeout (shape: the caveman plugin's) | `hooks/session-start.sh`, `.claude-plugin/plugin.json` | 2 | pending |
| 4.2 | Template: the locked session-start block over `context.playbooks`, two columns | `src/templates/hooks/session_start.md.j2` | 2 | pending |
| 4.3 | e2e: the template renders the block with project and global playbooks inside a project; the script prints nothing outside a project and nothing on a failing render | `booping-python/e2e/cases/render/session-start-*.txtar` | 2 | pending |
| 4.4 | Docs: a "Session start" section in `documentation/playbook.md` (what it injects, how a project starts as the manager via its CLAUDE.md); README mention; CLAUDE.md Layout gains `hooks/` | `documentation/playbook.md`, `README.md`, `CLAUDE.md` | 2 | pending |

Test surface: the template render and the hook script, integration tier through e2e txtar — inside a project, outside, failing render.

#### Definition of Done

Task 4.1
- [ ] `cd /tmp && CLAUDE_PLUGIN_ROOT=$PWD/… hooks/session-start.sh` prints nothing and exits 0; inside this repo it prints the block.

Task 4.2
- [ ] The rendered block matches the locked output; no column beyond Playbook and Trigger.

Task 4.3
- [ ] `just e2e -k session-start` passes.

Task 4.4
- [ ] The docs say how a project opts into the manager at start; CLAUDE.md Layout lists `hooks/`.

Return: the files changed and the Verify verdict, nothing else.

#### References

- `src/templates/skills/playbook.md.j2` — the playbook loop to mirror.
- `~/.claude/plugins/marketplaces/caveman/.claude-plugin/plugin.json` — hook declaration shape.

#### Verify

`just e2e -k session-start && bin/booping render src/templates/hooks/session_start.md.j2 | head -5`

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
