---
plans:
  - plans/20260608-plannotator-code-review-surface.md
date: 2026-06-10
goal_summary: Plannotator surface fully specced and wired via zero-core-change extension points, but the live round-trip (M4) was never run and the plan mis-specified the surface as optional/zero-touch — both required mid-sprint correction.
goal_verdicts:
  plans/20260608-plannotator-code-review-surface.md: partial
---

# Retrospective — Plannotator-backed code-review surface

## What went well

- **Zero-core-change architecture landed cleanly.** The integration attaches through two pre-existing booping extension points fed from the vault (`config.skills["code-review"].agents.<id>` registration + the `_extra_instructions(skill_code-review)` hook), so no structural change to the plugin core was needed to add a whole new review surface.
- **Two-layer transport split held.** Mechanical floor (`~/.claude/bin/booping-plannotator-review`: port, launch, poll, seed, capture, exit codes) vs interaction agent (`plannotator-reviewer`: findings→contract mapping, drive the script, return feedback). Port/poll/curl trivia stayed out of the prompt — lesson 0004 hierarchy applied correctly here.
- **Mechanism validated against the real binary before coding.** Endpoints, exit codes, the `external-annotations` contract, and `waitForDecision`/`transformReviewInput` were checked against `~/.local/bin/plannotator` plus a Gemini cross-validation. This caught the dead `--port` flag (the binary ignores it; `PLANNOTATOR_PORT` env is honored) before it became a runtime surprise.
- **Graceful degradation was a first-class contract**, not an afterthought: exit `3`/`4`/`5` → agent emits a degrade signal → caller falls back to chat-only, never hard-fails.

## What went wrong

#### /develop self-blocked on a repo-only constraint

**What happened**: At `/develop` intake the skill repeated the plan's own note — "developer agents touch only the attached repo, so they cannot build these artifacts" — and treated the whole plan as non-/develop-able manual authoring. The user overrode it: "no, you can do it … this limitation is artificial."

**Root cause**: A framework assumption (booping developer agents operate only inside the attached plugin repo) was promoted to a hard, plan-level execution-model invariant during groom, instead of being challenged. Deliverable *location* outside the repo was mistaken for *impossibility* of delegation.

**Impact**: Execution-time friction and a manual-authoring carve-out that wasn't actually necessary. The constraint was significant enough that the user filed a follow-up plan (`20260610-simplify-cli-delegation-to-global-agent`) to reverse it.

#### "ZERO touch" absolutism forced a plugin-repo edit

**What happened**: The plan made "ZERO Plannotator code in the booping repo / never touched" a hard invariant (Final Verification: `git status` must be empty). Making the surface mandatory then collided with the core skill's "output is chat-only" hard rule, and the only resolution was a generic softening clause added to core `code-review.md.j2` — a plugin-repo edit.

**Root cause**: The separation invariant was written as a blanket "never touch the repo at all" rather than the narrower intent it actually served — "no Plannotator-*specific* code in the repo." The over-broad form forbids even a generic, reusable extension-point edit, so an expected minor change reads as a violation.

**Impact**: A contradiction the implementer had to break unilaterally; the plan's central invariant was technically broken, and the user confirmed minor generic changes were in fact expected all along.

#### Surface mis-specified as optional

**What happened**: The plan described the Plannotator surface as "optional" with a chat-only fallback throughout (business_goal, Context, M3.2). Mid-sprint the implementer rewrote the vault extension to mandatory, no fallback. The user's clarification: Plannotator was always meant to be mandatory, vault-controlled, and guaranteed present — "I never mentioned it's optional."

**Root cause**: A load-bearing requirement (optional vs mandatory) was mis-captured at groom — "optional" was inferred as the safe default. The design then built opt-in/fallback machinery around the wrong assumption.

**Impact**: M3 work (opt-in prompts + chat-only fallback path) was built and then ripped out mid-sprint, and the correction landed off-plan without updating the plan or the sibling recipe doc — directly producing the next issue.

#### Stale plan/doc prose after in-sprint decisions

**What happened**: Several in-sprint decisions were recorded only as DoD deviation notes, leaving upstream prose stale: the recipe (`~/.claude/booping-plannotator-review.recipe.md`) still says "optional"/"opt in" while the extension is mandatory; the plan's Architecture and I/O-contract sections still document the dead `--port` flag and python-socket port picker; the M2 Goal still mentions the "kept/dismissed/added delta" that was moved to Out-of-scope.

**Root cause**: The plan and its sibling docs were treated as append-only (deviation noted at the DoD) rather than live documents updated in the same milestone — the exact gap lesson 0005 names.

**Impact**: Three inconsistent reference surfaces (plan prose, recipe, extension) that disagree on optional-vs-mandatory and on the port mechanism; a future reader can't trust any single one.

## Lesson gaps

- `lessons/0005_stale-reference-cleanup-belongs-in-sprint.md` — rule was "cleanup of references invalidated by a plan's own decisions belongs inside the same sprint with its own DoD," but here the optional→mandatory reversal and the `--port`→`PLANNOTATOR_PORT` deviation were left as DoD notes while the plan Architecture/IO-contract prose and the recipe were never reconciled, which caused issue #4.

## Action items & takeaways

| # | Type | Item | Owner | Status |
|---|------|------|-------|--------|
| 1 | Task | Fix recipe `~/.claude/booping-plannotator-review.recipe.md` optional→mandatory inline | Claude | Planned |
| 2 | Task | Reconcile plan prose inline: `--port`→`PLANNOTATOR_PORT`/`READY_FILE` in Architecture + I/O contract; drop "delta" from M2 Goal | Claude | Planned |
| 3 | Task | Run the M4 live end-to-end loop (seed→review→submit→feedback) on a real diff | User | Planned |
| 4 | Task | Fix wrong `/booping:compile` instruction (extension line 5) — global agents need no compile | User | Planned (separate) |
| 5 | Task | /develop repo-limitation reversal | — | Done — `20260610-simplify-cli-delegation-to-global-agent` filed |
| 6 | Heuristic | Optional-vs-mandatory is a load-bearing requirement — confirm it explicitly at groom before building fallback machinery; never infer "optional" as a safe default | standing | Planned |
| 7 | Heuristic | Scope separation invariants to the actual coupling being avoided ("no X-specific code"), not a blanket "never touch the repo" — absolutes force contradictions the implementer must break | standing | Planned |
| 8 | Heuristic | A deliverable living outside the attached repo (vault, `~/.claude/`) is a delegation-model question, not an automatic manual-authoring carve-out | standing | Planned |
| 9 | Heuristic | Plan prose is a live document — a DoD that records a deviation must update the upstream Architecture/contract in the same milestone (0005) | standing | Planned |
