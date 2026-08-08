---
title: Refactor /learn skill to groom pattern with unified review table and debug mode
type: refactoring
status: done
sp: 11
source: requests/20260423-refactor-learn-skill.md
created: 2026-04-23 00:00
planned: 2026-04-23
started: 2026-04-23
completed: 2026-04-23 00:00
retro: skipped
goal: skipped
summary: "/learn rewritten to groom shape: unified accept/reject review table across all targets, plus a plugin debug mode"
---

# Refactor /learn skill to groom pattern with unified review table and debug mode

## Context

`/learn` is the last stale skill in the four-skill core (`groom`, `develop`, `chat`, `retro`, `learn`). The 2026-04-23 retro (`retrospectives/20260423-skill-refactors-chat-develop-retro.md`) generated three action items explicitly tagged "Owner: /learn next invocation" — those need a working `/learn` to land. The current `skills/learn/SKILL.md`:

- Predates the Preflight-loads-partials pattern.
- Names `booping-techlead`, `booping-product-manager`, `booping-qa-lead` for Phase 1 classification — those agents were deleted in the same retro that produced the action items waiting on us.
- References `docs/partial_plan_transitions_learn.md` which doesn't exist (broken include).
- Has no user-facing review table — Phase 2 writes lessons, Phase 3 writes extensions, Phase 4 writes CLAUDE.md, each in a different cadence.
- Has no concept of debug mode (editing the plugin codebase from `/learn` when the user is shaping the framework itself).

Lesson 0003 ("refactor grooms probe delegation and deletion before v1") was applied in this groom's Phase 0. **Probe answers**:

- *Delegation*: techlead/PM/QA fan-out is dead (those agents were deleted in the 2026-04 retro). Researcher delegation adds a hop without protecting context — the retro is small and structured. Verdict: inline orchestrator extraction (encoded as D3).
- *Deletion*: dormant surfaces in the old `/learn` to remove — (a) the three role-agent classification calls (no longer exist), (b) the per-target separate confirmation flows (replaced by the unified table per user choice — encoded as D2), (c) the metrics initialization in Phase 5 (already a no-op since `/develop` writes the lesson-hits row). All three are gone in the new shape.
- *User-facing decisions probed via AskUserQuestion in Phase 2*: flag location (→ D1), confirmation cadence (→ D2 unified table), extension threshold (→ D4 always-create-on-first-applicable).

Lesson 0001 ("every loaded lesson leaves a plan trace") is honoured in **Applies lessons** below.

## Business goal

A `/learn` invocation that turns a retrospective into accepted, written changes across lessons, project-local extensions, and (in debug mode) plugin-side edits — surfacing every candidate in one review table the user can accept/reject/extend in a single pass, with no dependency on deleted role agents.

## Definition of Done

- [x] `skills/learn/SKILL.md` matches the groom shape: Preflight section that loads partials → numbered Phases → scoped Hard rules. Body ≤ ~160 lines.
- [x] Preflight references and includes (by relative path) every partial / template it relies on: `partial_project_resolution`, `partial_plan_statuses`, `partial_read_lessons`, `partial_plan_transitions_learn` (new), `partial_learn_targets` (new), `partial_debug_learn` (new), `template_learn_review_table` (new).
- [x] `docs/partial_plan_transitions_learn.md` exists and documents only `awaiting-learning → done` (the sole transition `/learn` owns).
- [x] `docs/partial_learn_targets.md` exists and documents the Type→Holds→Picked-when matrix for the five base types (`lesson`, `skill-ext`, `agent-ext`, `vault-claude-md`, `repo-claude-md`).
- [x] `docs/partial_debug_learn.md` exists, runs a mechanical `test -f <skill-dir>/.debug_enabled` (no hardcoded path), and emits an activation block extending the matrix with plugin-* types when the flag is present.
- [x] `docs/template_learn_review_table.md` exists and documents the unified review table format (columns, ordering, accept/reject, user-row-add, multi-target-split rule).
- [x] `.debug_enabled` is added to the plugin repo's `.gitignore` (bare entry, no directory prefix — matches anywhere).
- [x] `/learn` extracts candidates inline (no `booping-techlead` / `booping-product-manager` / `booping-qa-lead` references anywhere in the body — those agents are deleted).
- [x] `/learn` Phase 2 presents a single unified review table with columns `# | Target | Type | Brief description`, where `Type ∈ { lesson, skill-ext, agent-ext, vault-claude-md, repo-claude-md, plugin-skill, plugin-agent, plugin-partial }`. The plugin-* types appear only when `.debug_enabled` is present.
- [x] `/learn` Phase 4 (Framework review) is documented and runs in both modes — produces project-local extensions by default; produces plugin-edit candidates additionally when debug is on.
- [x] `/learn` writes lessons using `docs/template_lesson.md` (one rule per file, `Rule / Why / How to apply` body).
- [x] `/learn`'s "What learn does NOT do" section is silent on debug mode entirely (the default-behaviour SKILL body contains no debug-mode language; the additive debug behaviour is exclusively the partial's responsibility).
- [x] CLAUDE.md status section in the plugin repo flips `skills/learn/` from the stale list to the trustworthy list.
- [x] The plugin's `skills/help/SKILL.md` description of `/learn` matches the new behaviour (inputs, outputs, debug-mode mention).
- [x] No remaining reference in the plugin to `booping-techlead`, `booping-product-manager`, `booping-qa-lead`, `booping-teamlead`, or `booping-reviewer` outside of historical retros / lesson files.

## Design

### Architecture

The skill body becomes a thin orchestrator over partials and a single user-review table. Layered read-path:

```
/learn invocation
  ↓ Preflight loads → partial_project_resolution
                     → partial_plan_statuses
                     → partial_read_lessons  (loads ~/Claude/{project}/lessons/)
                     → partial_plan_transitions_learn  (NEW)
                     → partial_learn_targets         (NEW; the Type→Holds→Picked-when matrix)
                     → partial_debug_learn           (NEW; mechanical Bash test in skill dir;
                                                      activation block extends the matrix with
                                                      plugin-* types when debug is active)
                     → template_learn_review_table   (NEW; format for Phase 2's user-facing table)
                     → ~/Claude/{project}/_booping/skill_learn.md  (if present)
  ↓ Phase 0  Intake — resolve retro path, validate awaiting-learning status
  ↓ Phase 1  Extract candidate patterns inline (no role-agent fan-out)
  ↓ Phase 1.5 Update-vs-create + outdated sweep across existing lessons
  ↓ Phase 2  Present unified review table → user accepts / rejects / adds
  ↓ Phase 3  Write accepted items per target type (single pass, no per-edit prompts)
  ↓ Phase 4  Framework review — propose extensions where the retro patterns indicate
              a plugin skill or agent would benefit (extensions land in vault by default;
              plugin-side edits land only when .debug_enabled is set)
  ↓ Phase 5  Transition awaiting-learning → done; commit vault (and plugin repo when debug on)
```

The unified review table is the single user-facing review surface. The user does not see three separate confirmation flows for lessons, extensions, and CLAUDE.md edits — they see one table and one accept/reject/add interaction. After the table is accepted, the skill writes everything in one pass, then commits.

The debug toggle is a sentinel file at the plugin repo root, not a flag passed through the skill. `partial_debug_learn.md` reads the file's existence at Preflight and renders conditional instructions in-line — the rest of the skill body is identical in both modes; debug mode just unlocks additional rows in the review table.

### Decisions

| # | Decision | Alternative considered | Why this one |
|---|----------|------------------------|--------------|
| D1 | `.debug_enabled` lives **alongside the calling SKILL.md** (e.g. `skills/learn/.debug_enabled`), gitignored. The path is **never hardcoded** in any file — the partial expresses the location as "the same directory as the SKILL.md that loaded this partial", and the orchestrator resolves it from its own context (it knows where it just read SKILL.md from). | (a) Plugin repo root, (b) vault root, (c) `~/.claude/booping-debug` | The toggle's purpose is "I am developing the booping plugin itself", which is per-skill granular — different skills could have their own debug toggles in future. Per-skill placement removes the install-path coupling: the same partial works regardless of where the plugin is checked out. The user's assertion holds: if the orchestrator can read the partial at all, it knows the skill directory. The `.gitignore` entry `.debug_enabled` (bare, no directory prefix) catches the file anywhere it appears. |
| D2 | Unified review table for ALL learning categories (lessons + extensions + CLAUDE.md + plugin edits when debug) | Per-category confirmation flows (legacy /learn shape with separate Phase 3 / Phase 4 prompts) | User explicitly chose the table: one review surface, one accept/reject/add pass. Collapses three prompt cadences into one and forces the orchestrator to be honest about the full delta before any write. |
| D3 | Inline orchestrator extraction in Phase 1 (no agent delegation) | Delegate classification to role agents (techlead/PM/QA — old shape) or to a single researcher | Those role agents were deleted in the 2026-04 retro. Inline extraction matches /retro's "orchestrator owns synthesis" pattern. The retro is short and structured; researcher delegation would burn a hop with no context-protection benefit. |
| D4 | Always create/update an extension file on the first applicable pattern | Aggregate first; only materialize the extension when 2+ patterns target it | User picked "always". Consistent file-existence rule — no "is there an extension yet?" branch later. |
| D5 | Lessons stay one-rule-per-file using existing `docs/template_lesson.md` | Adopt aurora-api multi-rule lesson shape | Existing template already encodes the user's preferred shape ("compact, 1 file one lesson"). Aurora-api is content-style inspiration, not a structural model. |
| D6 | Debug-mode short-circuit is **mechanical, not prose-based**, and isolated entirely inside `partial_debug_learn.md`. The partial opens with: "Run `test -f <skill-dir>/.debug_enabled` where `<skill-dir>` is the directory of the SKILL.md that loaded this partial (the orchestrator resolves this from its own context — never hardcoded). Exit code 1: do nothing further; the activation block below is dead context. Exit code 0: record `debug_active=true` and apply the activation block." The SKILL body itself never runs the test, never names the flag, never names plugin-edit targets, never names additional review-table types, and never contains the phrase "debug mode" — those live only in the partial. | (a) Body-side `<debug_only>` block, (b) plain-prose "ignore the rest" guard relying on LLM compliance with no Bash test, (c) Bash test in the SKILL body itself, (d) mention debug-mode types in the SKILL body and let the partial only "activate" them, (e) hardcode the flag absolute path inside the partial | (a) invents a template language. (b) Cross-validation flagged this as unreliable — mechanical Bash test + recorded verdict is robust. (c) leaks the flag path into the SKILL body — defeats D6's isolation goal. (d) rots context for every non-debug invocation. (e) couples the partial to a specific install path (rejected per D1). The current shape (Bash test + activation block both inside the partial, path resolved from caller context) keeps debug context cost ≈ short paragraph and the SKILL body identical for debug and non-debug readers; the orchestrator's downstream branches are on the partial-recorded verdict. |
| D7 | Framework review (Phase 4) runs in both modes; debug only adds the plugin-edit option | Framework review runs only in debug mode | The default value of "scan plugin skills and propose `_booping/skill_<name>.md` extensions" is real — extensions land in the user's vault even with debug off. Debug only unlocks the additional plugin-edit channel. |
| D8 | Plan transition `awaiting-learning → done` is the only transition `/learn` owns | Also handle `awaiting-learning → cancelled` for retros that conclude "no lessons worth keeping" | Out of scope. `cancelled` is for product/priority shelving, not "/learn ran and decided nothing was actionable". A retro that yields no lessons still transitions to `done` — it has been processed. |
| D9 | Zero concrete-vault-file *instance* references in the SKILL body (no `lessons/0003_my-rule.md` style). **Path templates** like `lessons/{N}_<kebab>.md` and `_booping/skill_<name>.md` are allowed and required — Phase 3 needs them to construct write paths. | Inline a few canonical instance examples for clarity, OR forbid path templates too (would leave Phase 3 without write-path guidance) | Same rule applied in /retro refactor (D9 there). Concrete *examples* are project-specific — they live in `_booping/skill_learn.md`. *Templates* with placeholder syntax are wide-domain construction recipes, not instances; the SKILL must carry them so Phase 3's writes are deterministic. |
| D10 | Plugin-side edits in debug mode are written by the orchestrator inline (not delegated to a worker agent) | Delegate plugin edits to `booping-developer-senior` | Plugin edits in debug mode are rare, mechanical (file edits), and the orchestrator already has the diff. Delegating would move the diff context out of the orchestrator's hand and require a briefing for what is essentially "apply this Edit". The user-review table already contains the description; the Edit is a 1-2 line application. |
| D11 | Each accepted learning lands in **exactly one** target. A retro insight that covers two genuinely distinct rules is decomposed into two rows in the review table; the same rule must never be routed to two targets simultaneously. The single-location decision matrix lives in its own partial (`partial_learn_targets.md` per D12), not in the SKILL body. | Allow a single learning to land in lessons + extension + CLAUDE.md if "all three are relevant" (the existing `/learn`'s implicit shape) | Duplication across targets is silent drift waiting to happen — one copy gets edited, the others rot. The matrix forces the orchestrator to make the routing decision once, explicitly. Decomposition is the escape hatch for genuinely multi-rule insights; it forces the orchestrator to be honest about whether it's two rules (split into two rows) or one rule (pick one target). |
| D12 | The single-location decision matrix (Type → Holds → Picked-when) lives in its own partial: `docs/partial_learn_targets.md`. The SKILL body's Phase 1 references it. `partial_debug_learn`'s activation block extends the same matrix vocabulary with the three plugin-* types when active. | Inline the matrix in the SKILL body (the previous shape) | Per the user's instruction: "learning types mappings should be in partial". Extraction has three benefits: (a) SKILL body stays leaner; (b) the matrix is now a tunable policy artefact — projects with different methodology can override the matrix in `_booping/skill_learn.md` without rewriting the SKILL; (c) the partial becomes the single referenceable definition of the type vocabulary, which `partial_debug_learn` extends rather than parallel-defines. |
| D13 | The unified review table format lives in its own template: `docs/template_learn_review_table.md`. The SKILL body's Phase 2 references it. The template documents columns, ordering, accept/reject markers, the user-row-add convention, and the multi-target-split rule. | Inline the table format in the SKILL body | Per the user's instruction: "learn report template can be extracted to templates". The review-table format is a copy-into-place artefact — the SKILL constructs an instance of it per run. Extracting follows the same pattern as `template_retrospective.md` for `/retro`. Keeps the SKILL body focused on flow, not on artefact-construction details. |

### Applies lessons

- `lessons/0001_every-loaded-lesson-leaves-a-plan-trace.md` — every loaded lesson must be accounted for in the plan; this section is the trace.
  - 0001 itself: applies. The "every loaded lesson leaves a plan trace" principle is what this very section enforces.
  - 0002 (audit-workers-emit-verifier-output): applies in M3's audit task — Task 3.3's DoD requires the worker to paste `grep -E ...` output verbatim, not a prose claim.
  - 0003 (refactor-grooms-probe-delegation-and-deletion-before-v1): applied **at this groom's Phase 0**. Probed delegation: classification fan-out to role agents is dead; inline extraction is the right shape. Probed deletion: nothing in the new `/learn` body needs the dormant role agents; references removed.
  - 0004 (information-architecture-pattern): applies to every artefact this plan ships — SKILL body, two new partials, CLAUDE.md edit, help-skill description. Each must pass the four-check pass before the milestone closes (Verify commands enforce mechanical checks where possible).
- Lesson 0004's "no leakage" rule applies to the plugin-side edits unlocked by debug mode: `partial_debug_learn.md` must not name lessons, plan statuses, or vault paths that the plugin-side reader (a fresh agent in the plugin repo) doesn't need.

## Milestones

### M1: Partials + template + .gitignore — 5 SP | done

**Goal**: Land the three new partials (`partial_plan_transitions_learn`, `partial_learn_targets`, `partial_debug_learn`), the new template (`template_learn_review_table`), and gitignore `.debug_enabled` so the SKILL rewrite in M2 can reference them as live includes.

**Verify**:

```bash
ls /home/anton/Dev/@A/claude-booping/docs/partial_plan_transitions_learn.md \
   /home/anton/Dev/@A/claude-booping/docs/partial_learn_targets.md \
   /home/anton/Dev/@A/claude-booping/docs/partial_debug_learn.md \
   /home/anton/Dev/@A/claude-booping/docs/template_learn_review_table.md
grep -E '^\.debug_enabled$' /home/anton/Dev/@A/claude-booping/.gitignore
grep -E 'awaiting-learning' /home/anton/Dev/@A/claude-booping/docs/partial_plan_transitions_learn.md
# partial_debug_learn names the mechanical test but NOT a hardcoded absolute path
grep -E 'test -f' /home/anton/Dev/@A/claude-booping/docs/partial_debug_learn.md
grep -nE '/home/anton/Dev/@A/claude-booping' /home/anton/Dev/@A/claude-booping/docs/partial_debug_learn.md \
  && { echo "FAIL: hardcoded plugin path in partial_debug_learn"; exit 1; } \
  || echo "OK no hardcoded path"
# partial_learn_targets enumerates the base type vocabulary
for t in lesson skill-ext agent-ext vault-claude-md repo-claude-md; do
  grep -q "$t" /home/anton/Dev/@A/claude-booping/docs/partial_learn_targets.md \
    && echo "OK $t" \
    || { echo "MISSING type $t"; exit 1; }
done
# template_learn_review_table documents the column shape
grep -qE 'Target.*Type.*Brief description' /home/anton/Dev/@A/claude-booping/docs/template_learn_review_table.md \
  && echo "OK table columns documented" \
  || { echo "FAIL: table column documentation missing"; exit 1; }
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Write `docs/partial_plan_transitions_learn.md` documenting the sole `awaiting-learning → done` transition (date field set: `completed: <today>`). Mirror the structure of `partial_plan_transitions_retro.md` (intro sentence, transition table, edit guidance, verify command). | `docs/partial_plan_transitions_learn.md` (new) | 1 | done |
| 1.2 | Write `docs/partial_debug_learn.md`. Structure: opens with a **mechanical guard** as the first instruction (per D6 + D1) — ``Run `test -f <skill-dir>/.debug_enabled` via Bash, where `<skill-dir>` is the directory containing the SKILL.md that loaded this partial (the orchestrator resolves this from its own context — never hardcoded; if Claude Code can read this partial, it knows the skill directory). Exit code 1: do nothing further with this partial; the activation block below is dead context. Exit code 0: record `debug_active=true` and apply the activation block.`` The activation block (everything below the guard) declares: (a) three additional review-table row types `plugin-skill | plugin-agent | plugin-partial` that EXTEND the matrix vocabulary defined in `partial_learn_targets.md`; (b) the plugin-side commit shape using a `cd` boundary derived from `<skill-dir>` (e.g. `cd $(dirname $(dirname <skill-dir>))` to reach the plugin repo root if needed, OR rely on the orchestrator already knowing the plugin repo root from the SKILL location — also non-hardcoded). The partial MUST NOT contain any absolute path string (`/home/anton/...`) anywhere in its body. | `docs/partial_debug_learn.md` (new) | 1 | done |
| 1.3 | Add `.debug_enabled` to `/home/anton/Dev/@A/claude-booping/.gitignore` as a bare line (no directory prefix — matches the file anywhere it appears, including the future case where another skill grows its own debug toggle). | `/home/anton/Dev/@A/claude-booping/.gitignore` | 1 | done |
| 1.4 | Write `docs/partial_learn_targets.md` — the single-location decision matrix. Body: short intro paragraph stating the matrix is the canonical Type→Holds→Picked-when vocabulary for `/learn` candidates; one-table with columns `Type | Holds | Picked when`, populated for the five base types: `lesson` (cross-cutting principle that constrains future planning or implementation across multiple components — pick when the rule generalizes beyond a single skill or agent); `skill-ext` (methodology change for one named skill in this project — pick when the rule is a per-skill behaviour tweak); `agent-ext` (extra instruction for one named agent in this project — pick when the rule changes how a specific agent does its work); `vault-claude-md` (project-fact for the vault — pick when it's a navigation aid for vault structure or vault-side conventions); `repo-claude-md` (project-fact for the attached repo — pick when it's a layout/command/convention a fresh agent reading the repo needs); below the table, the decomposition rule: "If a candidate would otherwise span two targets, decompose into two distinct rows; never duplicate the same rule across targets." Below that, an "Extending the matrix" note that says other partials (such as `partial_debug_learn`) may add additional rows to this matrix at runtime. | `docs/partial_learn_targets.md` (new) | 1 | done |
| 1.5 | Write `docs/template_learn_review_table.md` — the unified review table template. Body: short intro stating this template is rendered by `/learn` Phase 2 inside an AskUserQuestion call; canonical column header (`# | Target | Type | Brief description`); per-row guidance (`#` is a stable per-run integer; `Target` is the path or path-template the write will land on; `Type` is one of the values from `partial_learn_targets.md` — including any extensions activated by other partials; `Brief description` is one sentence describing the rule); user interaction conventions: accept-all is the default, individual rows are rejected by name, new rows can be added by the user with the same column shape; the multi-target-split rule: "If a user-added row's `Brief description` covers two distinct rules, the orchestrator splits it into two rows before any write." | `docs/template_learn_review_table.md` (new) | 1 | done |

#### Task 1.1 DoD

- [x] File exists at `docs/partial_plan_transitions_learn.md`.
- [x] Documents one transition row: `awaiting-learning → done`, also-set `completed: YYYY-MM-DD` (today).
- [x] Includes the `booping-plans --status done` verification command.
- [x] Body shape parallels `partial_plan_transitions_retro.md` (intro line, table, edit guidance, verify).
- [x] No reference to other transitions (`/learn` only owns the one).

#### Task 1.2 DoD

- [x] File exists at `docs/partial_debug_learn.md`.
- [x] First instruction block is the **mechanical guard** that names the Bash test against `<skill-dir>/.debug_enabled` (placeholder syntax `<skill-dir>` resolved by the orchestrator), with exit-0 vs exit-1 branches both explicit.
- [x] Activation block (everything below the guard) lists the three additional review-table types: `plugin-skill`, `plugin-agent`, `plugin-partial`, and explicitly states they EXTEND the matrix from `partial_learn_targets.md` (rather than parallel-defining their own type system).
- [x] Activation block pins the commit shape to use a `cd <plugin-repo-root> && git add ... && git commit -m "..."` boundary; the plugin repo root is derived from `<skill-dir>` (e.g. `dirname dirname <skill-dir>` from a `skills/<name>/` skill), not hardcoded.
- [x] Does not leak vault concepts (concrete lessons paths, plan statuses, the word "lesson" outside the framing line that says the SKILL reads this partial) into the plugin-side instructions.
- [x] **No absolute path string anywhere in the body.** Verifier: `grep -nE '/home/|/Users/|/Dev/' docs/partial_debug_learn.md` returns no matches.
- [x] Body ≤ ~50 lines.
- [x] Verifier (run at M1 close): `head -10 /home/anton/Dev/@A/claude-booping/docs/partial_debug_learn.md | grep -E 'test -f.*\.debug_enabled'` returns at least one line, confirming the mechanical guard is the lead content.

#### Task 1.3 DoD

- [x] `.debug_enabled` appears on its own line in the plugin repo `.gitignore` as a bare entry (no directory prefix).
- [x] No other lines in the gitignore are touched.
- [x] `git check-ignore /home/anton/Dev/@A/claude-booping/skills/learn/.debug_enabled` exits 0 (file would be ignored if created in the skill directory).

#### Task 1.4 DoD

- [x] File exists at `docs/partial_learn_targets.md`.
- [x] Contains a single matrix table with columns `Type | Holds | Picked when` and rows for all five base types: `lesson`, `skill-ext`, `agent-ext`, `vault-claude-md`, `repo-claude-md`.
- [x] Each `Picked when` cell describes a deterministic test the orchestrator can apply (not a vague heuristic like "use your judgement").
- [x] Below the table, an explicit decomposition rule: "If a candidate would otherwise span two targets, decompose into two distinct rows; never duplicate the same rule across targets."
- [x] An "Extending the matrix" note documents that other partials (such as `partial_debug_learn`) may activate additional types at runtime.
- [x] Body ≤ ~60 lines.

#### Task 1.5 DoD

- [x] File exists at `docs/template_learn_review_table.md`.
- [x] Documents the canonical column header `# | Target | Type | Brief description`.
- [x] Per-row guidance covers: stable integer for `#`; path-or-path-template for `Target`; the `Type` is sourced from `partial_learn_targets.md` (including any extensions); one-sentence `Brief description`.
- [x] User interaction conventions documented: accept-all default, individual rejection by row number, user-added rows use the same column shape.
- [x] Multi-target-split rule documented: "If a user-added row's `Brief description` covers two distinct rules, the orchestrator splits it into two rows before any write."
- [x] Body ≤ ~60 lines.

---

### M2: Rewrite skills/learn/SKILL.md to groom shape — 4 SP | done

**Goal**: Replace the stale `skills/learn/SKILL.md` body with the new groom-shape implementation, wired to M1's partials, with the unified review table as the single user-facing surface.

**Verify**:

```bash
# Body shape: Preflight + numbered Phases (0..N) + Hard rules
grep -E '^## (Preflight|Phase [0-9]|Hard rules|What learn does NOT do)' /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md

# All Preflight partials + the template referenced
for p in partial_project_resolution partial_plan_statuses partial_read_lessons \
         partial_plan_transitions_learn partial_learn_targets partial_debug_learn \
         template_learn_review_table; do
  grep -q "$p" /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md \
    && echo "OK $p" \
    || { echo "MISSING $p"; exit 1; }
done

# Deleted agents must not appear
grep -nE 'booping-(techlead|product-manager|qa-lead|teamlead|reviewer)' \
  /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md \
  && { echo "FAIL: deleted agent referenced"; exit 1; } \
  || echo "OK no deleted-agent refs"

# Zero concrete vault-file INSTANCE references in the body (per D9). Templates like `lessons/{N}_<kebab>.md` are allowed.
grep -nE 'lessons/[0-9]{4}_[a-z]' /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md \
  && { echo "FAIL: concrete lesson instance in skill body"; exit 1; } \
  || echo "OK no concrete vault instance refs"
# Path templates ARE present (Phase 3 needs them)
grep -qE 'lessons/\{N\}|_booping/skill_<name>|_booping/agent_<name>' /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md \
  && echo "OK path templates present" \
  || { echo "FAIL: path templates missing — Phase 3 cannot construct writes"; exit 1; }

# Body length sanity
test "$(wc -l < /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md)" -le 220 \
  && echo "OK length" \
  || echo "WARN length"

# Mechanical Bash short-circuit for debug-mode is documented in Preflight (per D6)
grep -qE 'test -f.*\.debug_enabled|debug_active' /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md \
  && { echo "FAIL: SKILL body names .debug_enabled/debug_active — must live only in partial_debug_learn"; exit 1; } \
  || echo "OK no debug tokens in SKILL body"
# (Note: the test command itself goes in the partial; the SKILL Preflight delegates to it via 'load partial_debug_learn'.)

# No debug-mode leakage in the SKILL body (per D6) — these tokens belong only to partial_debug_learn.md
grep -nE '\.debug_enabled|plugin-(skill|agent|partial)|debug mode|debug_enabled' \
  /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md \
  && { echo "FAIL: debug-mode leakage in SKILL body"; exit 1; } \
  || echo "OK no debug leakage"

# Single-location rule referenced in SKILL body (matrix itself lives in partial_learn_targets per D12)
grep -qE 'one target|exactly one|single.location' /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md \
  && echo "OK single-location rule referenced" \
  || { echo "FAIL: single-location rule missing"; exit 1; }
# Matrix table itself MUST NOT be inlined in SKILL body — it lives only in partial_learn_targets
grep -qE '^\| Type \| Holds \| Picked when \|' /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md \
  && { echo "FAIL: matrix table inlined in SKILL — must live only in partial_learn_targets"; exit 1; } \
  || echo "OK matrix table not inlined"
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Rewrite `skills/learn/SKILL.md` end-to-end. New structure: frontmatter (keep `user-invocable: true`, `argument-hint: [retrospective file path]`, allowed-tools include `Read/Write/Edit/Glob/Grep/Bash(ls *)/Bash(test *)/Bash(git add *)/Bash(git commit *)/Bash(grep *)/AskUserQuestion`, `effort: xhigh`); Preflight loads ALL of `partial_project_resolution`, `partial_plan_statuses`, `partial_read_lessons`, `partial_plan_transitions_learn`, `partial_learn_targets`, `partial_debug_learn`, `template_learn_review_table`, plus `_booping/skill_learn.md` (the Preflight bullet for `partial_debug_learn` reads "Read [partial_debug_learn] — runs its own activation check and may extend the type vocabulary defined in `partial_learn_targets`"); High-level workflow (6 phases); a one-paragraph reference to `partial_learn_targets` for the single-location matrix (the matrix itself is NOT inlined per D12); Phase 0 Intake (resolve retro path, validate `awaiting-learning` status, stop with verbatim error if mismatched); Phase 1 Extract candidates inline (orchestrator reads retro's `What went wrong`, `Root causes`, `Action items`, `Takeaways` sections; **decomposes** each insight into atomic candidates BEFORE target assignment; categorizes each candidate using the matrix from `partial_learn_targets` — and admits the available type set for the run is `BASE_TYPES ∪ types-activated-by-loaded-partials` (without enumerating the partial-activated types — that would re-leak debug content)); Phase 1.5 Update-vs-create sweep — for each candidate the orchestrator first lists `~/Claude/{project_name}/lessons/`, then `ls ~/Claude/{project_name}/_booping/` and reads ONLY the `_booping/` files whose name matches a candidate-relevant skill/agent (filter, don't dump), then reads vault CLAUDE.md and repo CLAUDE.md (one-shot, lightweight files); decides for each candidate whether it duplicates an existing rule at ANY target — if yes, the candidate is an update of that existing target, not a new write to a different target; Phase 2 Present the unified review table via AskUserQuestion using the format from `template_learn_review_table` (no inline column documentation in the SKILL body — the template owns the format); Phase 3 Write accepted items in one pass per target type using path templates `lessons/{N}_<kebab>.md`, `_booping/skill_<name>.md`, `_booping/agent_<name>.md` (no per-edit confirmations — table acceptance is the consent); next lesson `{N}` computed from `ls lessons/` highest-prefix + 1; Phase 4 Framework review — list plugin `skills/` and `agents/` first; read ONLY the SKILL/agent files whose name appears in Phase 1's candidate list (filter, don't dump every file); if extension candidates surface, append additional rows to the table and re-confirm; Phase 5 Transition + commit (apply the `awaiting-learning → done` transition per `partial_plan_transitions_learn`; vault commit is pinned to the vault working directory: `cd ~/Claude/{project_name} && git add ... && git commit -m ...`; any plugin-related commit guidance — including its own `cd <plugin-repo>` boundary — comes from `partial_debug_learn` only). Hard rules section MUST include: (a) each learning lands in exactly one target, decomposition into multiple rows is the only escape hatch; (b) the SKILL body itself never names `.debug_enabled`, `plugin-skill`, `plugin-agent`, `plugin-partial`, or "debug mode" — those terms belong to `partial_debug_learn` only; (c) the SKILL body never inlines the matrix table itself — it lives in `partial_learn_targets`; (d) the SKILL body never inlines the review-table column-by-column documentation — it lives in `template_learn_review_table`. The body must contain zero concrete vault-file *instances*, zero references to deleted agents, zero leakage of stack details, and zero debug-mode tokens. | `skills/learn/SKILL.md` | 4 | done |

#### Task 2.1 DoD

- [x] Frontmatter intact: `name`, `description`, `argument-hint`, `user-invocable: true`, `allowed-tools`, `effort: xhigh`.
- [x] Preflight section references all six partials + the template by relative path (`../../docs/partial_*.md`, `../../docs/template_learn_review_table.md`) and `_booping/skill_learn.md` by absolute vault path.
- [x] High-level workflow lists 6 numbered phases.
- [x] A single-paragraph "Single-location rule" reference (placed between High-level workflow and Phase 0) points the reader at `partial_learn_targets.md` for the matrix and re-states the decomposition rule. **The matrix table itself is NOT inlined in the SKILL body** (lives only in `partial_learn_targets`).
- [x] Phase 2's documentation references `template_learn_review_table` for the column shape and user interaction conventions; **the column-by-column table description is NOT inlined in the SKILL body**.
- [x] Phase 0 includes the verbatim status-mismatch error string (parallels `/retro`'s pattern), e.g. `"/learn requires a plan in status 'awaiting-learning'; got '<current-status>' for <retro-path>. Run 'booping-plans --status awaiting-learning' to list candidates."`
- [x] Phase 1 names the retro sections it reads (`What went wrong`, `Root causes`, `Action items`, `Takeaways`), references `partial_learn_targets` as the matrix source, states that decomposition into atomic candidates happens BEFORE target assignment, and admits that the available type set for the run is `BASE_TYPES ∪ types-activated-by-loaded-partials` (without enumerating the partial-activated types — that would leak debug content).
- [x] Phase 1.5 documents the **filtered** sweep: `ls lessons/` + `ls _booping/`; read only `_booping/` files whose name matches a candidate-relevant skill/agent (no full-dump); read vault CLAUDE.md + repo CLAUDE.md (one-shot, lightweight). Sweep verdict for each candidate is one of: `new (no prior coverage)`, `update existing at target X`, or `conflict with existing at target X (surface to user in the table)`.
- [x] Phase 2 references `template_learn_review_table` for the table shape (column header, row conventions, accept/reject syntax, multi-target-split rule); **does not inline the column-by-column documentation**. The Phase 2 prose covers only the AskUserQuestion mechanics — the rest is the template's responsibility.
- [x] Phase 3 documents the single-pass write per target type using path templates (`lessons/{N}_<kebab>.md`, `_booping/skill_<name>.md`, `_booping/agent_<name>.md`); next lesson `{N}` is computed from `ls lessons/` (highest existing prefix + 1). No per-edit AskUserQuestion calls.
- [x] Phase 4 documents the **filtered** framework-review read: `ls skills/` + `ls agents/` first, then read only the files whose name is in Phase 1's candidate list. Appends rows to the table and re-confirms.
- [x] Phase 5 references `partial_plan_transitions_learn` for the transition mechanics; vault commit is pinned to `cd ~/Claude/{project_name}` to keep the working directory isolated. Plugin-related commit guidance (including its own `cd` boundary) comes from `partial_debug_learn`, not the SKILL body.
- [x] Hard rules section explicitly states: (a) orchestrator owns all writes; (b) no role-agent classification (those agents are deleted); (c) one rule per lesson file (template `docs/template_lesson.md`); (d) **each learning lands in exactly one target — decomposition is the only escape hatch**; (e) **the SKILL body never names `.debug_enabled`, `plugin-skill`, `plugin-agent`, `plugin-partial`, or "debug mode" — those terms belong to `partial_debug_learn` only**; (f) **the matrix table itself is not inlined — it lives in `partial_learn_targets`**; (g) **the review-table column-by-column documentation is not inlined — it lives in `template_learn_review_table`**.
- [x] "What learn does NOT do" section excludes status transitions other than `awaiting-learning → done`, and excludes regenerating `sprints.md` (chat owns that). It does NOT mention debug mode.
- [x] No reference to `booping-techlead`, `booping-product-manager`, `booping-qa-lead`, `booping-teamlead`, `booping-reviewer`.
- [x] No reference to a concrete lesson file (e.g. `lessons/0003_...`).
- [x] No occurrence of any of `.debug_enabled`, `plugin-skill`, `plugin-agent`, `plugin-partial`, `debug mode`, `debug_enabled` in the SKILL body (verifier in M2 Verify block enforces this).
- [x] Body line count ≤ ~220 (target ~160 — slightly larger than peer skills due to the matrix section).
- [x] All four checks of `lessons/0004_information-architecture-pattern.md` pass when the orchestrator reviews the new body before saving.

---

### M3: CLAUDE.md status flip + help-skill update + dead-reference audit — 2 SP | done

**Goal**: Reflect the new `/learn` in the plugin docs surface so a fresh agent reading the repo finds the trustworthy version, and confirm no stale references to deleted role agents linger anywhere in the plugin source.

**Verify**:

```bash
# CLAUDE.md status flip
grep -nE '^- `skills/(groom|chat|develop|retro|learn)/SKILL.md`' /home/anton/Dev/@A/claude-booping/CLAUDE.md
grep -nE 'skills/\{?install,help' /home/anton/Dev/@A/claude-booping/CLAUDE.md \
  && echo "OK install/help still in stale" \
  || echo "WARN install/help line shape changed"
grep -nE 'skills/\{?learn' /home/anton/Dev/@A/claude-booping/CLAUDE.md \
  && { echo "FAIL: learn still in stale list"; exit 1; } \
  || echo "OK learn no longer in stale list"

# help skill audit — current /learn description matches new behaviour
grep -nE 'learn|/learn' /home/anton/Dev/@A/claude-booping/skills/help/SKILL.md

# Dead-reference audit (plugin-wide)
grep -RnE 'booping-(techlead|product-manager|qa-lead|teamlead|reviewer)' \
  /home/anton/Dev/@A/claude-booping/skills /home/anton/Dev/@A/claude-booping/agents \
  /home/anton/Dev/@A/claude-booping/docs \
  2>/dev/null \
  && { echo "FAIL: deleted-agent reference still present in skills/agents/docs"; exit 1; } \
  || echo "OK no deleted-agent refs in skills/agents/docs"
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Edit plugin `CLAUDE.md`: add `skills/learn/SKILL.md` to the trustworthy list (alongside `groom/`, `chat/`, `develop/`, `retro/`); remove `learn` from the stale list (`skills/{install,help}/` only after this edit). Update the "When refactoring stale skills" partials list if `partial_plan_transitions_learn` and `partial_debug_learn` are referenced anywhere there. | `/home/anton/Dev/@A/claude-booping/CLAUDE.md` | 1 | done |
| 3.2 | Read the plugin `skills/help/SKILL.md`, identify every line that describes `/learn`, and update them to match new behaviour: inputs (retrospective path), outputs (lessons + extensions + optional plugin edits in debug mode), the unified review table mention, and the `awaiting-learning → done` transition it owns. Keep edits minimal — do not rewrite the help skill itself. | `/home/anton/Dev/@A/claude-booping/skills/help/SKILL.md` | 1 | done |
| 3.3 | Dead-reference audit. **Verifier**: ``grep -RnE 'booping-(techlead\|product-manager\|qa-lead\|teamlead\|reviewer)' /home/anton/Dev/@A/claude-booping/skills /home/anton/Dev/@A/claude-booping/agents /home/anton/Dev/@A/claude-booping/docs 2>/dev/null``. Worker MUST paste this exact command and its stdout (verbatim, including "no matches" if empty) in the Done report — prose claim alone is insufficient (Lesson 0002). If any match appears, fix it inline within scope (delete or replace) and re-run the verifier; both the pre-fix and post-fix verifier outputs go in the Done report. | `skills/`, `agents/`, `docs/` (read-only audit; edits scoped to whatever the audit surfaces) | 0 | done |

(Task 3.3 carries 0 SP — the work is enumerative and bundled into Task 3.2's briefing in practice; it's listed separately so the audit DoD is explicit.)

#### Task 3.1 DoD

- [x] Plugin `CLAUDE.md` "Current and trustworthy" bullet for skills lists all five: `groom`, `chat`, `develop`, `retro`, `learn`.
- [x] Plugin `CLAUDE.md` "Stale" bullet for skills lists only `{install,help}` (no `learn`).
- [x] No other lines in `CLAUDE.md` touched.

#### Task 3.2 DoD

- [x] Every line in `skills/help/SKILL.md` that mentions `/learn` reflects the new shape (inputs, outputs, debug-mode optional edits, the awaiting-learning→done transition).
- [x] No reference to deleted agents in the help skill.
- [x] Lines outside the `/learn`-describing scope are not edited.

#### Task 3.3 DoD

- [x] Worker Done report includes the verbatim grep command and its full stdout (or "no matches" indication).
- [x] If matches found: every match is either deleted or replaced; the grep is re-run and produces no matches; both passes are pasted in the Done report.
- [x] No false positives explained away — a deleted-agent name appearing in the body is a fail unless it's inside a code-fenced "do not use" example or a historical retro file (out of scope for this audit).

---

## Final Verification

```bash
# All M1 + M2 + M3 checks together
ls /home/anton/Dev/@A/claude-booping/docs/partial_plan_transitions_learn.md \
   /home/anton/Dev/@A/claude-booping/docs/partial_learn_targets.md \
   /home/anton/Dev/@A/claude-booping/docs/partial_debug_learn.md \
   /home/anton/Dev/@A/claude-booping/docs/template_learn_review_table.md
grep -E '^\.debug_enabled$' /home/anton/Dev/@A/claude-booping/.gitignore
grep -E '^## (Preflight|Phase [0-9]|Hard rules)' /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md
grep -nE 'booping-(techlead|product-manager|qa-lead|teamlead|reviewer)' \
  /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md \
  && { echo "FAIL"; exit 1; } || echo "OK SKILL clean"
grep -nE 'skills/\{?learn' /home/anton/Dev/@A/claude-booping/CLAUDE.md \
  && { echo "FAIL: learn still in stale list"; exit 1; } || echo "OK CLAUDE.md flipped"
grep -RnE 'booping-(techlead|product-manager|qa-lead|teamlead|reviewer)' \
  /home/anton/Dev/@A/claude-booping/skills /home/anton/Dev/@A/claude-booping/agents \
  /home/anton/Dev/@A/claude-booping/docs 2>/dev/null \
  && { echo "FAIL: stale agent refs"; exit 1; } || echo "OK plugin-wide clean"
grep -nE '\.debug_enabled|plugin-(skill|agent|partial)|debug mode|debug_enabled' \
  /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md \
  && { echo "FAIL: debug-mode leakage in SKILL body"; exit 1; } || echo "OK SKILL no debug leakage"
grep -qE 'one target|exactly one|single.location' \
  /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md \
  && echo "OK single-location rule referenced in SKILL" \
  || { echo "FAIL: single-location rule missing"; exit 1; }
grep -qE '^\| Type \| Holds \| Picked when \|' /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md \
  && { echo "FAIL: matrix inlined in SKILL — must live only in partial_learn_targets"; exit 1; } \
  || echo "OK matrix not inlined in SKILL"
# partial_debug_learn carries no absolute paths anywhere (per D1)
grep -nE '/home/|/Users/|/Dev/' /home/anton/Dev/@A/claude-booping/docs/partial_debug_learn.md \
  && { echo "FAIL: hardcoded absolute path in partial_debug_learn"; exit 1; } \
  || echo "OK partial_debug_learn has no hardcoded paths"
```

## Risk register

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Worker drifts and inlines a vault-concrete lesson reference in the new SKILL body (lesson 0004 leakage) | low | M2 Verify enforces `grep -nE 'lessons/[0-9]{4}_' SKILL.md` returns empty; checked at milestone close. |
| Worker forgets to delete the techlead/PM/QA Phase 1 block when rewriting | low | M2 Verify enforces plugin-wide grep for the five deleted agents; M3 Verify re-runs it across the whole plugin. |
| `.debug_enabled` partial body grows into a body-side conditional (templating language drift) | low | Task 1.2 DoD pins partial body shape: declarative prose + lead-position guard clause; verifier `head -20 partial_debug_learn.md \| grep -E 'ignore the rest\|debug.*off'` checks the guard is the lead. |
| **Debug-mode tokens leak into SKILL body, defeating D6's context-isolation goal** | medium | M2 Verify enforces `grep -nE '\.debug_enabled\|plugin-(skill\|agent\|partial)\|debug mode\|debug_enabled' SKILL.md` returns empty. Failure stops the milestone. |
| **Same rule routed to two targets, violating D11 single-location** | medium | M2 SKILL body's Phase 1.5 sweep + the matrix's decomposition rule make this a structural impossibility for orchestrator-extracted candidates. User-added candidates with multi-target nature get split by the orchestrator before write (called out in Phase 2 DoD). |
| Lessons-file template adoption skipped — worker writes a free-form lesson file | low | M2 SKILL body must reference `docs/template_lesson.md` as the lesson write target; lesson 0001 trace forces every lesson row in the review table to declare the template binding. |
| Lesson 0004 (no leakage) silently violated by `partial_debug_learn` (e.g. naming concrete vault paths or plan statuses inside the activation block) | medium | Task 1.2 DoD: "does not leak vault concepts" is checked at write time; `grep -nE 'lessons/[0-9]\|backlog\|in-progress\|awaiting-' partial_debug_learn.md` should produce zero matches inside the activation block (matches in the framing line that says the SKILL reads this partial are acceptable). |
| Lesson 0001 override row policy not yet codified — silent skips remain possible | medium | Out of scope for this plan (action item 1 from the trigger retro). The new `/learn` will produce that lesson on its first invocation; this plan's job is to ship the skill capable of producing it. |
| Lesson 0002 (audit verifier output) silently violated in M3 audit | low | Task 3.3 DoD requires verbatim grep + stdout in the Done report. Task 3.3 description carries an explicit `Verifier:` field naming the exact command. Briefing template (`partial_agents_mid_senior.md`) has not yet been updated for that universal rule (action item 2 from the trigger retro), so this plan's M3 briefing must spell the requirement out explicitly. |
| **Type-categorization paradox: SKILL body locks Phase 1 to base types and ignores partial-activated types** | medium | Task 2.1 description and DoD make it explicit that the available type set is `BASE_TYPES ∪ types-activated-by-loaded-partials`. The SKILL admits the union without enumerating the activated types (which would re-leak debug content). |
| **Path-template gap: D9 read too literally locks Phase 3 out of constructing write paths** | low | D9 wording explicitly distinguishes templates (allowed, required) from instances (forbidden). M2 Verify positively asserts templates are present; the instance-grep regex requires both `lessons/[0-9]{4}_` AND a kebab letter (`[a-z]`) so the template `lessons/{N}_<kebab>.md` does not falsely trigger. |
| **Context blowout in Phase 1.5 / Phase 4 from dumping every `_booping/` and plugin file** | medium | Task 2.1 description pins both phases to a `ls`-then-filter pattern: list directory, then read only the files whose names match candidate-relevant skill/agent identifiers. Vault and repo CLAUDE.md are tiny and read in full. |
| **Multi-repo git contamination: vault and plugin commits run from the wrong working directory** | medium | Vault commit shape is pinned in the SKILL body Phase 5 (`cd ~/Claude/{project_name} && git ...`). Plugin commit shape is pinned in `partial_debug_learn`'s activation block (`cd <plugin-repo-root> && git ...`, where `<plugin-repo-root>` is derived from the calling skill's directory — not hardcoded). Each `git` invocation is `cd`-scoped; no shared working-directory state between the two. |
| **Hardcoded plugin install path leaks into a partial, breaking portability for users with a different checkout location** | medium | M1 Verify enforces `grep -nE '/home/\|/Users/\|/Dev/' partial_debug_learn.md` returns no matches. Final Verification re-runs the same grep at sprint close. The placeholder `<skill-dir>` (and `<plugin-repo-root>` derived from it) is the only path expression in the partial. |
| **Matrix table or review-table format silently re-inlined in the SKILL body during the rewrite, defeating D12/D13** | low | M2 Verify positively asserts `grep -qE '^\| Type \| Holds \| Picked when \|' SKILL.md` returns nothing (matrix not inlined). The Phase 2 reference-to-template DoD bullet catches re-inlining of the table format. |
| **LLM-prose short-circuit: "ignore the rest of this partial" is unreliable for an LLM that processes the full context window** | medium | D6 replaces prose-based short-circuit with a mechanical Bash test (`test -f`). The orchestrator branches on the test's exit code (recorded as `debug_active=true|false`), not on prose interpretation. The activation block's content is still in the partial body, but the branch decision is mechanical. |

## Out of scope

- Implementing action items 1, 2, 4 from `retrospectives/20260423-skill-refactors-chat-develop-retro.md`. Those are the *consumers* of the new `/learn`; landing them is a follow-up `/learn` invocation against that retro, not part of this refactor.
- Refactoring `skills/install/SKILL.md` and `skills/help/SKILL.md` end-to-end. M3 only flips the CLAUDE.md status for `learn` (not install/help) and edits help-skill lines that describe `/learn` (not the rest of help).
- Refactoring `bin/booping-init` or `skills/install/template-claude-md.md`.
- Building a CLI/UI for toggling debug mode. The mechanism is `touch .debug_enabled` / `rm .debug_enabled` — no skill needed.
- Plugin-side metrics or change history when debug-mode edits land. The plugin-repo commit IS the history.

## CLAUDE.md impact

`/home/anton/Dev/@A/claude-booping/CLAUDE.md` has a Status section listing trustworthy and stale skills. M3 Task 3.1 owns the edit: add `skills/learn/SKILL.md` to the trustworthy bullet, remove `learn` from the stale bullet. No other CLAUDE.md sections are touched by this sprint.

The vault `~/Claude/claude-booping/CLAUDE.md` is not touched — the new `/learn` is wide-domain and project-local extensions live in `_booping/skill_learn.md`, not in CLAUDE.md.
