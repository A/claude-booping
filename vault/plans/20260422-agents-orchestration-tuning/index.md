---
title: Agents + orchestration tuning
type: refactoring
status: cancelled
sp: 37
source: ad-hoc — user feedback on booping skillset (session on 2026-04-22)
created: 2026-04-22 00:00
planned: 2026-04-22
started: null
completed: 2026-07-27 18:40
retro: null
goal: null
summary: "Collapse developer tiers to two, re-tier agent model/effort, dynamize groom routing, split sprints.md/backlog.md"
---

# Agents + orchestration tuning

## Context

Second-pass tuning of the plugin after the plans-as-data refactor shipped. User feedback consolidates nine loosely-coupled strands: collapse the three-tier developer roster to two, rebalance model tiers across every agent/skill, strip orchestrator-internal concepts from worker-agent bodies, dynamize `/groom`'s agent routing, move `/develop`'s unit of delegation from task to milestone, simplify lesson wiring so filtering lives in the skill (not in agents), split `sprints.md` so the backlog lives in its own file, and trim `docs/plan-schema.md`'s CLI guidance. Techlead's blast-radius report (250s, 11 strands mapped) is the reference for file-level scope; every milestone here derives from it.

## Definition of Done

- [ ] `booping-developer-junior` agent is gone and no file references the name
- [ ] `/develop` delegates one milestone at a time; tier = max task-SP in the milestone (1-2 → middle, 3-4 → senior, 5 → refuse)
- [ ] Every agent/skill frontmatter matches the target model/effort grid (§M2)
- [ ] Developer-agent bodies no longer mention `/learn`, "lessons tagged X", "tier calibration", "simpler approach than the plan", or "No monkey-patching"
- [ ] `docs/developer-agents.md` exists as canonical shared developer guidance; middle+senior inline from it with a drift-check
- [ ] `booping-teamlead` no longer holds the `Agent(...)` delegation tool; it is documented as a support agent (retro prose, session-log search, metrics rollup, user-question drafting)
- [ ] `/groom` orchestration is dynamic: bug/refactor → techlead only; feature → techlead then conditional PM/QA by heuristics; `booping-validate-plan` call budget ≤ 2 per groom run
- [ ] Skills (`/groom`, `/develop`, `/retro`, `/learn`) own lesson filtering — they read only lesson frontmatter for domain matching; agent Startup sections no longer explain tag filtering
- [ ] `docs/agent-wiring.md` is either deleted or reduced to a briefing-template stub; per-agent domain tables live inline in each skill that spawns agents
- [ ] `booping-plans sync-sprints` writes two files: `sprints.md` (Active + History) and `backlog.md` (backlog bucket only); `in-spec` plans appear in `sprints.md` Active, not in `backlog.md`
- [ ] Every prose reference to `sprints.md` across skills/agents/docs/CLAUDE.md templates names `backlog.md` too where the reader needs both (enumerated per lesson 0006)
- [ ] `docs/plan-schema.md` CLI section shows ≤ 5 example invocations and points to `booping-plans --help` as the authoritative reference
- [ ] `bin/tests/` suite is green after all changes (CLI + integration)
- [ ] Legacy-content audit (lesson 0006) is explicitly run for each data-flow-affecting milestone (M5, M6, M8, M9, M10) — not deferred

## Design

### Architecture

This sprint touches three planes:

1. **Agent plane** (`agents/*.md`): delete junior, rewrite middle/senior, strip internals, reshape teamlead; every agent's frontmatter gets re-tiered.
2. **Skill plane** (`skills/*/SKILL.md`): `/develop` moves to milestone-level delegation; `/groom` becomes dynamic; all four orchestrators own lesson filtering and inline their domain maps.
3. **CLI + artifact plane** (`bin/booping_plans.py`, `bin/booping-init`, `bin/tests/`): `sync-sprints` splits output into `sprints.md` + `backlog.md`; the init scaffold seeds both.

Lessons 0002 and 0006 are load-bearing here. M9 creates a new invariant ("only the CLI writes `sprints.md` AND `backlog.md`") — for the remainder of this sprint, `/develop` is bound to delegate every touch of either file to the CLI. M5/M6/M8/M9/M10 each change producer/consumer patterns and require explicit enumerate-every-consumer audit bullets (no spot checks per lesson 0001).

### Decisions

| # | Decision | Alternative considered | Why this one |
|---|----------|------------------------|--------------|
| D1 | Delete `booping-developer-junior`; middle owns 1-2 SP, senior 3-4 SP | Keep junior on haiku for 1-SP config-edit tasks | Operational: haiku tier adds routing complexity and drift risk with no measured latency/cost win; two tiers fit the work distribution we actually see |
| D2 | `/develop` delegates by milestone, not task | Keep per-task TaskCreate + per-task Agent briefing | Briefing cost dominates worker time; milestone briefing lets the worker plan the whole chunk, matching human reviewer mental model. Max-SP rule keeps tier selection mechanical |
| D3 | `xhigh` is a literal `effort` value (confirmed by user screenshot showing Claude Code surfacing `xHigh effort (default)` as a first-class tier) | Map `xhigh` → `effort: max + reasoning: high` combo | User confirmed `xhigh` is canonical; keep `reasoning:` out of the frontmatter to avoid undocumented keys silently no-oping |
| D4 | Shared developer guidance lives in `docs/developer-agents.md` as the canonical text; middle+senior agents inline the shared body with a drift-check `just` recipe | Agent frontmatter include mechanism (`include:` field) | Claude Code has no documented include; inlining + a byte-diff check is the cheapest guaranteed-consistent option |
| D5 | `booping-teamlead` loses `Agent(...)` from its `tools:` list; it is a support agent (no sub-delegation) | Keep Agent() so retro synthesis can sub-spawn | Orchestrator skills already spawn techlead/PM/QA directly (`/retro` Phase 2 already does this); teamlead's sub-delegation is unused in the happy path and user prefers explicit skill-level routing |
| D6 | Skills own lesson-domain filtering; agents just read paths listed in briefing | Keep per-agent domain maps in `docs/agent-wiring.md` | Lessons are planning constraints; by the time a worker runs, the plan already embeds them. Agent briefings stop being a second filter hop. Pulls filter logic closer to the caller that decides what's relevant |
| D7 | `sync-sprints` writes two files; `in-spec` is active, not backlog | `in-spec` in `backlog.md` (mid-spec = not ready) | User said backlog.md = backlog bucket only; `in-spec` is actively being worked by `/groom`, so it belongs on the active board |
| D8 | `docs/agent-wiring.md` reduced to a ≤30-line briefing-template stub; domain maps move inline into each skill | Delete the file entirely | Keep a canonical briefing-header format to avoid drift between four skills; everything else inlines |
| D9 | `booping-validate-plan` call budget is ≤ 2 per groom run (document as a hard cap) | No cap (today's implicit "call as many times as needed") | User observed 4+ calls in some sessions; a cap prevents pathological retry loops |
| D10 | `/groom` PM/QA invite mechanisms: (a) user-text exact-phrase match against a fixed list (`"plan tests"`, `"deep research"`, `"needs PM"`, `"verify requirements"`, `"product review"`); (b) techlead returns a `## Recommended additional reviewers` section naming PM/QA with rationale. No pre-routing SP threshold (SP is grooming output, not input) | Hardcode feature → always PM+QA (status quo); or a pre-routing SP threshold | Dynamic routing matches user's "simple tasks don't need four agents"; techlead reads the codebase first and is best positioned to flag product/QA complexity |

### Applies lessons

- [lessons/0001_verify-block-universal-quantifiers.md](../lessons/0001_verify-block-universal-quantifiers.md) — every DoD bullet with "every", "all", "each" gets an enumerating Verify command
- [lessons/0002_orchestrator-delegation-during-invariant-sprints.md](../lessons/0002_orchestrator-delegation-during-invariant-sprints.md) — M9 creates a "only CLI writes sprints.md + backlog.md" invariant; orchestrator bound for the remainder
- [lessons/0003_reviewer-followup-triage-rubric.md](../lessons/0003_reviewer-followup-triage-rubric.md) — M8 redefines milestone as delegation unit; reviewer deferral cap is now per-milestone-aggregate
- [lessons/0004_skill-body-regression-harness.md](../lessons/0004_skill-body-regression-harness.md) — M9 adds a CLI write path; the regression harness must exercise both file outputs
- [lessons/0005_cli-error-string-contract.md](../lessons/0005_cli-error-string-contract.md) — M9 may introduce new stderr strings for `backlog.md`; pin in a golden file if grepped by any skill
- [lessons/0006_agent-body-audit-after-dataflow-changes.md](../lessons/0006_agent-body-audit-after-dataflow-changes.md) — M5, M6, M8, M9, M10 each change producer/consumer patterns; full enumerated audit bullets required

## Milestones

### M1: Remove booping-developer-junior — 4 SP | pending

**Goal**: `booping-developer-junior` agent file is gone, `/develop`'s SP→tier routing is two-tier, and no other file references the removed agent by name.

**Verify**:
```bash
test ! -f /home/anton/Dev/@A/claude-booping/agents/booping-developer-junior.md
! grep -rn 'booping-developer-junior\|developer-junior' /home/anton/Dev/@A/claude-booping/agents /home/anton/Dev/@A/claude-booping/skills /home/anton/Dev/@A/claude-booping/docs /home/anton/Dev/@A/claude-booping/README.md /home/anton/Dev/@A/claude-booping/PRD.md
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Delete junior agent file + update `/develop` Phase 2.6 SP→tier table (1-2 → middle, 3-4 → senior, 5 → refuse) + Phase 4 step-2 delegate list | `agents/booping-developer-junior.md` (delete), `skills/develop/SKILL.md` (L67-76, L107-131) | 2 | pending |
| 1.2 | Audit + update every other consumer: teamlead `tools:` + responsibility prose, install skill Phase 5 wording, help skill Agents table + workflow diagram, docs/agent-wiring.md domain table + developer-exception note, README agent row, PRD agent row | `agents/booping-teamlead.md` (L4, L22), `skills/install/SKILL.md` (L74, L90), `skills/help/SKILL.md` (L60, L88), `docs/agent-wiring.md` (L37, L66), `README.md` (L62), `PRD.md` (L45) | 2 | pending |

#### Task 1.1 DoD

- [ ] `agents/booping-developer-junior.md` removed
- [ ] `skills/develop/SKILL.md` Phase 2.6 SP→agent table reads: `1–2 → booping-developer-middle (sonnet)`, `3–4 → booping-developer-senior (opus)`, `5 → refuse — kick back to /groom`
- [ ] Phase 4 step 2 delegate list names only middle + senior + techlead
- [ ] No occurrence of `booping-developer-junior` in `skills/develop/SKILL.md`
- [ ] `booping-plans` tests still green (`cd bin && pytest`)

#### Task 1.2 DoD

- [ ] `agents/booping-teamlead.md` `tools:` list no longer includes `booping-developer-junior`
- [ ] `agents/booping-teamlead.md` prose does not mention junior tier
- [ ] `skills/install/SKILL.md` Phase 5 header + notes do not name three tiers; use "two developer tiers (middle, senior)"
- [ ] `skills/help/SKILL.md` Agents section + Workflow block list middle + senior only
- [ ] `docs/agent-wiring.md` per-agent domain table does not include a `booping-developer-junior` row
- [ ] `README.md` Workers table does not list junior
- [ ] `PRD.md` § Agents list does not include the junior bullet
- [ ] Enumerated audit: `grep -rn 'booping-developer-junior\|developer-junior' .` returns zero hits across agents/, skills/, docs/, README.md, PRD.md

---

### M2: Model-tier overrides (agents + skill frontmatter) — 3 SP | pending

**Goal**: Every agent and skill frontmatter matches the target `model`/`effort` grid below.

**Target grid**:

| Target | `model:` | `effort:` |
|--------|----------|-----------|
| `/groom` skill | (skill, no model key) | `xhigh` |
| `booping-techlead` | `opus` | `xhigh` |
| `booping-product-manager` | `opus` | `xhigh` |
| `booping-teamlead` | `opus` | `high` |
| `booping-qa-lead` | `opus` | `high` |
| `booping-developer-senior` | `opus` | `high` |
| `booping-developer-middle` | `sonnet` | (default, no key) |
| `booping-reviewer` | `opus` | `high` (unchanged) |

Skills `/develop`, `/retro`, `/learn`, `/install`, `/chat`, `/help` are not in the override spec; leave their current `effort` values alone.

**Verify**:
```bash
for f in agents/booping-techlead.md agents/booping-product-manager.md agents/booping-teamlead.md agents/booping-qa-lead.md agents/booping-developer-senior.md agents/booping-developer-middle.md agents/booping-reviewer.md; do
  echo "=== $f ==="; head -10 "$f"
done
head -25 skills/groom/SKILL.md
```
(Diff the frontmatter vs the table above manually or via a pytest assertion.)

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Edit frontmatter on all six agents in the target grid; drop `reasoning: high` from senior (keep only `effort: high`); drop `effort: high` from middle (use default) | `agents/booping-techlead.md` (L5-7), `agents/booping-product-manager.md` (L5-7), `agents/booping-teamlead.md` (L5-6), `agents/booping-qa-lead.md` (L5-6), `agents/booping-developer-senior.md` (L5-7), `agents/booping-developer-middle.md` (L5-6) | 2 | pending |
| 2.2 | Edit `/groom` skill frontmatter: `effort: max` → `effort: xhigh` | `skills/groom/SKILL.md` (L22) | 1 | pending |

#### Task 2.1 DoD

- [ ] `agents/booping-techlead.md` frontmatter: `model: opus`, `effort: xhigh`
- [ ] `agents/booping-product-manager.md` frontmatter: `model: opus`, `effort: xhigh`
- [ ] `agents/booping-teamlead.md` frontmatter: `model: opus`, `effort: high`
- [ ] `agents/booping-qa-lead.md` frontmatter: `model: opus`, `effort: high`
- [ ] `agents/booping-developer-senior.md` frontmatter: `model: opus`, `effort: high` (and the `reasoning: high` line is removed)
- [ ] `agents/booping-developer-middle.md` frontmatter: `model: sonnet`; no `effort:` key (uses default)
- [ ] `agents/booping-reviewer.md` frontmatter unchanged (already `opus`/`high`)
- [ ] Enumerated audit: grep `^effort: ` across `agents/*.md` matches the target grid exactly (shell loop confirms each file)

#### Task 2.2 DoD

- [ ] `skills/groom/SKILL.md` frontmatter contains `effort: xhigh`
- [ ] No other skill frontmatter was altered (grep `^effort: ` across `skills/*/SKILL.md`, only groom changed vs git HEAD)

---

### M3: Strip orchestrator internals from agent bodies — 3 SP | pending

**Goal**: Agent bodies stop narrating orchestrator-level concepts. Agents read what's given; they do not explain why.

Specifically strip:
- Mentions of `/learn` as the author of project-local extension files
- Explanations of domain tag filtering ("lessons tagged code/tech/all")
- Worker-tier calibration prose on developer agents (middle/senior)
- Senior's "If you find a simpler approach than the plan, stop and report" line
- Developer agents' "No monkey-patching" hard-rule bullet (the same check stays in `/develop`'s hard rules)

The `agent_extension` concept stays — agents still read the path the briefing gives them — but the *reason* the file exists is not explained in the agent body.

**Verify**:
```bash
! grep -n 'written by \`/learn\`\|written by /learn' agents/*.md
! grep -n 'tagged `code`\|tagged `tech`\|tagged `qa`\|tagged `product`\|Do not scan the lessons directory' agents/*.md
! grep -n '## Tier calibration' agents/booping-developer-middle.md agents/booping-developer-senior.md
! grep -n 'If you find a simpler approach' agents/booping-developer-senior.md
! grep -n 'No monkey-patching' agents/booping-developer-middle.md agents/booping-developer-senior.md
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Strip `/learn` rationale + domain-tag narration + tier calibration section + monkey-patch bullet from developer-middle and developer-senior; strip "simpler approach" line from senior only | `agents/booping-developer-middle.md` (L16, L17, L21-23, L55-56), `agents/booping-developer-senior.md` (L17, L18, L21-23, L56-57) | 2 | pending |
| 3.2 | Apply the same `/learn` + domain-tag strip to orchestrator-role agents (techlead, PM, QA, reviewer, teamlead) Startup sections; they no longer explain which tags they receive | `agents/booping-techlead.md` (L16, L17), `agents/booping-product-manager.md` (L16, L17), `agents/booping-qa-lead.md` (L16, L17), `agents/booping-reviewer.md` (L16, L17), `agents/booping-teamlead.md` (L16, L17) | 1 | pending |

#### Task 3.1 DoD

- [ ] `agents/booping-developer-middle.md` Startup mentions only: read `agent_extension` path if provided, read paths under `Applicable lessons:`, proceed
- [ ] `agents/booping-developer-senior.md` same shape as middle (no "simpler approach" line)
- [ ] Neither file has a `## Tier calibration` section
- [ ] Neither file has a `No monkey-patching` hard-rule bullet
- [ ] Enumerated audit: each stripped phrase returns zero hits via the Verify block

#### Task 3.2 DoD

- [ ] Techlead, PM, QA, reviewer, teamlead Startup sections no longer say "written by `/learn`" or "tagged X"
- [ ] Each agent still reads `agent_extension` path (conditional on briefing) and paths listed under `Applicable lessons:`
- [ ] Enumerated audit: `grep -l '/learn\|tagged \`' agents/*.md` returns zero agents

---

### M4: Extract shared developer guidance to docs/ — 2 SP | pending

**Goal**: `docs/developer-agents.md` holds the canonical shared-developer-agent body (Startup, Workflow, Reporting back, Hard rules). The two tier files inline it verbatim + add a thin per-tier header (frontmatter, one-sentence role). A `just dev-agents-drift` recipe byte-diffs the shared body against each inlined copy.

**Verify**:
```bash
test -f docs/developer-agents.md
just dev-agents-drift
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Create `docs/developer-agents.md` with the canonical shared body (Startup, Workflow, Reporting back, Hard rules — the text M3 leaves standing) | `docs/developer-agents.md` (new) | 1 | pending |
| 4.2 | Update middle + senior to inline the doc's body between known marker comments (`<!-- BEGIN shared -->` / `<!-- END shared -->`); add `just dev-agents-drift` recipe that compares each agent file's shared block against `docs/developer-agents.md` verbatim | `agents/booping-developer-middle.md`, `agents/booping-developer-senior.md`, `justfile` | 1 | pending |

#### Task 4.1 DoD

- [ ] `docs/developer-agents.md` exists and contains the four sections: Startup, Workflow, Reporting back, Hard rules
- [ ] Content matches the post-M3 body (no `/learn`, no tier calibration, no monkey-patch rule)

#### Task 4.2 DoD

- [ ] `agents/booping-developer-middle.md` body between `<!-- BEGIN shared -->` and `<!-- END shared -->` matches `docs/developer-agents.md` byte-for-byte
- [ ] `agents/booping-developer-senior.md` same property
- [ ] `justfile` has a `dev-agents-drift` target that returns zero on a sync'd tree and non-zero on drift
- [ ] `just dev-agents-drift` passes

---

### M5: Reshape booping-teamlead as a support agent — 3 SP | pending

**Goal**: `booping-teamlead` is no longer a coordinator. It drafts retro prose, searches session logs, updates metrics rollups, and drafts user-facing questions. Orchestrator skills (`/groom`, `/retro`, `/learn`, `/develop`) own the Agent() routing.

Lesson 0006 applies: enumerate every file mentioning teamlead coordination and fix in this milestone.

**Verify** (every check exits non-zero on failure — no manual eyeball):
```bash
# (a) Agent() tool removed from teamlead frontmatter
! grep -qE '^tools:.*Agent\(booping-' agents/booping-teamlead.md

# (b) No coordinator verbs anywhere in teamlead body
! grep -qiE 'coordinate other agents|coordinate the above|you delegate|brief the other agents|delegate to.*booping-' agents/booping-teamlead.md

# (c) Across every consumer, no coordinator framing of teamlead survives. Enumerate all consumers.
for f in skills/groom/SKILL.md skills/develop/SKILL.md skills/retro/SKILL.md skills/learn/SKILL.md skills/help/SKILL.md README.md PRD.md; do
  if grep -inE 'teamlead.*coordinate|teamlead.*orchestrat|teamlead.*delegate|coordinate.*(techlead|pm|qa).*teamlead' "$f"; then
    echo "FAIL: $f still casts teamlead as coordinator"; exit 1;
  fi
done
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Edit `agents/booping-teamlead.md`: remove `Agent(booping-*)` from `tools:`; rewrite Responsibilities section as four support bullets (session-log search, retro synthesis, metrics updates, user-question drafting); drop Briefing format section (no sub-delegation) | `agents/booping-teamlead.md` (L4, L10, L22-36) | 2 | pending |
| 5.2 | Audit skill + README + PRD prose that calls teamlead "coordinator": rewrite `/groom` orchestration table (teamlead row → "synthesize plan document"); rewrite `/retro` Phase 3 framing (teamlead drafts user questions + synthesis, does not coordinate three agents); update README Orchestrators table; update PRD § Agents description | `skills/groom/SKILL.md` (L50, L56), `skills/retro/SKILL.md` (L56-61, L73, L119), `README.md` (L53), `PRD.md` (L38), `skills/help/SKILL.md` (L53) | 1 | pending |

#### Task 5.1 DoD

- [ ] `agents/booping-teamlead.md` `tools:` line does not contain `Agent(`
- [ ] Responsibilities section lists: (a) session-log search, (b) retro synthesis, (c) metrics rollup, (d) user-question drafting via AskUserQuestion — and nothing about coordinating other agents
- [ ] No "Briefing format" section remains (since teamlead does not brief anyone)
- [ ] Hard rules retain "never writes application code" + "only edits retrospective files + metrics"

#### Task 5.2 DoD

- [ ] `skills/groom/SKILL.md` orchestration table teamlead row does not contain "coordinate"; instead names synthesis output
- [ ] `skills/retro/SKILL.md` Phase 3 teamlead reference does not cast it as coordinator of techlead/PM/QA
- [ ] `README.md` + `PRD.md` + `skills/help/SKILL.md` teamlead descriptions match the support-agent framing
- [ ] Enumerated audit: every teamlead mention across `agents/`, `skills/`, `docs/`, `README.md`, `PRD.md` reviewed; none describes sub-delegation

---

### M6: Simplify lesson wiring — skill-side filtering — 4 SP | pending

**Goal**: Lesson filtering happens in the skill that spawns an agent. Skills read only lesson *frontmatter* (not full bodies) for domain matching. Agent Startup sections no longer explain filtering. `docs/agent-wiring.md` is trimmed to a briefing-template stub; per-agent domain maps inline into each skill.

Lesson 0006 applies: the lesson-data flow changes in this milestone; audit every consumer.

**Verify**:
```bash
# (a) docs/agent-wiring.md is ≤ 30 lines OR deleted
[ -f docs/agent-wiring.md ] && { wc -l docs/agent-wiring.md; grep -c '## Per-agent domain' docs/agent-wiring.md; } || echo "deleted"
# (b) no agent body describes tag filtering
! grep -rn 'domain `tech`\|tagged `code`\|tagged `qa`\|tagged `product`\|filter.*domain' agents/*.md
# (c) each skill that spawns agents has its inline domain map
grep -l 'domain.*tech\|domain.*product\|domain.*qa' skills/groom/SKILL.md skills/develop/SKILL.md skills/retro/SKILL.md skills/learn/SKILL.md
# (d) skills read lesson frontmatter explicitly
grep -n 'frontmatter\|only the frontmatter\|read.*frontmatter' skills/groom/SKILL.md skills/develop/SKILL.md skills/retro/SKILL.md skills/learn/SKILL.md
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Strip tag-filtering prose from all agent Startup sections; each Startup now says: "If briefing supplies `agent_extension`, read it. Read each path under `Applicable lessons:`. Proceed." | `agents/booping-techlead.md`, `agents/booping-product-manager.md`, `agents/booping-qa-lead.md`, `agents/booping-teamlead.md`, `agents/booping-reviewer.md`, `agents/booping-developer-middle.md`, `agents/booping-developer-senior.md`, plus `docs/developer-agents.md` from M4 | 1 | pending |
| 6.2 | Inline the per-agent domain map into each spawning skill; add explicit "read only frontmatter from each lesson file" instruction; the four skills each own their map | `skills/groom/SKILL.md`, `skills/develop/SKILL.md`, `skills/retro/SKILL.md`, `skills/learn/SKILL.md` | 2 | pending |
| 6.3 | Shrink `docs/agent-wiring.md` to a ≤ 30-line stub that defines the briefing-header format only (no domain maps, no per-agent tables); update back-references | `docs/agent-wiring.md`, plus link updates in `skills/groom/SKILL.md`, `skills/develop/SKILL.md`, `skills/retro/SKILL.md` | 1 | pending |

#### Task 6.1 DoD

- [ ] Every listed agent's Startup section matches the three-step shape; no explanation of which domains the agent receives
- [ ] `docs/developer-agents.md` Startup section matches the same shape
- [ ] Enumerated audit: `grep -n 'tagged \`' agents/*.md docs/developer-agents.md` returns zero hits

#### Task 6.2 DoD

- [ ] `skills/groom/SKILL.md` has an inline "Lessons flow" subsection listing: techlead ← `tech,code,all`, PM ← `product,all`, QA ← `qa,all`, teamlead ← `all`. Plus an instruction to read only frontmatter for domain matching
- [ ] `skills/develop/SKILL.md` has the same subsection restricted to developer tiers + reviewer (`code,tech,all`)
- [ ] `skills/retro/SKILL.md` has the same for its three-agent panel
- [ ] `skills/learn/SKILL.md` has the classification-time domain assignment table already (confirm still present; update if drifted)
- [ ] Each skill explicitly instructs "read only the frontmatter fields `id`, `title`, `domain` to select; do not read full bodies until the briefing is written"

#### Task 6.3 DoD

- [ ] `docs/agent-wiring.md` (if retained) ≤ 30 lines; contains briefing-header format only
- [ ] OR file deleted; all skill links to it are removed
- [ ] Enumerated audit: `grep -rn 'docs/agent-wiring.md' skills/ docs/` consistent with the chosen option

---

### M7: Dynamic /groom orchestration — 4 SP | pending

**Goal**: `/groom` is no longer hardcoded to the full PM+techlead+QA+teamlead panel. Default for bug and refactor is techlead only. For feature, techlead runs first; then the skill decides whether to invite PM or QA based on explicit, mechanical triggers (two kinds: user-text match, and techlead's own recommendation — not a pre-routing SP guess). `booping-validate-plan` has a hard cap of 2 invocations per groom run.

**Rationale on heuristics**: SP estimates are an *output* of grooming, not an input; a pre-routing SP threshold cannot be evaluated at orchestration time. Instead, techlead — who runs first and reads the codebase — returns a short `## Recommended additional reviewers` section in its report, naming PM and/or QA with a one-sentence reason. The orchestrator honors the recommendation. User-text triggers (listed below) are the other invite path.

**Verify**:
```bash
# Orchestration section describes per-type defaults
grep -nE 'bug.*techlead only|refactor.*techlead only|techlead runs first' skills/groom/SKILL.md

# User-text triggers enumerated
for phrase in 'plan tests' 'deep research' 'needs PM' 'verify requirements' 'product review'; do
  grep -qF "$phrase" skills/groom/SKILL.md || { echo "missing trigger phrase: $phrase"; exit 1; }
done

# Techlead-recommendation path documented
grep -nE 'Recommended additional reviewers|techlead.*(recommend|flag).*(PM|QA)' skills/groom/SKILL.md

# No pre-routing SP threshold (that was the vague heuristic)
! grep -nE 'preliminary SP estimate|SP > 8|SP threshold' skills/groom/SKILL.md

# Validator cap documented
grep -nE '≤ 2|at most 2|max 2 calls|two calls' skills/groom/SKILL.md
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | Rewrite `skills/groom/SKILL.md` Orchestration section: bug → techlead only; refactor → techlead only; feature → techlead runs first, then conditional PM/QA; teamlead still synthesizes the plan file at the end. Include a decision flowchart in fenced-code form | `skills/groom/SKILL.md` (L41-59) | 2 | pending |
| 7.2 | Define two (and only two) invite mechanisms: (a) user-text triggers — exact phrases `"plan tests"`, `"deep research"`, `"needs PM"`, `"verify requirements"`, `"product review"` — auto-invite PM and/or QA; (b) techlead-recommendation — techlead appends a `## Recommended additional reviewers` section to its report; the orchestrator honors any PM/QA named there. Also update `agents/booping-techlead.md` to emit this section in `/groom` mode | `skills/groom/SKILL.md` (new subsection in Orchestration), `agents/booping-techlead.md` (In /groom section, Output format block) | 1 | pending |
| 7.3 | Document the `booping-validate-plan` call budget: ≤ 2 per groom run. On second CRITICAL result, surface to user and halt — do not auto-retry a third time | `skills/groom/SKILL.md` (L140-160, Cross-validation subsection) | 1 | pending |

#### Task 7.1 DoD

- [ ] `skills/groom/SKILL.md` Orchestration section states: bug and refactoring default to techlead-only; feature runs techlead first, then decides PM/QA
- [ ] A decision flowchart or routing table names who calls whom per task-type
- [ ] Teamlead synthesizes the plan file at the end of every grooming run (all three types)

#### Task 7.2 DoD

- [ ] User-text triggers are an exact-string list, not a regex or fuzzy match: `"plan tests"`, `"deep research"`, `"needs PM"`, `"verify requirements"`, `"product review"`
- [ ] Techlead-recommendation path documented with the exact `## Recommended additional reviewers` section header
- [ ] `agents/booping-techlead.md` In-/groom output block includes the `## Recommended additional reviewers` section and instructions for when to populate it (with one-sentence rationale per reviewer)
- [ ] No pre-routing SP threshold survives in the orchestration prose (grep above enforces)

#### Task 7.3 DoD

- [ ] Cross-validation subsection states the ≤ 2 call cap explicitly
- [ ] On second CRITICAL: skill stops, surfaces the validator output to the user, and asks for direction — no auto-retry
- [ ] Exit-code table unchanged (0/1/2 semantics preserved)

---

### M8: /develop milestone-level delegation — 4 SP | pending

**Goal**: `/develop` delegates one milestone per Agent() call, not one task. Tier selection = max task-SP within the milestone (1-2 → middle, 3-4 → senior, 5 → refuse). Briefing carries the full milestone block with all tasks and aggregated DoD.

Lesson 0006 applies: briefing-header data flow changes; enumerate every consumer.

**Verify**:
```bash
grep -n 'one milestone per\|milestone as the unit\|max task-SP' skills/develop/SKILL.md
grep -n 'TaskCreate one task per plan task' skills/develop/SKILL.md  # should be absent
grep -n 'Milestone/task' skills/develop/SKILL.md  # briefing template updated
# Agents side: briefing header references a block, not a single line
grep -n 'Milestone block' agents/booping-developer-middle.md agents/booping-developer-senior.md docs/developer-agents.md
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 8.1 | Rewrite `skills/develop/SKILL.md` Phase 4 for milestone-level delegation: `TaskCreate` one per milestone; briefing contains the milestone's full task list + aggregate DoD; tier = max task-SP in that milestone | `skills/develop/SKILL.md` (L107-131) | 2 | pending |
| 8.2 | Update Phase 2.6 SP→tier table to describe "max task-SP" semantics (not per-task); add an explicit "mixed milestones (e.g. 1+1+4 SP) → senior tier, cap at 4" note | `skills/develop/SKILL.md` (L67-76) | 1 | pending |
| 8.3 | Update the canonical briefing template (inlined into `/develop` after M6 + the shrunk `docs/agent-wiring.md` stub if retained) to carry the exact milestone block shape specified below | `skills/develop/SKILL.md` (briefing block L116-131), `docs/agent-wiring.md` if retained, `agents/booping-developer-middle.md`, `agents/booping-developer-senior.md`, `docs/developer-agents.md` | 1 | pending |

**Canonical milestone briefing template (Task 8.3 must embed this exact string, with `{{…}}` substituted at runtime)**:

```text
project_root: ~/Claude/{{project}}
agent_extension: ~/Claude/{{project}}/_booping/agent_booping-developer.md

Applicable lessons:
- lessons/<id>_<title>.md
- …

Milestone: M{{N}} — {{milestone-title}} ({{milestone-SP}} SP total)
Goal: {{milestone-goal-sentence}}

Tasks:
- {{N}}.1 — {{task-description}} ({{sp}} SP) — files: {{paths}}
- {{N}}.2 — {{task-description}} ({{sp}} SP) — files: {{paths}}
  (…one bullet per task in this milestone…)

Aggregate DoD (check every box before reporting):
- [ ] {{task-1-dod-item-1}}
- [ ] {{task-1-dod-item-2}}
- [ ] {{task-2-dod-item-1}}
  (…flattened DoD across all tasks in this milestone…)

Verify command (run before reporting done):
{{exact shell command(s) from plan's milestone Verify block}}

Decisions that apply: {{D-IDs from plan}}
Files you may touch: {{union of all task file-lists}}
```

#### Task 8.1 DoD

- [ ] Phase 4 text says "For each milestone, TaskCreate one task, brief the chosen tier with the whole milestone"
- [ ] Phase 4 no longer contains "TaskCreate one task per plan task"
- [ ] Milestone-close commit semantics preserved (still one commit minimum per milestone)

#### Task 8.2 DoD

- [ ] Phase 2.6 table clearly states max task-SP selects the tier
- [ ] Mixed-milestone example spelled out (e.g. "1+1+4 SP → senior, cap at 4 SP per task")
- [ ] 5-SP refusal rule preserved

#### Task 8.3 DoD

- [ ] `skills/develop/SKILL.md` briefing block matches the canonical template above byte-for-byte (modulo `{{…}}` placeholder expansion)
- [ ] If `docs/agent-wiring.md` is retained, its briefing-template section matches the canonical template too
- [ ] `agents/booping-developer-middle.md`, `agents/booping-developer-senior.md`, `docs/developer-agents.md` Workflow sections describe receiving this exact shape (read every file across every task, check every DoD box, run the Verify before reporting)
- [ ] Enumerated audit: `diff` across the four sites returns no structural divergence (the block is the same wherever it appears)

---

### M9: Split sprints.md → sprints.md + backlog.md (CLI + tests + golden strings) — 5 SP | pending

**Goal**: `booping-plans sync-sprints` writes both `sprints.md` (Active + History tables) and `backlog.md` (backlog-only table). `in-spec` plans remain in `sprints.md` Active (D7). `bin/booping-init` pre-seeds both files. The test suite covers both outputs via an exec'd CLI invocation (lesson 0004). Any grepped stderr string is pinned to a golden file (lesson 0005). Plans with unknown `status` are surfaced, not dropped (D11).

**New decision introduced by validator pass 1**:

| # | Decision | Alternative | Why |
|---|----------|-------------|-----|
| D11 | Plans with unknown/misspelled `status` are logged to stderr (`warning: {path}: unknown status '{value}'`) and appended to a third "Unknown" section at the bottom of `sprints.md`, not silently dropped | Silently skip unknown statuses (current behavior for some malformed frontmatter) | User needs visibility; silent drop causes data loss |
| D12 | Two-file writes are NOT atomic (sequential `Path.write_text` calls). If one write fails, the other may already be on disk. Because `sync-sprints` is idempotent and deterministic, a half-write is self-healing on the next run — acceptable | Write both to `.tmp` then `os.rename` both to final | Cost of tmp+rename complexity exceeds the benefit; half-write window is measured in microseconds and the next invocation fixes it |

Lesson 0004 applies (CLI regression harness: exec the actual command). Lesson 0005 applies (stderr strings pinned in golden file). Lesson 0002 applies for M10 onward: CLI-only writer for both files.

**Verify**:
```bash
cd bin && pytest -x  # every test passes
grep -q 'backlog\.md' tests/test_booping_plans.py  # new coverage present
test -f tests/golden/error_messages.txt  # golden file exists
grep -qE '^warning:.*: ' tests/golden/error_messages.txt  # malformed-FM pattern pinned
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 9.1 | Rewrite `_cmd_sync_sprints` in `bin/booping_plans.py` to bucket plans into four sets (active, history, backlog, unknown-status), write `sprints.md` (active + history + optional unknown section) and `backlog.md` (backlog only). Preserve deterministic byte-equality. Two-file writes sequential (D12); unknown statuses logged to stderr + appended to Unknown section (D11). Add a `BACKLOG_STATUSES = {"backlog"}` constant near L15-31 | `bin/booping_plans.py` (L282-379 + L15-31) | 2 | pending |
| 9.2 | Update `bin/booping-init` to pre-seed `backlog.md` alongside `sprints.md`; update the inlined `CLAUDE.md` template in the script to list both files | `bin/booping-init` (L32-47, L75-82) | 1 | pending |
| 9.3 | Add exec'd CLI regression tests (lesson 0004): subprocess.run `booping-plans sync-sprints` against a tmp_project fixture; assert both `sprints.md` and `backlog.md` exist, have expected section headers, and are byte-deterministic on a second invocation. Update existing sync-sprints assertions for the new split; add lifecycle-integration tests for `backlog → in-spec` (row moves from backlog.md to sprints.md Active) and terminal transitions (backlog.md unchanged) | `bin/tests/test_booping_plans.py` (L294-400), `bin/tests/integration/test_lifecycle.py` (L31-128), `bin/tests/integration/test_fail_path.py` (L40-55), `bin/tests/integration/test_cancelled_path.py` (L29-56) | 1 | pending |
| 9.4 | Create `bin/tests/golden/error_messages.txt` pinning every stderr string `sync-sprints` emits verbatim (today: `warning: {path}: {yaml-error}`; post-D11: also `warning: {path}: unknown status '{value}'`). Add a pytest that diffs observed stderr against the golden for known-malformed fixtures | `bin/tests/golden/error_messages.txt` (new), `bin/tests/test_booping_plans.py` (new golden-diff test) | 1 | pending |

#### Task 9.1 DoD

- [ ] `_cmd_sync_sprints` writes two files (sequential writes, not atomic — see D12)
- [ ] `sprints.md` Active bucket contains plans with `status ∈ {in-spec, ready-for-dev, in-progress, awaiting-retro, awaiting-learning}`
- [ ] `sprints.md` History bucket contains terminal plans (`done`, `fail`, `cancelled`) — unchanged semantics
- [ ] `sprints.md` Unknown section appears only when there is ≥ 1 plan with an unrecognized `status` (D11); its rows name the plan and the offending status value
- [ ] `backlog.md` contains plans with `status == backlog` only
- [ ] Both files carry a "do not hand-edit — run the CLI" header line
- [ ] Consecutive runs with no changes produce byte-identical output (deterministic) for both files
- [ ] Malformed frontmatter still emits `warning: {p}: {e}` on stderr and returns the non-fatal exit code
- [ ] Unknown status emits `warning: {p}: unknown status '{value}'` on stderr (D11)
- [ ] `BACKLOG_STATUSES` constant added to the constants block near L15-31

#### Task 9.2 DoD

- [ ] `booping-init` creates an empty-skeleton `backlog.md` alongside `sprints.md` (same header line + empty table header row)
- [ ] The inlined `CLAUDE.md` template names both files in the Layout bullet list

#### Task 9.3 DoD

- [ ] Regression test subprocess-execs `booping-plans sync-sprints --project=<fixture>` and asserts on exit code, files created, table headers present (not a `_cmd_sync_sprints()` Python-level call)
- [ ] Test coverage: (a) `backlog.md` output for `status: backlog` plans, (b) `in-spec` plans appear in `sprints.md` Active not `backlog.md`, (c) `backlog → in-spec` moves the row from `backlog.md` to `sprints.md` Active, (d) terminal-state transitions (`→ done/fail/cancelled`) leave `backlog.md` byte-identical, (e) deterministic re-run byte-equality for both files
- [ ] `cd bin && pytest` returns green

#### Task 9.4 DoD

- [ ] `bin/tests/golden/error_messages.txt` exists and lists each verbatim stderr string `sync-sprints` can emit today
- [ ] Pytest asserts observed stderr on known-malformed fixtures matches the golden file
- [ ] Golden file is diffable on one line per error-pattern; no regex metacharacters (literal strings or template placeholders only)

---

### M10: Audit + update skill/agent prose to name backlog.md — 3 SP | pending

**Goal**: Every prose reference to `sprints.md` in the plugin is audited and updated per the explicit rules below. Per lesson 0006 this happens in the same sprint as M9, not deferred. Per lesson 0001, Verify is enumerated — not eyeballed.

**Explicit dual-vs-single naming rules** (no subjective judgment per site):

| Context | Rule |
|---------|------|
| **"Files to read" / "Read-before-first-reply" lists** (e.g. `/chat`) | List **both** `sprints.md` and `backlog.md` |
| **`git add` commit-stage lists** in skills (`/groom`, `/develop`, `/retro`, `/learn`) | List **both** `sprints.md` and `backlog.md` |
| **Layout bullet lists** in CLAUDE.md templates + `README.md` artifacts tree | List **both** |
| **"NEVER hand-edit" hard rules** (teamlead, skill Hard-rules sections) | Name **both** files in the same bullet |
| **"Do not hand-edit X — run the CLI" CLI-fallback blocks** | Name **both** files |
| **Sentences that describe the Active/History output semantics specifically** (e.g. "sprints.md is wholesale-regenerated into Active and History tables") | **Single**: `sprints.md` only — this statement is about the sprints file shape, not the backlog |
| **`/develop`'s internal "I write to sprints.md" invariants** (ownership assertions) | **Single**: `sprints.md` — CLI is the sole writer; `/develop` does not write `backlog.md` either |
| **PRD § Artifacts table `Writer` column** for the sprint-log row | **Single**: `sprints.md` row unchanged; add a new **Backlog** row with `backlog.md` as the path |
| **Any prose that recaps `booping-plans sync-sprints` behavior** | Name **both** output files |

**Verify** (mechanical, enumerated — not manual):
```bash
# (a) Expected "both-mention" files: every one contains 'backlog.md'
for f in skills/chat/SKILL.md skills/groom/SKILL.md skills/develop/SKILL.md skills/retro/SKILL.md skills/learn/SKILL.md skills/install/template-claude-md.md agents/booping-teamlead.md docs/plan-schema.md README.md PRD.md; do
  grep -q 'backlog\.md' "$f" || { echo "FAIL: $f does not mention backlog.md"; exit 1; }
done

# (b) Every `git add` line in the four orchestrator skills lists both files
for f in skills/groom/SKILL.md skills/develop/SKILL.md skills/retro/SKILL.md skills/learn/SKILL.md; do
  # Extract every git-add block and ensure each that names sprints.md also names backlog.md
  awk '/git add/{show=1} show{print} /^```$/{show=0}' "$f" | grep -E 'git add.*sprints\.md' | while read -r line; do
    echo "$line" | grep -q 'backlog\.md' || { echo "FAIL: $f: git add line names sprints.md but not backlog.md: $line"; exit 1; }
  done
done

# (c) Teamlead hard rule names both
grep -n 'NEVER hand-edit.*sprints\.md.*backlog\.md\|NEVER hand-edit.*backlog\.md.*sprints\.md' agents/booping-teamlead.md

# (d) /chat reads both
grep -A 5 'Read-before-first-reply' skills/chat/SKILL.md | grep -q 'backlog\.md'
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 10.1 | Apply the dual-vs-single rules above to every `sprints.md` mention in the enumerated file set. Use the rule table as the decision procedure per site — no judgment calls | `PRD.md` (L24 artifacts table + new backlog row), `README.md` (L43 skills table, L75 artifacts tree), `skills/help/SKILL.md` (L35, L45, L79, L105), `skills/develop/SKILL.md` (L3, L45, L96, L103, L166, L187), `skills/groom/SKILL.md` (L114, L169, L176, L211, L217, L225, L233), `skills/retro/SKILL.md` (L140, L147, L153, L173), `skills/learn/SKILL.md` (L126, L131, L137), `skills/chat/SKILL.md` (L33, L55), `skills/install/template-claude-md.md` (L16), `agents/booping-teamlead.md` (L50), `docs/plan-schema.md` (L5, L56) | 3 | pending |

#### Task 10.1 DoD

- [ ] Every "Files to read" and "git add" list in the four orchestrator skills (`/groom`, `/develop`, `/retro`, `/learn`) names both `sprints.md` and `backlog.md`
- [ ] `/chat` `Read-before-first-reply` lists both files
- [ ] `README.md` artifacts tree diagram shows both files under `{project}/` with a comment naming the CLI as writer
- [ ] `PRD.md` § Artifacts table has a new row for `backlog.md` (writer: `booping-plans sync-sprints` via `/groom`)
- [ ] `skills/install/template-claude-md.md` Layout bullet names both files
- [ ] `agents/booping-teamlead.md` Hard rule about not hand-editing names both files in the same bullet
- [ ] `docs/plan-schema.md` § "sprints.md generation" renamed to § "Generated registry files"; text covers both outputs (scope leaks into M11, which restructures it further)
- [ ] Sentences explicitly describing `sprints.md`'s Active/History shape remain single-file (no noise-additions)
- [ ] Enumerated audit: the four mechanical checks in Verify above all return success

---

### M11: Simplify docs/plan-schema.md CLI section — 2 SP | pending

**Goal**: `docs/plan-schema.md`'s "CLI and fallback" section becomes a short examples block pointing to `booping-plans --help` as authoritative. The "sprints.md generation" section reflects the two-file split from M9.

**Verify**:
```bash
wc -l docs/plan-schema.md
grep -n 'booping-plans --help' docs/plan-schema.md
grep -A 2 '## sprints.md generation\|## Generated files' docs/plan-schema.md | head -20
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 11.1 | Replace the "CLI and fallback" section with ≤ 5 example invocations covering: `set status=`, `set status= with key=value pair`, `sync-sprints`, the non-zero fallback pattern. Point the reader to `booping-plans --help` for the full reference | `docs/plan-schema.md` (L60-62 region) | 1 | pending |
| 11.2 | Rewrite the "sprints.md generation" section to name both `sprints.md` and `backlog.md`, with one-line buckets per file (active/history vs backlog) and a cross-ref to `booping-plans sync-sprints` behavior | `docs/plan-schema.md` (L54-56 region) | 1 | pending |

#### Task 11.1 DoD

- [ ] CLI section contains ≤ 5 fenced example blocks
- [ ] Section ends with: "Full reference: `booping-plans --help`."
- [ ] No long-form flag/exit-code tables (those live in `--help`)

#### Task 11.2 DoD

- [ ] `docs/plan-schema.md` names both output files
- [ ] Active/History vs Backlog buckets documented
- [ ] Deterministic byte-equality property still called out (applies to both files)

---

## Final Verification

Commands to run at end of sprint, in order:

```bash
# 1. Agent roster is two-tier, junior gone
test ! -f /home/anton/Dev/@A/claude-booping/agents/booping-developer-junior.md
! grep -rn 'booping-developer-junior\|developer-junior' /home/anton/Dev/@A/claude-booping/agents /home/anton/Dev/@A/claude-booping/skills /home/anton/Dev/@A/claude-booping/docs /home/anton/Dev/@A/claude-booping/README.md /home/anton/Dev/@A/claude-booping/PRD.md

# 2. Model frontmatter matches target grid (loop over each agent)
for f in agents/booping-techlead.md:opus:xhigh agents/booping-product-manager.md:opus:xhigh agents/booping-teamlead.md:opus:high agents/booping-qa-lead.md:opus:high agents/booping-developer-senior.md:opus:high agents/booping-reviewer.md:opus:high; do
  file="${f%%:*}"; rest="${f#*:}"; want_model="${rest%%:*}"; want_effort="${rest#*:}"
  got_model=$(grep -m1 '^model:' "$file" | awk '{print $2}')
  got_effort=$(grep -m1 '^effort:' "$file" | awk '{print $2}')
  [ "$got_model" = "$want_model" ] && [ "$got_effort" = "$want_effort" ] || { echo "MISMATCH: $file got model=$got_model effort=$got_effort want=$want_model/$want_effort"; exit 1; }
done
grep -m1 '^model: sonnet' agents/booping-developer-middle.md
! grep '^effort:' agents/booping-developer-middle.md
grep -m1 '^effort: xhigh' skills/groom/SKILL.md

# 3. Agent internals stripped
! grep -rn 'written by \`/learn\`\|Tier calibration\|If you find a simpler approach\|No monkey-patching\|tagged \`' agents/*.md

# 4. docs/developer-agents.md exists + drift-free
test -f docs/developer-agents.md
just dev-agents-drift

# 5. Teamlead is support, not coordinator
! grep -n '^tools: .*Agent(booping-' agents/booping-teamlead.md
! grep -n 'Coordinate other agents\|Coordinate the above\|you delegate' agents/booping-teamlead.md

# 6. Lesson wiring simplified
! grep -rn 'tagged \`' agents/*.md
[ -f docs/agent-wiring.md ] && [ "$(wc -l < docs/agent-wiring.md)" -le 30 ] || [ ! -f docs/agent-wiring.md ]

# 7. Groom is dynamic
grep -n 'techlead only\|techlead first\|plan tests\|deep research' skills/groom/SKILL.md
grep -n 'at most 2\|≤ 2\|max.*2 calls' skills/groom/SKILL.md

# 8. Develop is milestone-level
grep -n 'one milestone per\|milestone as the unit\|max task-SP' skills/develop/SKILL.md
! grep -n 'one task per plan task' skills/develop/SKILL.md

# 9. sync-sprints writes two files + tests pass; golden stderr file present
cd bin && pytest -x && cd -
test -f bin/tests/golden/error_messages.txt

# 10. sprints.md audit — every expected consumer names backlog.md
for f in skills/chat/SKILL.md skills/groom/SKILL.md skills/develop/SKILL.md skills/retro/SKILL.md skills/learn/SKILL.md skills/install/template-claude-md.md agents/booping-teamlead.md docs/plan-schema.md README.md PRD.md; do
  grep -q 'backlog\.md' "$f" || { echo "FAIL: $f missing backlog.md reference"; exit 1; }
done

# 11. plan-schema CLI trimmed
wc -l docs/plan-schema.md
grep -n 'booping-plans --help' docs/plan-schema.md
```

## Risk register

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| M9 creates a "CLI-only writer" invariant for sprints.md + backlog.md; worker agents during M10 inadvertently hand-edit backlog.md while auditing prose | medium | Lesson 0002 applies for the rest of this sprint; `_booping/skill_develop.md` already has the invariant-sprints rule. Flag to reviewer at M9 close |
| Claude Code silently ignores unknown frontmatter keys; `effort: xhigh` may not be honored on every model tier (user confirmed it's a valid tier in Claude Code UI, but plugin-frontmatter honoring is not independently tested) | low | Trust the user's screenshot evidence. If `xhigh` does not take effect, the regression is orthogonal to the rest of the sprint; can be retuned in a follow-up |
| M4's drift check (byte-diff between `docs/developer-agents.md` and each inlined agent body) may false-positive on unrelated whitespace edits | medium | Use block-marker fences (`<!-- BEGIN shared -->` / `<!-- END shared -->`) and diff only the enclosed region |
| M8 milestone-level delegation may exceed agent context on large milestones (6+ tasks) | low | Current largest milestones in real plans are 4-5 tasks; reviewer can flag if a milestone grows beyond that and require pre-split in grooming |
| M10 is the lesson-0006 audit milestone for M9; if the audit is spot-checked instead of enumerated (the classic regression lesson 0001 was extracted from), we will miss stale sprints.md-only mentions | high | Lesson 0001's enumeration-Verify rule is mandatory; the Verify block above greps the full file set |
| `booping-validate-plan` call-budget cap at 2 may hide real CRITICAL issues that a third retry would catch | low | Escalation path: on second CRITICAL, surface to user explicitly rather than silently accept |
| M9 two-file writes are non-atomic (D12): if the process dies between writing `sprints.md` and `backlog.md`, the vault has mixed state until the next sync | low | `sync-sprints` is idempotent + deterministic; a half-write self-heals on the next invocation. `git status` in the project vault makes the inconsistency visible. Accepted trade-off |
| M9 unknown-status handling (D11): plans with new/misspelled `status:` values surface in an "Unknown" section instead of being silently dropped — user must clean them up | low | Visibility is the right default; silent drop caused the lesson 0006 class of bug. The "Unknown" section names both the plan and the offending value |

## Out of scope

- Changing `/develop`, `/retro`, `/learn` skill frontmatter (`effort:`) — only `/groom` is in the override grid
- Adding a `reasoning:` frontmatter key anywhere (D3)
- Renaming any existing status in the 9-state lifecycle
- Changing the `booping-plans` CLI subcommand surface (only `sync-sprints`'s output changes)
- Migrating existing project vaults' `sprints.md` — first `sync-sprints` run after M9 lands handles it; no migration script
- Replacing the `_booping/agent_booping-developer.md` extension file shape — shared-between-tiers behavior preserved (D4)
- Introducing a project-local SP threshold override for the QA-invite heuristic in M7 — parked for a follow-up; default 8-SP threshold is plugin-shipped
- Touching `skills/chat/SKILL.md` beyond the sprints.md/backlog.md mention — `/chat` does not participate in any other strand here
- Introducing a golden file for CLI stderr strings (lesson 0005) — only add if M9 introduces a new grepped-verbatim string; no pre-work

## CLAUDE.md impact

- `~/Claude/claude-booping/CLAUDE.md` Layout section currently lists `sprints.md` as the only registry file — after M9 it must list both `sprints.md` and `backlog.md`. Task 9.2 updates the `booping-init` template; an owning task in M10 updates the project CLAUDE.md directly. (Add task 10.2 if the audit reveals the project CLAUDE.md Layout section is stale.)
- `skills/install/template-claude-md.md` Layout bullet is part of M10's enumerated audit; no separate task needed.
- No in-repo `<repo>/CLAUDE.md` changes required — this plan touches plugin internals, not a downstream codebase.
