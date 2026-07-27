# A/B check — monolithic /groom vs playbook-groom

Task 5.1 of "Groom-as-Playbook Pilot". Branch `feat/groom-as-playbook-pilot`.
Measured against project `claude-booping`, vault `/home/anton/Dev/@A/notes/projects/claude-booping` (**non-local vault** — `is_local_vault` false).

Sources compared:

- **OLD** — `bin/booping render src/templates/skills/groom.md.j2` (18 265 chars).
- **NEW** — `bin/booping render-playbook groom` (17 021 chars after stripping the stderr warning) + a driver body (`_project_context.j2` render + `_playbook_driving.j2` render + ~10 lines of skill instruction) + lazily fetched `--step` bodies.

---

## Part A — behavioral A/B

### Briefs

| # | Shape | Brief |
|---|-------|-------|
| B1 | bug, small | `Playbook.load_all` warns `playbook <dir>: no playbook.md, skipping` for **every** non-playbook subdirectory under a playbook root. Real symptom in this environment: `home_dir` resolves to `~/Dev/@A/notes/projects/`, so `<home_dir>/_playbooks/docs/` trips it and every `booping` invocation prints the warning to stderr. |
| B2 | feature, medium | Add `booping render-playbook <name> --wave N` — print every step body of wave N in one call, so a driver can fetch a whole parallel wave without one `--step` call per member. |
| B3 | refactoring, larger | De-duplicate the composed-render preamble: `_lessons.j2`, the `skill_<name>` extension block, and `## Project Context` are rendered both by a playbook's `playbook.md` preamble and by the driver skill. Extract so exactly one surface owns each. |

Both pipelines were walked as prompt-sets and the plan skeleton each would produce was derived. Skeletons are simulations, not executed groom runs; SP figures are indicative, the *shape* differences are the signal.

### B1 — bug (small)

| | OLD | NEW |
|---|---|---|
| Milestones | 1 (`Fix + regression test`) | 2 (`Silent skip`, `Regression test`) |
| Tasks | 2 | 2 |
| SP spread | 2 + 1 = 3 SP in one milestone | 1 / 1 = 2 SP |
| DoD specificity | "warning no longer emitted for non-playbook dirs; test added" | names `booping-python/src/booping/context/playbook.py:_load_one`, `tests/test_playbook.py`, and the verification commands `just test` / `bin/booping render-playbook groom 2>&1` producing no warning line; explicitly retains the `<step>/ has no prompt.md` warning |
| Branch offer | not rendered (non-local vault) | not rendered (non-local vault) — identical `is_local_vault` guard |
| Summary rule | fires (Craft bullet) | fires (`draft` step, item 3) |
| Approval gate | fires (Hard rules + transitions gate + Craft) | fires (Hard rules in preamble + `present` review-gate bullet + `present` body) |

Notes: NEW's `research-codebase` sub-agent returns a **Conventions** section ("build/test commands that must pass"), which is what pulls the concrete verification commands into the DoD. OLD has no equivalent forcing function — the commands only arrive if the model volunteers them. Cost: NEW imposes an unconditional `design` review gate on a 2 SP one-line fix; there is no trivial-work carve-out (the transitions table has one for cross-validation — "single-file-bug skip acceptable" — but no gate-skip exists at the playbook level).

### B2 — feature (medium)

| | OLD | NEW |
|---|---|---|
| Milestones | 4 (CLI arg + wave resolution / output format / tests / docs) | 5 (same four, plus a dedicated `--wave` ∥ `--step` contract milestone that falls out of the design step's *Surface changes* + *Out of scope* sections) |
| SP spread | 3 / 2 / 2 / 2 = 9 SP | 3 / 2 / 2 / 2 / 1 = 10 SP |
| DoD specificity | template `# Quality Checklist` driven; per-milestone bullets, verification commands sometimes generic (`tests pass`) | same checklist plus research-derived exact commands (`just lint`, `just typecheck`, `just test`, `bin/booping render-playbook groom --wave 2`), and out-of-scope stated per milestone |
| Branch offer | n/a here (non-local vault); identical text in both pipelines | same |
| Summary rule | fires | fires |
| Approval gate | fires | fires |

Notes: the open decision ("does `--wave` supersede `--step`? is N 1-based? are notices repeated?") is surfaced by the NEW `design` step's mandatory *Trade-offs* section and settled **before** any plan text is written. OLD tends to bake one interpretation into the drafted plan and expose it only at `present`, costing a re-draft loop. Lesson 0005 (stale-reference cleanup inside the sprint) is loaded in both, so the docs milestone appears in both. The `skill_groom` extension rule about a prose-reshape final milestone is present in both preambles.

### B3 — refactoring (larger)

| | OLD | NEW |
|---|---|---|
| Milestones | 5 (current-vs-target map / renderer change / template changes / golden tests / docs+CLAUDE.md) | 5–6 (same, with the ownership decision — driver-owns vs preamble-owns — pulled out as its own decision recorded in the plan) |
| SP spread | 3 / 4 / 3 / 3 / 2 = 15 SP | 2 / 4 / 3 / 3 / 2 (+1) = 14–15 SP |
| DoD specificity | no-behaviour-change DoD per `docs/task_refactoring.md` | same, plus a golden-output comparison DoD (`render` output before/after byte-identical except the removed block) traced to research **Conventions** |
| Branch offer / summary / approval | all fire | all fire |

Notes: this is where NEW's bounded research return contract bites. `research-codebase` caps at **≤15 blast-radius entries, ≤5 prior art, ≤5 conventions, ≤50 lines**. This refactor touches ~8 templates + 3 Python modules + tests, which fits, but a wider refactor would be silently truncated with no signal to the driver that the cap was hit. OLD's inline reading is unbounded (at the cost of context).

### Behavioral findings

Craft-bullet coverage is **complete** — every OLD `## Craft` bullet has an owner in NEW: challenge-scope → `intake`; review-the-codebase → `research-codebase`; research-when-uncertain + verify-external-references → `research-web`; draft-design-with-the-user → `design`; write-the-plan + write-`summary` + branch offer → `draft`; present-and-iterate → `present`. Hard rules, "What groom does NOT do", `## Plan editing`, the full transitions table, lessons, and the `skill_groom` extension all survive verbatim in the NEW preamble.

Strengthened in NEW:

1. **Positional anchoring.** The branch offer is now item 6 of `draft`, immediately before the `in-spec` move it protects — in OLD it is a Craft bullet with no positional anchor. Same for the summary rule and the estimation flow.
2. **Bounded returns.** Research runs in `booping:booping-researcher` with explicit return contracts, so blast-radius findings arrive compressed instead of rotting the driver context (lesson 0007 applied).
3. **Forced design/draft separation.** The `design` review gate makes design sign-off a hard stop. OLD can slide from a short question round straight into writing the plan file.
4. **Approval gate redundancy.** Explicit approval now appears in three places (preamble Hard rules, `present` review-gate bullet, `present` body) vs. three in OLD (Hard rules, Craft, transitions gate). Parity, both adequate.

Weakened or dropped in NEW:

1. **Agent roster is `design`-only.** `_available_agents.j2` renders inside `playbooks/groom/design/prompt.md` and nowhere else. Waves 1 and 2 still dispatch correctly (the composed section's `Run in sub-agent:` bullet names `booping:booping-researcher`), but the driver has no roster if it needs an ad-hoc delegation during `intake`, `draft`, or `present`.
2. **Resume paths skip task classification.** The preamble's resume rules allow re-entry at `research-codebase`, `design`, or `draft`. Task Classification and the matched `docs/task_<type>.md` load only in `intake`, so a resumed run at `draft` drafts without the type-specific guidance ever entering context. In a single unbroken run this is fine (all non-research steps run inline, so context carries).
3. **Web research is a one-shot byte-exact gate.** `intake` emits `web-research: yes|no`; on `no`, `research-web` never runs and `design` proceeds. The only escape hatch is the `design` step's "delegate a bounded follow-up", which is soft. OLD's "research when uncertain" applies at any moment with model judgment. Late-discovered external-reference uncertainty is more likely to slip through NEW.
4. **Review-gate text lives only in the composed doc.** `render-playbook groom --step present` output does **not** include the `review_gate` frontmatter — the gate text is emitted only by the composed render. If the driver's context is compacted between wave 1 and wave 5 and it re-fetches `--step present`, the explicit-approval gate text is gone. The transitions-table gate ("Explicit user approval captured") and the preamble Hard rule remain, so the gate degrades rather than vanishes — but the strongest phrasing is the one at risk.
5. **`_playbook_driving.j2` injects a wrong path.** The run-time context block appended to every step invocation is:
   ```
   specs_dir: {project directory}/specs
   project: {project name}
   ```
   The vault has no `specs/` directory — groom plans live in `plans/`. Any step that trusts `specs_dir` writes to the wrong place. `draft` happens to render its own absolute `.../plans/{YYYYMMDD}-{kebab-title}.md` path, so groom is not actually broken, but the injected value is wrong and contradicts it.
6. **No lessons reach research sub-agents.** The driving protocol appends only `specs_dir` + `project` to a step invocation. In OLD the whole run is one context that holds the lessons block. Groom's research steps do not currently need lessons, but the channel does not exist.
7. **Ceremony floor.** NEW imposes intake Q&A + design gate + present gate on every run regardless of size — 3 user stops minimum for a 2 SP bug. OLD's only mandatory stop is approval.
8. **Duplicate `## Project Context`.** Rendered by the driver and again inside the embedded `intake` body, including the "On skill load, report the resolved project context back to the user verbatim" instruction, which is no longer at skill load.
9. **Override-ordering prose is now positionally false.** The `skill_groom` extension block says "They override the skill instructions **above**", but in NEW it sits in the preamble *before* every step body.

---

## Part B — token counts

Estimator: chars / 4. Charged against the stderr-stripped composed render.

### Composition

| Component | Chars | ~Tokens |
|---|---:|---:|
| **OLD** — rendered `groom.md.j2` | 18 265 | 4 566 |
| NEW driver: `_project_context.j2` render | 365 | 91 |
| NEW driver: `_playbook_driving.j2` render | 2 005 | 501 |
| NEW driver: ~10 lines skill instruction (assumed) | 700 | 175 |
| NEW: `render-playbook groom` composed | 17 021 | 4 255 |
| **NEW-upfront total** | **20 091** | **5 023** |

### Deferred (lazy `--step` loads)

| Step | Chars | ~Tokens |
|---|---:|---:|
| `research-codebase` | 1 426 | 356 |
| `research-web` | 1 452 | 363 |
| `design` | 2 646 | 662 |
| `draft` | 6 539 | 1 635 |
| `present` | 919 | 230 |
| **Deferred total** | **12 982** | **3 246** |

(`intake` = 3 067 chars is not deferred — wave 1 is embedded in the composed render and already counted above.)

Full-run worst case (upfront + every deferred step, ignoring that `research-web` may be skipped): **33 073 chars / ~8 268 tokens** vs OLD **18 265 / ~4 566** — **+81 %**. Sub-agent steps do not land in the driver's context, so the realistic driver-side worst case is upfront + `design` + `draft` + `present` = **30 195 chars / ~7 549 tokens**, still **+65 %**.

### Where NEW-upfront spends its budget

| Block | Chars | Also in OLD? |
|---|---:|---|
| Plan Transitions table | 3 003 | yes (identical) |
| Lessons | 4 462 | yes (identical) |
| `skill_groom` user instructions | 1 269 | yes (identical) |
| Embedded `intake` body (incl. Project Context + Task Classification) | 3 269 | partly (692 of it is Task Classification) |
| Hard rules / does-NOT-do / Plan editing / header | 755 | yes |
| Conditional research wave | 656 | new |
| Resuming a groom run | 915 | new |
| Execution graph (mermaid + wave list) | 421 | new |
| 5 later-step stub sections | 2 271 | new |
| Driver body (project ctx + driving protocol + instruction) | 3 070 | new |

What NEW successfully defers: `## Sprint planning` (1 721) + `## Plan Structure` (3 272) → the `draft` step; `## Available Agents` (1 208) → the `design` step. **6 201 chars deferred.**

What NEW adds upfront: driving protocol + graph + stubs + conditional-research + resume + duplicated project context ≈ **7 400 chars**.

Net: **+1 826 chars, −10.0 %** (i.e. NEW-upfront is 10 % *larger* than OLD).

### Kill-criterion verdict

Criterion: NEW-upfront ≤ 70 % of OLD, i.e. ≤ 12 786 chars / ~3 196 tokens.

Measured: **20 091 chars / ~5 023 tokens = 110 % of OLD**. Reduction is **−10.0 %** (an increase). Shortfall to the threshold: **7 305 chars / ~1 826 tokens**.

**FAIL — the ≥30 % reduction kill criterion is not met, by a wide margin.**

Sensitivity — what would have to change to reach the bar:

| Variant | Chars | vs OLD |
|---|---:|---|
| As built | 20 091 | −10.0 % (fail) |
| Drop lessons + `skill_groom` block from the composed preamble (driver owns them, or they load lazily) | 14 360 | +21.4 % (still fail) |
| …and stop embedding the wave-1 (`intake`) body — make wave 1 lazy like every other wave | 11 091 | **+39.3 % (pass)** |

Both levers are structural properties of `render-playbook`, not of the groom playbook's authoring: the preamble is whatever `playbook.md` renders (currently `_lessons.j2` + `_extra_instructions.j2`), and wave-1 embedding is hardcoded composition behaviour. Groom-side trimming alone (tightening step prose) cannot close a 7 305-char gap — the five stub sections plus graph plus driving protocol total only 5 762 chars.

The honest framing: the playbook split buys **step-scoped context** and **bounded sub-agent returns**, not a smaller upfront load. If the kill criterion is meant to gate the rewire on upfront-token savings, it fails as measured; if the criterion can be restated as "no single step's context exceeds OLD" (max single-step context = upfront + `draft` = 26 630 chars for the inline driver, or 1 426–6 539 chars for a sub-agent step), the picture inverts for the delegated steps only.
