---
plans:
  - plans/20260423-refactor-chat-skill-to-groom-pattern.md
  - plans/20260423-refactor-develop-skill-to-groom-pattern.md
  - plans/20260423-refactor-retro-skill-to-groom-pattern.md
date: 2026-04-23
goal_summary: Three sister refactors propagated the groom pattern to /chat, /develop, and /retro; all three hit their DoD. Out-of-plan meta-refactors reshaped shared partials mid-stream — treated as intentional shaping of a young codebase, at the cost of plan-vs-file fidelity.
---

## What went well

- `/chat`, `/develop`, and `/retro` all match the groom shape (Preflight loads partials → phased workflow → scoped Hard rules, ≤130 lines). A fresh agent reading any of the three finds live references only.
- A failure mode became a durable rule **in the same session**: the user's "stop abusing cross-validation" interruption produced D14 in the /retro plan, which added the one-shot rule to `docs/partial_cross_validation.md`. Every future groom Preflight inherits it.
- D9 ("zero concrete vault references" in the retro skill body) held: `grep -E 'lessons/[0-9]{4}_' skills/retro/SKILL.md` returns empty. Per-project injection via `_booping/skill_retro.md` is the sole extensibility channel.
- Lesson 0001 (universal-quantifier enumeration) applied consistently in *plan* Verify blocks — every "every / zero / each" DoD bullet had a mechanical check, not a spot-check.
- Agent-surface cleanup: five deletions (techlead, product-manager, qa-lead, teamlead, reviewer) + `docs/agent-wiring.md` removed in one milestone. No agent remains dormant after the /retro sprint.

---

## What went wrong

### Cross-validation re-run discipline wasn't codified until mid-retro

**What happened**: The user had to stop Gemini re-runs twice during grooming — once in the /develop plan ("don't overuse cross-validation"), once in the /retro plan ("Stop abusing cross-validation, it's not a tool to run after every change"). The one-shot rule only landed in the /retro sprint's M1 (D14 → `docs/partial_cross_validation.md`), so the /chat and /develop grooms couldn't inherit it.

**Why**: `partial_cross_validation.md` existed but carried no cadence rule. The default behavior ("re-run after every substantive edit") was the implicit one, and no Preflight partial contradicted it.

**Impact**: Two user interruptions + two wasted validation runs across the three grooms. Small cost this time; would have grown linearly with future grooms if D14 hadn't landed.

### Lessons 0004 and 0005 were loaded every sprint but never applied or explicitly overridden (in two of three plans)

**What happened**: All three plans loaded `lessons/0004_skill-body-regression-harness.md` (pytest harness for documented CLI invocations) and `lessons/0005_cli-error-string-contract.md` (pin stderr strings a skill greps in a golden file) at Preflight. The /chat plan added the new `booping-plans --format=md` path and recorded an explicit override row in Risk register ("No tests. User-set policy."). The /develop and /retro plans each documented new CLI invocations (`booping-plans --status awaiting-learning`, `--status awaiting-retro`) and pinned verbatim error strings (e.g. `"/retro requires a plan in status 'awaiting-retro'..."`) — neither cited 0004 or 0005, and neither added an override row.

**Why**: Two causes compound. (a) The "No tests" project policy (repo `CLAUDE.md`) pre-overrides 0004 globally, but that override isn't annotated on the lesson file itself or in `partial_read_lessons.md`. (b) 0005 isn't blocked by the no-tests policy — it's about pinning strings regardless of whether tests exist — and was still silent on the /retro skill's new pinned error string, which is exactly the pattern 0005 names.

**Impact**: A loaded lesson that a plan silently doesn't apply is worse than an unloaded one — it creates the impression the rule was considered when it wasn't. If 0005's pattern becomes a real requirement later, there's no trail showing which plans silently skipped versus which explicitly overrode.

### Worker self-attestation without a mechanical verifier (/develop M3)

**What happened**: In /develop's M3 legacy audit, the junior worker reported "Hard-rules audit complete — no stale bullets found" for `skills/help/SKILL.md` without running or quoting a grep. The M3 reviewer caught a stale `sprints.md` ownership bullet the worker had missed; the orchestrator fixed it inline. Recorded in the /develop Risk register as a retro candidate.

**Why**: Task 3.1's brief required the audit but didn't require the worker to emit the `grep -E` command and its stdout/stderr as part of the Done report. The worker's prose claim propagated through the reviewer handoff unchallenged.

**Impact**: One reviewer catch this pass. The pattern — "agent claims 'I checked X' without the verifier string in its report" — generalizes; it would have bitten harder on a larger audit cohort.

### /retro grooming took three iterations to converge

**What happened**: The /retro plan's Context explicitly states "third iteration — condensed to its current shape after two prior draft passes". Each iteration was driven by a multi-item user correction: drop researcher-senior delegation, delete reviewer + role agents, remove domain-tag references, add the cross-validation partial update, externalize the retrospective template.

**Why**: v1 and v2 of the groom were written by analogy to the /develop groom without probing per-plan delegation boundaries and deletion candidates in Phase 0. The user's intent ("trim delegation to the minimum; retro owns the lesson cross-check inline; delete the dormant reviewer") emerged through critique of v1/v2 rather than being surfaced by an up-front question.

**Impact**: Two extra groom loops, two Gemini runs, a larger Risk register. Cost was entirely at grooming time; sprint execution itself was clean.

### Out-of-plan follow-up work during the awaiting-retro window

**What happened**: After /develop was marked `awaiting-retro`, commit `71044b6` ("per-project quality-check loop + tighten briefing plumbing") landed without being in the /develop plan. Between the /develop and /retro sprints, a stream of meta-refactors also landed: partial_agents_ rename (`6a82a74`), branch-naming extraction (`c8d60a2`), mid/senior delegation strategy (`50f6b16`), help skill pointing at delegation partial (`b563979`), lesson-template + read-lessons partial (`ef553fd`), agent-wiring moved into delegator partial (`ab792ef`). These reshaped partials the /develop plan had just produced.

**Why**: User's explicit stance (Phase 2 answer): *"they are in scope. it's mostly because the project is fresh and need to do some shaping to get it into a good form. So, it was faster to do in the chat session, rather than plan."* The meta-work is intentional young-project shaping — formal grooming of a rename or a partial-split is overhead that doesn't match the value at this stage.

**Impact**: The /develop plan's "done" state is historical, not current. A later reader diffing `skills/develop/SKILL.md` against the plan that built it will find divergence (e.g. the per-project quality-check loop is in the file but not in the plan). Not harmful today; the cost is plan-as-documentation fidelity for the next reader who expects plans to describe the current file.

---

## Root causes

1. **Codified rules lag the failure pattern.** D14 (cross-validation one-shot) was only written after the user had to stop the same behavior twice. The pattern — "failure happens → rule gets written → *later* sprints benefit" — is structural: the first N sprints are always unprotected until a rule crystallizes. The retro that catches the pattern is the first mechanism that enforces codification in the same session.

2. **Loaded-but-silent lessons create invisible drift.** Preflight loads every lesson, but nothing forces a plan to account for each one (apply / override / out-of-scope). The /chat plan's explicit Risk-row override for 0004 is the only model in this sprint trio. The other plans' silence on 0004 and 0005 is indistinguishable from negligence even when it's actually policy.

3. **Worker reports don't carry verifier artefacts.** The /develop M3 catch was a prose assertion that happened to be wrong. No part of the briefing template required the worker to paste the verifier command's output; the orchestrator (and reviewer) can't distinguish "I ran grep and it returned nothing" from "I eyeballed and it looked clean."

4. **Young-project shaping happens outside plans, by design.** User confirmed this is a deliberate speed/discipline tradeoff. It's coherent — but the file surface the meta-work touched (partials, delegation strategies, agent-wiring) is exactly the surface these three plans aimed to stabilize. So the stabilization is relative to a moving target, and the plans-as-documentation contract weakens during the shaping phase.

### Ignored / unapplied lessons

- `lessons/0004_skill-body-regression-harness.md` — rule was "exec every documented CLI invocation in skill bodies via a pytest harness". The /develop plan documented new invocations (`booping-plans --status awaiting-learning`, `--status ...`) and the /retro plan documented `booping-plans --status awaiting-retro`; neither cited 0004 or recorded an override. The /chat plan did record the override (Risk register row). The silent-skip pattern in 2 of 3 plans is the drift — if the project's no-tests policy is meant to override 0004 globally, that override should live on the lesson file itself (or in `partial_read_lessons.md`), not as a per-plan convention some grooms remember and others don't.
- `lessons/0005_cli-error-string-contract.md` — rule was "pin any CLI stderr string a skill greps verbatim in a golden file". The /retro plan added `"/retro requires a plan in status 'awaiting-retro'..."` at Phase 0 — exactly the stderr-pinning pattern 0005 names — without citing 0005 or recording an override. This one is orthogonal to the no-tests policy; it's not about running tests, it's about where the canonical string lives.
- `lessons/0001_verify-block-universal-quantifiers.md` — rule was "universal quantifiers in DoD must enumerate via a mechanical check, not a spot-check". Applied correctly to plan-level Verify blocks across all three sprints. *Not* extended to worker self-report inside /develop M3 — the briefing required "audit complete" as a checkbox but didn't require the enumeration command output. Lesson 0001's spirit reaches worker self-attestation; the letter, as currently written, stops at the plan's Verify block.

---

## Action items

| # | Action | Owner | Status |
|---|--------|-------|--------|
| 1 | Annotate lessons with an explicit `policy-override:` or `applies-when:` field (start with 0004 → "overridden by repo CLAUDE.md 'No tests' policy"). `/groom` Preflight's lesson summary prints the applies-or-override verdict per lesson so silent skipping is no longer possible. | `/learn` next invocation | Planned |
| 2 | Extend the briefing template for audit-type tasks: any DoD bullet of shape "audit X has no Y" requires the worker's Done report to include the mechanical check command AND its stdout/stderr, verbatim in a code block. Prose claims alone are insufficient. Fold into `partial_agents_mid_senior.md`. | `/learn` next invocation | Planned |
| 3 | Decide and record the in-session-shaping policy in repo `CLAUDE.md`: is orchestrator-direct editing of shared partials acceptable while the project is young (Y/N), and if Y, what milestone or signal flips the bit? This is what lets a future reader interpret `71086f4`-style commits without ambiguity. | User | Planned |
| 4 | Next stale-skill groom (`/learn`) begins Phase 0 with an explicit probe: "Which sub-agents should this skill touch? Which currently-referenced agents should be deleted?" — intended to collapse the v1→v2→v3 iteration cost the /retro groom paid. | Next `/groom` of a stale skill | Planned |

---

## Takeaways for this project

- **When the user interrupts twice for the same behavior, codify the rule *in the current sprint*, not the next one.** The /retro sprint's D14 is the model: the interruption became a plan-level decision, which landed a partial update, in the same session. Two earlier interruptions paid full cost because no one wrote it down.
- **Every loaded lesson must leave a trace in the plan — apply, override, or out-of-scope.** The /chat plan's Risk-row explicit override for 0004 is the template. "Silent" is not a valid third state.
- **Audit-task Done reports include the verifier's actual output, not a prose claim.** "I checked X and it's clean" is unverifiable. `grep -E 'pattern' files` followed by its stdout/stderr in a code block is verifiable. Bake into the briefing template for any audit-class task.
- **In-session shaping is a valid mode for a young codebase — but name it in the plan header or skip the plan altogether.** Half-in / half-out is the failure mode: a plan that describes a file which then gets reshaped out-of-plan during the awaiting-retro window becomes misleading documentation. Either the reshape waits for its own plan, or the original plan declares up front "this sprint lands a scaffold; polish follows in ad-hoc chat sessions until signal X".
- **Retro plans especially benefit from delegation-boundary and deletion probing *before* v1.** The /retro groom spent two iterations discovering what the user actually wanted. Those could have been one `AskUserQuestion` block in Phase 0.

---

## Information architecture pattern

A prescriptive framework surfaced during this session for every prompt-bearing artifact we author — skills, agents, partials, templates, briefings. Run four checks before saving any block; if any answer is "no" or "unsure", rewrite or move the block.

Context for the pattern: the 2026-04-23 refactor session surfaced three kinds of rot that accumulate without this pass. *Context rot* — a phrase added to defuse a past user correction ("never read any lessons") that rots into noise once the trigger is forgotten. *Leakage* — orchestrator concepts (lessons, `/learn`, plan statuses) ending up inside agent bodies that don't need them, bloating the system prompt and inviting the agent to reason about things outside its contract. *Encoded duplication* — the same rule repeated verbatim across multiple agent / skill files so a change touches many places and silently drifts in one. Today's developer-agent refactor hit all three: agents named `/learn`, agents carried a `/groom`-scoped "no monkey-patching" rule, three agent bodies duplicated the same workflow + hard rules, and "files to touch" phrasing contradicted a rename that hadn't propagated.

### (1) Scoping — does the consumer actually need this?

- Name the component that reads this block at runtime (agent spawn, skill invocation, groom read-through).
- Does the component need the information **to perform its job**, or would removing it change nothing about its behavior?
- Is the block leaking a higher-layer concept into a lower-layer consumer? Agents should not know about lessons, plan statuses, `/learn`, `/groom`, or the vault layout — they receive briefings. Skills should not carry stack-specific detail — that lives in `_booping/skill_<name>.md`.
- Is the block *context rot* — a defusing phrase born from a past correction that no longer describes a live rule? If you can't name the original trigger or the trigger is now resolved structurally, delete the phrase.

### (2) Duplication — does this block belong in more than one consumer?

- Does the same content (or near-same) already exist in another skill / agent / partial? If yes, one of the copies is drift waiting to happen.
- If two or more consumers need the block, extract to `docs/partial_<topic>.md` (runtime content) or `docs/template_<topic>.md` (copy-into-place content) and have each consumer reference the shared file.
- If the block only has one consumer *today* but is authoring-time content (a template, a decision checklist), extract anyway — a single-consumer partial has near-zero cost and sets the pattern for when the second consumer appears.
- If the block genuinely has one consumer and is small runtime content (e.g. one skill's Phase 0 command), keep it inline — premature partials are their own kind of rot.

### (3) Configurability — is this a specific behavior someone might want to tune?

- Is this block a *policy* that a different project might set differently (test framework choice, branch-prefix table, cross-validation cadence, lesson-scope annotations)? Policies belong in partials or project-local extensions, not baked into a wide-domain skill body.
- Keep inline when the block is part of the skill's main flow and extracting would fragment reader comprehension.
- Extract when the block is a detail the main flow doesn't need to explain — the reader understands "load partials at Preflight" without reading each partial's body. The rule: **extraction helps when it hides implementation; extraction hurts when it hides the flow**.
- When extracting, ask: will a future tweak touch the partial alone, or will it cascade into the skill? If "cascade", the partial boundary is wrong — redraw it.

### (4) Hierarchy — does the read-path form a clean tree?

- Good shape: skill → delegator partial → strategy partial → agent briefing template → agent body. Each layer owns one decision and references the next.
- Adding a new strategy should mean creating one new file (`partial_agents_<strategy>.md`), not editing the delegator or any agent.
- Adding a new agent tier should mean creating one new agent file and updating the strategy partial's roster — not touching the skill body.
- Changing the briefing header should be a single-file edit in the strategy partial — not a hunt across every skill that spawns agents.
- If a change requires edits in more than one layer, the hierarchy is wrong: some layer is claiming a responsibility it shouldn't own. Redraw the boundary before completing the edit.

### Forbidden anti-patterns

- Agent body that names any skill by command (`/groom`, `/learn`, `/develop`) — the agent doesn't invoke or coordinate skills.
- Skill body that lists stack-specific tooling or file layout — use `_booping/skill_<name>.md` extension.
- A "rule" in an agent body that only fires during authoring time (e.g. "before writing tests, consider X") — that's a `/groom` or `/learn` concern.
- A sentence whose only purpose is to negate something ("never scan the vault") without a positive rule attached — either say what TO do, or delete the negation.
- Three agent / skill files carrying the same paragraph — extract before committing the third copy.

---

## Self-review checklist

- [x] Each "what went wrong" item has a traceable cause (plan decision, blind spot, or carried debt).
- [x] Root causes are patterns, not restatements of individual issues.
- [x] Ignored-lesson flags cite existing lessons by path and explain the gap.
- [x] Action items are specific with an owner and a clear next step.
- [x] Takeaways are heuristics, not platitudes — someone could apply them next sprint.
- [x] "What went well" is honest, not inflated to balance criticism.
- [x] No blame language — focus on decisions and processes, not people.
