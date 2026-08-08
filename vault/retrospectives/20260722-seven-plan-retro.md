---
plans:
  - plans/20260722-booping-global-config-home-dir.md
  - plans/20260709-benchmark-framework-core.md
  - plans/20260709-benchmark-judge-groom-case-reports.md
  - plans/20260629-install-stop-seeding-duplicate-extensions.md
  - plans/20260628-local-vault-directories.md
  - plans/20260614-actualize-docs-site-and-readme.md
  - plans/20260610-simplify-cli-delegation-to-global-agent.md
date: 2026-07-22
goal_summary: All seven plans reached their goals (131 SP); the one strategic loss is the 71-SP benchmark harness whose goal was never challenged and is now unused.
goal_verdicts:
  plans/20260722-booping-global-config-home-dir.md: success
  plans/20260709-benchmark-framework-core.md: success
  plans/20260709-benchmark-judge-groom-case-reports.md: success
  plans/20260629-install-stop-seeding-duplicate-extensions.md: success
  plans/20260628-local-vault-directories.md: success
  plans/20260614-actualize-docs-site-and-readme.md: success
  plans/20260610-simplify-cli-delegation-to-global-agent.md: success
---

# Retro — seven plans, 2026-06-10 → 2026-07-22

Sprint set: 131 SP across 7 plans (11 + 35 + 36 + 5 + 17 + 17 + 10). All plan goals user-confirmed `success`; all Final Verification checklists pass; code review smooth across the set. Overall user read: good with caveats.

## What went well

- Global config + `home_dir` shipped end-to-end and the live vault migration to `~/Dev/@A/notes/projects/` passed the M3 user-driven checklist on the real machine — the user-named win of the set.
- The 35-SP bench-core sprint ran autonomously overnight against a pre-approved decision list; 3/3 calibration reps completed and the escalation policy held (single planned wake-up).
- The pi-developer permission-mode blocker discovered in the overnight run was subsequently resolved by the agent-wrapper switch for CLI agents — the failure fed a design correction rather than lingering.
- The simplification arc held across plans: the cli-agent wrapper subsystem was deleted wholesale (one invocation path for all external workers), and `/install` stopped seeding CLAUDE.md-duplicating extensions.
- Data contracts locked with the user before implementation (bench case dir, expect.yaml, result record, report shapes) kept two large bench sprints on rails with no contract rework.

## What went wrong

#### Groom drafts model-side logic where a script belongs

**What happened**: The global-config groom draft proposed AI-side fallback logic for directory resolution; the user had to demand a deterministic script call ("use script to deterministically get dir, not fallbacks in AI").

**Root cause**: Groom has no design heuristic preferring deterministic mechanisms over model-side judgment — the project applies exactly this split to `booping transition` (LLM decides the edge, command owns mechanics) but the principle is not stated anywhere groom reads, so new designs don't inherit it.

**Impact**: The user carries the burden of catching and redesigning resolution logic in plan review; uncaught cases would ship nondeterministic behavior into shell tooling.

#### Groom pads scope beyond the ask

**What happened**: The same draft included test-isolation framing and a prose-sweep task the user never asked for; both were cut in review ("why it's in scope ... sweep also is out of scope").

**Root cause**: Research-heavy grooming optimizes for completeness with no counterweight — no check that every milestone/task traces to the stated ask or a named risk before the draft is presented.

**Impact**: Larger drafts than requested, heavier review rounds, and recurring user work stripping unsolicited scope.

#### Framework-owned decisions reach the user uncaught

**What happened**: The global-config draft baked in decisions the framework owns ("Rule 4 violating ... Rule 7 - same, framework decides it"); the user, not the skill, caught the ownership violations.

**Root cause**: Lesson 0004's four-check pass is framed as a save-time gate on prompt artifacts, but groom never runs its Scoping check against the Information-ownership ladder on the *plan draft* before presenting — so ownership violations surface only in user review.

**Impact**: User review does work the skill should do; the IA pass exists but fires too late in the flow to prevent the class of error it names.

#### Long-running work goes dark

**What happened**: Bench-v2 M5 calibration sat for an hour with a stalled run (1/3 records) until the user prodded ("is everything all right? You're sitting on M5 for an hour already", "how many runs you did in total?").

**Root cause**: Plans and briefings for long-running external commands (docker reps, calibration runs) carry no expected-duration or progress contract, so the orchestrator cannot distinguish "working" from "stalled" and stays silent.

**Impact**: User becomes the watchdog; stalls burn wall-clock undetected; trust in autonomous execution erodes exactly where it matters most.

#### Audience-scoping fails at the delegation boundary

**What happened**: Local-vault user docs exposed internal `vault_path:` implementation detail; the user caught it post-hoc ("oversharing, remove", "same for doc index").

**Root cause**: Lesson 0006 lives in the skill-loaded lesson set, but doc-writing was delegated to a worker whose briefing carried only the task DoD — and the DoD had no audience line, so the lesson never reached the generation point.

**Impact**: Post-edit cleanup rounds on user-facing docs — the exact rework mode lesson 0006 exists to prevent, recurring for the third time (release notes, cli-agent docs review, now local-vault docs).

#### Docs coverage judged only post-hoc

**What happened**: After the local-vault sprint "looked good", the user still had to ask "Is documentation updated about local vault?" — triggering a doc pass beyond what the plan's docs milestone covered.

**Root cause**: No standing gate maps "user-visible behavior change" to a docs task enumerating the affected pages at groom time; doc coverage is assessed by the user after approval instead of by the plan before it.

**Impact**: Docs trail features until the user notices; the docs-actualize plan (17 SP) is partly the accumulated interest on this gap.

#### Lesson-0004 DoD gating is inconsistent across plans

**What happened**: Five of seven plans gate some prompt-bearing artifacts on the four-check IA pass and skip others of the same class — bench-core M5.2 omits the seeded plan body, bench-v2 M3/M5 have no IA-pass item at all, the install-seeding rewrite and the groom branch-offer template edit and the pi-developer agent all lack it.

**Root cause**: Folding lessons into DoDs is per-artifact recall rather than a rule keyed on artifact class ("task touches a prompt-bearing artifact ⇒ IA-pass DoD line"), so coverage depends on what the groomer happens to remember per milestone.

**Impact**: The lesson's protection is probabilistic; identical artifact classes are gated in one milestone and unguarded in the next.

#### Imported plans are flagged, not adapted

**What happened**: Plans authored in other projects were brought into this one; instead of being challenged and adapted against this project's guidelines, mismatched rules were simply flagged as violated (user-raised).

**Root cause**: No intake path exists for foreign plans — skills treat guideline mismatch as a violation to report rather than material to own and rewrite, because every flow assumes plans originate in-project.

**Impact**: Noise flags the user must resolve manually; imported work enters execution half-aligned with project conventions.

#### 71 SP of benchmarks shipped, then unused

**What happened**: Two sprints (35 + 36 SP) built a complete score-based benchmark harness; the user has not used it since, and working on evals now realizes the actual need is "unit test"-style evals for decomposed prompt instructions (user-raised: "mb better challenge me on goal, but think i was sure i need benchmarks").

**Root cause**: Groom challenges scope and design but never the goal — it accepted "benchmarks" as the deliverable without probing the underlying need (regression safety per prompt instruction), for which unit-test-style eval harnesses (promptfoo/DeepEval-pattern decomposed assertions) are the closer fit.

**Impact**: The set's largest investment sits idle; the underlying need remains unmet and will cost another build — though the bench checks engine and container runtime are partially reusable.

## Lesson gaps

- `lessons/0004_information-architecture-pattern.md` — rule is "run every prompt artefact through the four-check pass", but the pass was neither run on plan drafts before presenting (framework-owned decisions reached the user) nor consistently stamped into DoDs for same-class artifacts across five plans.
- `lessons/0006_audience-scoped-content.md` — rule is "audience-scoping is a generation-time decision, not a post-edit cleanup", but local-vault user docs shipped internal `vault_path:` detail and were cleaned only after user review, the third recurrence of this pattern.

## Action items & takeaways

| # | Type | Item | Owner | Status |
|---|------|------|-------|--------|
| 1 | Task | Add groom Craft heuristics: deterministic-mechanism default; every task traces to the stated ask or a named risk; draft-stage 0004 Scoping pass against the Information-ownership ladder before presenting | Next sprint (/learn) | Planned |
| 2 | Task | Plan-template rule: any task authoring/editing a prompt-bearing artifact carries the 0004 IA-pass DoD line; any docs task carries an audience-scope (0006) DoD line | Next sprint (/learn) | Planned |
| 3 | Task | Groom goal-challenge gate for large plans: restate the underlying need and offer at least one cheaper alternative before drafting | Next sprint (/learn) | Planned |
| 4 | Task | Foreign-plan intake: an adaptation pass (own-and-adapt against project guidelines; surface unadaptable items as decisions, not flags) when a plan originates outside the project | Next sprint (/learn) | Planned |
| 5 | Heuristic | Long-running Verify/calibration steps state expected wall time in the plan; /develop surfaces progress when the expectation is exceeded | standing | Planned |
| 6 | Task | Explore a unit-test-style eval harness for decomposed prompt instructions (promptfoo/DeepEval assertion pattern; bench `checks.py` + container runtime partially reusable) | User | Planned |

Takeaways:

- Challenge the *goal* before the scope — a well-groomed plan for the wrong deliverable is the most expensive failure mode this set produced.
- Lessons only fire where they're wired: a lesson not folded into a DoD line or briefing sentence is invisible at execution time, however prominent it is in the loaded set.
- Anything the model resolves at runtime that a script could resolve deterministically is a design smell — the same split that shaped `booping transition` applies to every new design.

## Self-review checklist

- [x] Each "what went wrong" item has a named root cause (a pattern, not a restatement).
- [x] Lesson gaps cite existing lessons by path and explain the gap.
- [x] Items are specific with an owner (or "standing" for heuristics) and a clear next step.
- [x] Heuristics are concrete enough that someone could apply them next sprint — not platitudes.
- [x] "What went well" is honest, not inflated to balance criticism.
- [x] No blame language — focus on decisions and processes, not people.
